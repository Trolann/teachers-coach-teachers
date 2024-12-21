import urllib
import json
import time
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
from jose import jwk, jwt
from jose.utils import base64url_decode

from config import CognitoConfig
from boto3 import client
from extensions.logging import get_logger

config = CognitoConfig()
logger = get_logger(__name__)
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

    def get_keys(self):
        """Get the JSON Web Key (JWK) for the user pool"""
        keys_url = f'https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json'
        with urllib.request.urlopen(keys_url) as f:
            response = f.read()
        self.keys = json.loads(response.decode('utf-8'))['keys']

    def verify_token(self, token):
        """Verify the JWT token"""
        # Get the kid (key ID) from the token header
        headers = jwt.get_unverified_headers(token)
        kid = headers['kid']

        # Find the matching key in the JWK set
        key = None
        for k in self.keys:
            if kid == k['kid']:
                key = k
                break
        if not key:
            raise ValueError('Public key not found in JWK set')

        # Get the public key
        public_key = jwk.construct(key)

        # Get the message and signature
        message, encoded_signature = str(token).rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

        # Verify the signature
        if not public_key.verify(message.encode('utf-8'), decoded_signature):
            raise ValueError('Signature verification failed')

        # Verify the claims
        claims = jwt.get_unverified_claims(token)

        # Verify expiration time
        if time.time() > claims['exp']:
            raise ValueError('Token has expired')

        # Verify audience (client ID)
        if claims['client_id'] != self.client_id:
            raise ValueError('Token was not issued for this client ID')

        # Verify issuer
        issuer = f'https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}'
        if claims['iss'] != issuer:
            raise ValueError('Invalid issuer')

        self.claims = claims
        return True


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        verifier = CognitoTokenVerifier()
        
        # Check for token in session first (for web UI)
        token = None
        if 'access_token' in session:
            token = session['access_token']
        else:
            # Check Authorization header (for API)
            auth_header = request.headers.get('Authorization')
            if auth_header:
                token = auth_header.replace('Bearer ', '')
        
        if not token:
            return redirect(url_for('admin.admin_dashboard.index'))

        try:
            verifier.verify_token(token)
            return f(*args, **kwargs)
        except Exception as e:
            session.clear()  # Clear invalid session
            return redirect(url_for('admin.admin_dashboard.index'))

    return decorated


class CognitoBackendAuthorizer:
    def __init__(self, user_pool_id=config.COGNITO_USER_POOL_ID,
                 client_id=config.COGNITO_CLIENT_ID,
                 region=config.COGNITO_REGION):
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.region = region

        # Configure AWS credentials
        self.client = client('cognito-idp', region_name=region)


    def login_as_admin(self, username, password):
        """Login user and verify admin access"""
        try:
            # First authenticate the user
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            # Get the access token
            auth_result = response['AuthenticationResult']

            # Check if user is in admins group
            is_admin = False if username.casefold() not in config.ADMIN_USERNAMES else True
            
            if not is_admin:
                return {"error": "User is not authorized for admin access"}
            
            logger.info(f'Admin user {username} logged in successfully')
            return auth_result
            
        except Exception as e:
            logger.error(f'Login error for user {username}: {str(e)}')
            return {"error": str(e)}


#  254   │             "username": "trevor.mathisen@sjsu.edu",
#  255   │             "password": "TestPassword123!",
