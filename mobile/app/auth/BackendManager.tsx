import { API_URL } from '../../config/api';
import TokenManager from './TokenManager';

/**
 * BackendManager handles all API calls to the backend,
 * automatically managing authentication tokens and headers
 * 
 * @class BackendManager
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
     * @param url - The URL to send the request to
     * @param method - The HTTP method to use
     * @param body - The request body (optional)
     */
    public async sendRequest(url: string, method: string, body?: any): Promise<any> {
        try {
            const headers = await this.getAuthHeaders();
            const options: RequestInit = {
                method: method,
                headers: headers,
            };
            
            if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
                headers.append('Content-Type', 'application/json');
                options.body = JSON.stringify(body);
            }
            
            const response = await fetch(`${API_URL}${url}`, options);

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
     * Submit a user application
     * 
     * @param applicationData - The application data to submit
     * @returns The response from the API
     */
    public async submitApplication(applicationData: {
        user_type: string;
        name: string;
        skills: string[];
        experience: string;
        availability: string;
        bio: string;
    }): Promise<any> {
        try {
            const response = await this.sendRequest('/api/users/submit_application', 'POST', applicationData);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to submit application');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error submitting application:', error);
            throw error;
        }
    }

    /**
     * Update a user application
     * 
     * @param updateData - The application data to update
     * @returns The response from the API
     */
    public async updateApplication(updateData: Record<string, any>): Promise<any> {
        try {
            const response = await this.sendRequest('/api/users/update_application', 'POST', updateData);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to update application');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error updating application:', error);
            throw error;
        }
    }

    /**
     * Get a user application
     * 
     * @returns The user application data
     */
    public async getApplication(): Promise<any> {
        try {
            const response = await this.sendRequest('/api/users/get_application', 'GET');
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to get application');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error getting application:', error);
            throw error;
        }
    }

    /**
     * Get a user application status
     * 
     * @returns The user application status
     */
    public async getApplicationStatus(): Promise<any> {
        try {
            const response = await this.sendRequest('/api/users/get_application_status', 'GET');
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to get application status');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error getting application status:', error);
            throw error;
        }
    }

    /**
     * Add additional API methods here. Every backend API call should go through here.
     */
}

export default BackendManager;
