import requests
import unittest

class TestCognitoAuth(unittest.TestCase):
    def setUp(self):
        self.base_url = 'http://localhost:5000'
        self.user_data = {
            "username": "trevor.mathisen@sjsu.edu",
            "password": "TestPassword123!",
            "phone_number": "+1234567890",
            "locale": "en_US",
            "email": "trevor.mathisen@sjsu.edu",
            "given_name": "John",
            "family_name": "Doe",
            "name": "John Doe"
        }
        self.auth_token = None

    def test_1_signup(self):
        """Test user signup process"""
        response = requests.post(f'{self.base_url}/signup', json=self.user_data)
        result = response.json()

        # User might already exist, which is fine for this test
        self.assertTrue(
            'UserSub' in result or  # Successful new signup
            ('error' in result and 'User already exists' in result['error'])  # Already exists
        )

    @unittest.skip("You need to manually confirm the signup in the console.")
    def test_2_confirm_signup(self):
        """Test user confirmation"""
        # Tell user to check email and get confirmation code, then take it as input:
        print("Please check your email for the confirmation code.")
        code = input("Enter the confirmation code: ")
        confirmation_data = {
            "username": self.user_data["username"],
            "confirmation_code": code  # The code from your email
        }

        response = requests.post(f'{self.base_url}/confirm-signup', json=confirmation_data)
        result = response.json()
        print(result)
        # If user was already confirmed, that's fine too
        self.assertTrue(
            'error' not in result or
            ('error' in result and 'User is already confirmed' in result['error'])
        )

    def test_3_login(self):
        """Test user login and token retrieval"""
        login_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        }

        response = requests.post(f'{self.base_url}/test-auth', json=login_data)
        result = response.json()

        self.assertIn('AccessToken', result)
        self.auth_token = result['AccessToken']

    def test_4_protected_resource_without_auth(self):
        """Test accessing protected resource without authentication"""
        response = requests.get(f'{self.base_url}/protected-resource')
        self.assertEqual(response.status_code, 401)

        result = response.json()
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'No authorization token provided')

    def test_5_protected_resource_with_auth(self):
        """Test accessing protected resource with authentication"""
        # First login to get token if we don't have it
        if not self.auth_token:
            self.test_3_login()

        headers = {'Authorization': f'Bearer {self.auth_token}'}
        response = requests.get(f'{self.base_url}/protected-resource', headers=headers)

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn('message', result)
        self.assertEqual(result['message'], 'Access granted')
        self.assertIn('user', result)

if __name__ == '__main__':
    unittest.main()