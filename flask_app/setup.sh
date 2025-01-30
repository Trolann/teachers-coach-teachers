#!/bin/bash

# Create main directory structure
mkdir -p models extensions api admin/routes admin/templates/dashboard admin/templates/users admin/templates/logs admin/static/{css,js}

# Create models module files
touch models/__init__.py models/{user,session,credit,vector}.py

# Create extensions module files
touch extensions/__init__.py extensions/{database,vector,auth,logging}.py

# Create API module files
mkdir -p api/{auth,mentors,matching,sessions,credits}
for dir in api/*/; do
    touch "${dir}__init__.py" "${dir}routes.py"
done
touch api/__init__.py

# Create admin module files
touch admin/__init__.py
touch admin/routes/__init__.py admin/routes/{dashboard,users,logs}.py
touch admin/templates/base.html
touch admin/templates/dashboard/index.html
touch admin/templates/users/list.html
touch admin/templates/logs/viewer.html

# Create root level files
touch config.py app.py run.py

# Add basic Python package markers
echo "from flask import Flask
from extensions.database import db
from extensions.vector import vector_db
from api import create_api_blueprint
from admin import create_admin_blueprint
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    vector_db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(create_api_blueprint(), url_prefix='/api')
    app.register_blueprint(create_admin_blueprint(), url_prefix='/admin')
    
    return app" > app.py

echo "from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()" > run.py

# Make script executable
chmod +x setup.sh

# Create requirements.txt with basic dependencies
echo "flask
flask-sqlalchemy
psycopg2-binary
python-dotenv" > requirements.txt

# Set proper permissions
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;

echo "Project structure created successfully!"
