from app import create_app
from config import FlaskConfig
from extensions.logging import get_logger
from os import environ

logger = get_logger(__name__)

def init_server():
    """Initialize and configure the Flask application server"""
    logger.info("Initializing server components")
    try:
        logger.debug("Creating Flask configuration object")
        config = FlaskConfig()
        
        logger.debug("Creating Flask application instance")
        app = create_app()
        
        logger.info("Server initialization completed successfully")
        return app, config
    except Exception as e:
        logger.error(f"Failed to initialize server: {str(e)}")
        logger.exception(e)
        raise

if __name__ == '__main__':
    try:
        logger.info("Starting server initialization")
        app, config = init_server()
        
        env = environ.get('FLASK_ENV')
        host = config.FLASK_RUN_HOST
        port = config.FLASK_RUN_PORT
        
        logger.info(f"Server environment: {env if env else 'development'}")
        logger.debug(f"Host: {host}, Port: {port}")
        
        if env == 'production':
            logger.info("Configuring production server with Waitress")
            logger.debug("Setting log level to WARN for production")
            logger.setLevel('WARN')
            
            # Configure Waitress logging
            logger.debug("Configuring Waitress logger")
            waitress_logger = get_logger('waitress')
            waitress_logger.setLevel(logger.level)
            waitress_logger.parent = logger
            
            # Start production server
            from waitress import serve
            logger.info(f"Starting Waitress production server on {host}:{port}")
            serve(app, host=host, port=port)
        else:
            # Start development server
            logger.info(f"Starting Flask development server on {host}:{port}")
            logger.debug("Debug mode enabled for development server")
            app.run(host=host, port=port, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        logger.exception(e)
        raise
