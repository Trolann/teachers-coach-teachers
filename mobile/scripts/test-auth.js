const dotenv = require('dotenv');
const path = require('path');
const { CognitoIdentityProviderClient, InitiateAuthCommand } = require("@aws-sdk/client-cognito-identity-provider");

// Load environment variables from the root .env file
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

async function testAuth(username, password) {
    const cognitoClient = new CognitoIdentityProviderClient({
        region: 'us-east-1',
        credentials: {
            accessKeyId: process.env.AWS_ACCESS_KEY_ID,
            secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
        }
    });

    try {
        const command = new InitiateAuthCommand({
            AuthFlow: "USER_PASSWORD_AUTH",
            ClientId: '3umm6mktk1e6jib36iffor7g2a',
            AuthParameters: {
                USERNAME: username,
                PASSWORD: password,
            },
        });

        console.log('Attempting authentication...');
        const response = await cognitoClient.send(command);
        console.log('Authentication successful!');
        console.log('Tokens:', {
            accessToken: response.AuthenticationResult.AccessToken.substring(0, 20) + '...',
            refreshToken: response.AuthenticationResult.RefreshToken.substring(0, 20) + '...',
            idToken: response.AuthenticationResult.IdToken.substring(0, 20) + '...',
            expiresIn: response.AuthenticationResult.ExpiresIn,
        });
        return response;
    } catch (error) {
        console.error('Authentication failed:', error);
        throw error;
    }
}

// Usage
const username = process.argv[2];
const password = process.argv[3];

if (!username || !password) {
    console.error('Usage: node test-auth.js <username> <password>');
    process.exit(1);
}

testAuth(username, password)
    .then(() => process.exit(0))
    .catch(() => process.exit(1));
