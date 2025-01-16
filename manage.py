from os import path as os_path
from sys import path as sys_path
# Add flask_app to path
flask_app_path = os_path.join(os_path.dirname(__file__), 'flask_app')
sys_path.insert(0, flask_app_path)

# Now import using the exact path where create_app exists
from flask_app.app import create_app
from flask_app.config import FlaskConfig

app = create_app(FlaskConfig())