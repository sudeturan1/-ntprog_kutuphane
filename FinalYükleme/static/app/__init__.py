from flask import Flask
import mysql.connector

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Veritabanı bağlantısı
    app.db = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
