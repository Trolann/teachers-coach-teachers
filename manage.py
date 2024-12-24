import os
import sys
# Add flask_app to path
flask_app_path = os.path.join(os.path.dirname(__file__), 'flask_app')
sys.path.insert(0, flask_app_path)

# Now import using the exact path where create_app exists
from flask_app.app import create_app
from flask_app.config import FlaskConfig

app = create_app(FlaskConfig())