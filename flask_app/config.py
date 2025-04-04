from os import environ
from extensions.logging import get_logger

logger = get_logger(__name__)

class OpenAIConfig:
    def __init__(self):
        logger.info("Initializing OpenAI configuration")

        # OpenAI API key
        self.OPENAI_API_KEY = environ.get('OPENAI_API_KEY')
        if not self.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("Missing required OPENAI_API_KEY configuration")

        # OpenAI model
        self.EMBEDDING_MODEL = "text-embedding-3-small"

        # Log configuration details (excluding sensitive data)
        logger.debug(f"OpenAI config initialized with model={self.OPENAI_MODEL}")
        logger.info("OpenAI configuration completed successfully")

class FlaskConfig:
    def __init__(self):
        logger.info("Initializing Flask configuration")
        
        # Database configuration
        self.SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
        if not self.SQLALCHEMY_DATABASE_URI:
            logger.error("SQLALCHEMY_DATABASE_URI environment variable not set")
            raise ValueError("Missing required SQLALCHEMY_DATABASE_URI configuration")
            
        # Flask configuration
        self.SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
        self.FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT', '5000')
        self.FLASK_RUN_HOST = environ.get('FLASK_RUN_HOST', '0.0.0.0')
        self.DEBUG = False
        self.FLASK_ENV = 'production'
        
        # Log configuration details (excluding sensitive data)
        logger.debug(f"Flask config initialized with host={self.FLASK_RUN_HOST}, port={self.FLASK_RUN_PORT}")
        logger.debug(f"Track modifications: {self.SQLALCHEMY_TRACK_MODIFICATIONS}")
        logger.debug("Database URI configured (hidden for security)")
        logger.debug(f"Environment: {self.FLASK_ENV}, Debug mode: {self.DEBUG}")
        logger.info("Flask configuration completed successfully")

class CognitoConfig:
    def __init__(self):
        logger.info("Initializing Cognito authentication configuration")
        self.ADMIN_GROUP_NAME = environ.get('ADMIN_GROUP_NAME', 'admins')
        self.DISTRICT_ADMIN_GROUP_NAME = environ.get('DISTRICT_ADMIN_GROUP_NAME', 'district_admin')
        
        try:
            # AWS Cognito configuration
            self.COGNITO_USER_POOL_ID = environ.get('COGNITO_USER_POOL_ID')
            if not self.COGNITO_USER_POOL_ID:
                logger.error("COGNITO_USER_POOL_ID environment variable not set")
                raise ValueError("Missing required COGNITO_USER_POOL_ID configuration")
                
            self.COGNITO_CLIENT_ID = environ.get('COGNITO_CLIENT_ID')
            if not self.COGNITO_CLIENT_ID:
                logger.error("COGNITO_CLIENT_ID environment variable not set")
                raise ValueError("Missing required COGNITO_CLIENT_ID configuration")
                
            self.COGNITO_REGION = environ.get('COGNITO_REGION')
            if not self.COGNITO_REGION:
                logger.error("COGNITO_REGION environment variable not set")
                raise ValueError("Missing required COGNITO_REGION configuration")


                
            # Log configuration details (excluding sensitive data)
            logger.debug(f"Cognito config initialized with region={self.COGNITO_REGION}")
            logger.debug("User pool and client IDs configured (hidden for security)")
            logger.info("Cognito authentication configuration completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Cognito configuration: {str(e)}")
            logger.exception(e)
            raise
