from flask import Blueprint, jsonify
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy import text, inspect
from extensions.database import db
from extensions.cognito import require_auth
from extensions.logging import get_logger

logger = get_logger(__name__)

debug_bps = Blueprint('debug', __name__)


@debug_bps.route('/check-database', methods=['GET'])
@require_auth
def check_database():
    logger.info("Checking database connection")
    try:
        db.session.execute(text('SELECT 1'))
        logger.info("Database connection successful")
        return jsonify({"message": "Database 'tct_database' exists and is accessible"})

    except OperationalError as e:
        # possible connection issue (wrong host, credentials, etc.)
        logger.error(f"Database connection failed: {str(e)}")
        return jsonify({
            "error": "Database connection failed",
            "details": str(e)
        }), 500

    except ProgrammingError as e:
        # check if database does not exit
        logger.error(f"Database does not exist: {str(e)}")
        return jsonify({
            "error": "Database does not exist",
            "details": str(e)
        }), 404

    except Exception as e:
        # other unexpected exceptions
        logger.error(f"Unexpected database error: {str(e)}")
        return jsonify({
            "error": "Unexpected error occurred",
            "details": str(e)
        }), 500

@debug_bps.route('/health', methods=['GET'])
def health_check():
    logger.debug("Health check endpoint called")
    return jsonify({"status": "Flask app with PostgreSQL is running"}), 200
