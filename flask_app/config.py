from os import environ

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class FlaskConfig:
    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')