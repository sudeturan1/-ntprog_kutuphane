# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app,session
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        kullanici_adi = request.form['kullanici_adi']
        sifre = request.form['sifre']
        # Burada basit doğrulama (demo amaçlı)
        if kullanici_adi == 'admin' and sifre == 'admin123':
            session['admin_giris'] = True
            return redirect(url_for('main.index'))
        else:
            flash('Kullanıcı adı veya şifre yanlış!', 'danger')
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/index')
def index():
    conn = current_app.db
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM kitap")
    kitaplar = cur.fetchall()
    cur.close()
    return render_template('index.html', kitaplar=kitaplar)

    conn = current_app.db
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM kitap")
    kitaplar = cur.fetchall()
    cur.close()
    return render_template('index.html', kitaplar=kitaplar)

@main.route('/logout')
def logout():
    session.pop('admin_giris', None)
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('main.login'))

@main.route('/admin')
def admin_dashboard():
    conn = current_app.db
    cur = conn.cursor(dictionary=True)

    # Kitaplar
    cur.execute("SELECT * FROM kitap")
    kitaplar = cur.fetchall()

    # Kullanıcılar
    cur.execute("SELECT * FROM kullanici")
    kullanicilar = cur.fetchall()

    # Ödünçler + Kitap ve Kullanıcı bilgisi (kapak + kullanıcı adı için join)
    cur.execute("""
        SELECT o.*, k.baslik, k.kapak_yolu, u.ad_soyad
        FROM odunc o
        JOIN kitap k ON o.kitap_id = k.id
        JOIN kullanici u ON o.kullanici_id = u.id
    """)
    oduncler = cur.fetchall()

    cur.close()
    return render_template('admin_dashboard.html', kitaplar=kitaplar, kullanicilar=kullanicilar, oduncler=oduncler)




@main.route('/kitap_odunc_al/<int:kitap_id>', methods=['POST'])
def kitap_odunc_al(kitap_id):
    ad_soyad = request.form['ad_soyad']
    conn = current_app.db
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM kullanici WHERE ad_soyad = %s", (ad_soyad,))
    kullanici = cur.fetchone()
    if not kullanici:
        cur.execute("INSERT INTO kullanici (ad_soyad) VALUES (%s)", (ad_soyad,))
        conn.commit()
        cur.execute("SELECT LAST_INSERT_ID() AS id")
        kullanici = cur.fetchone()
    cur.execute("SELECT stok FROM kitap WHERE id = %s", (kitap_id,))
    kitap = cur.fetchone()
    if kitap and kitap['stok'] > 0:
        cur.execute("""
            INSERT INTO odunc (kitap_id, kullanici_id, odunc_tarihi)
            VALUES (%s, %s, CURDATE())
        """, (kitap_id, kullanici['id']))
        cur.execute("UPDATE kitap SET stok = stok - 1 WHERE id = %s", (kitap_id,))
        conn.commit()
        flash('Kitap ödünç verildi.', 'success')
    else:
        flash('Stokta kitap kalmadı!', 'danger')
    cur.close()
    return redirect(url_for('main.admin_dashboard'))

UPLOAD_FOLDER = 'app/static/img/kitap_kapaklari'

@main.route('/kitap_ekle', methods=['POST'])
def kitap_ekle():
    baslik = request.form['baslik']
    yazar = request.form['yazar']
    yayin_tarihi = request.form['yayin_tarihi']  # 'YYYY-MM-DD' formatında string
    kategori = request.form['kategori']
    stok = request.form['stok']

    dosya = request.files['kapak_dosyasi']
    dosya_ad = secure_filename(dosya.filename)
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    dosya_yolu = os.path.join(UPLOAD_FOLDER, dosya_ad)
    dosya.save(dosya_yolu)

    conn = current_app.db
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO kitap (baslik, yazar, yayin_yili, kategori, stok, kapak_yolu)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (baslik, yazar, yayin_tarihi, kategori, stok, dosya_ad))
    conn.commit()
    cur.close()

    flash('Kitap başarıyla eklendi.', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/kitap_iade_et/<int:odunc_id>', methods=['POST'])
def kitap_iade_et(odunc_id):
    conn = current_app.db
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT kitap_id FROM odunc WHERE id = %s", (odunc_id,))
    result = cur.fetchone()
    if result:
        kitap_id = result['kitap_id']
        cur.execute("UPDATE kitap SET stok = stok + 1 WHERE id = %s", (kitap_id,))
        cur.execute("UPDATE odunc SET teslim_edildi = TRUE, iade_tarihi = CURDATE() WHERE id = %s", (odunc_id,))
        conn.commit()
        flash('Kitap iade alındı.', 'success')
    cur.close()
    return redirect(url_for('main.admin_dashboard'))

@main.route('/kitap_sil/<int:kitap_id>', methods=['POST'])
def kitap_sil(kitap_id):
    conn = current_app.db
    cur = conn.cursor()
    # Önce o kitapla ilgili ödünç kayıtlarını temizleyelim (varsa)
    cur.execute("DELETE FROM odunc WHERE kitap_id = %s", (kitap_id,))
    # Sonra kitabı sil
    cur.execute("DELETE FROM kitap WHERE id = %s", (kitap_id,))
    conn.commit()
    cur.close()
    flash('Kitap başarıyla silindi.', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/kullanici/<int:kullanici_id>')
def kullanici_profili(kullanici_id):
    conn = current_app.db
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM kullanici WHERE id = %s", (kullanici_id,))
    kullanici = cur.fetchone()
    cur.execute("""
        SELECT o.*, k.baslik, DATEDIFF(CURDATE(), o.odunc_tarihi) AS gun_farki
        FROM odunc o
        JOIN kitap k ON o.kitap_id = k.id
        WHERE o.kullanici_id = %s AND o.teslim_edildi = FALSE
    """, (kullanici_id,))
    aktif_oduncler = cur.fetchall()
    cur.execute("SELECT gunluk_ceza FROM ayar WHERE id = 1")
    ayar = cur.fetchone()
    gunluk_ceza = ayar['gunluk_ceza'] if ayar else 2.0
    ceza_toplam = 0
    for odunc in aktif_oduncler:
        gecikme = max(0, odunc['gun_farki'] - 14)
        odunc['gecikme'] = gecikme
        odunc['ceza'] = gecikme * gunluk_ceza
        ceza_toplam += odunc['ceza']
    cur.close()
    return render_template(
        'kullanici_profili.html',
        kullanici=kullanici,
        oduncler=aktif_oduncler,
        ceza_toplam=ceza_toplam,
        gunluk_ceza=gunluk_ceza
    )

@main.route('/ayar', methods=['GET', 'POST'])
def ayar():
    conn = current_app.db
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        gunluk_ceza = request.form['gunluk_ceza']
        cur.execute("UPDATE ayar SET gunluk_ceza = %s WHERE id = 1", (gunluk_ceza,))
        conn.commit()
        flash('Ayarlar başarıyla kaydedildi.', 'success')

    cur.execute("SELECT * FROM ayar WHERE id = 1")
    ayar = cur.fetchone()
    cur.close()

    return render_template('ayar.html', ayar=ayar)



@main.route('/ayar', methods=['POST'])
def ayar_kaydet():
    yeni_ceza = request.form['gunluk_ceza']
    conn = current_app.db
    cur = conn.cursor()
    cur.execute("UPDATE ayar SET gunluk_ceza = %s WHERE id = 1", (yeni_ceza,))
    conn.commit()
    cur.close()
    flash("Ceza tutarı güncellendi", "success")
    return redirect(url_for('main.ayar'))

@main.route('/kullanicilar')
def kullanici_listesi():
    conn = current_app.db
    cur = conn.cursor(dictionary=True)
    # Kullanıcıları getir (aktif ödünç sayısı ve gecikme var mı bilgisi ile)
    cur.execute("""
        SELECT u.id, u.ad_soyad, u.kayit_tarihi,
          COUNT(o.id) AS aktif_odunc_sayisi,
          SUM(CASE WHEN DATEDIFF(CURDATE(), o.odunc_tarihi) > 14 AND o.teslim_edildi = FALSE THEN 1 ELSE 0 END) AS gecikme_sayisi
        FROM kullanici u
        LEFT JOIN odunc o ON u.id = o.kullanici_id AND o.teslim_edildi = FALSE
        GROUP BY u.id
        ORDER BY u.ad_soyad
    """)
    kullanicilar = cur.fetchall()
    cur.close()
    return render_template('kullanici_listesi.html', kullanicilar=kullanicilar)

@main.route('/kullanici_ekle', methods=['GET', 'POST'])
def kullanici_ekle():
    if request.method == 'POST':
        ad_soyad = request.form['ad_soyad']
        conn = current_app.db
        cur = conn.cursor()
        cur.execute("INSERT INTO kullanici (ad_soyad, kayit_tarihi) VALUES (%s, CURDATE())", (ad_soyad,))
        conn.commit()
        cur.close()
        flash('Kullanıcı başarıyla eklendi.', 'success')
        return redirect(url_for('main.kullanici_listesi'))
    return render_template('kullanici_ekle.html')

@main.route('/kullanici_sil/<int:kullanici_id>', methods=['POST'])
def kullanici_sil(kullanici_id):
    conn = current_app.db
    cur = conn.cursor()
    # İlgili kullanıcı ödünç kayıtlarını da temizle
    cur.execute("DELETE FROM odunc WHERE kullanici_id = %s", (kullanici_id,))
    cur.execute("DELETE FROM kullanici WHERE id = %s", (kullanici_id,))
    conn.commit()
    cur.close()
    flash('Kullanıcı silindi.', 'success')
    return redirect(url_for('main.kullanici_listesi'))

