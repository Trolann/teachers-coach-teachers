const dotenv = require('dotenv');
const path = require('path');

// Load environment variables from the root .env file
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

async function testAuth(username, password) {
    try {
        const response = await fetch(`${process.env.COGNITO_USER_POOL_URL}/oauth2/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                grant_type: 'password',
                client_id: process.env.COGNITO_CLIENT_ID,
                username,
                password,
            }).toString(),
        });

        const data = await response.json();
        
        if (data.access_token) {
            console.log('Authentication successful!');
            console.log('Tokens:', {
                accessToken: data.access_token.substring(0, 20) + '...',
                refreshToken: data.refresh_token?.substring(0, 20) + '...',
                idToken: data.id_token?.substring(0, 20) + '...',
                expiresIn: data.expires_in,
            });
            return data;
        } else {
            throw new Error(data.error || 'Authentication failed');
        }
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
