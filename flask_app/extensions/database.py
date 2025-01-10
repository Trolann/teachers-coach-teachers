from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy with no settings
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize the database with the app"""
    db.init_app(app)
    migrate.init_app(app, db)
    app.db = db  # Make db available as app attribute
