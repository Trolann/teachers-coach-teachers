from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from admin.routes import create_admin_blueprint
from config import FlaskConfig
from secrets import token_hex

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=FlaskConfig()):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Set a secure secret key for sessions
    app.secret_key = token_hex(32)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(create_admin_blueprint(), url_prefix='/admin')

    return app
