/**
 * Pi-PVARR Installation Wizard
 * Handles all functionality for the step-by-step installation wizard
 */

// DriveManager class for handling storage-related operations
class DriveManager {
    constructor() {
        this.drives = [];
        this.networkShares = [];
        this.mediaPaths = {};
        this.eventHandlers = new Map();
        this.drivesContainer = null;
        this.networkSharesContainer = null;
        this.mediaPathsContainer = null;
    }
    
    async initialize(drivesContainer, networkSharesContainer, mediaPathsContainer) {
        console.log('DriveManager.initialize() called');
        this.drivesContainer = drivesContainer;
        this.networkSharesContainer = networkSharesContainer;
        this.mediaPathsContainer = mediaPathsContainer;
        
        try {
            // Fetch available drives
            await this.loadDrives();
            
            // Fetch network shares
            await this.loadNetworkShares();
            
            // Fetch media paths
            await this.loadMediaPaths();
            
            console.log('DriveManager initialized successfully');
        } catch (error) {
            console.error('Error initializing DriveManager:', error);
            this.dispatchEvent('error', { 
                message: 'Failed to initialize drive manager', 
                error 
            });
            throw error;
        }
    }
    
    async loadDrives() {
        try {
            console.log('Fetching drives from API...');
            const response = await fetch('/api/storage/drives');
            if (!response.ok) {
                throw new Error(`Failed to fetch drives: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Received drives data:', data);
            
            if (!data.drives && Array.isArray(data)) {
                // Handle case where API returns array directly (legacy format)
                console.warn('API returned array format instead of {drives: [...]}');
                this.drives = data;
            } else {
                // Normal case where API returns {drives: [...]}
                this.drives = data.drives || [];
            }
            
            console.log('Processed drives data:', this.drives);
            this.renderDrives();
            return this.drives;
        } catch (error) {
            console.error('Error loading drives:', error);
            this.dispatchEvent('error', {
                message: 'Failed to load drives',
                error
            });
            throw error;
        }
    }
    
    async loadNetworkShares() {
        try {
            const response = await fetch('/api/storage/shares');
            if (!response.ok) {
                throw new Error(`Failed to fetch network shares: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            this.networkShares = data.shares || [];
            this.renderNetworkShares();
            return this.networkShares;
        } catch (error) {
            console.error('Error loading network shares:', error);
            this.dispatchEvent('error', {
                message: 'Failed to load network shares',
                error
            });
            throw error;
        }
    }
    
    async loadMediaPaths() {
        try {
            const response = await fetch('/api/storage/media/paths');
            if (!response.ok) {
                throw new Error(`Failed to fetch media paths: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            this.mediaPaths = data.paths || {};
            this.renderMediaPaths();
            return this.mediaPaths;
        } catch (error) {
            console.error('Error loading media paths:', error);
            this.dispatchEvent('error', {
                message: 'Failed to load media paths',
                error
            });
            throw error;
        }
    }
    
    renderDrives() {
        if (!this.drivesContainer) {
            console.error('Drives container is not set');
            return;
        }
        
        console.log('Rendering drives:', this.drives);
        
        let html = '<div class="drives-list">';
        
        if (this.drives.length === 0) {
            html += `
                <div class="no-drives-message">
                    <i class="fas fa-hdd"></i>
                    <p>No storage drives detected</p>
                    <p class="hint">Connect a USB drive or add a network share to continue</p>
                </div>
            `;
        } else {
            // Sort drives - USB drives first, then by size
            const sortedDrives = [...this.drives].sort((a, b) => {
                // USB drives first
                if (a.is_usb && !b.is_usb) return -1;
                if (!a.is_usb && b.is_usb) return 1;
                
                // Then by size (larger first)
                const sizeA = typeof a.size === 'string' ? parseInt(a.size) : a.size;
                const sizeB = typeof b.size === 'string' ? parseInt(b.size) : b.size;
                return sizeB - sizeA;
            });
            
            sortedDrives.forEach(drive => {
                // Get drive size information
                let size = drive.size;
                let used = 'Unknown';
                let available = 'Unknown';
                let usedPercent = 0;
                
                if (typeof size === 'string') {
                    // Handle size strings like "8G" or "1T"
                    size = size.replace(/([0-9.]+)([GT])B?/, (match, num, unit) => {
                        return parseFloat(num) * (unit === 'T' ? 1024 : 1) + ' GB';
                    });
                } else if (typeof size === 'number') {
                    // Handle size in bytes
                    const sizeGB = (size / (1024 * 1024 * 1024)).toFixed(1);
                    size = `${sizeGB} GB`;
                } else {
                    size = 'Unknown';
                }
                
                // If we have usage information
                if (drive.used && drive.available) {
                    used = drive.used;
                    available = drive.available;
                    usedPercent = drive.percent || 0;
                }
                
                // Create a nicer display name
                const displayName = drive.label || drive.model || (drive.is_usb ? `USB Drive (${drive.device})` : drive.device);
                
                // Add USB icon if it's a USB drive
                const driveIcon = drive.is_usb ? 
                    '<i class="fas fa-usb device-icon usb-icon"></i>' : 
                    '<i class="fas fa-hdd device-icon"></i>';
                
                html += `
                    <div class="drive-item ${drive.is_usb ? 'usb-drive' : ''}" data-device="${drive.device}">
                        <div class="drive-info">
                            ${driveIcon}
                            <div class="drive-name-container">
                                <div class="drive-name">${displayName}</div>
                                <div class="drive-details">
                                    <span class="drive-size">${size}</span>
                                    <span class="drive-type">${drive.fstype || 'Unknown'}</span>
                                    <span class="drive-mount">${drive.mountpoint || 'Not mounted'}</span>
                                </div>
                            </div>
                        </div>
                        <div class="drive-usage">
                            <div class="progress-container">
                                <div class="progress-bar" style="width: ${usedPercent}%;">
                                    <span class="progress-text">${usedPercent}%</span>
                                </div>
                            </div>
                            <div class="usage-text">
                                ${used !== 'Unknown' ? `${used} free of ${size}` : size}
                            </div>
                        </div>
                        <div class="drive-actions">
                            ${drive.mountpoint ? `
                                <button class="btn btn-primary btn-sm select-drive" data-device="${drive.device}" data-mountpoint="${drive.mountpoint}">
                                    <i class="fas fa-check"></i> Select
                                </button>
                                <button class="btn btn-danger btn-sm unmount-drive" data-device="${drive.device}" data-mountpoint="${drive.mountpoint}">
                                    <i class="fas fa-eject"></i> Unmount
                                </button>
                            ` : `
                                <button class="btn btn-primary btn-sm mount-drive" data-device="${drive.device}" data-drive-path="${drive.path || drive.device}">
                                    <i class="fas fa-hdd"></i> Mount
                                </button>
                            `}
                        </div>
                    </div>
                `;
            });
        }
        
        html += '</div>';
        this.drivesContainer.innerHTML = html;
        
        // Add event listeners
        this.drivesContainer.querySelectorAll('.select-drive').forEach(button => {
            button.addEventListener('click', () => {
                const devicePath = button.getAttribute('data-device');
                const mountpoint = button.getAttribute('data-mountpoint');
                const drive = this.drives.find(d => d.device === devicePath);
                
                if (drive && mountpoint) {
                    this.dispatchEvent('driveSelected', {
                        drive,
                        mountpoint
                    });
                }
            });
        });
        
        this.drivesContainer.querySelectorAll('.mount-drive').forEach(button => {
            button.addEventListener('click', () => {
                const devicePath = button.getAttribute('data-device');
                const drivePath = button.getAttribute('data-drive-path');
                const drive = this.drives.find(d => d.device === devicePath);
                
                if (!drive) {
                    console.error(`Drive not found: ${devicePath}`);
                    return;
                }
                
                console.log(`Mount button clicked for drive: ${devicePath}`);
                alert(`Mounting drive ${devicePath}. This functionality will be implemented in a future update.`);
            });
        });
        
        this.drivesContainer.querySelectorAll('.unmount-drive').forEach(button => {
            button.addEventListener('click', () => {
                const devicePath = button.getAttribute('data-device');
                const mountpoint = button.getAttribute('data-mountpoint');
                const drive = this.drives.find(d => d.device === devicePath);
                
                if (!drive || !mountpoint) return;
                
                console.log(`Unmount button clicked for drive: ${devicePath}, mountpoint: ${mountpoint}`);
                alert(`Unmounting drive ${devicePath}. This functionality will be implemented in a future update.`);
            });
        });
    }
    
    renderNetworkShares() {
        if (!this.networkSharesContainer) return;
        
        let html = '<div class="network-shares-list">';
        
        if (this.networkShares.length === 0) {
            html += `
                <div class="no-shares-message">
                    <i class="fas fa-network-wired"></i>
                    <p>No network shares configured</p>
                    <p class="hint">Add a network share using the button below</p>
                </div>
            `;
        } else {
            this.networkShares.forEach(share => {
                html += `
                    <div class="share-item" data-share-id="${share.id}">
                        <div class="share-info">
                            <div class="share-name">${share.name}</div>
                            <div class="share-details">
                                <span class="share-type">${share.type}</span>
                                <span class="share-server">${share.server}</span>
                                <span class="share-path">${share.share_name}</span>
                                <span class="share-mount">${share.mountpoint || 'Not mounted'}</span>
                            </div>
                        </div>
                        <div class="share-actions">
                            ${share.mountpoint ? `
                                <button class="btn btn-primary btn-sm select-share" data-share-id="${share.id}">
                                    <i class="fas fa-check"></i> Select
                                </button>
                                <button class="btn btn-danger btn-sm unmount-share" data-share-id="${share.id}">
                                    <i class="fas fa-eject"></i> Unmount
                                </button>
                            ` : `
                                <button class="btn btn-primary btn-sm mount-share" data-share-id="${share.id}">
                                    <i class="fas fa-network-wired"></i> Mount
                                </button>
                            `}
                            <button class="btn btn-danger btn-sm remove-share" data-share-id="${share.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
            });
        }
        
        html += `
            <div class="button-row">
                <button class="btn btn-primary" id="add-network-share">
                    <i class="fas fa-plus"></i> Add Network Share
                </button>
            </div>
        `;
        
        html += '</div>';
        this.networkSharesContainer.innerHTML = html;
    }
    
    renderMediaPaths() {
        if (!this.mediaPathsContainer) return;
        
        console.log('Rendering media paths:', this.mediaPaths);
        
        let html = '<div class="media-paths">';
        
        if (!this.mediaPaths || Object.keys(this.mediaPaths).length === 0) {
            html += `
                <div class="no-paths-message">
                    <i class="fas fa-folder"></i>
                    <p>No media paths configured</p>
                    <p class="hint">Configure your storage first by selecting a drive or adding a network share</p>
                </div>
            `;
        } else {
            html += '<ul class="paths-list">';
            
            for (const [key, pathObj] of Object.entries(this.mediaPaths)) {
                // Handle the media path object structure
                // The API returns {path: "/path/to/dir", exists: true/false}
                let path = '';
                let exists = false;
                
                if (typeof pathObj === 'object' && pathObj !== null) {
                    path = pathObj.path || '';
                    exists = pathObj.exists || false;
                } else if (typeof pathObj === 'string') {
                    path = pathObj;
                    exists = false;
                } else {
                    console.warn(`Invalid media path data for ${key}:`, pathObj);
                    path = '[Invalid path data]';
                    exists = false;
                }
                
                html += `
                    <li class="${exists ? 'path-exists' : 'path-missing'}">
                        <div class="path-type">${key}</div>
                        <div class="path-value">${path}</div>
                        ${exists ? 
                            '<div class="path-status"><i class="fas fa-check-circle"></i> Directory exists</div>' : 
                            '<div class="path-status"><i class="fas fa-exclamation-circle"></i> Will be created</div>'}
                    </li>
                `;
            }
            
            html += '</ul>';
        }
        
        html += '</div>';
        this.mediaPathsContainer.innerHTML = html;
    }
    
    addEventListener(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        
        this.eventHandlers.get(event).push(handler);
    }
    
    dispatchEvent(event, data) {
        if (this.eventHandlers.has(event)) {
            this.eventHandlers.get(event).forEach(handler => handler(data));
        }
    }
}

// Create a DriveManager instance
const driveManager = new DriveManager();

document.addEventListener('DOMContentLoaded', () => {
    // State management
    const state = {
        currentStep: 'system-check',
        systemCheckPassed: false,
        basicConfig: {},
        networkConfig: {},
        storageConfig: {},
        selectedServices: {},
        configSummary: {},
        installationInProgress: false,
        installationComplete: false,
        installationProgress: 0,
        installationStage: '',
        availableDrives: []
    };

    // DOM elements
    const elements = {
        loadingOverlay: document.getElementById('loading-overlay'),
        wizardProgressFill: document.getElementById('wizard-progress-fill'),
        steps: {
            'system-check': document.getElementById('system-check'),
            'basic-config': document.getElementById('basic-config'),
            'network-config': document.getElementById('network-config'),
            'storage-config': document.getElementById('storage-config'),
            'service-selection': document.getElementById('service-selection'),
            'install': document.getElementById('install'),
            'install-progress': document.getElementById('install-progress'),
            'install-complete': document.getElementById('install-complete')
        },
        stepIndicators: document.querySelectorAll('.wizard-step'),
        btnRunSystemCheck: document.getElementById('btn-run-system-check'),
        btnSystemCheckNext: document.getElementById('btn-system-check-next'),
        btnBasicConfigPrev: document.getElementById('btn-basic-config-prev'),
        btnBasicConfigNext: document.getElementById('btn-basic-config-next'),
        btnNetworkConfigPrev: document.getElementById('btn-network-config-prev'),
        btnNetworkConfigNext: document.getElementById('btn-network-config-next'),
        btnStorageConfigPrev: document.getElementById('btn-storage-config-prev'),
        btnStorageConfigNext: document.getElementById('btn-storage-config-next'),
        btnServiceSelectionPrev: document.getElementById('btn-service-selection-prev'),
        btnServiceSelectionNext: document.getElementById('btn-service-selection-next'),
        btnInstallPrev: document.getElementById('btn-install-prev'),
        btnStartInstall: document.getElementById('btn-start-install'),
        systemCheckResults: document.getElementById('system-check-results'),
        systemCheckLoader: document.getElementById('system-check-loader'),
        vpnEnabled: document.getElementById('vpn-enabled'),
        vpnDetails: document.getElementById('vpn-details'),
        tailscaleEnabled: document.getElementById('tailscale-enabled'),
        tailscaleDetails: document.getElementById('tailscale-details'),
        drivesLoading: document.getElementById('drives-loading'),
        drivesContainer: document.getElementById('drives-container'),
        networkSharesContainer: document.getElementById('network-shares-container'),
        mediaPathsContainer: document.getElementById('media-paths-container'),
        summaryContent: document.getElementById('summary-content'),
        installProgressBar: document.getElementById('install-progress-bar'),
        installPercentage: document.getElementById('install-percentage'),
        installStage: document.getElementById('install-stage'),
        stageList: document.querySelector('.stage-list'),
        installLog: document.getElementById('install-log'),
        serviceUrls: document.getElementById('service-urls'),
        btnAddShare: document.getElementById('btn-add-share'),
        sharesContainer: document.getElementById('shares-container')
    };

    // Initialize the wizard
    init();

    /**
     * Initialize the wizard
     */
    function init() {
        // Set up event listeners
        setupEventListeners();
        
        // Check if there's an ongoing installation
        checkInstallationStatus();

        // Set up theme from localStorage
        initializeTheme();
        
        // Set up WebSocket connection
        setupWebSocket();
        
        // Hide the loading overlay
        elements.loadingOverlay.classList.add('hidden');
    }
    
    /**
     * Set up WebSocket connection for real-time updates
     */
    function setupWebSocket() {
        // Connect to the WebSocket server
        wsClient.connect();
        
        // Set up event handlers
        wsClient.on('installation_status', handleInstallationStatusUpdate);
        wsClient.on('installation_complete', handleInstallationComplete);
        
        // Set up connection status handlers
        wsClient.options.onOpen = () => {
            console.log('WebSocket connection established');
        };
        
        wsClient.options.onClose = () => {
            console.log('WebSocket connection closed');
        };
        
        wsClient.options.onError = (error) => {
            console.error('WebSocket error:', error);
        };
        
        wsClient.options.onReconnect = (attempt, delay) => {
            console.log(`WebSocket reconnecting (attempt ${attempt})...`);
        };
    }
    
    /**
     * Handle installation status updates from WebSocket
     * @param {Object} data - The status update data
     */
    function handleInstallationStatusUpdate(data) {
        console.log('Received installation status update:', data);
        
        // Update our state
        state.installationInProgress = data.status === 'in_progress';
        state.installationComplete = data.status === 'completed';
        state.installationProgress = data.overall_progress;
        state.installationStage = data.current_stage;
        
        // If we're on the installation progress screen, update the UI
        if (state.currentStep === 'install-progress') {
            updateInstallationProgress(data);
        } 
        // If we're on any other screen and installation is complete, go to completion screen
        else if (state.installationComplete && state.currentStep !== 'install-complete') {
            goToStep('install-complete');
            populateServiceUrls(data.service_urls);
        }
    }
    
    /**
     * Handle installation completion event from WebSocket
     * @param {Object} data - The completion event data
     */
    function handleInstallationComplete(data) {
        console.log('Installation complete:', data);
        
        // Show success notification
        showNotification(
            'Installation Complete', 
            `Installation completed successfully in ${data.elapsed_time} seconds.`,
            'success'
        );
        
        // Go to completion screen if we're not already there
        if (state.currentStep !== 'install-complete') {
            goToStep('install-complete');
        }
    }
    
    /**
     * Initialize theme based on localStorage or system preference
     */
    function initializeTheme() {
        const themeToggle = document.getElementById('theme-toggle');
        const storedTheme = localStorage.getItem('theme');
        
        // Check if theme is stored in localStorage or if system prefers dark mode
        if (storedTheme === 'dark' || 
            (!storedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.setAttribute('data-theme', 'dark');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    }

    /**
     * Set up all event listeners
     */
    function setupEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        themeToggle.addEventListener('click', toggleTheme);
        
        // Mobile menu toggle
        const menuToggle = document.getElementById('menu-toggle');
        const sidebar = document.getElementById('sidebar');
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
        
        // System Check step
        elements.btnRunSystemCheck.addEventListener('click', runSystemCheck);
        elements.btnSystemCheckNext.addEventListener('click', () => goToStep('basic-config'));

        // Basic Config step
        elements.btnBasicConfigPrev.addEventListener('click', () => goToStep('system-check'));
        elements.btnBasicConfigNext.addEventListener('click', () => {
            // Only proceed if validation passes
            if (saveBasicConfig()) {
                // Clear any existing error messages
                const errorContainer = document.getElementById('form-errors');
                if (errorContainer) {
                    errorContainer.remove();
                }
                
                goToStep('network-config');
            }
        });

        // Network Config step
        elements.btnNetworkConfigPrev.addEventListener('click', () => goToStep('basic-config'));
        elements.btnNetworkConfigNext.addEventListener('click', () => {
            // Only proceed if validation passes
            if (saveNetworkConfig()) {
                // Clear any existing error messages
                const errorContainer = document.getElementById('network-form-errors');
                if (errorContainer) {
                    errorContainer.remove();
                }
                
                goToStep('storage-config');
            }
        });

        // VPN toggle
        elements.vpnEnabled.addEventListener('change', () => {
            elements.vpnDetails.classList.toggle('hidden', !elements.vpnEnabled.checked);
        });

        // Tailscale toggle
        elements.tailscaleEnabled.addEventListener('change', () => {
            elements.tailscaleDetails.classList.toggle('hidden', !elements.tailscaleEnabled.checked);
        });

        // Storage Config step
        elements.btnStorageConfigPrev.addEventListener('click', () => goToStep('network-config'));
        elements.btnStorageConfigNext.addEventListener('click', () => {
            saveStorageConfig();
            goToStep('service-selection');
        });

        // Add share button
        elements.btnAddShare.addEventListener('click', addShareItem);

        // Service Selection step
        elements.btnServiceSelectionPrev.addEventListener('click', () => goToStep('storage-config'));
        elements.btnServiceSelectionNext.addEventListener('click', () => {
            saveServiceSelection();
            generateSummary();
            goToStep('install');
        });

        // Install step
        elements.btnInstallPrev.addEventListener('click', () => goToStep('service-selection'));
        elements.btnStartInstall.addEventListener('click', startInstallation);
    }
    
    /**
     * Toggle between light and dark theme
     */
    function toggleTheme() {
        const themeToggle = document.getElementById('theme-toggle');
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        
        if (currentTheme === 'light') {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    }

    /**
     * Check the current installation status
     */
    async function checkInstallationStatus() {
        try {
            const status = await api.getInstallationStatus();
            
            if (status.installation_in_progress) {
                state.installationInProgress = true;
                goToStep('install-progress');
                startProgressTracking();
            } else if (status.installation_complete) {
                state.installationComplete = true;
                goToStep('install-complete');
                populateServiceUrls(status.service_urls);
            }
        } catch (error) {
            console.error('Error checking installation status:', error);
        }
    }

    /**
     * Run the system compatibility check
     */
    async function runSystemCheck() {
        elements.systemCheckResults.classList.add('hidden');
        elements.systemCheckLoader.classList.remove('hidden');
        elements.btnRunSystemCheck.disabled = true;
        
        try {
            const results = await api.checkSystemCompatibility();
            displaySystemCheckResults(results);
            
            state.systemCheckPassed = results.compatible;
            elements.btnSystemCheckNext.disabled = !state.systemCheckPassed;
            
        } catch (error) {
            displayError('System check failed', error);
        } finally {
            elements.systemCheckLoader.classList.add('hidden');
            elements.systemCheckResults.classList.remove('hidden');
            elements.btnRunSystemCheck.disabled = false;
        }
    }

    /**
     * Display the system check results
     * @param {object} results - The system check results from the API
     */
    function displaySystemCheckResults(results) {
        const resultHTML = `
            <div class="system-check-result ${results.compatible ? 'success' : 'error'}">
                <div class="result-header">
                    <i class="fas ${results.compatible ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                    <h3>${results.compatible ? 'System is compatible!' : 'System compatibility issues detected'}</h3>
                </div>
                <div class="result-details">
                    <ul class="check-list">
                        ${results.checks.map(check => `
                            <li class="${check.passed ? 'passed' : 'failed'}">
                                <span class="check-icon">
                                    <i class="fas ${check.passed ? 'fa-check' : 'fa-times'}"></i>
                                </span>
                                <span class="check-name">${check.name}</span>
                                <span class="check-status">${check.status}</span>
                                ${check.passed ? '' : `<span class="check-message">${check.message}</span>`}
                            </li>
                        `).join('')}
                    </ul>
                </div>
                ${!results.compatible ? `
                    <div class="incompatible-warning">
                        <p><strong>Note:</strong> You can still proceed with the installation, but some features may not work correctly.</p>
                    </div>
                ` : ''}
            </div>
        `;
        
        elements.systemCheckResults.innerHTML = resultHTML;
    }

    /**
     * Save the basic configuration
     * @returns {boolean} - True if validation passed, false otherwise
     */
    function saveBasicConfig() {
        const form = document.getElementById('basic-config-form');
        const formData = new FormData(form);
        
        // Form validation
        let isValid = true;
        const errors = [];
        
        // Validate PUID/PGID
        const puid = parseInt(formData.get('puid'));
        const pgid = parseInt(formData.get('pgid'));
        
        if (isNaN(puid) || puid < 0 || puid > 65535) {
            isValid = false;
            errors.push('PUID must be a number between 0 and 65535');
            highlightField('puid', true);
        } else {
            highlightField('puid', false);
        }
        
        if (isNaN(pgid) || pgid < 0 || pgid > 65535) {
            isValid = false;
            errors.push('PGID must be a number between 0 and 65535');
            highlightField('pgid', true);
        } else {
            highlightField('pgid', false);
        }
        
        // Validate directories
        const mediaDir = formData.get('media_dir');
        const downloadsDir = formData.get('downloads_dir');
        
        if (!mediaDir || mediaDir.trim() === '') {
            isValid = false;
            errors.push('Media directory is required');
            highlightField('media_dir', true);
        } else if (!isValidPath(mediaDir)) {
            isValid = false;
            errors.push('Media directory must be an absolute path (e.g., /mnt/media)');
            highlightField('media_dir', true);
        } else {
            highlightField('media_dir', false);
        }
        
        if (!downloadsDir || downloadsDir.trim() === '') {
            isValid = false;
            errors.push('Downloads directory is required');
            highlightField('downloads_dir', true);
        } else if (!isValidPath(downloadsDir)) {
            isValid = false;
            errors.push('Downloads directory must be an absolute path (e.g., /mnt/downloads)');
            highlightField('downloads_dir', true);
        } else {
            highlightField('downloads_dir', false);
        }
        
        // If validation failed, show errors
        if (!isValid) {
            displayValidationErrors(errors);
            return false;
        }
        
        // If validation passed, save the config
        state.basicConfig = {
            puid: puid,
            pgid: pgid,
            timezone: formData.get('timezone'),
            media_dir: mediaDir,
            downloads_dir: downloadsDir
        };
        
        return true;
    }
    
    /**
     * Check if a path is valid (starts with /)
     * @param {string} path - The path to validate
     * @returns {boolean} - True if valid, false otherwise
     */
    function isValidPath(path) {
        return path.startsWith('/');
    }
    
    /**
     * Highlight a form field as valid or invalid
     * @param {string} fieldId - The ID of the field to highlight
     * @param {boolean} isError - True to highlight as error, false for valid
     */
    function highlightField(fieldId, isError) {
        const field = document.getElementById(fieldId);
        if (field) {
            if (isError) {
                field.classList.add('error');
            } else {
                field.classList.remove('error');
            }
        }
    }
    
    /**
     * Display validation errors on the form
     * @param {Array} errors - Array of error messages
     */
    function displayValidationErrors(errors) {
        // Create error container if it doesn't exist
        let errorContainer = document.getElementById('form-errors');
        
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.id = 'form-errors';
            errorContainer.className = 'error-container';
            
            // Insert at the beginning of the form
            const form = document.getElementById('basic-config-form');
            form.insertBefore(errorContainer, form.firstChild);
        }
        
        // Update error container content
        errorContainer.innerHTML = `
            <ul class="error-list">
                ${errors.map(error => `<li><i class="fas fa-exclamation-circle"></i> ${error}</li>`).join('')}
            </ul>
        `;
    }

    /**
     * Save the network configuration
     * @returns {boolean} - True if validation passed, false otherwise
     */
    function saveNetworkConfig() {
        let isValid = true;
        const errors = [];
        
        // Validate VPN configuration if enabled
        if (elements.vpnEnabled.checked) {
            const vpnUsername = document.getElementById('vpn-username').value;
            const vpnPassword = document.getElementById('vpn-password').value;
            
            if (!vpnUsername || vpnUsername.trim() === '') {
                isValid = false;
                errors.push('VPN username is required when VPN is enabled');
                highlightField('vpn-username', true);
            } else {
                highlightField('vpn-username', false);
            }
            
            if (!vpnPassword || vpnPassword.trim() === '') {
                isValid = false;
                errors.push('VPN password is required when VPN is enabled');
                highlightField('vpn-password', true);
            } else {
                highlightField('vpn-password', false);
            }
        }
        
        // If validation failed, show errors
        if (!isValid) {
            displayNetworkValidationErrors(errors);
            return false;
        }
        
        // If validation passed, save the config
        state.networkConfig = {
            vpn: {
                enabled: elements.vpnEnabled.checked,
                provider: elements.vpnEnabled.checked ? document.getElementById('vpn-provider').value : null,
                username: elements.vpnEnabled.checked ? document.getElementById('vpn-username').value : null,
                password: elements.vpnEnabled.checked ? document.getElementById('vpn-password').value : null,
                region: elements.vpnEnabled.checked ? document.getElementById('vpn-region').value : null
            },
            tailscale: {
                enabled: elements.tailscaleEnabled.checked,
                auth_key: elements.tailscaleEnabled.checked ? document.getElementById('tailscale-auth-key').value : null
            }
        };
        
        return true;
    }
    
    /**
     * Display network configuration validation errors
     * @param {Array} errors - Array of error messages
     */
    function displayNetworkValidationErrors(errors) {
        // Create error container if it doesn't exist
        let errorContainer = document.getElementById('network-form-errors');
        
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.id = 'network-form-errors';
            errorContainer.className = 'error-container';
            
            // Insert at the beginning of the form
            const form = document.getElementById('network-config-form');
            form.insertBefore(errorContainer, form.firstChild);
        }
        
        // Update error container content
        errorContainer.innerHTML = `
            <ul class="error-list">
                ${errors.map(error => `<li><i class="fas fa-exclamation-circle"></i> ${error}</li>`).join('')}
            </ul>
        `;
    }

    /**
     * Initialize the DriveManager for storage configuration
     */
    async function initializeDriveManager() {
        console.log('Initializing DriveManager...');
        elements.drivesLoading.classList.remove('hidden');
        elements.drivesContainer.classList.add('hidden');
        
        try {
            // Get references to container elements
            const drivesContainer = document.getElementById('drives-container');
            const networkSharesContainer = document.getElementById('network-shares-container');
            const mediaPathsContainer = document.getElementById('media-paths-container');
            
            console.log('Container elements:', {
                drivesContainer,
                networkSharesContainer,
                mediaPathsContainer
            });
            
            // Initialize the DriveManager with the containers
            console.log('Calling driveManager.initialize()...');
            await driveManager.initialize(drivesContainer, networkSharesContainer, mediaPathsContainer);
            console.log('DriveManager initialized with drives:', driveManager.drives);
            
            // Set up event listeners for DriveManager events
            driveManager.addEventListener('driveSelected', handleDriveSelected);
            driveManager.addEventListener('shareSelected', handleShareSelected);
            driveManager.addEventListener('error', handleDriveManagerError);
            
            // Set up advanced options toggle
            const advancedOptionsToggle = document.getElementById('show-advanced-drive-options');
            if (advancedOptionsToggle) {
                advancedOptionsToggle.addEventListener('change', toggleAdvancedDriveOptions);
            }
            
            // Store drive data in state
            state.availableDrives = driveManager.drives;
            console.log('Stored drives in state:', state.availableDrives);
            
            // Display notification with drive count
            if (driveManager.drives.length > 0) {
                showNotification(
                    'Drives Detected', 
                    `Found ${driveManager.drives.length} storage drives (${driveManager.drives.filter(d => d.is_usb).length} USB)`,
                    'info'
                );
            }
        } catch (error) {
            console.error('Error initializing drive manager:', error);
            displayError('Error initializing drive manager', error);
        } finally {
            elements.drivesLoading.classList.add('hidden');
            elements.drivesContainer.classList.remove('hidden');
        }
    }
    
    /**
     * Handle drive selected event from DriveManager
     * @param {object} data - The event data with drive and mountpoint
     */
    function handleDriveSelected(data) {
        const { drive, mountpoint } = data;
        
        // Update form inputs with selected drive info
        document.getElementById('media-directory').value = `${mountpoint}/media`;
        document.getElementById('downloads-directory').value = `${mountpoint}/downloads`;
        
        // Update share path with selected drive
        document.getElementById('share-path-1').value = `${mountpoint}/media`;
        
        // Show notification
        showNotification(
            'Drive Selected', 
            `Drive ${drive.name} selected for media storage.`,
            'success'
        );
    }
    
    /**
     * Handle share selected event from DriveManager
     * @param {object} data - The event data with share and mountpoint
     */
    function handleShareSelected(data) {
        const { share, mountpoint } = data;
        
        // Update form inputs with selected share info
        document.getElementById('media-directory').value = `${mountpoint}/media`;
        document.getElementById('downloads-directory').value = `${mountpoint}/downloads`;
        
        // Update share path with selected share
        document.getElementById('share-path-1').value = `${mountpoint}/media`;
        
        // Show notification
        showNotification(
            'Network Share Selected', 
            `Share ${share.name} selected for media storage.`,
            'success'
        );
    }
    
    /**
     * Handle error event from DriveManager
     * @param {object} data - The error event data
     */
    function handleDriveManagerError(data) {
        displayError(data.message, data.error);
    }
    
    /**
     * Toggle advanced drive options visibility
     */
    function toggleAdvancedDriveOptions() {
        const showAdvanced = document.getElementById('show-advanced-drive-options').checked;
        
        // Hide/show mount/unmount/format buttons based on toggle
        document.querySelectorAll('.mount-drive, .unmount-drive, .format-drive').forEach(btn => {
            if (showAdvanced) {
                btn.style.display = 'inline-flex';
            } else {
                btn.style.display = 'none';
            }
        });
    }

    /**
     * Save the storage configuration
     */
    function saveStorageConfig() {
        const mediaDir = document.getElementById('media-directory').value;
        const downloadsDir = document.getElementById('downloads-directory').value;
        const shareMethod = document.getElementById('share-method').value;
        
        // Get media paths from DriveManager
        const mediaPaths = driveManager.mediaPaths;
        
        // Collect share items
        const shares = [];
        const shareItems = document.querySelectorAll('.share-item');
        
        shareItems.forEach((item, index) => {
            const shareName = document.getElementById(`share-name-${index + 1}`).value;
            const sharePath = document.getElementById(`share-path-${index + 1}`).value;
            const sharePublic = document.getElementById(`share-public-${index + 1}`).checked;
            
            shares.push({
                name: shareName,
                path: sharePath,
                public: sharePublic
            });
        });
        
        // Get the selected drives
        const selectedDrives = driveManager.drives
            .filter(drive => drive.status === 'mounted')
            .map(drive => ({
                path: drive.path,
                mountpoint: drive.mountpoint,
                label: drive.label || drive.name
            }));
            
        // Get the network shares
        const networkShares = driveManager.networkShares
            .filter(share => share.status === 'mounted')
            .map(share => ({
                id: share.id,
                name: share.name,
                type: share.type,
                server: share.server,
                share_name: share.share_name,
                mountpoint: share.mountpoint
            }));
        
        state.storageConfig = {
            media_dir: mediaDir,
            downloads_dir: downloadsDir,
            share_method: shareMethod,
            shares: shares,
            drives: selectedDrives,
            network_shares: networkShares,
            media_paths: mediaPaths
        };
    }

    /**
     * Add a new share item to the form
     */
    function addShareItem() {
        const shareItems = document.querySelectorAll('.share-item');
        const newIndex = shareItems.length + 1;
        
        const newShareItem = document.createElement('div');
        newShareItem.className = 'share-item';
        newShareItem.innerHTML = `
            <div class="form-group">
                <label for="share-name-${newIndex}">Share Name</label>
                <input type="text" id="share-name-${newIndex}" name="share-name-${newIndex}" value="Share${newIndex}">
            </div>
            
            <div class="form-group">
                <label for="share-path-${newIndex}">Share Path</label>
                <input type="text" id="share-path-${newIndex}" name="share-path-${newIndex}" value="/mnt/media/share${newIndex}">
            </div>
            
            <div class="form-group toggle-container">
                <label for="share-public-${newIndex}">Public (No Authentication)</label>
                <label class="toggle-switch">
                    <input type="checkbox" id="share-public-${newIndex}" name="share-public-${newIndex}">
                    <span class="toggle-slider"></span>
                </label>
            </div>
            
            <button type="button" class="btn btn-danger btn-sm remove-share">
                <i class="fas fa-trash"></i> Remove
            </button>
        `;
        
        elements.sharesContainer.appendChild(newShareItem);
        
        // Add event listener to the remove button
        newShareItem.querySelector('.remove-share').addEventListener('click', () => {
            elements.sharesContainer.removeChild(newShareItem);
        });
    }

    /**
     * Save the service selection
     */
    function saveServiceSelection() {
        const services = {};
        
        // Media Management
        services.sonarr = document.getElementById('service-sonarr').checked;
        services.radarr = document.getElementById('service-radarr').checked;
        services.prowlarr = document.getElementById('service-prowlarr').checked;
        services.lidarr = document.getElementById('service-lidarr').checked;
        services.readarr = document.getElementById('service-readarr').checked;
        services.bazarr = document.getElementById('service-bazarr').checked;
        
        // Download Clients
        services.transmission = document.getElementById('service-transmission').checked;
        services.qbittorrent = document.getElementById('service-qbittorrent').checked;
        services.nzbget = document.getElementById('service-nzbget').checked;
        services.sabnzbd = document.getElementById('service-sabnzbd').checked;
        services.jdownloader = document.getElementById('service-jdownloader').checked;
        
        // Media Servers
        services.jellyfin = document.getElementById('service-jellyfin').checked;
        services.plex = document.getElementById('service-plex').checked;
        services.emby = document.getElementById('service-emby').checked;
        
        // Utilities
        services.heimdall = document.getElementById('service-heimdall').checked;
        services.overseerr = document.getElementById('service-overseerr').checked;
        services.tautulli = document.getElementById('service-tautulli').checked;
        services.portainer = document.getElementById('service-portainer').checked;
        services.get_iplayer = document.getElementById('service-get-iplayer').checked;
        
        state.selectedServices = services;
    }

    /**
     * Generate the installation summary
     */
    function generateSummary() {
        // Combine all configurations
        state.configSummary = {
            ...state.basicConfig,
            network: state.networkConfig,
            storage: state.storageConfig,
            services: state.selectedServices
        };
        
        // Generate summary HTML
        const summaryHTML = `
            <div class="summary-section">
                <h4><i class="fas fa-cog"></i> Basic Configuration</h4>
                <ul>
                    <li><strong>PUID:</strong> ${state.basicConfig.puid}</li>
                    <li><strong>PGID:</strong> ${state.basicConfig.pgid}</li>
                    <li><strong>Timezone:</strong> ${state.basicConfig.timezone}</li>
                    <li><strong>Media Directory:</strong> ${state.basicConfig.media_dir}</li>
                    <li><strong>Downloads Directory:</strong> ${state.basicConfig.downloads_dir}</li>
                </ul>
            </div>
            
            <div class="summary-section">
                <h4><i class="fas fa-network-wired"></i> Network Configuration</h4>
                <ul>
                    <li><strong>VPN:</strong> ${state.networkConfig.vpn.enabled ? 'Enabled' : 'Disabled'}</li>
                    ${state.networkConfig.vpn.enabled ? `
                        <li><strong>VPN Provider:</strong> ${state.networkConfig.vpn.provider}</li>
                        <li><strong>VPN Region:</strong> ${state.networkConfig.vpn.region}</li>
                    ` : ''}
                    <li><strong>Tailscale:</strong> ${state.networkConfig.tailscale.enabled ? 'Enabled' : 'Disabled'}</li>
                </ul>
            </div>
            
            <div class="summary-section">
                <h4><i class="fas fa-hdd"></i> Storage Configuration</h4>
                <ul>
                    <li><strong>Media Directory:</strong> ${state.storageConfig.media_dir}</li>
                    <li><strong>Downloads Directory:</strong> ${state.storageConfig.downloads_dir}</li>
                    <li><strong>Share Method:</strong> ${state.storageConfig.share_method}</li>
                    <li><strong>Shares:</strong> ${state.storageConfig.shares.length}</li>
                    <li><strong>Mounted Drives:</strong> ${state.storageConfig.drives?.length || 0}</li>
                    <li><strong>Network Shares:</strong> ${state.storageConfig.network_shares?.length || 0}</li>
                </ul>
                
                ${state.storageConfig.drives?.length > 0 ? `
                <div class="summary-subsection">
                    <h5>Mounted Drives</h5>
                    <ul>
                        ${state.storageConfig.drives.map(drive => `
                            <li>${drive.label} (${drive.path}) → ${drive.mountpoint}</li>
                        `).join('')}
                    </ul>
                </div>` : ''}
                
                ${state.storageConfig.network_shares?.length > 0 ? `
                <div class="summary-subsection">
                    <h5>Network Shares</h5>
                    <ul>
                        ${state.storageConfig.network_shares.map(share => `
                            <li>${share.name} (${share.type}://${share.server}/${share.share_name}) → ${share.mountpoint}</li>
                        `).join('')}
                    </ul>
                </div>` : ''}
                
                ${Object.keys(state.storageConfig.media_paths || {}).length > 0 ? `
                <div class="summary-subsection">
                    <h5>Media Paths</h5>
                    <ul>
                        ${Object.entries(state.storageConfig.media_paths).map(([key, value]) => `
                            <li><strong>${key}:</strong> ${value}</li>
                        `).join('')}
                    </ul>
                </div>` : ''}
            </div>
            
            <div class="summary-section">
                <h4><i class="fas fa-th-large"></i> Selected Services</h4>
                <div class="service-summary-grid">
                    ${generateServiceSummary(state.selectedServices)}
                </div>
            </div>
        `;
        
        elements.summaryContent.innerHTML = summaryHTML;
    }

    /**
     * Generate the service summary HTML
     * @param {object} services - The selected services
     * @returns {string} - The HTML for the service summary
     */
    function generateServiceSummary(services) {
        const serviceGroups = {
            'Media Management': ['sonarr', 'radarr', 'prowlarr', 'lidarr', 'readarr', 'bazarr'],
            'Download Clients': ['transmission', 'qbittorrent', 'nzbget', 'sabnzbd', 'jdownloader'],
            'Media Servers': ['jellyfin', 'plex', 'emby'],
            'Utilities': ['heimdall', 'overseerr', 'tautulli', 'portainer', 'get_iplayer']
        };
        
        const serviceNames = {
            sonarr: 'Sonarr',
            radarr: 'Radarr',
            prowlarr: 'Prowlarr',
            lidarr: 'Lidarr',
            readarr: 'Readarr',
            bazarr: 'Bazarr',
            transmission: 'Transmission',
            qbittorrent: 'qBittorrent',
            nzbget: 'NZBGet',
            sabnzbd: 'SABnzbd',
            jdownloader: 'JDownloader',
            jellyfin: 'Jellyfin',
            plex: 'Plex',
            emby: 'Emby',
            heimdall: 'Heimdall',
            overseerr: 'Overseerr',
            tautulli: 'Tautulli',
            portainer: 'Portainer',
            get_iplayer: 'Get iPlayer'
        };
        
        let summaryHTML = '';
        
        Object.entries(serviceGroups).forEach(([groupName, serviceList]) => {
            summaryHTML += `<div class="service-group"><h5>${groupName}</h5><ul>`;
            
            serviceList.forEach(service => {
                const isEnabled = services[service];
                summaryHTML += `
                    <li class="${isEnabled ? 'enabled' : 'disabled'}">
                        <i class="fas ${isEnabled ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                        ${serviceNames[service]}
                    </li>
                `;
            });
            
            summaryHTML += `</ul></div>`;
        });
        
        return summaryHTML;
    }

    /**
     * Start the installation process
     */
    async function startInstallation() {
        elements.btnStartInstall.disabled = true;
        
        try {
            // Combine all configuration data
            const config = {
                basic: state.basicConfig,
                network: state.networkConfig,
                storage: state.storageConfig,
                services: state.selectedServices
            };
            
            // Start the installation
            await api.startInstallation(config);
            
            // Show the installation progress screen
            goToStep('install-progress');
            
            // Start tracking the installation progress
            startProgressTracking();
            
        } catch (error) {
            displayError('Failed to start installation', error);
            elements.btnStartInstall.disabled = false;
        }
    }

    /**
     * Start tracking the installation progress
     * This function is kept for backward compatibility but now uses WebSockets
     * instead of polling for updates
     */
    function startProgressTracking() {
        // Update progress initially
        updateInstallationProgress();
        
        // WebSocket connection should already be established in init(),
        // and the event handlers will update the UI when updates are received
        
        // Just show a notification that we're using WebSockets for real-time updates
        showNotification(
            'Real-time Updates Enabled', 
            'Installation progress will update in real-time via WebSocket connection.',
            'info'
        );
    }

    /**
     * Update the installation progress display
     * @param {object} status - The installation status from the API
     */
    async function updateInstallationProgress(status) {
        if (!status) {
            try {
                status = await api.getInstallationStatus();
            } catch (error) {
                console.error('Error fetching installation status:', error);
                return;
            }
        }
        
        // Update progress bar and percentage
        const progressPercent = status.overall_progress || 0;
        elements.installProgressBar.style.width = `${progressPercent}%`;
        elements.installPercentage.textContent = `${Math.round(progressPercent)}%`;
        
        // Update current stage
        elements.installStage.textContent = status.current_stage_name || 'Preparing...';
        
        // Update log
        if (status.logs && status.logs.length > 0) {
            elements.installLog.textContent = status.logs.join('\n');
            // Scroll to bottom of log
            elements.installLog.scrollTop = elements.installLog.scrollHeight;
        }
        
        // Generate stages list if needed
        if (!status.stages) {
            const stages = [
                { id: "pre_check", name: "System Compatibility Check" },
                { id: "dependency_install", name: "Installing Dependencies" },
                { id: "docker_setup", name: "Setting up Docker" },
                { id: "generate_compose", name: "Generating Docker Compose Files" },
                { id: "service_setup", name: "Setting up Services" },
                { id: "container_creation", name: "Creating Containers" },
                { id: "post_install", name: "Performing Post-Installation Tasks" },
                { id: "finalization", name: "Finalizing Installation" }
            ];
            
            // Find current stage index
            const currentStageIndex = stages.findIndex(stage => stage.id === status.current_stage);
            
            updateStagesList(stages, currentStageIndex >= 0 ? currentStageIndex : 0);
        } else {
            updateStagesList(status.stages, status.current_stage_index);
        }
    }
    
    /**
     * Show a notification to the user
     * @param {string} title - The notification title
     * @param {string} message - The notification message
     * @param {string} type - The notification type (success, error, warning)
     */
    function showNotification(title, message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        // Set icon based on type
        let icon;
        switch (type) {
            case 'success':
                icon = 'fa-check-circle';
                break;
            case 'error':
                icon = 'fa-exclamation-triangle';
                break;
            case 'warning':
                icon = 'fa-exclamation-circle';
                break;
            default:
                icon = 'fa-info-circle';
        }
        
        notification.innerHTML = `
            <div class="notification-header">
                <i class="fas ${icon}"></i>
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
     * Update the stages list in the installation progress
     * @param {Array} stages - The list of installation stages
     * @param {number} currentIndex - The index of the current stage
     */
    function updateStagesList(stages, currentIndex) {
        const stagesHTML = stages.map((stage, index) => {
            let statusClass = '';
            let statusIcon = '';
            
            if (index < currentIndex) {
                // Completed stage
                statusClass = 'completed';
                statusIcon = '<i class="fas fa-check"></i>';
            } else if (index === currentIndex) {
                // Current stage
                statusClass = 'current';
                statusIcon = '<i class="fas fa-spinner fa-spin"></i>';
            } else {
                // Future stage
                statusClass = 'pending';
                statusIcon = '<i class="fas fa-circle"></i>';
            }
            
            return `
                <div class="installation-stage ${statusClass}">
                    <div class="stage-status">${statusIcon}</div>
                    <div class="stage-name">${stage}</div>
                </div>
            `;
        }).join('');
        
        elements.stageList.innerHTML = stagesHTML;
    }

    /**
     * Populate the service URLs on the completion screen
     * @param {object} serviceUrls - Object containing service names and URLs
     */
    function populateServiceUrls(serviceUrls) {
        if (!serviceUrls || Object.keys(serviceUrls).length === 0) {
            elements.serviceUrls.innerHTML = '<p>No service URLs available.</p>';
            return;
        }
        
        const urlsHTML = Object.entries(serviceUrls).map(([service, url]) => {
            return `
                <div class="service-url-item">
                    <div class="service-icon">
                        <i class="fas fa-external-link-alt"></i>
                    </div>
                    <div class="service-details">
                        <div class="service-name">${service}</div>
                        <a href="${url}" target="_blank" class="service-link">${url}</a>
                    </div>
                </div>
            `;
        }).join('');
        
        elements.serviceUrls.innerHTML = urlsHTML;
    }

    /**
     * Navigate to a specific step in the wizard
     * @param {string} step - The step to navigate to
     */
    function goToStep(step) {
        // Hide all steps
        Object.values(elements.steps).forEach(element => {
            element.classList.add('hidden');
        });
        
        // Show the target step
        elements.steps[step].classList.remove('hidden');
        
        // Update current step
        state.currentStep = step;
        
        // Update step indicators
        updateStepIndicators(step);
        
        // Update progress bar
        updateProgressBar(step);
        
        // Step-specific initialization
        if (step === 'storage-config') {
            initializeDriveManager();
        }
    }

    /**
     * Update the step indicators
     * @param {string} currentStep - The current step ID
     */
    function updateStepIndicators(currentStep) {
        elements.stepIndicators.forEach(indicator => {
            const step = indicator.dataset.step;
            
            // Remove all classes
            indicator.classList.remove('active', 'completed');
            
            // Add appropriate class
            if (step === currentStep) {
                indicator.classList.add('active');
            } else {
                // Get the step indices for comparison
                const stepIndex = getStepIndex(step);
                const currentIndex = getStepIndex(currentStep);
                
                if (stepIndex < currentIndex) {
                    indicator.classList.add('completed');
                }
            }
        });
    }

    /**
     * Update the progress bar
     * @param {string} currentStep - The current step ID
     */
    function updateProgressBar(currentStep) {
        const stepIndex = getStepIndex(currentStep);
        const totalSteps = Object.keys(elements.steps).length - 2; // Exclude progress and complete
        const progressPercentage = (stepIndex / totalSteps) * 100;
        
        elements.wizardProgressFill.style.width = `${progressPercentage}%`;
    }

    /**
     * Get the index of a step
     * @param {string} step - The step ID
     * @returns {number} - The step index
     */
    function getStepIndex(step) {
        const steps = [
            'system-check',
            'basic-config',
            'network-config',
            'storage-config',
            'service-selection',
            'install'
        ];
        
        return steps.indexOf(step);
    }

    /**
     * Display an error message
     * @param {string} title - The error title
     * @param {Error} error - The error object
     */
    function displayError(title, error) {
        console.error(title, error);
        
        // Create a notification element
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.innerHTML = `
            <div class="notification-header">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${title}</span>
                <button class="close-notification">×</button>
            </div>
            <div class="notification-content">
                ${error.message}
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
     * Format a file size in bytes to a human-readable format
     * @param {number} bytes - The size in bytes
     * @returns {string} - The formatted size string
     */
    function formatSize(bytes) {
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
    }
});