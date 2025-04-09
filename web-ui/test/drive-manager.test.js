/**
 * Unit tests for the Drive Manager
 */

// Import the DriveManager class
const drivePath = '../js/drive-manager.js';

describe('DriveManager', () => {
  let driveManager;
  let mockDrivesContainer;
  let mockNetworkSharesContainer;
  let mockMediaPathsContainer;
  
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Import DriveManager
    try {
      driveManager = require(drivePath).DriveManager;
    } catch (error) {
      // If it's not directly exported, use the global variable
      driveManager = global.driveManager;
    }
    
    // Create mock container elements
    mockDrivesContainer = {
      innerHTML: '',
      appendChild: jest.fn(),
      removeChild: jest.fn()
    };
    
    mockNetworkSharesContainer = {
      innerHTML: '',
      appendChild: jest.fn(),
      removeChild: jest.fn()
    };
    
    mockMediaPathsContainer = {
      innerHTML: '',
      appendChild: jest.fn(),
      removeChild: jest.fn()
    };
    
    // Mock document.createElement to return HTML elements with expected properties
    document.createElement = jest.fn().mockImplementation((tag) => {
      const element = {
        tagName: tag.toUpperCase(),
        classList: {
          add: jest.fn(),
          remove: jest.fn(),
          contains: jest.fn(),
          toggle: jest.fn()
        },
        style: {},
        dataset: {},
        children: [],
        addEventListener: jest.fn(),
        appendChild: jest.fn((child) => {
          element.children.push(child);
          return child;
        }),
        querySelector: jest.fn().mockReturnValue({
          addEventListener: jest.fn()
        }),
        querySelectorAll: jest.fn().mockReturnValue([]),
        innerHTML: ''
      };
      return element;
    });
    
    // Reset API mocks with default implementation
    global.api.getAvailableDrives.mockClear();
    global.api.mountDrive.mockClear();
    global.api.unmountDrive.mockClear();
    global.api.formatDrive.mockClear();
    global.api.getNetworkShares.mockClear();
    global.api.addNetworkShare.mockClear();
    global.api.removeNetworkShare.mockClear();
    global.api.getMediaPaths.mockClear();
    global.api.updateMediaPaths.mockClear();
  });
  
  // Core functionality tests
  describe('Core functionality', () => {
    it('should initialize correctly', () => {
      // Instantiate a new DriveManager
      const manager = new driveManager();
      
      // Verify initial state
      expect(manager.drives).toEqual([]);
      expect(manager.networkShares).toEqual([]);
      expect(manager.mediaPaths).toEqual({});
      expect(manager.eventListeners).toEqual({});
    });
    
    it('should initialize with containers', async () => {
      // Instantiate a new DriveManager
      const manager = new driveManager();
      
      // Initialize with containers
      await manager.initialize(
        mockDrivesContainer,
        mockNetworkSharesContainer,
        mockMediaPathsContainer
      );
      
      // Verify containers were stored and API calls were made
      expect(manager.drivesContainer).toBe(mockDrivesContainer);
      expect(manager.networkSharesContainer).toBe(mockNetworkSharesContainer);
      expect(manager.mediaPathsContainer).toBe(mockMediaPathsContainer);
      
      // Verify API calls
      expect(global.api.getAvailableDrives).toHaveBeenCalled();
      expect(global.api.getNetworkShares).toHaveBeenCalled();
      expect(global.api.getMediaPaths).toHaveBeenCalled();
    });
    
    it('should handle event listeners correctly', () => {
      const manager = new driveManager();
      const testEventHandler = jest.fn();
      
      // Add event listener
      manager.addEventListener('test-event', testEventHandler);
      
      // Verify event listener was added
      expect(manager.eventListeners['test-event']).toContain(testEventHandler);
      
      // Dispatch event
      const testData = { foo: 'bar' };
      manager.dispatchEvent('test-event', testData);
      
      // Verify event handler was called with correct data
      expect(testEventHandler).toHaveBeenCalledWith(testData);
    });
  });
  
  // API interaction tests
  describe('API interaction', () => {
    it('should refresh drives from API', async () => {
      const manager = new driveManager();
      const eventSpy = jest.fn();
      
      manager.addEventListener('drivesUpdated', eventSpy);
      
      // Get drives
      await manager.refreshDrives();
      
      // Verify API call was made
      expect(global.api.getAvailableDrives).toHaveBeenCalled();
      
      // Verify drives were stored
      expect(manager.drives.length).toBe(3);
      expect(manager.drives[0].name).toBe('sda');
      
      // Verify event was dispatched
      expect(eventSpy).toHaveBeenCalledWith(manager.drives);
    });
    
    it('should refresh network shares from API', async () => {
      const manager = new driveManager();
      const eventSpy = jest.fn();
      
      manager.addEventListener('networkSharesUpdated', eventSpy);
      
      // Get network shares
      await manager.refreshNetworkShares();
      
      // Verify API call was made
      expect(global.api.getNetworkShares).toHaveBeenCalled();
      
      // Verify network shares were stored
      expect(manager.networkShares.length).toBe(2);
      expect(manager.networkShares[0].name).toBe('Media Share');
      
      // Verify event was dispatched
      expect(eventSpy).toHaveBeenCalledWith(manager.networkShares);
    });
    
    it('should refresh media paths from API', async () => {
      const manager = new driveManager();
      const eventSpy = jest.fn();
      
      manager.addEventListener('mediaPathsUpdated', eventSpy);
      
      // Get media paths
      await manager.refreshMediaPaths();
      
      // Verify API call was made
      expect(global.api.getMediaPaths).toHaveBeenCalled();
      
      // Verify media paths were stored
      expect(Object.keys(manager.mediaPaths).length).toBe(4);
      expect(manager.mediaPaths.tv).toBe('/mnt/media/tv');
      
      // Verify event was dispatched
      expect(eventSpy).toHaveBeenCalledWith(manager.mediaPaths);
    });
    
    it('should handle API errors gracefully', async () => {
      const manager = new driveManager();
      const errorSpy = jest.fn();
      
      manager.addEventListener('error', errorSpy);
      
      // Mock API to throw error
      global.api.getAvailableDrives.mockRejectedValueOnce(new Error('API error'));
      
      // Try to refresh drives
      try {
        await manager.refreshDrives();
        // This should not be reached as an error should be thrown
        expect(true).toBe(false);
      } catch (error) {
        // Verify error was handled and propagated
        expect(error.message).toBe('API error');
        expect(errorSpy).toHaveBeenCalled();
        expect(errorSpy.mock.calls[0][0].message).toBe('Failed to refresh drives');
      }
    });
  });
  
  // Drive operations tests
  describe('Drive operations', () => {
    let manager;
    
    beforeEach(async () => {
      manager = new driveManager();
      
      // Initialize drives
      await manager.refreshDrives();
    });
    
    it('should mount a drive', async () => {
      const eventSpy = jest.fn();
      manager.addEventListener('driveAction', eventSpy);
      
      // Mount a drive
      await manager.mountDrive('/dev/sdb1', '/mnt/test', { options: 'defaults' });
      
      // Verify API call was made with correct parameters
      expect(global.api.mountDrive).toHaveBeenCalledWith('/dev/sdb1', '/mnt/test', { options: 'defaults' });
      
      // Verify drives were refreshed
      expect(global.api.getAvailableDrives).toHaveBeenCalledTimes(2);
      
      // Verify event was dispatched
      expect(eventSpy).toHaveBeenCalledWith({ 
        action: 'mount', 
        drive: '/dev/sdb1', 
        success: true 
      });
    });
    
    it('should unmount a drive', async () => {
      const eventSpy = jest.fn();
      manager.addEventListener('driveAction', eventSpy);
      
      // Unmount a drive
      await manager.unmountDrive('/dev/sda1');
      
      // Verify API call was made with correct parameters
      expect(global.api.unmountDrive).toHaveBeenCalledWith('/dev/sda1');
      
      // Verify drives were refreshed
      expect(global.api.getAvailableDrives).toHaveBeenCalledTimes(2);
      
      // Verify event was dispatched
      expect(eventSpy).toHaveBeenCalledWith({ 
        action: 'unmount', 
        drive: '/dev/sda1', 
        success: true 
      });
    });
    
    it('should format a drive', async () => {
      const eventSpy = jest.fn();
      manager.addEventListener('driveAction', eventSpy);
      
      // Format a drive
      await manager.formatDrive('/dev/sdc', 'ext4', 'New Drive');
      
      // Verify API call was made with correct parameters
      expect(global.api.formatDrive).toHaveBeenCalledWith('/dev/sdc', 'ext4', 'New Drive');
      
      // Verify drives were refreshed
      expect(global.api.getAvailableDrives).toHaveBeenCalledTimes(2);
      
      // Verify event was dispatched
      expect(eventSpy).toHaveBeenCalledWith({ 
        action: 'format', 
        drive: '/dev/sdc', 
        success: true 
      });
    });
    
    it('should handle operation errors', async () => {
      const eventSpy = jest.fn();
      manager.addEventListener('error', eventSpy);
      
      // Mock API to throw error
      global.api.mountDrive.mockRejectedValueOnce(new Error('Mount error'));
      
      // Try to mount a drive that will fail
      try {
        await manager.mountDrive('/dev/invalid', '/mnt/test');
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        // Verify error was handled
        expect(error.message).toBe('Mount error');
        expect(eventSpy).toHaveBeenCalled();
        expect(eventSpy.mock.calls[0][0].message).toBe('Failed to mount drive /dev/invalid');
      }
    });
  });
  
  // Network shares operations tests
  describe('Network shares operations', () => {
    let manager;
    
    beforeEach(async () => {
      manager = new driveManager();
      
      // Initialize network shares
      await manager.refreshNetworkShares();
    });
    
    it('should add a network share', async () => {
      const eventSpy = jest.fn();
      manager.addEventListener('networkShareAction', eventSpy);
      
      const shareConfig = {
        name: 'Test Share',
        type: 'smb',
        server: '192.168.1.200',
        share_name: 'test',
        mountpoint: '/mnt/networkshare/test',
        username: 'testuser',
        password: 'testpass'
      };
      
      // Add a network share
      await manager.addNetworkShare(shareConfig);
      
      // Verify API call was made with correct parameters
      expect(global.api.addNetworkShare).toHaveBeenCalledWith(shareConfig);
      
      // Verify network shares were refreshed
      expect(global.api.getNetworkShares).toHaveBeenCalledTimes(2);
      
      // Verify event was dispatched
      expect(eventSpy).toHaveBeenCalledWith({ 
        action: 'add', 
        share: shareConfig, 
        success: true 
      });
    });
    
    it('should remove a network share', async () => {
      const eventSpy = jest.fn();
      manager.addEventListener('networkShareAction', eventSpy);
      
      // Remove a network share
      await manager.removeNetworkShare('1');
      
      // Verify API call was made with correct parameters
      expect(global.api.removeNetworkShare).toHaveBeenCalledWith('1');
      
      // Verify network shares were refreshed
      expect(global.api.getNetworkShares).toHaveBeenCalledTimes(2);
      
      // Verify event was dispatched
      expect(eventSpy).toHaveBeenCalledWith({ 
        action: 'remove', 
        shareId: '1', 
        success: true 
      });
    });
    
    it('should handle operation errors', async () => {
      const eventSpy = jest.fn();
      manager.addEventListener('error', eventSpy);
      
      // Mock API to throw error
      global.api.removeNetworkShare.mockRejectedValueOnce(new Error('Remove error'));
      
      // Try to remove a network share that will fail
      try {
        await manager.removeNetworkShare('invalid');
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        // Verify error was handled
        expect(error.message).toBe('Remove error');
        expect(eventSpy).toHaveBeenCalled();
        expect(eventSpy.mock.calls[0][0].message).toBe('Failed to remove network share invalid');
      }
    });
  });
  
  // Media paths operations tests
  describe('Media paths operations', () => {
    let manager;
    
    beforeEach(async () => {
      manager = new driveManager();
      
      // Initialize media paths
      await manager.refreshMediaPaths();
    });
    
    it('should update media paths', async () => {
      const eventSpy = jest.fn();
      manager.addEventListener('mediaPathsUpdated', eventSpy);
      
      const paths = {
        tv: '/mnt/media/television',
        movies: '/mnt/media/films',
        books: '/mnt/media/books'
      };
      
      // Update media paths
      await manager.updateMediaPaths(paths);
      
      // Verify API call was made with correct parameters
      expect(global.api.updateMediaPaths).toHaveBeenCalledWith(paths);
      
      // Verify media paths were updated
      expect(manager.mediaPaths.tv).toBe('/mnt/media/television');
      expect(manager.mediaPaths.movies).toBe('/mnt/media/films');
      expect(manager.mediaPaths.books).toBe('/mnt/media/books');
      expect(manager.mediaPaths.music).toBe('/mnt/media/music'); // Original value preserved
      
      // Verify event was dispatched
      expect(eventSpy).toHaveBeenCalledWith(manager.mediaPaths);
    });
    
    it('should handle operation errors', async () => {
      const eventSpy = jest.fn();
      manager.addEventListener('error', eventSpy);
      
      // Mock API to throw error
      global.api.updateMediaPaths.mockRejectedValueOnce(new Error('Update error'));
      
      // Try to update media paths that will fail
      try {
        await manager.updateMediaPaths({ invalid: '/invalid/path' });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        // Verify error was handled
        expect(error.message).toBe('Update error');
        expect(eventSpy).toHaveBeenCalled();
        expect(eventSpy.mock.calls[0][0].message).toBe('Failed to update media paths');
      }
    });
  });
  
  // UI rendering tests
  describe('UI rendering', () => {
    let manager;
    
    beforeEach(async () => {
      manager = new driveManager();
      
      // Initialize with containers
      await manager.initialize(
        mockDrivesContainer,
        mockNetworkSharesContainer,
        mockMediaPathsContainer
      );
    });
    
    it('should render drives UI correctly', () => {
      // Verify initial render
      expect(mockDrivesContainer.innerHTML).toBe('');
      expect(mockDrivesContainer.appendChild).toHaveBeenCalled();
      
      // Get the drives grid that was created
      const drivesGrid = mockDrivesContainer.appendChild.mock.calls[0][0];
      expect(drivesGrid.classList.add).toHaveBeenCalledWith('drives-grid');
      
      // For more detailed testing, we'd need to mock more DOM functionality
    });
    
    it('should render network shares UI correctly', () => {
      // Verify initial render
      expect(mockNetworkSharesContainer.innerHTML).toBe('');
      
      // For this test we're just verifying that the function runs without errors
      // For more detailed testing, we'd need to mock more DOM functionality
      expect(() => {
        manager.renderNetworkSharesUI();
      }).not.toThrow();
    });
    
    it('should render media paths UI correctly', () => {
      // Verify initial render
      expect(mockMediaPathsContainer.innerHTML).toBe('');
      
      // For this test we're just verifying that the function runs without errors
      // For more detailed testing, we'd need to mock more DOM functionality
      expect(() => {
        manager.renderMediaPathsUI();
      }).not.toThrow();
    });
    
    it('should handle empty drives list correctly', () => {
      // Set drives to empty array
      manager.drives = [];
      
      // Render drives UI
      manager.renderDrivesUI();
      
      // Verify "no drives" message
      expect(mockDrivesContainer.innerHTML).toContain('No drives found');
    });
  });
  
  // User interaction tests
  describe('User interaction', () => {
    let manager;
    
    beforeEach(async () => {
      manager = new driveManager();
      
      // Mock showMountDialog
      manager.showMountDialog = jest.fn().mockResolvedValue('/mnt/mockpath');
      
      // Mock showFormatDialog
      manager.showFormatDialog = jest.fn().mockResolvedValue({
        filesystem: 'ext4',
        label: 'Mock Drive'
      });
      
      // Mock showConfirmDialog
      manager.showConfirmDialog = jest.fn().mockResolvedValue(true);
      
      // Mock showNotification
      manager.showNotification = jest.fn();
      
      // Initialize with data
      await manager.refreshDrives();
      await manager.refreshNetworkShares();
    });
    
    it('should handle mount drive button click', async () => {
      // Mock mountDrive
      manager.mountDrive = jest.fn().mockResolvedValue({});
      
      // Call handler
      await manager.handleMountDrive({
        path: '/dev/sdb1',
        name: 'sdb'
      });
      
      // Verify dialog was shown
      expect(manager.showMountDialog).toHaveBeenCalled();
      
      // Verify drive was mounted
      expect(manager.mountDrive).toHaveBeenCalledWith('/dev/sdb1', '/mnt/mockpath');
      
      // Verify notification was shown
      expect(manager.showNotification).toHaveBeenCalledWith(
        'Drive Mounted', 
        expect.stringContaining('mounted at /mnt/mockpath'), 
        'success'
      );
    });
    
    it('should handle format drive button click', async () => {
      // Mock formatDrive
      manager.formatDrive = jest.fn().mockResolvedValue({});
      
      // Call handler
      await manager.handleFormatDrive({
        path: '/dev/sdc',
        name: 'sdc'
      });
      
      // Verify dialog was shown
      expect(manager.showFormatDialog).toHaveBeenCalled();
      
      // Verify drive was formatted
      expect(manager.formatDrive).toHaveBeenCalledWith('/dev/sdc', 'ext4', 'Mock Drive');
      
      // Verify notification was shown
      expect(manager.showNotification).toHaveBeenCalledWith(
        'Drive Formatted', 
        expect.stringContaining('formatted as ext4'), 
        'success'
      );
    });
    
    it('should handle select drive button click', () => {
      // Mock document.getElementById
      document.getElementById.mockImplementation((id) => {
        if (id === 'media-directory' || id === 'downloads-directory') {
          return { value: '' };
        }
        return null;
      });
      
      // Create spy for dispatchEvent
      const dispatchSpy = jest.spyOn(manager, 'dispatchEvent');
      
      // Call handler
      manager.handleSelectDrive({
        path: '/dev/sda1',
        name: 'sda',
        mountpoint: '/mnt/media'
      });
      
      // Verify inputs were updated
      expect(document.getElementById).toHaveBeenCalledWith('media-directory');
      expect(document.getElementById).toHaveBeenCalledWith('downloads-directory');
      
      // Verify event was dispatched
      expect(dispatchSpy).toHaveBeenCalledWith('driveSelected', expect.objectContaining({
        drive: expect.objectContaining({
          path: '/dev/sda1'
        })
      }));
    });
    
    it('should handle add network share click', async () => {
      // Mock showAddShareDialog
      manager.showAddShareDialog = jest.fn().mockResolvedValue({
        name: 'Test Share',
        type: 'smb',
        server: '192.168.1.200',
        share_name: 'test'
      });
      
      // Mock addNetworkShare
      manager.addNetworkShare = jest.fn().mockResolvedValue({});
      
      // Call handler
      await manager.handleAddNetworkShare();
      
      // Verify dialog was shown
      expect(manager.showAddShareDialog).toHaveBeenCalled();
      
      // Verify share was added
      expect(manager.addNetworkShare).toHaveBeenCalled();
      
      // Verify notification was shown
      expect(manager.showNotification).toHaveBeenCalledWith(
        'Share Added', 
        expect.stringContaining('has been added'), 
        'success'
      );
    });
  });
  
  // Helper methods tests
  describe('Helper methods', () => {
    it('should format file sizes correctly', () => {
      const manager = new driveManager();
      
      // Test various sizes
      expect(manager.formatSize(0)).toBe('0 B');
      expect(manager.formatSize(1024)).toBe('1.00 KB');
      expect(manager.formatSize(1024 * 1024)).toBe('1.00 MB');
      expect(manager.formatSize(1024 * 1024 * 1024)).toBe('1.00 GB');
      expect(manager.formatSize(1024 * 1024 * 1024 * 1024)).toBe('1.00 TB');
      
      // Test non-round numbers
      expect(manager.formatSize(1536)).toBe('1.50 KB');
      expect(manager.formatSize(1024 * 1024 * 2.5)).toBe('2.50 MB');
    });
  });
  
  // Integration with Wizard tests
  describe('Integration with Wizard', () => {
    it('should handle advanced toggle correctly', () => {
      const manager = new driveManager();
      
      // Create mock button elements
      const buttons = [
        { style: { display: 'none' } },
        { style: { display: 'none' } },
        { style: { display: 'none' } }
      ];
      
      // Mock querySelectorAll to return our mock buttons
      document.querySelectorAll = jest.fn().mockReturnValue(buttons);
      
      // Define toggle function (similar to wizard.js)
      const toggleAdvancedDriveOptions = (showAdvanced) => {
        document.querySelectorAll('.mount-drive, .unmount-drive, .format-drive').forEach(btn => {
          if (showAdvanced) {
            btn.style.display = 'inline-flex';
          } else {
            btn.style.display = 'none';
          }
        });
      };
      
      // Test showing advanced options
      toggleAdvancedDriveOptions(true);
      
      // Verify buttons are shown
      buttons.forEach(btn => {
        expect(btn.style.display).toBe('inline-flex');
      });
      
      // Test hiding advanced options
      toggleAdvancedDriveOptions(false);
      
      // Verify buttons are hidden
      buttons.forEach(btn => {
        expect(btn.style.display).toBe('none');
      });
    });
  });
});