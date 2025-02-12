import TokenManager from '../app/auth/TokenManager.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

async function testSignup() {
    try {
        const tokenManager = TokenManager.getInstance();
        
        // Test user details - replace with your test values
        const testUser = {
            username: "testuser@example.com",
            password: "TestPassword123!",
            email: "testuser@example.com",
            name: "Test User",
            'custom:role': "user"
        };

        console.log('Attempting to sign up user:', testUser.username);
        await tokenManager.signUp(testUser);
        console.log('Signup test completed successfully');
    } catch (error) {
        console.error('Signup test failed:', error);
    }
}

// Run the test
testSignup();
