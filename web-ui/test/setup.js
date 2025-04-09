// Mock browser environment
Object.defineProperty(global.document, 'body', {
  value: {
    innerHTML: '',
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    contains: jest.fn().mockReturnValue(true)
  },
  writable: true
});

// Mock DOM elements
global.document.getElementById = jest.fn().mockImplementation((id) => {
  return {
    id,
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn().mockReturnValue(false),
      toggle: jest.fn()
    },
    style: {},
    dispatchEvent: jest.fn(),
    addEventListener: jest.fn(),
    querySelector: jest.fn(),
    querySelectorAll: jest.fn().mockReturnValue([]),
    innerHTML: ''
  };
});

// Mock querySelector
global.document.querySelector = jest.fn().mockImplementation(() => {
  return {
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(),
      toggle: jest.fn()
    },
    addEventListener: jest.fn(),
    querySelector: jest.fn(),
    querySelectorAll: jest.fn().mockReturnValue([]),
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    textContent: '',
    innerHTML: '',
    style: {}
  };
});

// Mock querySelectorAll
global.document.querySelectorAll = jest.fn().mockReturnValue([]);

// Mock createElement
global.document.createElement = jest.fn().mockImplementation((tag) => {
  return {
    tagName: tag.toUpperCase(),
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(),
      toggle: jest.fn()
    },
    style: {},
    addEventListener: jest.fn(),
    appendChild: jest.fn(),
    innerHTML: '',
    querySelector: jest.fn(),
    querySelectorAll: jest.fn().mockReturnValue([])
  };
});

// Mock API client
global.api = {
  get: jest.fn(),
  post: jest.fn(),
  checkSystemCompatibility: jest.fn().mockResolvedValue({
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
  }),
  getInstallationStatus: jest.fn().mockResolvedValue({
    current_stage: 'pre_check',
    current_stage_name: 'System Compatibility Check',
    stage_progress: 100,
    overall_progress: 5,
    status: 'in_progress',
    logs: ['Log entry 1', 'Log entry 2'],
    errors: [],
    start_time: Date.now() / 1000,
    end_time: null,
    elapsed_time: null
  }),
  saveBasicConfig: jest.fn().mockResolvedValue({
    status: 'success',
    message: 'Basic configuration setup completed',
    config: {
      puid: 1000,
      pgid: 1000,
      timezone: 'Europe/London',
      media_dir: '/mnt/media',
      downloads_dir: '/mnt/downloads'
    }
  }),
  saveNetworkConfig: jest.fn().mockResolvedValue({
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
  }),
  saveStorageConfig: jest.fn().mockResolvedValue({
    status: 'success',
    message: 'Storage configuration setup completed',
    config: {
      media_dir: '/mnt/media',
      downloads_dir: '/mnt/downloads'
    }
  }),
  saveServices: jest.fn().mockResolvedValue({
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
  }),
  startInstallation: jest.fn().mockResolvedValue({
    status: 'success',
    message: 'Installation started successfully',
    installation_id: '12345'
  }),
  getAvailableDrives: jest.fn().mockResolvedValue({
    status: 'success',
    drives: [
      {
        name: 'sda',
        path: '/dev/sda1',
        type: 'usb',
        size: 1099511627776, // 1TB
        used_percent: 25,
        mountpoint: '/mnt/media',
        status: 'mounted',
        filesystem: 'ext4',
        label: 'Media Drive'
      },
      {
        name: 'sdb',
        path: '/dev/sdb1',
        type: 'usb',
        size: 549755813888, // 512GB
        used_percent: 10,
        mountpoint: null,
        status: 'unmounted',
        filesystem: 'ext4',
        label: 'Backup Drive'
      },
      {
        name: 'sdc',
        path: '/dev/sdc',
        type: 'usb',
        size: 274877906944, // 256GB
        used_percent: 0,
        mountpoint: null,
        status: 'unformatted',
        filesystem: null,
        label: null
      }
    ]
  }),
  mountDrive: jest.fn().mockResolvedValue({
    status: 'success',
    message: 'Drive mounted successfully',
    mountpoint: '/mnt/test'
  }),
  unmountDrive: jest.fn().mockResolvedValue({
    status: 'success',
    message: 'Drive unmounted successfully'
  }),
  formatDrive: jest.fn().mockResolvedValue({
    status: 'success',
    message: 'Drive formatted successfully',
    filesystem: 'ext4'
  }),
  getNetworkShares: jest.fn().mockResolvedValue({
    status: 'success',
    shares: [
      {
        id: '1',
        name: 'Media Share',
        type: 'smb',
        server: '192.168.1.100',
        share_name: 'media',
        mountpoint: '/mnt/networkshare/media',
        username: 'user',
        status: 'mounted'
      },
      {
        id: '2',
        name: 'Backup Share',
        type: 'nfs',
        server: '192.168.1.101',
        share_name: '/volume1/backup',
        mountpoint: '/mnt/networkshare/backup',
        status: 'unmounted'
      }
    ]
  }),
  addNetworkShare: jest.fn().mockResolvedValue({
    status: 'success',
    message: 'Network share added successfully',
    id: '3'
  }),
  removeNetworkShare: jest.fn().mockResolvedValue({
    status: 'success',
    message: 'Network share removed successfully'
  }),
  getMediaPaths: jest.fn().mockResolvedValue({
    status: 'success',
    paths: {
      tv: '/mnt/media/tv',
      movies: '/mnt/media/movies',
      music: '/mnt/media/music',
      downloads: '/mnt/downloads'
    }
  }),
  updateMediaPaths: jest.fn().mockResolvedValue({
    status: 'success',
    message: 'Media paths updated successfully'
  })
};

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

// Mock console methods to prevent noise in test output
console.error = jest.fn();
console.log = jest.fn();
console.warn = jest.fn();

// Mock setTimeout and clearTimeout
global.originalSetTimeout = global.setTimeout;
global.setTimeout = jest.fn().mockImplementation((callback, delay) => {
  return Math.floor(Math.random() * 1000);
});

global.originalClearTimeout = global.clearTimeout;
global.clearTimeout = jest.fn();

// Mock global window
global.window = {
  matchMedia: jest.fn().mockImplementation((query) => {
    return {
      matches: false,
      addListener: jest.fn()
    };
  })
};

// Mock Promise.all for batch tests
const originalPromiseAll = Promise.all;
Promise.all = jest.fn().mockImplementation((promises) => {
  return originalPromiseAll(promises);
});