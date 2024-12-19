import urllib
import json
import time
from functools import wraps
from flask import request, jsonify
from jose import jwk, jwt
from jose.utils import base64url_decode
from config import CognitoConfig
from boto3 import client
from extensions.logging import logger
config = CognitoConfig()

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
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401

        try:
            token = auth_header.replace('Bearer ', '')
            verifier.verify_token(token)
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401

    return decorated


class CognitoBackendAuthorizer:
    def __init__(self, user_pool_id=config.COGNITO_USER_POOL_ID,
                 client_id=config.COGNITO_CLIENT_ID,
                 region=config.COGNITO_REGION):
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.region = region
        self.client = client('cognito-idp', region_name=region)


    def login(self, username, password):
        """Simulate user login and get tokens"""
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            logger.info(f'User {username} logged in')
            print(f'{response}')
            return response['AuthenticationResult']
        except Exception as e:
            print(f'Error: {str(e)}')
            return {"error": str(e)}


#  254   │             "username": "trevor.mathisen@sjsu.edu",
#  255   │             "password": "TestPassword123!",