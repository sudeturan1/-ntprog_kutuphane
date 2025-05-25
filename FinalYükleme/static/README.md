# Kütüphane Yönetim Sistemi

Bu proje, Flask ve mysql kullanarak geliştirilmiş modern bir **Kütüphane Yönetim Sistemi** uygulamasıdır. Admin odaklı bir arayüz ile kitap takibi, kullanıcı işlemleri, ceza hesaplama, stok yönetimi gibi birçok gelişmiş işlevi içerir.

## 🔧 Kurulum

1. Bu repoyu klonlayın veya ZIP olarak indirin ve çıkarın.
2. Terminalde proje klasörüne geçin:
   ```bash
   cd kutuphane_yonetim_sistemi 
   ```
3. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
4. `.env` dosyasında gerekli ayarları yapın.
5. Veritabanını oluşturmak için `kutuphane_veritabani.sql` dosyasını çalıştırın. aksi halde hata alırsınız 
6. Uygulamayı başlatın:
   - Windows için: `baslat.bat` dosyasını çift tıklayın.
   - Veya terminalden:
     ```bash
     python app.py
     ```

## 🧩 Özellikler

- 📚 Kitap Galerisi (Kapak fotoğraflarıyla)
- 👤 Yalnızca Admin Girişi
- 🧾 Kullanıcı bazlı ödünç alma ve iade sistemi
- ⏱ Geri getirme süresine göre ceza hesaplama (sayfa sayısına göre varsayılan süre)
- 🔔 Süresi geçen kitaplar için uyarı sistemi
- ⚙️ Admin paneli üzerinden ceza ayarları
- 🎨 Karanlık ve açık tema desteği
- 📊 Kitap stok takibi ve istatistik sayfası
- 📂 Kategorilere göre kitap listeleme ve filtreleme

## 📁 Proje Yapısı

```
kutuphane_yonetim_sistemi/
│
├── app.py                # Ana uygulama dosyası
├── config.py             # Yapılandırmalar
├── kutuphane_veritabani.sql # SQLite veritabanı şeması
├── requirements.txt      # Gerekli kütüphaneler
├── baslat.bat            # Windows için başlatıcı
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── forms.py
│   ├── utils.py
│   ├── static/
│   │   ├── css/
│   │   └── img/kitap_kapaklari/
│   └── templates/
│       └── *.html
```

## 👨‍💻 Geliştirici Notları

- Tema geçişi JavaScript ile sağlanmaktadır.
- Kitaplar stok durumuna göre gösterilir: “Stok: 0” olanlar “Tükendi” olarak işaretlenir.
- Tüm ceza ve ödünç ayarları admin panelinden yönetilebilir.

## 📜 Lisans

Bu proje kişisel ve akademik kullanım için geliştirilmiştir. Ticari kullanımlar için geliştiriciyle iletişime geçin.