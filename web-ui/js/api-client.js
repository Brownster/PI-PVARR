/**
 * Pi-PVARR API Client
 * Handles all API communication for the Pi-PVARR web interface
 */

class ApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
    }

    /**
     * Makes a GET request to the API
     * @param {string} endpoint - The API endpoint to call
     * @param {number} retries - Number of retries (default: 3)
     * @returns {Promise<any>} - Promise resolving to the API response
     */
    async get(endpoint, retries = 3) {
        let lastError;
        
        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                const response = await fetch(`${this.baseUrl}/${endpoint}`, {
                    headers: {
                        'Accept': 'application/json',
                        'Cache-Control': 'no-cache'
                    },
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`API error: ${response.status} - ${errorText || 'Unknown error'}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error(`Error fetching ${endpoint} (attempt ${attempt + 1}/${retries + 1}):`, error);
                lastError = error;
                
                // If this wasn't the last attempt, wait before retrying
                if (attempt < retries) {
                    // Exponential backoff
                    const backoffTime = Math.min(1000 * Math.pow(2, attempt), 8000);
                    await new Promise(resolve => setTimeout(resolve, backoffTime));
                }
            }
        }
        
        // If we get here, all retries failed
        this.handleRequestFailure(endpoint, lastError);
        throw lastError;
    }

    /**
     * Makes a POST request to the API
     * @param {string} endpoint - The API endpoint to call
     * @param {object} data - The data to send in the request body
     * @param {number} retries - Number of retries (default: 3)
     * @returns {Promise<any>} - Promise resolving to the API response
     */
    async post(endpoint, data, retries = 3) {
        let lastError;
        
        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                const response = await fetch(`${this.baseUrl}/${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Cache-Control': 'no-cache'
                    },
                    body: JSON.stringify(data),
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`API error: ${response.status} - ${errorText || 'Unknown error'}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error(`Error posting to ${endpoint} (attempt ${attempt + 1}/${retries + 1}):`, error);
                lastError = error;
                
                // If this wasn't the last attempt, wait before retrying
                if (attempt < retries) {
                    // Exponential backoff
                    const backoffTime = Math.min(1000 * Math.pow(2, attempt), 8000);
                    await new Promise(resolve => setTimeout(resolve, backoffTime));
                }
            }
        }
        
        // If we get here, all retries failed
        this.handleRequestFailure(endpoint, lastError);
        throw lastError;
    }
    
    /**
     * Handle a failed request after all retries
     * @param {string} endpoint - The API endpoint that was called
     * @param {Error} error - The error that occurred
     */
    handleRequestFailure(endpoint, error) {
        // Create an error notification for the user
        this.showErrorNotification(
            `API Request Failed: ${endpoint}`,
            `Could not communicate with the server. Please check your connection and try again.`
        );
    }
    
    /**
     * Show an error notification to the user
     * @param {string} title - The notification title
     * @param {string} message - The notification message
     */
    showErrorNotification(title, message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.innerHTML = `
            <div class="notification-header">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${title}</span>
                <button class="close-notification">×</button>
            </div>
            <div class="notification-content">
                ${message}
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Add event listener for close button
        notification.querySelector('.close-notification').addEventListener('click', () => {
            document.body.removeChild(notification);
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 5000);
    }

    /**
     * Check system compatibility
     * @returns {Promise<any>} - Promise resolving to compatibility check results
     */
    async checkSystemCompatibility() {
        return this.get('install/compatibility');
    }

    /**
     * Get the current installation status
     * @returns {Promise<any>} - Promise resolving to the installation status
     */
    async getInstallationStatus() {
        return this.get('install/status');
    }

    /**
     * Save basic configuration
     * @param {object} config - The basic configuration data
     * @returns {Promise<any>} - Promise resolving to the API response
     */
    async saveBasicConfig(config) {
        return this.post('install/config', config);
    }

    /**
     * Save network configuration
     * @param {object} config - The network configuration data
     * @returns {Promise<any>} - Promise resolving to the API response
     */
    async saveNetworkConfig(config) {
        return this.post('install/network', config);
    }

    /**
     * Save storage configuration
     * @param {object} config - The storage configuration data
     * @returns {Promise<any>} - Promise resolving to the API response
     */
    async saveStorageConfig(config) {
        return this.post('install/storage', config);
    }

    /**
     * Save service selection
     * @param {object} services - The selected services data
     * @returns {Promise<any>} - Promise resolving to the API response
     */
    async saveServices(services) {
        return this.post('install/services', services);
    }

    /**
     * Start the installation process
     * @param {object} config - The complete configuration data
     * @returns {Promise<any>} - Promise resolving to the API response
     */
    async startInstallation(config) {
        return this.post('install/run', config);
    }

    /**
     * Get available storage drives
     * @returns {Promise<any>} - Promise resolving to the list of available drives
     */
    async getAvailableDrives() {
        return this.get('drives');
    }
    
    /**
     * Mount a drive
     * @param {string} drive - The drive device path to mount
     * @param {string} mountpoint - The directory to mount to
     * @param {object} options - Mount options
     * @returns {Promise<any>} - Promise resolving to the mount result
     */
    async mountDrive(drive, mountpoint, options = {}) {
        return this.post('drives/mount', { drive, mountpoint, options });
    }
    
    /**
     * Unmount a drive
     * @param {string} drive - The drive or mountpoint to unmount
     * @returns {Promise<any>} - Promise resolving to the unmount result
     */
    async unmountDrive(drive) {
        return this.post('drives/unmount', { drive });
    }
    
    /**
     * Format a drive
     * @param {string} drive - The drive to format
     * @param {string} filesystem - The filesystem type to format as
     * @param {string} label - The label for the drive
     * @returns {Promise<any>} - Promise resolving to the format result
     */
    async formatDrive(drive, filesystem, label) {
        return this.post('drives/format', { drive, filesystem, label });
    }
    
    /**
     * Get all network shares
     * @returns {Promise<any>} - Promise resolving to the list of network shares
     */
    async getNetworkShares() {
        return this.get('network/shares');
    }
    
    /**
     * Add a network share
     * @param {object} shareConfig - The share configuration
     * @returns {Promise<any>} - Promise resolving to the add result
     */
    async addNetworkShare(shareConfig) {
        return this.post('network/shares', shareConfig);
    }
    
    /**
     * Remove a network share
     * @param {string} id - The share ID to remove
     * @returns {Promise<any>} - Promise resolving to the remove result
     */
    async removeNetworkShare(id) {
        return this.post('network/shares', { id }, 'DELETE');
    }
    
    /**
     * Get media paths
     * @returns {Promise<any>} - Promise resolving to the media paths
     */
    async getMediaPaths() {
        return this.get('paths');
    }
    
    /**
     * Update media paths
     * @param {object} paths - The paths to update
     * @returns {Promise<any>} - Promise resolving to the update result
     */
    async updateMediaPaths(paths) {
        return this.post('paths', { paths }, 'PUT');
    }
}

// Create a global API client instance
const api = new ApiClient();