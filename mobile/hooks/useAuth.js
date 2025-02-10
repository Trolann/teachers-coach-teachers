import { useState, useMemo, useEffect } from 'react';
import * as WebBrowser from 'expo-web-browser';
import { useAuthRequest, exchangeCodeAsync, revokeAsync, ResponseType } from 'expo-auth-session';
import { COGNITO_CLIENT_ID, COGNITO_USER_POOL_URL} from '@env';

WebBrowser.maybeCompleteAuthSession();

const redirectUri = 'http://localhost:8081';

const discoveryDocument = {
  authorizationEndpoint: `${COGNITO_USER_POOL_URL}/oauth2/authorize`,
  tokenEndpoint: `${COGNITO_USER_POOL_URL}/oauth2/token`,
  revocationEndpoint: `${COGNITO_USER_POOL_URL}/oauth2/revoke`,
};

export function useAuth() {
  const [authTokens, setAuthTokens] = useState(null);

  // Uses Proof of Key Code Exchange
  const [request, response, promptAsync] = useAuthRequest(
    {
      clientId: COGNITO_CLIENT_ID,
      responseType: ResponseType.Code,
      redirectUri: COGNITO_REDIRECT_URI,
      usePKCE: true,
    },
    discoveryDocument
  );

  useEffect(() => {
    const exchangeFn = async (exchangeTokenReq) => {
      try {
        const exchangeTokenResponse = await exchangeCodeAsync(
          exchangeTokenReq,
          discoveryDocument
        );
        setAuthTokens(exchangeTokenResponse);
      } catch (error) {
        console.error('Token exchange failed:', error);
      }
    };

    if (response?.type === 'success') {
      exchangeFn({
        clientId: COGNITO_CLIENT_ID,
        code: response.params.code,
        redirectUri: COGNITO_REDIRECT_URI,
        extraParams: {
          code_verifier: request.codeVerifier,
        },
      });
    }
  }, [request, response]);

  // Uses Resource Owner Password Credentials
  const loginWithCredentials = async (username, password) => {
    try {
      const response = await fetch(`${COGNITO_USER_POOL_URL}/oauth2/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
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
    }
  };

  // Logout function
  const logout = async () => {
    if (!authTokens?.refreshToken) return;
    try {
      await revokeAsync(
        {
          clientId: COGNITO_CLIENT_ID,
          token: authTokens.refreshToken,
        },
        discoveryDocument
      );
      setAuthTokens(null);
    } catch (error) {
      console.error('Error revoking token:', error);
    }
  };

  return {
    authTokens,
    login: () => promptAsync(), // PKCE
    loginWithCredentials, // ROPC
    logout,
  };
}
