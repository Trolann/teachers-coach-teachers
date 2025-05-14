import { API_URL } from '../../config/api';
import TokenManager from './TokenManager';
import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import { MentorProfile, MenteeProfile } from '../utils/types';

/**
 * Updates to BackendManager class to support mentor and mentee application submissions
 */

// Add these types to your existing types file or within BackendManager.ts
export interface MentorApplicationData {
    // Personal Information
    firstName: string;
    lastName: string;
    phoneNumber: string;
    
    // Geographic Information
    country: string;
    stateProvince: string;
    county: string;
    schoolDistrict: string;
    timeZone: string;
    
    // Teaching Experience
    primarySubject: string;
    educationCertifications: string;
    specializedPrograms: string;
    schoolType: string;
    currentGradeLevels: string;
    previousGradeLevels: string;
    expertiseGradeLevels: string;
    
    // Years of Experience
    yearsInEducation: string;
    yearsInCurrentRole: string;
    yearsInCurrentGradeLevel: string;
    yearsInCurrentSubject: string;
    
    // Student Demographics
    racialDemographic: string;
    secondaryDemographic: string;
    socioeconomicDemographic: string;
    ellPercentage: string;
    
    // Professional Qualifications
    teachingCertifications: string;
    advancedDegrees: string;
    pdLeadershipExperience: string;
    pedagogicalExpertise: string;
    
    // Mentorship Experience
    previousMentoringExperience: string;
    numTeachersMentored: string;
    mentoringStyle: string;
    maxMentees: string;
    
    // Specializations
    classroomManagement: boolean;
    technologyIntegration: boolean;
    assessmentDataAnalysis: boolean;
    curriculumDevelopment: boolean;
    studentEngagement: boolean;
    differentiatedInstruction: boolean;
    crisisResponse: boolean;
    specialEducation: boolean;
    additionalSpecializations: string;
    
    // Availability
    availabilityFrequency: string;
    preferredContactMethod: string;
    
    // Mentorship Philosophy
    mentoringPhilosophy: string;
    successMetrics: string;
}

export interface MenteeApplicationData {
    // Personal Information
    firstName: string;
    lastName: string;
    phoneNumber: string;
    
    // Geographic Information
    country: string;
    stateProvince: string;
    county: string;
    schoolDistrict: string;
    timeZone: string;
    
    // Teaching Experience
    primarySubject: string;
    educationCertifications: string;
    specializedPrograms: string;
    schoolType: string;
    currentGradeLevels: string;
    previousGradeLevels: string;
    
    // Years of Experience
    yearsInEducation: string;
    yearsInCurrentRole: string;
    yearsInCurrentGradeLevel: string;
    yearsInCurrentSubject: string;
    
    // Student Demographics
    racialDemographic: string;
    secondaryDemographic: string;
    socioeconomicDemographic: string;
    ellPercentage: string;
    
    // Community Context
    schoolSocioeconomicDesignation: string;
    freeReducedLunchPercentage: string;
    primaryLanguages: string;
    majorIndustries: string;
    studentBarriers: string;
    householdIncomeRange: string;
    housingInsecurityPercentage: string;
    technologyAccess: string;
    
    // Mentorship Goals
    supportAreas: string;
    immediateChallenges: string;
    mentorshipGoals: string;
    improvementTimeline: string;
    sessionFrequency: string;
    desiredMentorCharacteristics: string;
    
    // Professional Goals
    shortTermGoals: string;
    longTermGoals: string;
    professionalGrowthAreas: string;
    skillsToDevelop: string;
    
    // Current Resources
    currentSupportSystems: string;
    previousMentorship: string;
    professionalDevelopmentAccess: string;
    districtConstraints: string;

    // Pre-Matching Preferences
    selectedCategories: string[];
    selectedIssues: string[];
    goal: string;
}

/**
 * BackendManager handles all API calls to the backend,
 * automatically managing authentication tokens and headers
 * 
 * @class BackendManager
 */
class BackendManager {
    private static instance: BackendManager;
    private tokenManager: TokenManager;
    private cachedUserName: string = "User";
    private cachedUserData: any = null;
    private readonly USER_NAME_KEY = 'cached_user_name';

    private constructor() {
        this.tokenManager = TokenManager.getInstance();
        // Load cached name from storage when instance is created
        this.loadCachedName();
    }

    /**
     * Get username (synchronous version for immediate UI display)
     */
    public getCachedUserName(): string {
        return this.cachedUserName;
    }

    /**
     * Load cached user name from secure storage
     */
    private async loadCachedName(): Promise<void> {
        try {
            const storedName = await this.getStorageItem(this.USER_NAME_KEY);
            if (storedName) {
                this.cachedUserName = storedName;
            }
        } catch (error) {
            console.error('Error loading cached name:', error);
        }
    }

    /**
     * Store item in secure storage based on platform
     */
    private async setStorageItem(key: string, value: string): Promise<void> {
        if (Platform.OS === 'web') {
            await AsyncStorage.setItem(key, value);
        } else {
            await SecureStore.setItemAsync(key, value);
        }
    }

    /**
     * Get item from secure storage based on platform
     */
    private async getStorageItem(key: string): Promise<string | null> {
        if (Platform.OS === 'web') {
            return await AsyncStorage.getItem(key);
        } else {
            return await SecureStore.getItemAsync(key);
        }
    }

    /**
     * Remove item from secure storage based on platform
     */
    private async removeStorageItem(key: string): Promise<void> {
        if (Platform.OS === 'web') {
            await AsyncStorage.removeItem(key);
        } else {
            await SecureStore.deleteItemAsync(key);
        }
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
        console.log(`[getAuthHeaders] Getting authentication tokens`);
        const tokens = await this.tokenManager.getTokens();
        console.log(`[getAuthHeaders] Tokens received:`, tokens ? 'Valid tokens object' : 'No tokens');

        if (!tokens) {
            console.error('[getAuthHeaders] No authentication tokens found');
            throw new Error('No authentication tokens found');
        }

        console.log(`[getAuthHeaders] Creating headers with tokens`);
        const headers = new Headers();
        headers.append('Authorization', `Bearer ${tokens.accessToken}`);
        headers.append('X-Refresh-Token', tokens.refreshToken);
        headers.append('X-Id-Token', tokens.idToken);
        headers.append('X-Token-Expires', tokens.expiresIn.toString());
        
        console.log(`[getAuthHeaders] Headers created successfully`);
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
        console.log(`[sendRequest] Starting request: ${method} ${url}`);
        try {
            console.log(`[sendRequest] Getting auth headers`);
            const headers = await this.getAuthHeaders();
            console.log(`[sendRequest] Headers retrieved successfully`);

            const options: RequestInit = {
                method: method,
                headers: headers,
            };

            console.log(`[sendRequest] Request options initialized:`, {
                method: options.method,
                headers: Array.from(headers.entries())
            });
            
            if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
                console.log(`[sendRequest] Adding Content-Type and body to request`);
                headers.append('Content-Type', 'application/json');
                options.body = JSON.stringify(body);
                console.log(`[sendRequest] Body size:`, options.body.length, 'characters');
                
                // log first 100 chars of body
                console.log(`[sendRequest] Body preview:`, options.body.substring(0, 100) + '...');

            }
            const fullUrl = `${API_URL}${url}`;
            console.log(`[sendRequest] Sending fetch request to: ${fullUrl}`);
            console.time('[sendRequest] Request time');
            
            const response = await fetch(`${API_URL}${url}`, options);
            console.timeEnd('[sendRequest] Request time');


            console.log(`[sendRequest] Response received:`, {
                status: response.status,
                statusText: response.statusText,
                headers: Array.from(response.headers.entries()),
                ok: response.ok
            });

            // clone response for logging
            if (!response.ok) {
                console.error(`[sendRequest] Error response: ${response.status} ${response.statusText}`);
                try {
                    // Clone the response so we can read it twice
                    const responseClone = response.clone();
                    const errorText = await responseClone.text();
                    console.error(`[sendRequest] Error response body:`, errorText);
                } catch (textError) {
                    console.error(`[sendRequest] Couldn't read error response body:`, textError);
                }
            }

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
            console.error('[sendRequest] Backend error:', error);
            console.error('[sendRequest] Error stack:', error.stack);
            console.error('Backend error:', error);
            throw error;
        }
    }

    /**
     * Submit a user picture
     * 
     * @param imageUri - URI of the selected image
     * @returns The response from the API
     */
    public async submitPicture(imageUri: string): Promise<any> {
        try {
            const headers = await this.getAuthHeaders();
            headers.delete('Content-Type'); // Let fetch auto-set it for FormData

            const res = await fetch(imageUri);
            const blob = await res.blob();

            const formData = new FormData();
            const filename = imageUri.split('/').pop() || 'profile.png';
            const match = /\.(\w+)$/.exec(filename ?? '');
            const type = match ? `image/${match[1]}` : `image`;

            formData.append('file', blob, filename);

            const response = await fetch(`${API_URL}/api/pictures/uploads`, {
                method: 'POST',
                headers,
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to upload image');
            }

            return await response.json();
        } catch (error) {
            console.error('Error uploading image:', error);
            throw error;
        }
    }

    /**
     * Get a user's picture by their user_id
     * 
     * @param userId - The Cognito ID of the user
     * @returns The user picture
     */
    public async getPicture(userId: string): Promise<Blob> {
        try {
          const headers = await this.getAuthHeaders();
          const response = await fetch(`${API_URL}/api/pictures/${userId}`, {
            method: 'GET',
            headers,
          });
      
          if (response.status === 404) {
            return null;
          }

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to fetch profile picture');
          }
      
          return await response.blob();
        } catch (error) {
          console.error('Error fetching profile picture:', error);
          return null;
          // throw error;
        }
      }

   /**
 * Submit any type of application (mentor or mentee)
 * 
 * @param applicationType - The type of application ('mentor' or 'mentee')
 * @param applicationData - The complete application data
 * @returns The response from the API
 */
public async submitApplication(applicationType: 'MENTOR' | 'MENTEE', applicationData: MentorApplicationData | MenteeApplicationData): Promise<any> {
    try {
      let apiData: any = {
        user_type: applicationType
      };
      
      try {
        // Try to process as mentor data first
        if (applicationType === 'MENTOR') {
          const mentorData = applicationData as MentorApplicationData;
          
          // Extract specializations as an array of strings
          const specializations = [];
          if (mentorData.classroomManagement) specializations.push('Classroom Management Strategies');
          if (mentorData.technologyIntegration) specializations.push('Technology Integration');
          if (mentorData.assessmentDataAnalysis) specializations.push('Assessment and Data Analysis');
          if (mentorData.curriculumDevelopment) specializations.push('Curriculum Development');
          if (mentorData.studentEngagement) specializations.push('Student Engagement Techniques');
          if (mentorData.differentiatedInstruction) specializations.push('Differentiated Instruction');
          if (mentorData.crisisResponse) specializations.push('Crisis Response/Trauma-Informed Teaching');
          if (mentorData.specialEducation) specializations.push('Special Education Integration');
          
          // Add any additional specializations the user entered
          if (mentorData.additionalSpecializations) {
            const additionalItems = mentorData.additionalSpecializations
              .split(',')
              .map(item => item.trim())
              .filter(item => item.length > 0);
            specializations.push(...additionalItems);
          }
          
          // Add all fields directly to apiData without nesting
          apiData = {
            ...apiData,
            // Personal Information
            firstName: mentorData.firstName,
            lastName: mentorData.lastName,
            phoneNumber: mentorData.phoneNumber,
            
            // Geographic Information
            country: mentorData.country,
            state_province: mentorData.stateProvince,
            county: mentorData.county,
            school_district: mentorData.schoolDistrict,
            time_zone: mentorData.timeZone,
            
            // Teaching Experience
            primary_subject: mentorData.primarySubject,
            education_certifications: mentorData.educationCertifications,
            specialized_programs: mentorData.specializedPrograms,
            school_type: mentorData.schoolType,
            current_grade_levels: mentorData.currentGradeLevels,
            previous_grade_levels: mentorData.previousGradeLevels,
            expertise_grade_levels: mentorData.expertiseGradeLevels,
            
            // Experience Years (convert to numbers)
            education_years: parseInt(mentorData.yearsInEducation) || 0,
            current_role_years: parseInt(mentorData.yearsInCurrentRole) || 0,
            current_grade_level_years: parseInt(mentorData.yearsInCurrentGradeLevel) || 0,
            current_subject_years: parseInt(mentorData.yearsInCurrentSubject) || 0,
            
            // Student Demographics
            racial_demographic: mentorData.racialDemographic,
            secondary_demographic: mentorData.secondaryDemographic,
            socioeconomic_demographic: mentorData.socioeconomicDemographic,
            ell_percentage: mentorData.ellPercentage,
            
            // Qualifications
            teaching_certifications: mentorData.teachingCertifications,
            advanced_degrees: mentorData.advancedDegrees,
            pd_leadership_experience: mentorData.pdLeadershipExperience,
            pedagogical_expertise: mentorData.pedagogicalExpertise,
            
            // Mentorship Experience
            previous_mentoring_experience: mentorData.previousMentoringExperience,
            teachers_mentored: parseInt(mentorData.numTeachersMentored) || 0,
            mentoring_style: mentorData.mentoringStyle,
            max_mentees: parseInt(mentorData.maxMentees) || 1,
            
            // Specializations
            specializations: specializations,
            
            // Availability
            availability_frequency: mentorData.availabilityFrequency,
            preferred_contact_method: mentorData.preferredContactMethod,
            
            // Philosophy
            mentoring_philosophy: mentorData.mentoringPhilosophy,
            success_metrics: mentorData.successMetrics
          };
        } else {
          // Process as mentee data
          const menteeData = applicationData as MenteeApplicationData;
          apiData = {
            ...apiData,
            // Personal Information
            firstName: menteeData.firstName,
            lastName: menteeData.lastName,
            phoneNumber: menteeData.phoneNumber,
            
            // Geographic Information
            country: menteeData.country,
            state_province: menteeData.stateProvince,
            county: menteeData.county,
            school_district: menteeData.schoolDistrict,
            time_zone: menteeData.timeZone,
            
            // Teaching Experience
            primary_subject: menteeData.primarySubject,
            education_certifications: menteeData.educationCertifications,
            specialized_programs: menteeData.specializedPrograms,
            school_type: menteeData.schoolType,
            current_grade_levels: menteeData.currentGradeLevels,
            previous_grade_levels: menteeData.previousGradeLevels,
            
            // Experience Years (convert to numbers)
            education_years: parseInt(menteeData.yearsInEducation) || 0,
            current_role_years: parseInt(menteeData.yearsInCurrentRole) || 0,
            current_grade_level_years: parseInt(menteeData.yearsInCurrentGradeLevel) || 0,
            current_subject_years: parseInt(menteeData.yearsInCurrentSubject) || 0,
            
            // Student Demographics
            racial_demographic: menteeData.racialDemographic,
            secondary_demographic: menteeData.secondaryDemographic,
            socioeconomic_demographic: menteeData.socioeconomicDemographic,
            ell_percentage: menteeData.ellPercentage,
            
            // Community Context
            socioeconomic_designation: menteeData.schoolSocioeconomicDesignation,
            free_reduced_lunch: menteeData.freeReducedLunchPercentage,
            primary_languages: menteeData.primaryLanguages,
            major_industries: menteeData.majorIndustries,
            student_barriers: menteeData.studentBarriers,
            household_income_range: menteeData.householdIncomeRange,
            housing_insecurity: menteeData.housingInsecurityPercentage,
            technology_access: menteeData.technologyAccess,
            
            // Mentorship Goals
            support_areas: menteeData.supportAreas,
            immediate_challenges: menteeData.immediateChallenges,
            mentorship_goals: menteeData.mentorshipGoals,
            improvement_timeline: menteeData.improvementTimeline,
            session_frequency: menteeData.sessionFrequency,
            desired_mentor_characteristics: menteeData.desiredMentorCharacteristics,
            
            // Professional Goals
            short_term_goals: menteeData.shortTermGoals,
            long_term_goals: menteeData.longTermGoals,
            professional_growth_areas: menteeData.professionalGrowthAreas,
            skills_to_develop: menteeData.skillsToDevelop,
            
            // Current Resources
            current_support_systems: menteeData.currentSupportSystems,
            previous_mentorship: menteeData.previousMentorship,
            professional_development_access: menteeData.professionalDevelopmentAccess,
            district_constraints: menteeData.districtConstraints
          };
        }
      } catch (formattingError) {
        console.error(`Error formatting ${applicationType} data:`, formattingError);
        throw new Error(`Failed to format ${applicationType} application data: ${formattingError.message}`);
      }
  
      // Use unified endpoint for both application types
      const endpoint = '/api/users/submit_application';
      console.log(`Submitting ${applicationType} application to ${endpoint}`);

      console.log('Application data being sent:', JSON.stringify(apiData, null, 2));
      
      // Send the request
      console.log(`[submitApplication] Calling sendRequest with endpoint: ${endpoint}`);
      const response = await this.sendRequest(endpoint, 'POST', apiData);
      console.log(`[submitApplication] Response received from sendRequest:`, response);
      console.log(`[submitApplication] Response status:`, response.status, response.statusText);

      // Check for errors
      if (!response.ok) {
        let errorMessage = 'Failed to submit application';
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorMessage;
        } catch (jsonError) {
          errorMessage = `${errorMessage}: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }
      
      // Return the successful response
      return await response.json();
    } catch (error) {
      console.error(`Error submitting ${applicationType} application:`, error);
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
            // Return cached data if available
            if (this.cachedUserData) {
                return this.cachedUserData;
            }
            
            const response = await this.sendRequest('/api/users/get_application', 'GET');

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to get application');
            }
            
            const data = await response.json();
            // Cache the user data
            this.cachedUserData = data;
            
            // Cache the user name if available
            if (data && data.profile_data && data.profile_data.firstName) {
                this.cachedUserName = data.profile_data.firstName;
                // Store in persistent storage
                await this.setStorageItem(this.USER_NAME_KEY, data.profile_data.firstName);
            }
            
            return data;
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
            const headers = await this.getAuthHeaders();
            headers.set('Content-Type', 'application/json');

            let url = `${API_URL}/api/matching/find_matches`;
            if (limit) {
                url += `?limit=${limit}`;
            }

            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(searchCriteria),
            });

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
     * Get the user's full name from application data
     * 
     * @returns The user's first name (cached or from backend)
     */
    public async getUserName(): Promise<string> {
        try {
            // Return cached name immediately
            const currentCachedName = this.cachedUserName;
            
            // Try to get the latest name from application data in the background
            this.getApplication().then(applicationData => {
                if (applicationData && applicationData.profile_data && applicationData.profile_data.firstName) {
                    this.cachedUserName = applicationData.profile_data.firstName;
                    // Store in persistent storage
                    this.setStorageItem(this.USER_NAME_KEY, applicationData.profile_data.firstName)
                        .catch(err => console.error('Error storing name:', err));
                }
            }).catch(error => {
                console.error('Error updating user name in background:', error);
            });
            
            // Return the cached name while the update happens in background
            return currentCachedName;
        } catch (error) {
            console.error('Error getting user name:', error);
            return null;
        }
    }
    
    /**
     * Clear cached user data (useful after logout)
     */
    public async clearUserCache(): Promise<void> {
        this.cachedUserName = "User";
        this.cachedUserData = null;
        
        // Clear from persistent storage
        try {
            await this.removeStorageItem(this.USER_NAME_KEY);
        } catch (error) {
            console.error('Error clearing cached name:', error);
        }
    }

    /**
     * Get list of mentors who matched with the authenticated mentee
     * 
     * @returns Array of mentor profiles
     */
    public async getMatchesForMentee(): Promise<MentorProfile[]> {
        try {
          const headers = await this.getAuthHeaders();

          const response = await fetch(`${API_URL}/api/matching/get_matches_for_mentee`, {
            method: 'GET',
            headers,
          });
      
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to fetch matches');
          }
      
          const data = await response.json();

          // Debug
          // console.log("Data Variable in Backend Manager: " + data.matches);

          // For each mentor, fetch their picture and swipe card information
          const mentors = await Promise.all(
            data.matches.map(async (mentor: any) => {
              const pictureBlob = await this.getPicture(mentor.user_id);
              const pictureUrl = pictureBlob ? URL.createObjectURL(pictureBlob) : '';
              //const pictureUrl = '';
      
              return {
                ...mentor,
                picture: pictureUrl,
              } as MentorProfile;
            })
          );
      
          return mentors;

        } catch (error) {
          console.error('Error fetching matches for mentee:', error);
          throw error;
        }
    }

    /**
     * Submit a mentee request to a mentor
     * 
     * @param mentorId The Cognito sub of the mentor
     */
    public async submitMenteeRequest(mentorId: string): Promise<void> {
        try {
        const headers = await this.getAuthHeaders();
    
        const response = await fetch(`${API_URL}/api/matching/mentee_request`, {
            method: 'POST',
            headers: {
            ...headers,
            'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mentor_id: mentorId }),
        });
    
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to submit mentee request');
        }
    
        } catch (error) {
        console.error('Error submitting mentee request:', error);
        throw error;
        }
    }

    /**
     * Get list of mentees who requested the authenticated mentor
     * 
     * @returns Array of mentee profiles
     */
    public async getRequestsForMentor(): Promise<MenteeProfile[]> {
        try {
        const headers = await this.getAuthHeaders();
    
        const response = await fetch(`${API_URL}/api/matching/get_mentee_requests`, {
            method: 'GET',
            headers,
        });
    
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to fetch mentee requests');
        }
    
        const data = await response.json();

        // For each mentee, fetch their picture and swipe card information
        const mentees = await Promise.all(
            data.mentee_requests.map(async (mentee: any) => {
              const pictureBlob = await this.getPicture(mentee.user_id);
              const pictureUrl = pictureBlob ? URL.createObjectURL(pictureBlob) : '';
      
              return {
                ...mentee,
                picture: pictureUrl,
              } as MenteeProfile;
            })
          );
      
          return mentees;
    
        } catch (error) {
        console.error('Error fetching mentee requests:', error);
        throw error;
        }
    }

    /**
     * Add additional API methods here. Every backend API call should go through here.
     */
}

export default BackendManager;
