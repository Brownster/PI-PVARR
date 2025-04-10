/**
 * Pi-PVARR API Client
 * Provides a centralized interface for making API requests
 */

// Base API configuration
const API_BASE_URL = '/api';
const DEFAULT_HEADERS = {
  'Content-Type': 'application/json'
};

/**
 * Send an API request to the server
 * @param {string} endpoint - API endpoint path
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Response data
 */
async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: DEFAULT_HEADERS,
      ...options
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Request failed with status ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * System API methods
 */
export const systemApi = {
  /**
   * Get system information
   * @returns {Promise<Object>} System information
   */
  getSystemInfo: () => apiRequest('/system')
};

/**
 * Configuration API methods
 */
export const configApi = {
  /**
   * Get configuration
   * @returns {Promise<Object>} Configuration
   */
  getConfig: () => apiRequest('/config'),
  
  /**
   * Save configuration
   * @param {Object} config - Configuration to save
   * @returns {Promise<Object>} Response
   */
  saveConfig: (config) => apiRequest('/config', {
    method: 'POST',
    body: JSON.stringify(config)
  }),
  
  /**
   * Get services configuration
   * @returns {Promise<Object>} Services configuration
   */
  getServices: () => apiRequest('/services'),
  
  /**
   * Save services configuration
   * @param {Object} services - Services configuration to save
   * @returns {Promise<Object>} Response
   */
  saveServices: (services) => apiRequest('/services', {
    method: 'POST',
    body: JSON.stringify(services)
  })
};

/**
 * Docker container API methods
 */
export const containerApi = {
  /**
   * Get all containers
   * @returns {Promise<Object>} Container statuses
   */
  getContainers: () => apiRequest('/containers'),
  
  /**
   * Get container information
   * @param {string} containerName - Container name
   * @returns {Promise<Object>} Container information
   */
  getContainerInfo: (containerName) => apiRequest(`/containers/${containerName}`),
  
  /**
   * Get container logs
   * @param {string} containerName - Container name
   * @param {number} lines - Number of log lines to retrieve
   * @returns {Promise<Object>} Container logs
   */
  getContainerLogs: (containerName, lines = 100) => apiRequest(`/containers/${containerName}/logs?lines=${lines}`),
  
  /**
   * Start a container
   * @param {string} containerName - Container name
   * @returns {Promise<Object>} Response
   */
  startContainer: (containerName) => apiRequest(`/containers/${containerName}/start`, {
    method: 'POST'
  }),
  
  /**
   * Stop a container
   * @param {string} containerName - Container name
   * @returns {Promise<Object>} Response
   */
  stopContainer: (containerName) => apiRequest(`/containers/${containerName}/stop`, {
    method: 'POST'
  }),
  
  /**
   * Restart a container
   * @param {string} containerName - Container name
   * @returns {Promise<Object>} Response
   */
  restartContainer: (containerName) => apiRequest(`/containers/${containerName}/restart`, {
    method: 'POST'
  }),
  
  /**
   * Update all containers
   * @returns {Promise<Object>} Response
   */
  updateContainers: () => apiRequest('/containers/update', {
    method: 'POST'
  })
};

/**
 * Storage API methods
 */
export const storageApi = {
  /**
   * Get drives information
   * @returns {Promise<Object>} Drives information
   */
  getDrives: () => apiRequest('/storage/drives'),
  
  /**
   * Get directory information
   * @param {string} path - Directory path
   * @returns {Promise<Object>} Directory information
   */
  getDirectoryInfo: (path) => apiRequest(`/storage/directory?path=${encodeURIComponent(path)}`),
  
  /**
   * Get shares information
   * @returns {Promise<Object>} Shares information
   */
  getShares: () => apiRequest('/storage/shares'),
  
  /**
   * Get media paths
   * @returns {Promise<Object>} Media paths information
   */
  getMediaPaths: () => apiRequest('/storage/media/paths')
};

/**
 * Network API methods
 * Note: These endpoints will be implemented in a future update
 */
export const networkApi = {
  /**
   * Get network information
   * @returns {Promise<Object>} Network information
   */
  getNetworkInfo: () => apiRequest('/network'),
  
  /**
   * Get VPN status
   * @returns {Promise<Object>} VPN status
   */
  getVpnStatus: () => apiRequest('/network/vpn')
};