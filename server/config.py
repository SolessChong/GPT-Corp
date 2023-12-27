class Config:
    SECRET_KEY = 'ljksfdai23(&(4kj9w82j3klke*823^(&(4kj9w82j3klke*823^(&(4kj9w82j3klke*823^(&(4kj9w82j3klke*823^'
    JWT_SECRET_KEY = 'ljksfdai23(&(4kj9w82j3klke*823^(&(4kj9w21312j3klke*823^(&(4kj9w82j3klke*823^(&(4kj9w82j3klke*823^'
    BASIC_AUTH_REALM = 'My Application Realm'
    BASIC_AUTH_USERNAME = 'admin'
    BASIC_AUTH_PASSWORD = 'admin_password'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///production.db'
