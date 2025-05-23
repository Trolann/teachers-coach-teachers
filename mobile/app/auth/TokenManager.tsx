import 'react-native-get-random-values';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import {
  CognitoIdentityProviderClient,
  SignUpCommand,
  SignUpCommandInput,
  InitiateAuthCommand
} from "@aws-sdk/client-cognito-identity-provider";

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  idToken: string;
  expiresIn: number;
}

type UserRole = 'mentor' | 'mentee';

/**
 * TokenManager handles the storage and retrieval of authentication tokens
 * using SecureStore for persistent secure storage between app sessions.
 */
class TokenManager {
  private static instance: TokenManager;
  private readonly TOKEN_KEY = 'auth_tokens';
  private readonly USER_ROLE_KEY = 'user_role';

  private cognitoClient: CognitoIdentityProviderClient;
  private readonly COGNITO_CLIENT_ID = process.env.EXPO_PUBLIC_COGNITO_CLIENT_ID || '';
  private readonly COGNITO_USER_POOL_REGION = process.env.COGNITO_REGION || 'us-east-1';

  private constructor() {
    this.cognitoClient = new CognitoIdentityProviderClient({
      region: this.COGNITO_USER_POOL_REGION
    });
  }

  /**
   * Get the singleton instance of TokenManager
   */
  public static getInstance(): TokenManager {
    if (!TokenManager.instance) {
      TokenManager.instance = new TokenManager();
    }
    return TokenManager.instance;
  }

  /**
   * Store authentication tokens securely
   */
  private async setStorageItem(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') {
      await AsyncStorage.setItem(key, value);
    } else {
      await SecureStore.setItemAsync(key, value);
    }
  }

  private async getStorageItem(key: string): Promise<string | null> {
    if (Platform.OS === 'web') {
      return await AsyncStorage.getItem(key);
    } else {
      return await SecureStore.getItemAsync(key);
    }
  }

  private async removeStorageItem(key: string): Promise<void> {
    if (Platform.OS === 'web') {
      await AsyncStorage.removeItem(key);
    } else {
      await SecureStore.deleteItemAsync(key);
    }
  }

  public async setTokens(tokens: AuthTokens): Promise<void> {
    try {
      await this.setStorageItem(this.TOKEN_KEY, JSON.stringify(tokens));
    } catch (error) {
      console.error('Error storing tokens:', error);
      throw error;
    }
  }

  /**
   * Retrieve stored authentication tokens
   */
  public async getTokens(): Promise<AuthTokens | null> {
    try {
      const tokensStr = await this.getStorageItem(this.TOKEN_KEY);
      return tokensStr ? JSON.parse(tokensStr) : null;
    } catch (error) {
      console.error('Error retrieving tokens:', error);
      return null;
    }
  }

  /**
   * Store the user's selected role
   */
  public async setUserRole(role: UserRole): Promise<void> {
    try {
      await this.setStorageItem(this.USER_ROLE_KEY, role);
    } catch (error) {
      console.error('Error storing user role:', error);
      throw error;
    }
  }

  /**
   * Retrieve the user's role
   */
  public async getUserRole(): Promise<UserRole | null> {
    try {
      const role = await this.getStorageItem(this.USER_ROLE_KEY);
      return role as UserRole | null;
    } catch (error) {
      console.error('Error retrieving user role:', error);
      return null;
    }
  }

  /**
   * Clear stored authentication tokens
   */
  public async clearTokens(): Promise<void> {
    try {
      await Promise.all([
        this.removeStorageItem(this.TOKEN_KEY),
        this.removeStorageItem(this.USER_ROLE_KEY)
      ]);
    } catch (error) {
      console.error('Error clearing tokens and role:', error);
      throw error;
    }
  }

  /**
   * Check if we have valid tokens stored
   */
  public async hasValidTokens(): Promise<boolean> {
    const tokens = await this.getTokens();
    return tokens !== null;
    // TODO: Add token expiration check when implementing refresh flow
  }

  /**
   * Sign up a new user with Cognito
   * @param kwargs - Object containing at minimum username and password, plus any additional attributes
   */
  public async signUp(kwargs: { [key: string]: string }): Promise<boolean> {
    const { username, password, ...userAttributes } = kwargs;

    // Transform additional attributes to Cognito format
    const attributes = Object.entries(userAttributes).map(([Name, Value]) => ({
      Name,
      Value
    }));

    const input: SignUpCommandInput = {
      ClientId: this.COGNITO_CLIENT_ID,
      Username: username,
      Password: password,
      UserAttributes: attributes
    };

    try {
      const command = new SignUpCommand(input);
      const response = await this.cognitoClient.send(command);
      console.error('Signup response:', response);
      if (response.UserSub && !response.UserConfirmed) {
        // Successful signup, user needs to confirm their account
        return true;
      }
      // Something went wrong
      return false;
    } catch (error) {
      console.error('Error during signup:', error);
      throw error;
    }
  }

  /**
   * Login a user with their credentials to receive an access token from Cognito
   */
  public async loginWithCredentials(username: string, password: string): Promise<boolean> {
    try {
      const command = new InitiateAuthCommand({
        AuthFlow: 'USER_PASSWORD_AUTH',
        ClientId: this.COGNITO_CLIENT_ID,
        AuthParameters: {
          USERNAME: username,
          PASSWORD: password,
        },
      });

      const response = await this.cognitoClient.send(command);

      if (response.AuthenticationResult) {
        const tokens: AuthTokens = {
          accessToken: response.AuthenticationResult.AccessToken!,
          refreshToken: response.AuthenticationResult.RefreshToken!,
          idToken: response.AuthenticationResult.IdToken!,
          expiresIn: response.AuthenticationResult.ExpiresIn!,
        };
        // Store the tokens securely
        await this.setTokens(tokens);
        return true;
      } else {
        console.error('Login failed');
        return false;
      }
    } catch (error) {
      console.error('Error logging in with credentials:', error);
      // Print stack trace for debugging
      console.error('Stack trace:', error.stack);
      throw error;
    }
  }
}

export default TokenManager;
