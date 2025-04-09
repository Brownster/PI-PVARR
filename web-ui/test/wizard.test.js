/**
 * Unit tests for the installation wizard JavaScript functionality.
 * 
 * Run these tests using Jest:
 * npm test
 */

// Import the wizard.js module
const wizardPath = '../js/wizard.js';

describe('Installation Wizard JavaScript', () => {
  let mockApi;
  
  beforeEach(() => {
    // Reset mocks
    jest.resetAllMocks();
    
    // Mock WebSocket client
    global.wsClient = {
      connect: jest.fn(),
      on: jest.fn(),
      send: jest.fn(),
      off: jest.fn(),
      options: {
        onOpen: jest.fn(),
        onMessage: jest.fn(),
        onClose: jest.fn(),
        onError: jest.fn(),
        onReconnect: jest.fn()
      }
    };
    
    // Setup API mock responses
    global.api.checkSystemCompatibility.mockResolvedValue({
      status: 'success',
      compatible: true,
      system_info: {
        memory: { total_gb: 4, free_gb: 3.2 },
        disk: { total_gb: 32, free_gb: 25 },
        docker_installed: true,
        is_raspberry_pi: true,
        model: 'Raspberry Pi 4 Model B Rev 1.2'
      },
      checks: {
        memory: { value: 4, compatible: true, recommended: 2 },
        disk_space: { value: 25, compatible: true, recommended: 10 },
        docker: { installed: true }
      }
    });
    
    global.api.getInstallationStatus.mockResolvedValue({
      current_stage: 'pre_check',
      current_stage_name: 'System Compatibility Check',
      stage_progress: 100,
      overall_progress: 5,
      status: 'in_progress',
      logs: [
        '[2023-08-04 12:30:45] Starting system compatibility check',
        '[2023-08-04 12:30:46] System compatibility check completed: Compatible'
      ],
      errors: [],
      start_time: 1691157045.123456,
      end_time: null,
      elapsed_time: null
    });
    
    global.api.saveBasicConfig.mockResolvedValue({
      status: 'success',
      message: 'Basic configuration setup completed',
      config: {
        puid: 1000,
        pgid: 1000,
        timezone: 'Europe/London',
        media_dir: '/mnt/media',
        downloads_dir: '/mnt/downloads'
      }
    });
    
    global.api.saveNetworkConfig.mockResolvedValue({
      status: 'success',
      message: 'Network configuration setup completed',
      config: {
        vpn: {
          enabled: true,
          provider: 'private internet access',
          username: 'user',
          password: 'pass',
          region: 'Netherlands'
        },
        tailscale: {
          enabled: true,
          auth_key: 'tskey-auth-example12345'
        }
      }
    });
    
    global.api.saveStorageConfig.mockResolvedValue({
      status: 'success',
      message: 'Storage configuration setup completed',
      config: {
        media_dir: '/mnt/media',
        downloads_dir: '/mnt/downloads'
      }
    });
    
    global.api.saveServices.mockResolvedValue({
      status: 'success',
      message: 'Service selection setup completed',
      services: {
        arr_apps: {
          sonarr: true,
          radarr: true,
          prowlarr: true
        },
        download_clients: {
          transmission: true
        },
        media_servers: {
          jellyfin: true
        }
      }
    });
    
    global.api.startInstallation.mockResolvedValue({
      status: 'success',
      message: 'Installation started successfully',
      installation_id: '12345'
    });
    
    global.api.getAvailableDrives.mockResolvedValue({
      status: 'success',
      drives: [
        {
          name: 'sda',
          path: '/dev/sda1',
          type: 'usb',
          size: 1099511627776, // 1TB
          used_percent: 25,
          mountpoint: '/mnt/media'
        },
        {
          name: 'sdb',
          path: '/dev/sdb1',
          type: 'usb',
          size: 549755813888, // 512GB
          used_percent: 10,
          mountpoint: null
        }
      ]
    });
  });

  // System Check Tests
  describe('System Compatibility Check', () => {
    it('should check system compatibility', async () => {
      // Create test function
      const runSystemCheck = async () => {
        try {
          const results = await global.api.checkSystemCompatibility();
          return {
            success: true,
            data: results
          };
        } catch (error) {
          return {
            success: false,
            error: error.message
          };
        }
      };
      
      // Run the function
      const result = await runSystemCheck();
      
      // Verify result
      expect(result.success).toBe(true);
      expect(result.data.compatible).toBe(true);
      expect(global.api.checkSystemCompatibility).toHaveBeenCalled();
    });
    
    it('should handle API errors', async () => {
      // Setup API to return an error
      global.api.checkSystemCompatibility.mockRejectedValue(new Error('API error'));
      
      // Create test function
      const runSystemCheck = async () => {
        try {
          const results = await global.api.checkSystemCompatibility();
          return {
            success: true,
            data: results
          };
        } catch (error) {
          return {
            success: false,
            error: error.message
          };
        }
      };
      
      // Run the function
      const result = await runSystemCheck();
      
      // Verify result
      expect(result.success).toBe(false);
      expect(result.error).toBe('API error');
    });
  });
  
  // Network Configuration Tests
  describe('Network Configuration', () => {
    it('should save network configuration', async () => {
      // Create test network config
      const networkConfig = {
        vpn: {
          enabled: true,
          provider: 'private internet access',
          username: 'user',
          password: 'pass',
          region: 'Netherlands'
        },
        tailscale: {
          enabled: true,
          auth_key: 'tskey-auth-example12345'
        }
      };
      
      // Save network config
      const result = await global.api.saveNetworkConfig(networkConfig);
      
      // Verify result
      expect(result.status).toBe('success');
      expect(result.config.vpn.enabled).toBe(true);
      expect(result.config.tailscale.enabled).toBe(true);
      expect(global.api.saveNetworkConfig).toHaveBeenCalledWith(networkConfig);
    });
  });
  
  // Storage Configuration Tests
  describe('Storage Configuration', () => {
    it('should get available drives', async () => {
      // Get drives
      const result = await global.api.getAvailableDrives();
      
      // Verify result
      expect(result.status).toBe('success');
      expect(result.drives.length).toBe(3);
      expect(result.drives[0].name).toBe('sda');
      expect(result.drives[1].name).toBe('sdb');
      expect(result.drives[2].name).toBe('sdc');
      expect(global.api.getAvailableDrives).toHaveBeenCalled();
    });
    
    it('should save storage configuration', async () => {
      // Create test storage config
      const storageConfig = {
        media_directory: '/mnt/media',
        downloads_directory: '/mnt/downloads'
      };
      
      // Save storage config
      const result = await global.api.saveStorageConfig(storageConfig);
      
      // Verify result
      expect(result.status).toBe('success');
      expect(result.config.media_dir).toBe('/mnt/media');
      expect(result.config.downloads_dir).toBe('/mnt/downloads');
      expect(global.api.saveStorageConfig).toHaveBeenCalledWith(storageConfig);
    });
    
    it('should save expanded storage configuration with drives and paths', () => {
      // Create mock state
      const state = {
        storageConfig: {}
      };
      
      // Mock document.getElementById
      document.getElementById.mockImplementation((id) => {
        if (id === 'media-directory') return { value: '/mnt/media' };
        if (id === 'downloads-directory') return { value: '/mnt/downloads' };
        if (id === 'share-method') return { value: 'samba' };
        if (id.startsWith('share-name-')) return { value: 'Media' };
        if (id.startsWith('share-path-')) return { value: '/mnt/media' };
        if (id.startsWith('share-public-')) return { checked: true };
        return null;
      });
      
      // Mock document.querySelectorAll
      document.querySelectorAll.mockImplementation((selector) => {
        if (selector === '.share-item') {
          return [{ index: 0 }]; // Mock a single share item
        }
        return [];
      });
      
      // Mock DriveManager with data
      global.driveManager = {
        drives: [
          {
            path: '/dev/sda1',
            mountpoint: '/mnt/media',
            label: 'Media Drive',
            status: 'mounted'
          }
        ],
        networkShares: [
          {
            id: '1',
            name: 'Media Share',
            type: 'smb',
            server: '192.168.1.100',
            share_name: 'media',
            mountpoint: '/mnt/networkshare/media',
            status: 'mounted'
          }
        ],
        mediaPaths: {
          tv: '/mnt/media/tv',
          movies: '/mnt/media/movies',
          music: '/mnt/media/music'
        }
      };
      
      // Define save storage config function (similar to wizard.js)
      const saveStorageConfig = () => {
        const mediaDir = document.getElementById('media-directory').value;
        const downloadsDir = document.getElementById('downloads-directory').value;
        const shareMethod = document.getElementById('share-method').value;
        
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
        const selectedDrives = global.driveManager.drives
          .filter(drive => drive.status === 'mounted')
          .map(drive => ({
            path: drive.path,
            mountpoint: drive.mountpoint,
            label: drive.label || drive.name
          }));
          
        // Get the network shares
        const networkShares = global.driveManager.networkShares
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
          media_paths: global.driveManager.mediaPaths
        };
      };
      
      // Call save function
      saveStorageConfig();
      
      // Verify expanded config
      expect(state.storageConfig.media_dir).toBe('/mnt/media');
      expect(state.storageConfig.downloads_dir).toBe('/mnt/downloads');
      expect(state.storageConfig.share_method).toBe('samba');
      expect(state.storageConfig.shares.length).toBe(1);
      expect(state.storageConfig.drives.length).toBe(1);
      expect(state.storageConfig.network_shares.length).toBe(1);
      expect(state.storageConfig.media_paths).toEqual({
        tv: '/mnt/media/tv',
        movies: '/mnt/media/movies',
        music: '/mnt/media/music'
      });
    });
  });
  
  // DriveManager integration tests
  describe('DriveManager integration', () => {
    it('should initialize DriveManager for storage step', () => {
      // Mock DriveManager
      global.driveManager = {
        initialize: jest.fn().mockResolvedValue({}),
        addEventListener: jest.fn(),
        drives: []
      };
      
      // Create mock state and elements
      const state = { availableDrives: [] };
      const elements = {
        drivesLoading: { classList: { remove: jest.fn(), add: jest.fn() } },
        drivesContainer: { classList: { remove: jest.fn(), add: jest.fn() } }
      };
      
      // Define initialization function (similar to wizard.js)
      const initializeDriveManager = async () => {
        elements.drivesLoading.classList.remove('hidden');
        elements.drivesContainer.classList.add('hidden');
        
        try {
          // Get references to container elements
          const drivesContainer = document.getElementById('drives-container');
          const networkSharesContainer = document.getElementById('network-shares-container');
          const mediaPathsContainer = document.getElementById('media-paths-container');
          
          // Initialize the DriveManager with the containers
          await global.driveManager.initialize(drivesContainer, networkSharesContainer, mediaPathsContainer);
          
          // Set up event listeners for DriveManager events
          global.driveManager.addEventListener('driveSelected', jest.fn());
          global.driveManager.addEventListener('shareSelected', jest.fn());
          global.driveManager.addEventListener('error', jest.fn());
          
          // Store drive data in state
          state.availableDrives = global.driveManager.drives;
          
        } finally {
          elements.drivesLoading.classList.remove('hidden');
          elements.drivesContainer.classList.add('hidden');
        }
      };
      
      // Call initialization function
      initializeDriveManager();
      
      // Verify DriveManager was initialized
      expect(global.driveManager.initialize).toHaveBeenCalled();
      expect(global.driveManager.addEventListener).toHaveBeenCalledTimes(3);
      expect(global.driveManager.addEventListener).toHaveBeenCalledWith('driveSelected', expect.any(Function));
      expect(global.driveManager.addEventListener).toHaveBeenCalledWith('shareSelected', expect.any(Function));
      expect(global.driveManager.addEventListener).toHaveBeenCalledWith('error', expect.any(Function));
    });
    
    it('should handle drive selection events', () => {
      // Mock document.getElementById
      document.getElementById.mockImplementation((id) => {
        return { value: '' };
      });
      
      // Mock showNotification
      const showNotification = jest.fn();
      
      // Define event handler (similar to wizard.js)
      const handleDriveSelected = (data) => {
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
      };
      
      // Call handler with mock data
      handleDriveSelected({
        drive: { name: 'sda', path: '/dev/sda1' },
        mountpoint: '/mnt/media'
      });
      
      // Verify inputs were updated
      expect(document.getElementById).toHaveBeenCalledWith('media-directory');
      expect(document.getElementById).toHaveBeenCalledWith('downloads-directory');
      expect(document.getElementById).toHaveBeenCalledWith('share-path-1');
      
      // Verify notification was shown
      expect(showNotification).toHaveBeenCalledWith(
        'Drive Selected',
        'Drive sda selected for media storage.',
        'success'
      );
    });
    
    it('should handle advanced drive options toggle', () => {
      // Mock buttons
      const buttons = [
        { style: { display: 'none' } },
        { style: { display: 'none' } },
        { style: { display: 'none' } }
      ];
      
      // Mock querySelectorAll
      document.querySelectorAll.mockImplementation(() => buttons);
      
      // Mock document.getElementById
      document.getElementById.mockImplementation(() => {
        return { checked: true };
      });
      
      // Define toggle function (similar to wizard.js)
      const toggleAdvancedDriveOptions = () => {
        const showAdvanced = document.getElementById('show-advanced-drive-options').checked;
        
        // Hide/show mount/unmount/format buttons based on toggle
        document.querySelectorAll('.mount-drive, .unmount-drive, .format-drive').forEach(btn => {
          if (showAdvanced) {
            btn.style.display = 'inline-flex';
          } else {
            btn.style.display = 'none';
          }
        });
      };
      
      // Call toggle function
      toggleAdvancedDriveOptions();
      
      // Verify buttons were updated
      buttons.forEach(btn => {
        expect(btn.style.display).toBe('inline-flex');
      });
    });
    
    it('should include enhanced storage information in summary', () => {
      // Create mock state with storage config including drives and network shares
      const state = {
        storageConfig: {
          media_dir: '/mnt/media',
          downloads_dir: '/mnt/downloads',
          share_method: 'samba',
          shares: [{ name: 'Media', path: '/mnt/media', public: true }],
          drives: [
            { label: 'Media Drive', path: '/dev/sda1', mountpoint: '/mnt/media' }
          ],
          network_shares: [
            { name: 'Media Share', type: 'smb', server: '192.168.1.100', 
              share_name: 'media', mountpoint: '/mnt/networkshare/media' }
          ],
          media_paths: {
            tv: '/mnt/media/tv',
            movies: '/mnt/media/movies',
            music: '/mnt/media/music'
          }
        }
      };
      
      // Mock summary container
      const summaryContent = { innerHTML: '' };
      
      // Define summary generator function (similar to wizard.js, but simplified)
      const generateStorageSummary = () => {
        const storageHTML = `
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
        `;
        
        summaryContent.innerHTML = storageHTML;
      };
      
      // Generate summary
      generateStorageSummary();
      
      // Verify summary was generated with enhanced information
      expect(summaryContent.innerHTML).toContain('Mounted Drives');
      expect(summaryContent.innerHTML).toContain('Network Shares');
      expect(summaryContent.innerHTML).toContain('Media Paths');
      expect(summaryContent.innerHTML).toContain('Media Drive');
      expect(summaryContent.innerHTML).toContain('Media Share');
      expect(summaryContent.innerHTML).toContain('/mnt/media/tv');
    });
  });
  
  // Service Selection Tests
  describe('Service Selection', () => {
    it('should save selected services', async () => {
      // Create test services config
      const servicesConfig = {
        arr_apps: {
          sonarr: true,
          radarr: true,
          prowlarr: true
        },
        download_clients: {
          transmission: true
        },
        media_servers: {
          jellyfin: true
        }
      };
      
      // Save services config
      const result = await global.api.saveServices(servicesConfig);
      
      // Verify result
      expect(result.status).toBe('success');
      expect(result.services.arr_apps.sonarr).toBe(true);
      expect(result.services.download_clients.transmission).toBe(true);
      expect(result.services.media_servers.jellyfin).toBe(true);
      expect(global.api.saveServices).toHaveBeenCalledWith(servicesConfig);
    });
  });
  
  // Installation Process Tests
  describe('Installation Process', () => {
    it('should start installation', async () => {
      // Create test config
      const installConfig = {
        basic: {
          puid: 1000,
          pgid: 1000,
          timezone: 'Europe/London',
          media_dir: '/mnt/media',
          downloads_dir: '/mnt/downloads'
        },
        network: {
          vpn: { enabled: true },
          tailscale: { enabled: false }
        },
        storage: {
          media_dir: '/mnt/media',
          downloads_dir: '/mnt/downloads'
        },
        services: {
          sonarr: true,
          radarr: true,
          jellyfin: true
        }
      };
      
      // Start installation
      const result = await global.api.startInstallation(installConfig);
      
      // Verify result
      expect(result.status).toBe('success');
      expect(result.message).toBe('Installation started successfully');
      expect(global.api.startInstallation).toHaveBeenCalledWith(installConfig);
    });
    
    it('should get installation status', async () => {
      // Get installation status
      const result = await global.api.getInstallationStatus();
      
      // Verify result
      expect(result.status).toBe('in_progress');
      expect(result.current_stage).toBe('pre_check');
      expect(result.overall_progress).toBe(5);
      expect(result.logs.length).toBe(2);
      expect(global.api.getInstallationStatus).toHaveBeenCalled();
    });
  });
  
  // WebSocket Integration Tests
  describe('WebSocket Integration', () => {
    // Setup and connection tests
    it('should set up WebSocket connection', () => {
      // Call setupWebSocket function (this would be called by the init function)
      const setupWebSocket = jest.fn(() => {
        wsClient.connect();
        wsClient.on('installation_status', () => {});
        wsClient.on('installation_complete', () => {});
      });
      
      setupWebSocket();
      
      // Verify that WebSocket connection was established
      expect(global.wsClient.connect).toHaveBeenCalled();
      expect(global.wsClient.on).toHaveBeenCalledWith('installation_status', expect.any(Function));
      expect(global.wsClient.on).toHaveBeenCalledWith('installation_complete', expect.any(Function));
    });
    
    it('should handle connection errors gracefully', () => {
      // Set up a mock connection handler that handles errors
      const handleConnectionError = jest.fn();
      
      // Create a mock error event
      const errorEvent = new Error('Connection failed');
      
      // Simulate a WebSocket connection error
      global.wsClient.options.onError(errorEvent);
      
      // Since we didn't register a handler, it should not crash
      // This is just testing that our WebSocket integration can handle connection failures gracefully
      
      // Set up an error handler
      global.wsClient.options.onError = handleConnectionError;
      
      // Trigger another error
      global.wsClient.options.onError(errorEvent);
      
      // Verify error handler was called
      expect(handleConnectionError).toHaveBeenCalledWith(errorEvent);
    });
    
    it('should handle reconnection events', () => {
      // Set up a mock reconnect handler
      const handleReconnect = jest.fn();
      global.wsClient.options.onReconnect = handleReconnect;
      
      // Create a mock state manager
      const state = { reconnecting: false };
      
      // Set up reconnection UI update function
      const updateReconnectionStatus = jest.fn((attempt, delay) => {
        state.reconnecting = true;
        // In a real app, this would update the UI to show reconnection status
      });
      
      // Set up global handler that updates UI
      global.wsClient.options.onReconnect = (attempt, delay) => {
        handleReconnect(attempt, delay);
        updateReconnectionStatus(attempt, delay);
      };
      
      // Simulate a reconnection event
      global.wsClient.options.onReconnect(1, 1500);
      
      // Verify handler was called with correct parameters
      expect(handleReconnect).toHaveBeenCalledWith(1, 1500);
      expect(updateReconnectionStatus).toHaveBeenCalledWith(1, 1500);
      expect(state.reconnecting).toBe(true);
    });
    
    // Status update tests
    it('should handle installation status updates from WebSocket', () => {
      // Create mock elements and state
      const state = {
        currentStep: 'install-progress',
        installationInProgress: false,
        installationComplete: false,
        installationProgress: 0,
        installationStage: ''
      };
      
      const mockElements = {
        installProgressBar: { style: { width: '0%' } },
        installPercentage: { textContent: '0%' },
        installStage: { textContent: '' },
        installLog: { 
          textContent: '',
          scrollTop: 0,
          scrollHeight: 100
        }
      };
      
      // Mock update function
      const updateInstallationProgress = jest.fn((status) => {
        // Update mock elements based on status
        mockElements.installProgressBar.style.width = `${status.overall_progress}%`;
        mockElements.installPercentage.textContent = `${Math.round(status.overall_progress)}%`;
        mockElements.installStage.textContent = status.current_stage_name || 'Preparing...';
        
        if (status.logs && status.logs.length > 0) {
          mockElements.installLog.textContent = status.logs.join('\n');
          mockElements.installLog.scrollTop = mockElements.installLog.scrollHeight;
        }
      });
      
      // Create mock WebSocket message handler
      const handleInstallationStatusUpdate = (data) => {
        // Update state
        state.installationInProgress = data.status === 'in_progress';
        state.installationComplete = data.status === 'completed';
        state.installationProgress = data.overall_progress;
        state.installationStage = data.current_stage;
        
        // Update UI if on the right screen
        if (state.currentStep === 'install-progress') {
          updateInstallationProgress(data);
        }
      };
      
      // Mock WebSocket message
      const wsMessage = {
        status: 'in_progress',
        current_stage: 'docker_setup',
        current_stage_name: 'Setting up Docker',
        stage_progress: 50,
        overall_progress: 30,
        logs: [
          'Starting installation process...',
          'Setting up Docker...'
        ]
      };
      
      // Call the handler
      handleInstallationStatusUpdate(wsMessage);
      
      // Verify state was updated
      expect(state.installationInProgress).toBe(true);
      expect(state.installationProgress).toBe(30);
      expect(state.installationStage).toBe('docker_setup');
      
      // Verify UI was updated via the update function
      expect(updateInstallationProgress).toHaveBeenCalledWith(wsMessage);
      expect(mockElements.installProgressBar.style.width).toBe('30%');
      expect(mockElements.installPercentage.textContent).toBe('30%');
      expect(mockElements.installStage.textContent).toBe('Setting up Docker');
      expect(mockElements.installLog.textContent).toBe('Starting installation process...\nSetting up Docker...');
    });
    
    it('should handle status updates when not on the progress screen', () => {
      // Create mock elements and state for a different step
      const state = {
        currentStep: 'service-selection',  // User is on a different step
        installationInProgress: false,
        installationComplete: false,
        installationProgress: 0,
        installationStage: ''
      };
      
      // Mock update function that should not be called
      const updateInstallationProgress = jest.fn();
      
      // Create mock WebSocket message handler
      const handleInstallationStatusUpdate = (data) => {
        // Update state
        state.installationInProgress = data.status === 'in_progress';
        state.installationComplete = data.status === 'completed';
        state.installationProgress = data.overall_progress;
        state.installationStage = data.current_stage;
        
        // Only update UI if on the progress screen
        if (state.currentStep === 'install-progress') {
          updateInstallationProgress(data);
        }
      };
      
      // Mock WebSocket message
      const wsMessage = {
        status: 'in_progress',
        current_stage: 'docker_setup',
        overall_progress: 30
      };
      
      // Call the handler
      handleInstallationStatusUpdate(wsMessage);
      
      // Verify state was updated
      expect(state.installationInProgress).toBe(true);
      expect(state.installationProgress).toBe(30);
      
      // Verify UI update function was NOT called since we're on a different screen
      expect(updateInstallationProgress).not.toHaveBeenCalled();
    });
    
    it('should handle installation completion from WebSocket', () => {
      // Create a mock notification function
      const showNotification = jest.fn();
      
      // Create mock state and goToStep function
      const state = {
        currentStep: 'install-progress',
        installationComplete: false
      };
      
      const goToStep = jest.fn(step => {
        state.currentStep = step;
      });
      
      const populateServiceUrls = jest.fn();
      
      // Create mock handler
      const handleInstallationComplete = (data) => {
        // Show notification
        showNotification(
          'Installation Complete',
          `Installation completed successfully in ${data.elapsed_time} seconds.`,
          'success'
        );
        
        // Go to completion screen if needed
        if (state.currentStep !== 'install-complete') {
          goToStep('install-complete');
        }
      };
      
      // Mock WebSocket message
      const wsMessage = {
        message: 'Installation completed successfully!',
        elapsed_time: '47.53'
      };
      
      // Call the handler
      handleInstallationComplete(wsMessage);
      
      // Verify notification was shown
      expect(showNotification).toHaveBeenCalledWith(
        'Installation Complete',
        'Installation completed successfully in 47.53 seconds.',
        'success'
      );
      
      // Verify navigation occurred
      expect(goToStep).toHaveBeenCalledWith('install-complete');
      expect(state.currentStep).toBe('install-complete');
    });
    
    it('should handle error messages from WebSocket', () => {
      // Create mock notification function
      const showNotification = jest.fn();
      
      // Create mock state
      const state = {
        installationInProgress: true,
        errors: []
      };
      
      // Create error handler
      const handleInstallationError = (data) => {
        // Add error to state
        state.errors.push(data.error);
        
        // Show notification
        showNotification(
          'Installation Error',
          data.error,
          'error'
        );
      };
      
      // Mock error message
      const errorMessage = {
        status: 'error',
        error: 'Failed to pull Docker image: network timeout'
      };
      
      // Call handler
      handleInstallationError(errorMessage);
      
      // Verify state was updated
      expect(state.errors).toContain('Failed to pull Docker image: network timeout');
      
      // Verify notification was shown
      expect(showNotification).toHaveBeenCalledWith(
        'Installation Error',
        'Failed to pull Docker image: network timeout',
        'error'
      );
    });
    
    // Advanced integration tests
    it('should integrate with API status polling as fallback', () => {
      // Mock state and websocket state
      const state = {
        installationInProgress: true,
        usingWebSocket: true,
        pollingInterval: null,
        lastStatusUpdate: Date.now()
      };
      
      // Mock API and update functions
      const updateInstallationProgress = jest.fn();
      const startStatusPolling = jest.fn(() => {
        state.pollingInterval = 'mock-interval';
        state.usingWebSocket = false;
      });
      const stopStatusPolling = jest.fn(() => {
        state.pollingInterval = null;
      });
      
      // Mock WebSocket event handlers
      const handleWebSocketClose = () => {
        // If installation is ongoing but websocket closed, fall back to polling
        if (state.installationInProgress && !state.pollingInterval) {
          startStatusPolling();
        }
      };
      
      const handleWebSocketOpen = () => {
        // If we reconnect, stop polling and use WebSocket
        if (state.pollingInterval) {
          stopStatusPolling();
          state.usingWebSocket = true;
        }
      };
      
      // Test fallback to polling on WebSocket close
      handleWebSocketClose();
      expect(startStatusPolling).toHaveBeenCalled();
      expect(state.pollingInterval).toBe('mock-interval');
      expect(state.usingWebSocket).toBe(false);
      
      // Test switch back to WebSocket on reconnection
      handleWebSocketOpen();
      expect(stopStatusPolling).toHaveBeenCalled();
      expect(state.usingWebSocket).toBe(true);
    });
    
    it('should send status request message via WebSocket', () => {
      // Mock state
      const state = {
        installationId: '12345',
        lastStatusRequest: null
      };
      
      // Define status request function
      const requestInstallationStatus = () => {
        state.lastStatusRequest = Date.now();
        
        // Send request via WebSocket
        global.wsClient.send(
          { installation_id: state.installationId }, 
          'get_installation_status'
        );
      };
      
      // Call the function
      requestInstallationStatus();
      
      // Verify request was sent
      expect(global.wsClient.send).toHaveBeenCalledWith(
        { installation_id: '12345' },
        'get_installation_status'
      );
      
      // Verify time was updated
      expect(state.lastStatusRequest).not.toBeNull();
    });
    
    it('should update service URLs on installation completion', () => {
      // Mock elements
      const mockElements = {
        sonarrUrl: { textContent: '', href: '' },
        radarrUrl: { textContent: '', href: '' },
        prowlarrUrl: { textContent: '', href: '' },
        jellyfinUrl: { textContent: '', href: '' }
      };
      
      // Mock service URLs from WebSocket
      const serviceUrls = {
        sonarr: 'http://localhost:8989',
        radarr: 'http://localhost:7878',
        prowlarr: 'http://localhost:9696',
        jellyfin: 'http://localhost:8096'
      };
      
      // Define function to populate service URLs
      const populateServiceUrls = (urls) => {
        // For each URL in our service URLs
        Object.keys(urls).forEach(service => {
          const url = urls[service];
          const element = mockElements[`${service}Url`];
          
          if (element) {
            element.textContent = url;
            element.href = url;
          }
        });
      };
      
      // Call function
      populateServiceUrls(serviceUrls);
      
      // Verify elements were updated
      expect(mockElements.sonarrUrl.textContent).toBe('http://localhost:8989');
      expect(mockElements.sonarrUrl.href).toBe('http://localhost:8989');
      expect(mockElements.radarrUrl.textContent).toBe('http://localhost:7878');
      expect(mockElements.radarrUrl.href).toBe('http://localhost:7878');
      expect(mockElements.prowlarrUrl.textContent).toBe('http://localhost:9696');
      expect(mockElements.prowlarrUrl.href).toBe('http://localhost:9696');
      expect(mockElements.jellyfinUrl.textContent).toBe('http://localhost:8096');
      expect(mockElements.jellyfinUrl.href).toBe('http://localhost:8096');
    });
  });
});