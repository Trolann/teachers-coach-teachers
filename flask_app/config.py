from os import environ

class FlaskConfig:
    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
        self.FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
        self.FLASK_RUN_HOST = environ.get('FLASK_RUN_HOST')
        self.DEBUG = False
        self.FLASK_ENV = 'production'

class CognitoConfig:
    def __init__(self):
        self.COGNITO_USER_POOL_ID = environ.get('COGNITO_USER_POOL_ID')
        self.COGNITO_CLIENT_ID = environ.get('COGNITO_CLIENT_ID')
        self.COGNITO_REGION = environ.get('COGNITO_REGION')
        self.ADMIN_USERNAMES = environ.get('ADMIN_USERNAMES').split(',')