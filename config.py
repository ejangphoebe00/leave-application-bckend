from os import environ
import pyodbc
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()


class Config(object):
    """ app configuration class """
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = environ.get('SECRET_KEY')
    USER = environ.get('DB_USER')
    PASSWORD = environ.get('DB_PASSWORD')
    DB_NAME = environ.get('DB_NAME')
    HOST = environ.get('DB_HOST')
    
    SQLALCHEMY_DATABASE_URI=f"mssql+pyodbc://{USER}:{PASSWORD}@{HOST}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # jwt configuarations for the user auth api
    JWT_SECRET_KEY = environ.get('SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

    # file upload configurations
    # MAX_CONTENT_LENGTH = 1024 * 1024 # 1MB
    # UPLOAD_FOLDER = 'static/files'
    # ALLOWED_EXTENSIONS = ['.pdf']

    # Mail Configs
    # MAIL_SERVER = environ.get('MAIL_SERVER')
    # MAIL_PORT = environ.get('MAIL_PORT')
    # MAIL_USE_TLS = True
    # MAIL_USE_SSL = False
    # MAIL_USERNAME = environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = str(environ.get('MAIL_PASSWORD'))
    # MAIL_DEFAULT_SENDER = environ.get('MAIL_DEFAULT_SENDER')
    # SECURITY_PASSWORD_SALT = environ.get('SECURITY_PASSWORD_SALT')

class DevelopmentConfig(Config):
    """ app development configuration class """
    ENV = "development"
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
