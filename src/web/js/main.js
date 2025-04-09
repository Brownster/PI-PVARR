/**
 * Pi-PVARR Main UI JavaScript
 * Handles UI interactions and data display
 */

import { systemApi, configApi, containerApi, storageApi, networkApi } from './api-client.js';

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize the UI
  initUI();
  
  // Fetch initial data
  fetchSystemInfo();
  fetchServices();
  
  // Set up auto-refresh intervals
  setInterval(fetchSystemInfo, 30000); // Update system info every 30 seconds
  setInterval(fetchServices, 15000);   // Update services status every 15 seconds
});

/**
 * Initialize UI elements and event listeners
 */
function initUI() {
  // Theme toggle
  initThemeToggle();
  
  // Main navigation tabs
  initTabNavigation();
  
  // Storage tabs
  initStorageTabs();
  
  // Main content tabs
  initMainContentTabs();
  
  // Category tabs for services
  initCategoryTabs();
  
  // Button event listeners
  initButtonListeners();
  
  // Check if first-time setup is needed
  checkFirstTimeSetup();
}

/**
 * Initialize theme toggle functionality
 */
function initThemeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      document.body.classList.toggle('dark-mode');
      const icon = this.querySelector('i');
      
      if (document.body.classList.contains('dark-mode')) {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
        localStorage.setItem('theme', 'dark');
      } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
        localStorage.setItem('theme', 'light');
      }
    });
    
    // Apply saved theme
    if (localStorage.getItem('theme') === 'dark') {
      document.body.classList.add('dark-mode');
      const icon = themeToggle.querySelector('i');
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
    }
  }
}

/**
 * Initialize main navigation tabs
 */
function initTabNavigation() {
  const navLinks = document.querySelectorAll('nav a');
  
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Update active tab
      navLinks.forEach(navLink => navLink.classList.remove('active'));
      this.classList.add('active');
      
      // Hide the tab content before switching tabs
      document.querySelectorAll('.main .tab-content').forEach(content => {
        content.style.display = 'none';
      });
      
      // Show the selected tab content
      const tabId = this.getAttribute('data-tab');
      document.getElementById(tabId).style.display = 'block';
    });
  });
}

/**
 * Initialize storage tabs
 */
function initStorageTabs() {
  const storageTabs = document.querySelectorAll('[data-storage-tab]');
  
  storageTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      // Update active tab
      storageTabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      
      // Hide all storage tab content
      document.querySelectorAll('.storage-info .tab-content').forEach(content => {
        content.classList.remove('active');
      });
      
      // Show the selected storage tab content
      const tabId = this.getAttribute('data-storage-tab') + '-tab';
      document.getElementById(tabId).classList.add('active');
    });
  });
}

/**
 * Initialize main content tabs
 */
function initMainContentTabs() {
  const mainTabs = document.querySelectorAll('[data-main-tab]');
  
  mainTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      // Update active tab
      mainTabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      
      // Hide all main content tab content
      document.querySelectorAll('.main-content .tab-content').forEach(content => {
        content.classList.remove('active');
      });
      
      // Show the selected main content tab content
      const tabId = this.getAttribute('data-main-tab') + '-tab';
      document.getElementById(tabId).classList.add('active');
    });
  });
}

/**
 * Initialize category tabs for services
 */
function initCategoryTabs() {
  const categoryTabs = document.querySelectorAll('[data-category]');
  
  categoryTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      // Update active tab
      categoryTabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      
      // Filter services by category
      const category = this.getAttribute('data-category');
      filterServicesByCategory(category);
    });
  });
}

/**
 * Initialize button event listeners
 */
function initButtonListeners() {
  // System refresh button
  document.getElementById('refresh-system')?.addEventListener('click', fetchSystemInfo);
  
  // Storage refresh button
  document.getElementById('refresh-storage')?.addEventListener('click', fetchStorageInfo);
  
  // Services management buttons
  document.getElementById('start-all-services')?.addEventListener('click', startAllServices);
  document.getElementById('stop-all-services')?.addEventListener('click', stopAllServices);
  document.getElementById('restart-all-services')?.addEventListener('click', restartAllServices);
  document.getElementById('update-all-services')?.addEventListener('click', updateAllServices);
  
  // Add service button
  document.getElementById('add-service')?.addEventListener('click', addService);
  
  // Add drive button
  document.getElementById('add-drive')?.addEventListener('click', addDrive);
  
  // Add share button
  document.getElementById('add-share')?.addEventListener('click', addShare);
}

/**
 * Check if first-time setup is needed
 */
async function checkFirstTimeSetup() {
  try {
    const config = await configApi.getConfig();
    
    if (config.installation_status === 'not_started') {
      showSetupModal();
    }
  } catch (error) {
    console.error('Failed to check installation status:', error);
    // Assume setup is needed if config check fails
    showSetupModal();
  }
}

/**
 * Show the setup modal
 */
function showSetupModal() {
  const setupModal = document.getElementById('setup-modal');
  if (setupModal) {
    setupModal.style.display = 'block';
    
    // Close setup modal when clicking the close button
    document.getElementById('close-setup')?.addEventListener('click', function() {
      setupModal.style.display = 'none';
    });
  }
}

/**
 * Fetch system information from the API
 */
async function fetchSystemInfo() {
  try {
    showLoading();
    
    const systemInfo = await systemApi.getSystemInfo();
    
    // Update system information display
    updateSystemInfo(systemInfo);
    
    hideLoading();
  } catch (error) {
    console.error('Failed to fetch system information:', error);
    hideLoading();
  }
}

/**
 * Update system information in the UI
 * @param {Object} data - System information data
 */
function updateSystemInfo(data) {
  // Basic system info
  document.getElementById('hostname').textContent = data.hostname || 'Unknown';
  document.getElementById('os').textContent = data.os?.pretty_name || 'Unknown';
  document.getElementById('architecture').textContent = data.architecture || 'Unknown';
  
  // Get primary IP address from network interfaces
  let ipAddress = 'Unknown';
  if (data.network && data.network.interfaces) {
    for (const [name, info] of Object.entries(data.network.interfaces)) {
      if (info.addresses && info.addresses.length > 0) {
        ipAddress = info.addresses[0].address;
        break;
      }
    }
  }
  document.getElementById('ip-address').textContent = ipAddress;
  
  // CPU usage
  updateResourceBar('cpu-usage', data.cpu_usage_percent || 0);
  document.getElementById('cpu-usage-value').textContent = `${Math.round(data.cpu_usage_percent || 0)}%`;
  
  // Memory usage
  if (data.memory_total && data.memory_available) {
    const memoryUsed = data.memory_total - data.memory_available;
    const memoryPercent = Math.round((memoryUsed / data.memory_total) * 100);
    const memoryUsedGB = (memoryUsed / (1024 * 1024 * 1024)).toFixed(1);
    const memoryTotalGB = (data.memory_total / (1024 * 1024 * 1024)).toFixed(1);
    
    updateResourceBar('memory-usage', memoryPercent);
    document.getElementById('memory-usage-value').textContent = `${memoryUsedGB} GB / ${memoryTotalGB} GB`;
  }
  
  // Disk usage
  if (data.disk_total && data.disk_free) {
    const diskUsed = data.disk_total - data.disk_free;
    const diskPercent = Math.round((diskUsed / data.disk_total) * 100);
    const diskUsedGB = (diskUsed / (1024 * 1024 * 1024)).toFixed(1);
    const diskTotalGB = (data.disk_total / (1024 * 1024 * 1024)).toFixed(1);
    
    updateResourceBar('disk-usage', diskPercent);
    document.getElementById('disk-usage-value').textContent = `${diskUsedGB} GB / ${diskTotalGB} GB`;
  }
  
  // Temperature
  if (data.temperature_celsius) {
    const temp = data.temperature_celsius;
    
    // Scale temperature to a percentage (assuming 85°C is 100%)
    const tempPercent = Math.min(Math.round((temp / 85) * 100), 100);
    
    updateResourceBar('temperature', tempPercent);
    document.getElementById('temperature-value').textContent = `${temp.toFixed(1)}°C`;
    
    // Update color based on temperature
    const tempBar = document.getElementById('temperature-bar');
    if (tempBar) {
      if (temp > 75) {
        tempBar.style.backgroundColor = '#e74c3c'; // Red for hot
      } else if (temp > 60) {
        tempBar.style.backgroundColor = '#f39c12'; // Orange for warm
      } else {
        tempBar.style.backgroundColor = '#2ecc71'; // Green for cool
      }
    }
  }
}

/**
 * Update a resource bar in the UI
 * @param {string} id - Element ID (without -bar suffix)
 * @param {number} percent - Percentage value
 */
function updateResourceBar(id, percent) {
  const bar = document.getElementById(`${id}-bar`);
  const text = document.getElementById(id);
  
  if (bar && text) {
    bar.style.width = `${percent}%`;
    text.textContent = `${Math.round(percent)}%`;
    
    // Update color based on usage
    if (percent > 80) {
      bar.style.backgroundColor = '#e74c3c'; // Red for high usage
    } else if (percent > 60) {
      bar.style.backgroundColor = '#f39c12'; // Orange for medium usage
    } else {
      bar.style.backgroundColor = '#2ecc71'; // Green for low usage
    }
  }
}

/**
 * Fetch services (Docker containers) information
 */
async function fetchServices() {
  try {
    const containers = await containerApi.getContainers();
    
    // Convert containers object to array
    const containerArray = Object.entries(containers).map(([name, data]) => ({
      name,
      ...data
    }));
    
    // Update services table
    updateServicesTable(containerArray);
    
    // Filter services based on current category
    const activeCategory = document.querySelector('.category-tab.active');
    if (activeCategory) {
      filterServicesByCategory(activeCategory.getAttribute('data-category'));
    }
  } catch (error) {
    console.error('Failed to fetch services:', error);
  }
}

/**
 * Update the services table in the UI
 * @param {Array} services - Array of service objects
 */
function updateServicesTable(services) {
  const tableBody = document.getElementById('services-table-body');
  if (!tableBody) return;
  
  let tableHTML = '';
  
  if (services.length === 0) {
    tableHTML = '<tr><td colspan="5">No services found</td></tr>';
  } else {
    services.forEach(service => {
      if (service.name === 'error') return; // Skip error entries
      
      // Determine status class for styling
      let statusClass = 'status-stopped';
      if (service.status === 'running') {
        statusClass = 'status-running';
      } else if (service.status === 'error') {
        statusClass = 'status-error';
      }
      
      // Create action buttons based on current status
      let actions = '';
      if (service.status === 'running') {
        actions = `
          <button class="action-btn btn-warning" onclick="restartService('${service.name}')">
            <i class="fas fa-sync-alt"></i>
          </button>
          <button class="action-btn btn-danger" onclick="stopService('${service.name}')">
            <i class="fas fa-stop"></i>
          </button>
        `;
        
        if (service.url) {
          actions += `
            <a href="${service.url}" target="_blank" class="action-btn btn-primary">
              <i class="fas fa-external-link-alt"></i>
            </a>
          `;
        }
      } else {
        actions = `
          <button class="action-btn btn-success" onclick="startService('${service.name}')">
            <i class="fas fa-play"></i>
          </button>
        `;
      }
      
      // Add row to table
      tableHTML += `
        <tr data-service-type="${service.type || 'other'}">
          <td>${service.name}</td>
          <td><span class="status-badge ${statusClass}">${service.status}</span></td>
          <td>${service.type || 'other'}</td>
          <td>${service.url || 'N/A'}</td>
          <td>${actions}</td>
        </tr>
      `;
    });
  }
  
  tableBody.innerHTML = tableHTML;
  
  // Add global functions for service management
  window.startService = startService;
  window.stopService = stopService;
  window.restartService = restartService;
}

/**
 * Filter services table by category
 * @param {string} category - Category name
 */
function filterServicesByCategory(category) {
  const rows = document.querySelectorAll('#services-table-body tr');
  
  rows.forEach(row => {
    if (category === 'all' || row.getAttribute('data-service-type') === category) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}

/**
 * Start a service
 * @param {string} serviceName - Name of the service to start
 */
async function startService(serviceName) {
  try {
    showLoading();
    await containerApi.startContainer(serviceName);
    await fetchServices(); // Refresh services list
    hideLoading();
  } catch (error) {
    console.error(`Failed to start service ${serviceName}:`, error);
    hideLoading();
  }
}

/**
 * Stop a service
 * @param {string} serviceName - Name of the service to stop
 */
async function stopService(serviceName) {
  try {
    showLoading();
    await containerApi.stopContainer(serviceName);
    await fetchServices(); // Refresh services list
    hideLoading();
  } catch (error) {
    console.error(`Failed to stop service ${serviceName}:`, error);
    hideLoading();
  }
}

/**
 * Restart a service
 * @param {string} serviceName - Name of the service to restart
 */
async function restartService(serviceName) {
  try {
    showLoading();
    await containerApi.restartContainer(serviceName);
    await fetchServices(); // Refresh services list
    hideLoading();
  } catch (error) {
    console.error(`Failed to restart service ${serviceName}:`, error);
    hideLoading();
  }
}

/**
 * Start all services
 */
async function startAllServices() {
  // Confirm action with user
  if (!confirm('Are you sure you want to start all services?')) {
    return;
  }
  
  try {
    showLoading();
    
    // Get all containers
    const containers = await containerApi.getContainers();
    
    // Start all stopped containers
    const startPromises = [];
    for (const [name, data] of Object.entries(containers)) {
      if (data.status !== 'running') {
        startPromises.push(containerApi.startContainer(name));
      }
    }
    
    await Promise.all(startPromises);
    
    await fetchServices(); // Refresh services list
    hideLoading();
  } catch (error) {
    console.error('Failed to start all services:', error);
    hideLoading();
  }
}

/**
 * Stop all services
 */
async function stopAllServices() {
  // Confirm action with user
  if (!confirm('Are you sure you want to stop all services?')) {
    return;
  }
  
  try {
    showLoading();
    
    // Get all containers
    const containers = await containerApi.getContainers();
    
    // Stop all running containers
    const stopPromises = [];
    for (const [name, data] of Object.entries(containers)) {
      if (data.status === 'running') {
        stopPromises.push(containerApi.stopContainer(name));
      }
    }
    
    await Promise.all(stopPromises);
    
    await fetchServices(); // Refresh services list
    hideLoading();
  } catch (error) {
    console.error('Failed to stop all services:', error);
    hideLoading();
  }
}

/**
 * Restart all services
 */
async function restartAllServices() {
  // Confirm action with user
  if (!confirm('Are you sure you want to restart all services?')) {
    return;
  }
  
  try {
    showLoading();
    
    // Get all containers
    const containers = await containerApi.getContainers();
    
    // Restart all running containers
    const restartPromises = [];
    for (const [name, data] of Object.entries(containers)) {
      if (data.status === 'running') {
        restartPromises.push(containerApi.restartContainer(name));
      }
    }
    
    await Promise.all(restartPromises);
    
    await fetchServices(); // Refresh services list
    hideLoading();
  } catch (error) {
    console.error('Failed to restart all services:', error);
    hideLoading();
  }
}

/**
 * Update all services
 */
async function updateAllServices() {
  // Confirm action with user
  if (!confirm('Are you sure you want to update all services? This may take several minutes.')) {
    return;
  }
  
  try {
    showLoading();
    await containerApi.updateContainers();
    await fetchServices(); // Refresh services list
    hideLoading();
    
    alert('All services updated successfully');
  } catch (error) {
    console.error('Failed to update all services:', error);
    hideLoading();
    
    alert('Error updating services: ' + error.message);
  }
}

/**
 * Add a new service
 * Currently just a placeholder function
 */
function addService() {
  alert('Service management will be implemented in a future update');
}

/**
 * Add a new drive
 * Currently just a placeholder function
 */
function addDrive() {
  alert('Drive management will be implemented in a future update');
}

/**
 * Add a new share
 * Currently just a placeholder function
 */
function addShare() {
  alert('Share management will be implemented in a future update');
}

/**
 * Show loading overlay
 */
function showLoading() {
  const loadingOverlay = document.getElementById('loading-overlay');
  if (loadingOverlay) {
    loadingOverlay.classList.add('show');
  }
}

/**
 * Hide loading overlay
 */
function hideLoading() {
  const loadingOverlay = document.getElementById('loading-overlay');
  if (loadingOverlay) {
    loadingOverlay.classList.remove('show');
  }
}

/**
 * Fetch storage information
 * Currently uses placeholder data
 */
function fetchStorageInfo() {
  // This function will be expanded in a future update
  console.log('Fetching storage information...');
}

// Expose necessary functions globally
window.startService = startService;
window.stopService = stopService;
window.restartService = restartService;