import { useState, useMemo, useEffect } from 'react';
import * as WebBrowser from 'expo-web-browser';
import { useAuthRequest, exchangeCodeAsync, revokeAsync, ResponseType } from 'expo-auth-session';

WebBrowser.maybeCompleteAuthSession();

// Still need to update the following
const clientId = '<your-client-id-here>'; 
const userPoolUrl = 'https://<your-user-pool-domain>.auth.<your-region>.amazoncognito.com';
const redirectUri = '<your-redirect-uri>';

const discoveryDocument = {
  authorizationEndpoint: `${userPoolUrl}/oauth2/authorize`,
  tokenEndpoint: `${userPoolUrl}/oauth2/token`,
  revocationEndpoint: `${userPoolUrl}/oauth2/revoke`,
};

export function useAuth() {
  const [authTokens, setAuthTokens] = useState(null);

  const [request, response, promptAsync] = useAuthRequest(
    {
      clientId,
      responseType: ResponseType.Code,
      redirectUri,
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
        clientId,
        code: response.params.code,
        redirectUri,
        extraParams: {
          code_verifier: request.codeVerifier,
        },
      });
    }
  }, [request, response]);

  const logout = async () => {
    if (!authTokens?.refreshToken) return;
    try {
      await revokeAsync(
        {
          clientId,
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
    login: () => promptAsync(),
    logout,
  };
}
