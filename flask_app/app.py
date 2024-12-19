from flask import Flask
from admin.routes import create_admin_blueprint
from config import FlaskConfig
from secrets import token_hex
from extensions.database import db, init_db

def create_app(config_class=FlaskConfig()):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Set a secure secret key for sessions
    app.secret_key = token_hex(32)

    # Initialize extensions
    init_db(app)

    # Register blueprints
    app.register_blueprint(create_admin_blueprint(), url_prefix='/admin')

    return app
