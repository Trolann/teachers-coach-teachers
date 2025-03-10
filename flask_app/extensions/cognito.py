import urllib
import json
import time
from functools import wraps
from flask import request, session, redirect, url_for
from jose import jwk, jwt
from jose.utils import base64url_decode

from config import CognitoConfig
from boto3 import client
from extensions.logging import get_logger
from extensions.database import db
from flask_app.models.user import User, UserType

config = CognitoConfig()
logger = get_logger(__name__)


logger.info("Initializing Cognito authentication module")
# TODO: Remove admin group name magic value (add to config)

class CognitoTokenVerifier:
    def __init__(self,user_pool_id=config.COGNITO_USER_POOL_ID,
                 client_id=config.COGNITO_CLIENT_ID,
                 region=config.COGNITO_REGION):
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.region = region
        self.keys = None
        self.claims = None
        self.get_keys()
        # Configure AWS credentials
        self.client = client('cognito-idp', region_name=region)

    def login_as_admin(self, username, password):
        """Login user and verify admin access"""
        logger.info(f"Attempting admin login for user: {username}")
        try:
            # First authenticate the user
            logger.debug("Initiating Cognito authentication")
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            logger.debug("Authentication response received")

            # Get the authentication result
            auth_result = response['AuthenticationResult']

            # Get user attributes
            user_info = self.get_user_attributes(auth_result['AccessToken'])
            if not user_info:
                return {"error": "Failed to get user information"}

            # Check if user is in admins group
            is_admin = self.is_user_admin(auth_result['AccessToken'], given_user_info=user_info)
            logger.debug(f"Admin status check for {username}: {is_admin}")

            if not is_admin:
                logger.warning(f"Unauthorized admin access attempt by user: {username}")
                return {"error": "User is not authorized for admin access"}

            logger.info(f"Admin user {username} logged in successfully")
            return {
                **auth_result,
                "user_info": user_info
            }
        except Exception as e:
            logger.error(f"Login error for user {username}: {str(e)}")
            logger.exception(e)
            return {"error": str(e)}

    def _check_user_group(self, access_token, group_name, given_user_info = None):
        logger.debug(f"Checking if user is in {group_name} group")
        try:
            user_info = self.get_user_attributes(access_token) if not given_user_info else given_user_info
            logger.debug(f'User info: {user_info}')
            if not user_info:
                return False
            is_in_group = False if group_name not in user_info['groups'] else True
            logger.debug(f"{group_name} status check for {user_info['username']}: {is_in_group}")
            return is_in_group
        except Exception as e:
            logger.error(f"Error checking {group_name} status: {str(e)}")
            logger.exception(e)

    def is_user_district_admin(self, access_token):
        """Check if user is in the district_admin group"""
        logger.debug("Checking if user is in district_admin group")
        return self._check_user_group(access_token, 'district_admin')

    def is_user_admin(self, access_token, given_user_info=None):
        """Check if user is in admins group"""
        logger.debug("Checking if user is in admins group")
        return self._check_user_group(access_token, 'admins')

    def get_keys(self):
        """Get the JSON Web Key (JWK) for the user pool"""
        keys_url = f'https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json'
        logger.debug(f"Fetching JWK from: {keys_url}")
        try:
            with urllib.request.urlopen(keys_url) as f:
                response = f.read()
            self.keys = json.loads(response.decode('utf-8'))['keys']
            logger.debug("Successfully retrieved JWK keys")
        except Exception as e:
            logger.error(f"Failed to fetch JWK keys: {str(e)}")
            logger.exception(e)
            raise

    def verify_token(self, token):
        """Verify the JWT token"""
        logger.debug("Starting token verification")
        try:
            # Get the kid (key ID) from the token header
            headers = jwt.get_unverified_headers(token)
            kid = headers['kid']
            logger.debug(f"Token kid: {kid}")

            # Find the matching key in the JWK set
            key = None
            for k in self.keys:
                if kid == k['kid']:
                    key = k
                    break
            if not key:
                logger.error("Public key not found in JWK set")
                raise ValueError('Public key not found in JWK set')

            # Get the public key
            public_key = jwk.construct(key)
            logger.debug("Successfully constructed public key")

            # Get the message and signature
            message, encoded_signature = str(token).rsplit('.', 1)
            decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

            # Verify the signature
            if not public_key.verify(message.encode('utf-8'), decoded_signature):
                logger.error("Token signature verification failed")
                raise ValueError('Signature verification failed')

            # Verify the claims
            claims = jwt.get_unverified_claims(token)
            logger.debug("Retrieved token claims")

            # Verify expiration time
            if time.time() > claims['exp']:
                logger.warning("Token has expired")
                raise ValueError('Token has expired')

            # Verify audience (client ID)
            if claims['client_id'] != self.client_id:
                logger.error(f"Token client ID mismatch. Expected: {self.client_id}")
                raise ValueError('Token was not issued for this client ID')

            # Verify issuer
            issuer = f'https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}'
            if claims['iss'] != issuer:
                logger.error(f"Token issuer mismatch. Expected: {issuer}")
                raise ValueError('Invalid issuer')

            self.claims = claims
            logger.info("Token successfully verified")
            self.setup_user(token)
            return True
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            logger.exception(e)
            raise

    def get_user_attributes(self, access_token):
        """Get user attributes using the access token"""
        try:
            user_info = self.client.get_user(
                AccessToken=access_token
            )
            groups = self.client.admin_list_groups_for_user(
                Username=user_info['Username'],
                UserPoolId=self.user_pool_id
            )
            logger.debug(f'Got user info: {user_info}')
            logger.debug(f'Got user groups: {groups}')
            return {
                'user_id': next((attr['Value'] for attr in user_info['UserAttributes'] if attr['Name'] == 'sub'), None),
                'email': next((attr['Value'] for attr in user_info['UserAttributes'] if attr['Name'] == 'email'), None),
                'name': next((attr['Value'] for attr in user_info['UserAttributes'] if attr['Name'] == 'name'), None),
                'username': user_info['Username'],
                'groups': [group_name for group_name in [group['GroupName'] for group in groups['Groups']]]
            }
        except Exception as e:
            logger.error(f"Error getting user attributes: {str(e)}")
            logger.exception(e)
            return None

    def setup_user(self, access_token):
        """Get user attributes using the access token"""
        try:
            user_info = self.get_user_attributes(access_token)
            user_id = user_info['user_id']

            logger.debug(f'Checking for existing user.')
            existing_user = db.session.query(User).filter(User.cognito_sub == user_id).first()
            logger.debug(f'Existing user: {existing_user}')
            if not existing_user:
                user = User(
                    cognito_sub=user_id,
                    email=user_info['email'],  # Modified to directly access email from user_info
                    user_type=UserType.ADMIN
                )
                logger.debug(f"Adding new user to database: {user.email}")
                db.session.add(user)
                db.session.commit()
                logger.debug(f'User {user.email} added to database')
                return True

            logger.debug(f"User {user_info['email']} already exists in database")
            return False
        except Exception as e:
            logger.error(f"Error getting user attributes: {str(e)}")
            logger.exception(e)
            return None

def parse_headers(headers):
    """Parse headers from a request object"""
    logger.warning(f'Headers: {headers}')
    auth_header = headers.get('Authorization')
    refresh_token = headers.get('X-Refresh-Token')
    id_token = headers.get('X-Id-Token')
    expires_in = headers.get('X-Token-Expires')
    logger.warning(f'Auth Header: {auth_header}')

    if auth_header:
        auth_header = auth_header.replace('Bearer ', '')

    return auth_header, refresh_token, id_token, expires_in

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        verifier = CognitoTokenVerifier()
        
        # Check for token in session first (for web UI)
        token = None
        if 'access_token' in session:
            token = session['access_token']
        else:
            # Parse tokens from request headers
            auth_header = request.headers.get('Authorization')
            logger.warning(f'Headers: {auth_header}')
            # Parse tokens from request headers
            if isinstance(auth_header, str):
                token = auth_header.replace('Bearer ', '')
                refresh_token = ''
                id_token = ''
                expires_in = ''
            else:
                token, refresh_token, id_token, expires_in = parse_headers(auth_header)
            logger.warning(f'Token: {token}')
            if token:
                # Debug log first part of tokens
                logger.debug(f"Access Token: {token[:15] if token else 'None'}")
                logger.debug(f"Refresh Token: {refresh_token[:15] if refresh_token else 'None'}")
                logger.debug(f"ID Token: {id_token[:5] if id_token else 'None'}")
                logger.debug(f"Token Expires In: {expires_in}")
        
        if not token:
            return redirect(url_for('admin.admin_dashboard.index'))

        try:
            # This is left in if debugging is still needed. Uncomment and prefix your token with `test` to pass
            if token.startswith('test'):
                logger.warning("Using development token")
                return f(*args, **kwargs)
            logger.warn(f'Verifying token: {token}')
            verifier.verify_token(token)
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            session.clear()  # Clear invalid session
            return redirect(url_for('admin.admin_dashboard.index'))

    return decorated
