# Contributing to Teachers Coach Teachers

## Table of Contents
- [Project Structure](#project-structure)
- [Development Environment](#development-environment)
- [Flask Backend Architecture](#flask-backend-architecture)
- [Adding New Routes](#adding-new-routes)
- [Code Style Guidelines](#code-style-guidelines)

## Project Structure

The backend is organized in a modular structure under `flask_app/`:

```
flask_app/
├── admin/                   # Admin panel routes and templates
│   ├── routes/             # Admin route handlers
│   └── templates/          # Admin HTML templates
├── api/                    # API endpoints
│   ├── auth/              # Authentication related code
│   ├── matching/          # Matching service routes
│   └── mentors/           # Mentor specific routes
├── extensions/            # Flask extensions and utilities
├── models/               # SQLAlchemy models
├── app.py                # Application factory
└── config.py            # Configuration classes
```

## Development Environment

See repo root README.md for instructions on setting up the development environment.

## Flask Backend Architecture

The backend uses a Blueprint-based architecture for modularity:

- Each feature area (admin, api, etc.) is organized as a Blueprint
- Blueprints are registered in the application factory (`app.py`)
- Routes are grouped by functionality in separate modules
- Models define the database schema using SQLAlchemy

### Blueprint Structure
Each blueprint follows this pattern:

__File:__ `flask_app/[admin/api]/[sub-folders]/__init__.py`

```python
from flask import Blueprint

def create_blueprint():
    bp = Blueprint('name', __name__)
    
    # Register child blueprints/routes
    from .routes import some_routes
    bp.register_blueprint(some_routes, url_prefix='/prefix')
    
    return bp
```

__File:__ `flask_app/[admin/api]/[sub-folders]/routes/some_route.py`
```python
from flask import Blueprint

bp = Blueprint('some_feature', __name__)

@bp.route('/endpoint')
def handler():
    """Endpoint description"""
    return {"status": "ok"}
```

## Adding New Routes

1. Create a new route module in the appropriate blueprint:
   - API endpoints go in `api/` in an appropriate subfolder
   - Admin pages go in `admin/routes/`
   
2. Define your routes.

3. Register your routes in the blueprint's `__init__.py`

4. Update `app.py` to register the blueprint in the application factory:
    
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from admin.routes import create_admin_blueprint
from api.some_route import create_some_route_blueprint  # Import your blueprint here
from config import FlaskConfig

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=FlaskConfig()):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(create_admin_blueprint(), url_prefix='/admin')
    app.register_blueprint(create_some_route_blueprint(), url_prefix='/some_route')  # Register your blueprint here

    return app
```

## Code Style Guidelines

### Type Hints
- Use type hints for all function parameters and return values
- Import types from `typing` module
- Use descriptive type names

```python
from typing import List, Dict, Optional

def get_user(user_id: int) -> Optional[Dict[str, str]]:
    """Get user by ID"""
    pass
```

### Docstrings
- Every module, class, and function should have a docstring
- Use clear descriptions of parameters and return values
- Include usage examples for complex functions

```python
def process_data(data: Dict[str, any]) -> List[str]:
    """Process the input data and return results
    
    Args:
        data: Dictionary containing input values
        
    Returns:
        List of processed strings
        
    Example:
        >>> process_data({"key": "value"})
        ['processed_value']
    """
    pass
```

### Best Practices
- Follow PEP 8 style guidelines
- Keep functions focused and small
- Use meaningful variable names
- Add comments only when code isn't self-documenting (Should be the exception)
- Use constants for magic values
- Handle errors gracefully with try/except

### Testing
- Write unit tests for new functionality
- Place tests in the `tests/` directory matching the module structure
- Use pytest fixtures for common setup
- Mock external dependencies

## Getting Help
- Check existing code for examples
- Review the documentation in docstrings
- Ask questions in Discord early and often
- Reach out to Trevor