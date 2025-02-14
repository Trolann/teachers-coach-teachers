import {useState, useContext, createContext} from 'react';
import {CognitoIdentityProviderClient, InitiateAuthCommand} from "@aws-sdk/client-cognito-identity-provider";
import {COGNITO_CLIENT_ID, COGNITO_REGION} from '@env';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const auth = useProvideAuth();
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  return useContext(AuthContext);
};

export function useProvideAuth() {
  const [authTokens, setAuthTokens] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const client = new CognitoIdentityProviderClient({region: COGNITO_REGION});

  // Uses Resource Owner Password Credentials
  const loginWithCredentials = async (username, password) => {
    setLoading(true);
    setError(null);

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
        setAuthTokens(response.AuthenticationResult);
      } else {
        setError.error('Login failed');
      }
    } catch (error) {
      console.error('Error logging in with credentials:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    setAuthTokens(null);
  };

  return {
    authTokens,
    loginWithCredentials, // ROPC
    logout,
    loading,
    error
  };
}