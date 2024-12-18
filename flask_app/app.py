from flask import Flask
from flask_app.extensions.database import db
from api import create_api_blueprint
from admin import create_admin_blueprint
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(create_api_blueprint(), url_prefix='/api')
    app.register_blueprint(create_admin_blueprint(), url_prefix='/admin')

    return app
