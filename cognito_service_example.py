import boto3
import requests
import json
from jose import jwk, jwt
from jose.utils import base64url_decode
import time
import urllib.request
from flask import Flask, jsonify, request
from functools import wraps

class CognitoAuthTester:
    def __init__(self, user_pool_id='us-east-1_ZEQwxeGbb',
                 client_id='3umm6mktk1e6jib36iffor7g2a',
                 client_secret=None,
                 region='us-east-1'):
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.region = region
        self.client = boto3.client('cognito-idp', region_name=region)

    def simulate_signup(self, username, password, user_attributes):
        """
        Simulate user signup with all required attributes

        user_attributes should contain:
        - phone_number
        - locale
        - email
        - given_name
        - family_name
        - name
        """
        try:
            attributes = [
                {'Name': 'phone_number', 'Value': user_attributes['phone_number']},
                {'Name': 'locale', 'Value': user_attributes['locale']},
                {'Name': 'email', 'Value': user_attributes['email']},
                {'Name': 'given_name', 'Value': user_attributes['given_name']},
                {'Name': 'family_name', 'Value': user_attributes['family_name']},
                {'Name': 'name', 'Value': user_attributes['name']}
            ]

            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=username,
                Password=password,
                UserAttributes=attributes
            )
            return response
        except self.client.exceptions.UsernameExistsException:
            return {"error": "User already exists"}
        except Exception as e:
            return {"error": str(e)}

    def confirm_signup(self, username, confirmation_code):
        try:
            response = self.client.confirm_sign_up(
                ClientId=self.client_id,
                Username=username,
                ConfirmationCode=confirmation_code
            )
            return response
        except Exception as e:
            return {"error": str(e)}

    def simulate_login(self, username, password):
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
            return response['AuthenticationResult']
        except Exception as e:
            return {"error": str(e)}

class CognitoTokenVerifier:
    def __init__(self,user_pool_id='us-east-1_ZEQwxeGbb',
                 client_id='3umm6mktk1e6jib36iffor7g2a',
                 region='us-east-1'):
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

# Initialize Flask app
app = Flask(__name__)

# Initialize the verifier (replace with your values)
verifier = CognitoTokenVerifier()

@app.route('/confirm-signup', methods=['POST'])
def confirm_signup():
    tester = CognitoAuthTester()

    data = request.get_json()
    if not data.get('username') or not data.get('confirmation_code'):
        return jsonify({'error': 'Username and confirmation code are required'}), 400

    response = tester.confirm_signup(
        username=data['username'],
        confirmation_code=data['confirmation_code']
    )

    return jsonify(response)

@app.route('/signup', methods=['POST'])
def signup():
    tester = CognitoAuthTester()

    data = request.get_json()
    required_fields = [
        'username', 'password', 'phone_number', 'locale',
        'email', 'given_name', 'family_name', 'name'
    ]

    # Check if all required fields are present
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400

    # Create user attributes dictionary
    user_attributes = {
        'phone_number': data['phone_number'],
        'locale': data['locale'],
        'email': data['email'],
        'given_name': data['given_name'],
        'family_name': data['family_name'],
        'name': data['name']
    }

    response = tester.simulate_signup(
        username=data['username'],
        password=data['password'],
        user_attributes=user_attributes
    )

    return jsonify(response)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
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

@app.route('/protected-resource')
@require_auth
def protected_resource():
    return jsonify({
        'message': 'Access granted',
        'user': verifier.claims['sub']
    })

# Optional: Add a test endpoint
@app.route('/test-auth', methods=['POST'])
def test_auth():
    tester = CognitoAuthTester()

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    login_response = tester.simulate_login(username, password)
    return jsonify(login_response)

if __name__ == '__main__':
    app.run(debug=True)