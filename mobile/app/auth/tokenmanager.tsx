import * as SecureStore from 'expo-secure-store';

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  idToken: string;
  expiresIn: number;
}

/**
 * TokenManager handles the storage and retrieval of authentication tokens
 * using SecureStore for persistent secure storage between app sessions.
 */
class TokenManager {
  private static instance: TokenManager;
  private readonly TOKEN_KEY = 'auth_tokens';

  private constructor() {}

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
  public async setTokens(tokens: AuthTokens): Promise<void> {
    try {
      await SecureStore.setItemAsync(
        this.TOKEN_KEY,
        JSON.stringify(tokens)
      );
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
      const tokensStr = await SecureStore.getItemAsync(this.TOKEN_KEY);
      return tokensStr ? JSON.parse(tokensStr) : null;
    } catch (error) {
      console.error('Error retrieving tokens:', error);
      return null;
    }
  }

  /**
   * Clear stored authentication tokens
   */
  public async clearTokens(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(this.TOKEN_KEY);
    } catch (error) {
      console.error('Error clearing tokens:', error);
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
}

export default TokenManager;
