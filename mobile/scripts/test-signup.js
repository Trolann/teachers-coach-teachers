import TokenManager from '../app/auth/TokenManager.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

async function testSignup() {
    try {
        const tokenManager = TokenManager.getInstance();
        
        // Test user details - replace with your test values
        const testUser = {
            username: "trevor.mathisen@sjsu.edu",
            password: "TestPassword123!",
            email: "trevor.mathisen@sjsu.edu",
            name: "Test User"
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
