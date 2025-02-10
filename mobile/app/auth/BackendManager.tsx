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
     * Check database connection status
     */
    public async checkDatabase(): Promise<string> {
        try {
            const headers = await this.getAuthHeaders();
            const response = await fetch(`${API_URL}/admin/debug/check-database`, {
                method: 'GET',
                headers: headers
            });

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
}

export default BackendManager;
