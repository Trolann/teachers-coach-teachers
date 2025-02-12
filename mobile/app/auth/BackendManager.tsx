import { API_URL } from '../../config/api';
import TokenManager from './TokenManager';

/**
 * BackendManager handles all API calls to the backend,
 * automatically managing authentication tokens and headers
 */
class BackendManager {
    private static instance: BackendManager;
    private tokenManager: TokenManager;

    private constructor() {
        this.tokenManager = TokenManager.getInstance();
    }

    /**
     * Get the singleton instance of BackendManager
     */
    public static getInstance(): BackendManager {
        if (!BackendManager.instance) {
            BackendManager.instance = new BackendManager();
        }
        return BackendManager.instance;
    }

    /**
     * Creates headers with authentication token
     */
    private async getAuthHeaders(): Promise<Headers> {
        const tokens = await this.tokenManager.getTokens();
        if (!tokens) {
            throw new Error('No authentication tokens found');
        }

        const headers = new Headers();
        headers.append('Authorization', `Bearer ${tokens.accessToken}`);
        headers.append('X-Refresh-Token', tokens.refreshToken);
        headers.append('X-Id-Token', tokens.idToken);
        headers.append('X-Token-Expires', tokens.expiresIn.toString());
        return headers;
    }

    /**
     * Send a request to the backend with the given URL, method, and body with authentication headers
     *
     * @param url
     * @param method
     * @param body
     */
    public async sendRequest(url: string, method: string, body?: any): Promise<any> {
        try {
            const headers = await this.getAuthHeaders();
            const response = await fetch(`${API_URL}${url}`, {
                method: method,
                headers: headers,
                body: JSON.stringify(body)
            });

            return response;
        } catch (error) {
            console.error('Backend error:', error);
            throw error;
        }
    }

    /**
     * Check database connection status
     */
    public async checkDatabase(): Promise<string> {
        try {
            const response = await this.sendRequest('/admin/debug/check-database', 'GET');

            if (!response.ok) {
                throw new Error('Failed to fetch database status');
            }

            const data = await response.json();
            return data.message;
        } catch (error) {
            console.error('Backend error:', error);
            throw error;
        }
    }

    /**
     * Add additional API methods here. Every backend API call should go through here.
     */
}

export default BackendManager;
