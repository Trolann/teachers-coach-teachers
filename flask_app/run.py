from app import create_app
from config import FlaskConfig
from extensions.logging import logger, getLogger
from os import environ


if __name__ == '__main__':
    config = FlaskConfig()
    app = create_app()
    if environ.get('FLASK_ENV') == 'production':
        logger.info("Starting production server")
        logger.setLevel('WARN')
        waitress_logger = getLogger('waitress')
        waitress_logger.setLevel(logger.level)
        waitress_logger.parent = logger
        logger.info(f"Starting Flask server on {config.FLASK_RUN_HOST}:{config.FLASK_RUN_PORT}")
        from waitress import serve
        serve(app, host=config.FLASK_RUN_HOST, port=config.FLASK_RUN_PORT)
    else:
        from fake_data.mentor_profile_faking import populate_mentors
        with app.app_context():
            if populate_mentors(10):
                logger.info("Successfully populated database with fake mentor profiles")
            else:
                logger.error("Failed to populate database with fake mentor profiles")
        logger.info(f"Starting Flask server on {config.FLASK_RUN_HOST}:{config.FLASK_RUN_PORT}")
        app.run(host=config.FLASK_RUN_HOST, port=config.FLASK_RUN_PORT, debug=True)
