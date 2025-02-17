// test.js
import {CognitoIdentityProviderClient, InitiateAuthCommand} from "@aws-sdk/client-cognito-identity-provider";

const COGNITO_CLIENT_ID='3umm6mktk1e6jib36iffor7g2a';
const COGNITO_REGION='us-east-1';

async function testLoginWithCredentials(username, password) {
  const client = new CognitoIdentityProviderClient({ region: COGNITO_REGION });

  try {
    const command = new InitiateAuthCommand({
      AuthFlow: 'USER_PASSWORD_AUTH',
      ClientId: COGNITO_CLIENT_ID,
      AuthParameters: {
        USERNAME: username,
        PASSWORD: password,
      },
    });

    const response = await client.send(command);

    if (response.AuthenticationResult) {
      console.log('Login successful');
      console.log('Access Token:', response.AuthenticationResult.AccessToken);
      console.log('ID Token:', response.AuthenticationResult.IdToken);
      console.log('Refresh Token:', response.AuthenticationResult.RefreshToken);
    } else {
      console.error('Login failed: No AuthenticationResult');
    }
  } catch (error) {
    console.error('Error logging in:', error.message);
  }
}

// Usage, insert valid username and password for a successful login
const username = '...';
const password = '...';

testLoginWithCredentials(username, password);