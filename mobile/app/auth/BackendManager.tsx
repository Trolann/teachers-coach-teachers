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
     * List credit pools owned by a specific user
     * 
     * @param userEmail - Optional email to filter pools by owner
     * @returns List of credit pools
     */
    public async listCreditPools(userEmail?: string): Promise<any> {
        try {
            const url = userEmail 
                ? `/api/credits/pools?user_email=${encodeURIComponent(userEmail)}`
                : '/api/credits/pools';
                
            const response = await this.sendRequest(url, 'GET');
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to list credit pools');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error listing credit pools:', error);
            throw error;
        }
    }

    /**
     * Create a new credit pool
     * 
     * @param name - Name of the credit pool
     * @param initialCredits - Optional initial credits amount
     * @returns The created pool data
     */
    public async createCreditPool(name: string, initialCredits?: number): Promise<any> {
        try {
            const poolData = {
                name: name,
                initial_credits: initialCredits || 0
            };
            
            const response = await this.sendRequest('/api/credits/pools', 'POST', poolData);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to create credit pool');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating credit pool:', error);
            throw error;
        }
    }

    /**
     * Update a credit pool
     * 
     * @param poolId - ID of the pool to update
     * @param updateData - Data to update (name, is_active)
     * @returns The updated pool data
     */
    public async updateCreditPool(poolId: string, updateData: {name?: string, is_active?: boolean}): Promise<any> {
        try {
            const response = await this.sendRequest(`/api/credits/pools/${poolId}`, 'PUT', updateData);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to update credit pool');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error updating credit pool:', error);
            throw error;
        }
    }

    /**
     * Add a user access to a credit pool by pool code
     * 
     * @param userEmail - Email of the user to add
     * @param poolCode - Code of the pool to add the user to
     * @returns The response from the API
     */
    public async addPoolAccess(userEmail: string, poolCode: string): Promise<any> {
        try {
            const accessData = {
                user_email: userEmail,
                pool_code: poolCode
            };
            
            const response = await this.sendRequest('/api/credits/pools/access', 'POST', accessData);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to add user to pool');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error adding user to pool:', error);
            throw error;
        }
    }

    /**
     * Generate credit codes
     * 
     * @param numCodes - Number of codes to generate
     * @param creditsPerCode - Credits per code
     * @returns The generated codes
     */
    public async generateCredits(numCodes: number, creditsPerCode: number): Promise<any> {
        try {
            const generateData = {
                num_codes: numCodes,
                credits_per_code: creditsPerCode
            };
            
            const response = await this.sendRequest('/api/credits/generate', 'POST', generateData);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to generate credits');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error generating credits:', error);
            throw error;
        }
    }

    /**
     * Redeem a credit code to a credit pool
     * 
     * @param code - The credit code to redeem
     * @param poolId - ID of the pool to redeem to
     * @returns The response from the API
     */
    public async redeemCredit(code: string, poolId: string): Promise<any> {
        try {
            const redeemData = {
                code: code,
                pool_id: poolId
            };
            
            const response = await this.sendRequest('/api/credits/redeem', 'POST', redeemData);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to redeem credit');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error redeeming credit:', error);
            throw error;
        }
    }

    /**
     * Remove a user from a credit pool
     * 
     * @param poolId - ID of the pool
     * @param userId - ID of the user to remove
     * @returns The response from the API
     */
    public async removeUserFromPool(poolId: number, userId: number): Promise<any> {
        try {
            const response = await this.sendRequest(`/api/credits/pools/${poolId}/users/${userId}`, 'DELETE');
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to remove user from pool');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error removing user from pool:', error);
            throw error;
        }
    }

    /**
     * Find matches for the current user based on provided criteria
     * 
     * @param searchCriteria - Object with keys as criteria and values as text to match
     * @param limit - Maximum number of results to return (optional)
     * @returns The matched users sorted by relevance
     */
    public async findMatches(searchCriteria: Record<string, string>, limit?: number): Promise<any> {
        try {
            let url = '/matching/find_matches';
            if (limit) {
                url += `?limit=${limit}`;
            }
            
            const response = await this.sendRequest(url, 'POST', searchCriteria);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to find matches');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error finding matches:', error);
            throw error;
        }
    }

    /**
     * Get the total number of credits available to the current user
     * 
     * @returns The total number of credits available across all pools
     */
    public async getAvailableCredits(): Promise<number> {
        try {
            const response = await this.sendRequest('/api/credits/available', 'GET');
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to get available credits');
            }
            
            const data = await response.json();
            return data.total_credits_available;
        } catch (error) {
            console.error('Error getting available credits:', error);
            throw error;
        }
    }

    /**
     * Add additional API methods here. Every backend API call should go through here.
     */
}

export default BackendManager;
