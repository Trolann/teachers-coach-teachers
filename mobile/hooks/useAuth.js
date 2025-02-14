import {useState, useContext, createContext} from 'react';
import {COGNITO_CLIENT_ID, COGNITO_USER_POOL_ID, COGNITO_REGION} from '@env';

const COGNITO_DOMAIN = `https://${COGNITO_USER_POOL_ID}.auth.${COGNITO_REGION}.amazoncognito.com`;
const TOKEN_ENDPOINT = `${COGNITO_DOMAIN}/oauth2/token`;

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const auth = useProvideAuth();
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  return useContext(AuthContext);
};

export function useAuth() {
  const [authTokens, setAuthTokens] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Uses Resource Owner Password Credentials
  const loginWithCredentials = async (username, password) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(TOKEN_ENDPOINT, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({
          grant_type: 'password',
          client_id: COGNITO_CLIENT_ID,
          username,
          password,
        }).toString(),
      });

      const data = await response.json();
      if (data.access_token) {
        setAuthTokens(data);
      } else {
        console.error('Login failed:', data);
      }
    } catch (error) {
      console.error('Error logging in with credentials:', error);
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