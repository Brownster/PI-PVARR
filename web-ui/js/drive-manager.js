/**
 * Pi-PVARR Drive Manager
 * Handles storage drive management for the Pi-PVARR media server
 */

class DriveManager {
    constructor() {
        this.drives = [];
        this.networkShares = [];
        this.mediaPaths = {};
        this.eventListeners = {};
    }

    /**
     * Initialize the drive manager
     * @param {HTMLElement} drivesContainer - The container for the drives UI
     * @param {HTMLElement} networkSharesContainer - The container for network shares UI
     * @param {HTMLElement} mediaPathsContainer - The container for media paths UI
     */
    async initialize(drivesContainer, networkSharesContainer, mediaPathsContainer) {
        this.drivesContainer = drivesContainer;
        this.networkSharesContainer = networkSharesContainer;
        this.mediaPathsContainer = mediaPathsContainer;
        
        // Load initial data
        await this.refreshDrives();
        await this.refreshNetworkShares();
        await this.refreshMediaPaths();
        
        // Render the UI
        this.renderDrivesUI();
        this.renderNetworkSharesUI();
        this.renderMediaPathsUI();
    }
    
    /**
     * Add an event listener
     * @param {string} event - The event to listen for
     * @param {Function} callback - The callback function
     */
    addEventListener(event, callback) {
        if (!this.eventListeners[event]) {
            this.eventListeners[event] = [];
        }
        this.eventListeners[event].push(callback);
    }
    
    /**
     * Dispatch an event
     * @param {string} event - The event to dispatch
     * @param {any} data - The event data
     */
    dispatchEvent(event, data) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => callback(data));
        }
    }
    
    /**
     * Refresh drives data from API
     */
    async refreshDrives() {
        try {
            const response = await api.getAvailableDrives();
            this.drives = response.drives || [];
            this.dispatchEvent('drivesUpdated', this.drives);
            return this.drives;
        } catch (error) {
            console.error('Error refreshing drives:', error);
            this.dispatchEvent('error', { message: 'Failed to refresh drives', error });
            throw error;
        }
    }
    
    /**
     * Refresh network shares data from API
     */
    async refreshNetworkShares() {
        try {
            const response = await api.getNetworkShares();
            this.networkShares = response.shares || [];
            this.dispatchEvent('networkSharesUpdated', this.networkShares);
            return this.networkShares;
        } catch (error) {
            console.error('Error refreshing network shares:', error);
            this.dispatchEvent('error', { message: 'Failed to refresh network shares', error });
            throw error;
        }
    }
    
    /**
     * Refresh media paths data from API
     */
    async refreshMediaPaths() {
        try {
            const response = await api.getMediaPaths();
            this.mediaPaths = response.paths || {};
            this.dispatchEvent('mediaPathsUpdated', this.mediaPaths);
            return this.mediaPaths;
        } catch (error) {
            console.error('Error refreshing media paths:', error);
            this.dispatchEvent('error', { message: 'Failed to refresh media paths', error });
            throw error;
        }
    }
    
    /**
     * Mount a drive
     * @param {string} drive - The drive to mount
     * @param {string} mountpoint - The mountpoint
     * @param {object} options - Mount options
     */
    async mountDrive(drive, mountpoint, options = {}) {
        try {
            const response = await api.mountDrive(drive, mountpoint, options);
            await this.refreshDrives();
            this.dispatchEvent('driveAction', { action: 'mount', drive, success: true });
            return response;
        } catch (error) {
            console.error(`Error mounting drive ${drive}:`, error);
            this.dispatchEvent('error', { message: `Failed to mount drive ${drive}`, error });
            throw error;
        }
    }
    
    /**
     * Unmount a drive
     * @param {string} drive - The drive to unmount
     */
    async unmountDrive(drive) {
        try {
            const response = await api.unmountDrive(drive);
            await this.refreshDrives();
            this.dispatchEvent('driveAction', { action: 'unmount', drive, success: true });
            return response;
        } catch (error) {
            console.error(`Error unmounting drive ${drive}:`, error);
            this.dispatchEvent('error', { message: `Failed to unmount drive ${drive}`, error });
            throw error;
        }
    }
    
    /**
     * Format a drive
     * @param {string} drive - The drive to format
     * @param {string} filesystem - The filesystem type
     * @param {string} label - The volume label
     */
    async formatDrive(drive, filesystem, label) {
        try {
            const response = await api.formatDrive(drive, filesystem, label);
            await this.refreshDrives();
            this.dispatchEvent('driveAction', { action: 'format', drive, success: true });
            return response;
        } catch (error) {
            console.error(`Error formatting drive ${drive}:`, error);
            this.dispatchEvent('error', { message: `Failed to format drive ${drive}`, error });
            throw error;
        }
    }
    
    /**
     * Add a network share
     * @param {object} shareConfig - The share configuration
     */
    async addNetworkShare(shareConfig) {
        try {
            const response = await api.addNetworkShare(shareConfig);
            await this.refreshNetworkShares();
            this.dispatchEvent('networkShareAction', { action: 'add', share: shareConfig, success: true });
            return response;
        } catch (error) {
            console.error('Error adding network share:', error);
            this.dispatchEvent('error', { message: 'Failed to add network share', error });
            throw error;
        }
    }
    
    /**
     * Remove a network share
     * @param {string} id - The share ID to remove
     */
    async removeNetworkShare(id) {
        try {
            const response = await api.removeNetworkShare(id);
            await this.refreshNetworkShares();
            this.dispatchEvent('networkShareAction', { action: 'remove', shareId: id, success: true });
            return response;
        } catch (error) {
            console.error(`Error removing network share ${id}:`, error);
            this.dispatchEvent('error', { message: `Failed to remove network share ${id}`, error });
            throw error;
        }
    }
    
    /**
     * Update media paths
     * @param {object} paths - The paths to update
     */
    async updateMediaPaths(paths) {
        try {
            const response = await api.updateMediaPaths(paths);
            this.mediaPaths = { ...this.mediaPaths, ...paths };
            this.dispatchEvent('mediaPathsUpdated', this.mediaPaths);
            return response;
        } catch (error) {
            console.error('Error updating media paths:', error);
            this.dispatchEvent('error', { message: 'Failed to update media paths', error });
            throw error;
        }
    }
    
    /**
     * Render the drives UI
     */
    renderDrivesUI() {
        if (!this.drivesContainer) return;
        
        // Clear the container
        this.drivesContainer.innerHTML = '';
        
        if (this.drives.length === 0) {
            this.drivesContainer.innerHTML = '<p class="no-drives-message">No drives found. Please attach storage devices.</p>';
            return;
        }
        
        // Create drives grid
        const drivesGrid = document.createElement('div');
        drivesGrid.className = 'drives-grid';
        
        // Add drives to grid
        this.drives.forEach(drive => {
            const driveCard = this.createDriveCard(drive);
            drivesGrid.appendChild(driveCard);
        });
        
        this.drivesContainer.appendChild(drivesGrid);
    }
    
    /**
     * Create a drive card element
     * @param {object} drive - The drive data
     * @returns {HTMLElement} - The drive card element
     */
    createDriveCard(drive) {
        const card = document.createElement('div');
        card.className = `drive-card ${drive.status}`;
        card.dataset.drive = drive.path;
        
        const isUsable = drive.status === 'mounted' || drive.status === 'unmounted';
        const canMount = drive.status === 'unmounted' && drive.filesystem;
        const canUnmount = drive.status === 'mounted';
        const canFormat = drive.status === 'unmounted' || drive.status === 'unformatted';
        
        // Determine icon based on drive type
        let icon = 'fa-hdd';
        if (drive.type === 'usb') icon = 'fa-usb';
        else if (drive.type === 'sd') icon = 'fa-sd-card';
        
        // Create drive card content
        card.innerHTML = `
            <div class="drive-card-header">
                <div class="drive-icon">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="drive-title">
                    <h4>${drive.label || drive.name}</h4>
                    <span class="drive-model">${drive.model || drive.path}</span>
                </div>
                <div class="drive-status">
                    <span class="status-badge ${drive.status}">${drive.status}</span>
                </div>
            </div>
            <div class="drive-card-details">
                <div class="detail-row">
                    <span class="detail-label">Path:</span>
                    <span class="detail-value">${drive.path}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Size:</span>
                    <span class="detail-value">${this.formatSize(drive.size)}</span>
                </div>
                ${drive.mountpoint ? `
                <div class="detail-row">
                    <span class="detail-label">Mount:</span>
                    <span class="detail-value">${drive.mountpoint}</span>
                </div>` : ''}
                ${drive.filesystem ? `
                <div class="detail-row">
                    <span class="detail-label">Filesystem:</span>
                    <span class="detail-value">${drive.filesystem}</span>
                </div>` : ''}
                ${drive.used_percent ? `
                <div class="detail-row">
                    <span class="detail-label">Used:</span>
                    <div class="usage-bar">
                        <div class="usage-fill" style="width: ${drive.used_percent}%"></div>
                    </div>
                    <span class="usage-text">${drive.used_percent}%</span>
                </div>` : ''}
            </div>
            <div class="drive-card-actions">
                ${canMount ? `
                <button class="btn btn-sm btn-primary mount-drive" title="Mount Drive" style="display: none;">
                    <i class="fas fa-plug"></i> Mount
                </button>` : ''}
                ${canUnmount ? `
                <button class="btn btn-sm btn-warning unmount-drive" title="Unmount Drive" style="display: none;">
                    <i class="fas fa-eject"></i> Unmount
                </button>` : ''}
                ${canFormat ? `
                <button class="btn btn-sm btn-danger format-drive" title="Format Drive" style="display: none;">
                    <i class="fas fa-eraser"></i> Format
                </button>` : ''}
                ${isUsable ? `
                <button class="btn btn-sm btn-success select-drive" title="Select for Media">
                    <i class="fas fa-check"></i> Select
                </button>` : ''}
            </div>
        `;
        
        // Add event listeners
        if (canMount) {
            card.querySelector('.mount-drive').addEventListener('click', () => this.handleMountDrive(drive));
        }
        
        if (canUnmount) {
            card.querySelector('.unmount-drive').addEventListener('click', () => this.handleUnmountDrive(drive));
        }
        
        if (canFormat) {
            card.querySelector('.format-drive').addEventListener('click', () => this.handleFormatDrive(drive));
        }
        
        if (isUsable) {
            card.querySelector('.select-drive').addEventListener('click', () => this.handleSelectDrive(drive));
        }
        
        return card;
    }
    
    /**
     * Handle mount drive button click
     * @param {object} drive - The drive to mount
     */
    async handleMountDrive(drive) {
        // Show mount drive dialog
        const mountpoint = await this.showMountDialog(drive);
        
        if (mountpoint) {
            try {
                await this.mountDrive(drive.path, mountpoint);
                this.showNotification('Drive Mounted', `Drive ${drive.path} has been mounted at ${mountpoint}`, 'success');
            } catch (error) {
                this.showNotification('Mount Failed', `Failed to mount drive ${drive.path}`, 'error');
            }
        }
    }
    
    /**
     * Handle unmount drive button click
     * @param {object} drive - The drive to unmount
     */
    async handleUnmountDrive(drive) {
        // Show confirmation dialog
        const confirmed = await this.showConfirmDialog('Unmount Drive', `Are you sure you want to unmount ${drive.path} from ${drive.mountpoint}?`);
        
        if (confirmed) {
            try {
                await this.unmountDrive(drive.path);
                this.showNotification('Drive Unmounted', `Drive ${drive.path} has been unmounted`, 'success');
            } catch (error) {
                this.showNotification('Unmount Failed', `Failed to unmount drive ${drive.path}`, 'error');
            }
        }
    }
    
    /**
     * Handle format drive button click
     * @param {object} drive - The drive to format
     */
    async handleFormatDrive(drive) {
        // Show format drive dialog
        const result = await this.showFormatDialog(drive);
        
        if (result) {
            const { filesystem, label } = result;
            
            try {
                await this.formatDrive(drive.path, filesystem, label);
                this.showNotification('Drive Formatted', `Drive ${drive.path} has been formatted as ${filesystem}`, 'success');
            } catch (error) {
                this.showNotification('Format Failed', `Failed to format drive ${drive.path}`, 'error');
            }
        }
    }
    
    /**
     * Handle select drive button click
     * @param {object} drive - The selected drive
     */
    handleSelectDrive(drive) {
        const mountpoint = drive.mountpoint || '/mnt/' + drive.name;
        
        // Update media directory inputs
        const mediaDir = document.getElementById('media-directory');
        const downloadsDir = document.getElementById('downloads-directory');
        
        if (mediaDir) mediaDir.value = `${mountpoint}/media`;
        if (downloadsDir) downloadsDir.value = `${mountpoint}/downloads`;
        
        this.dispatchEvent('driveSelected', { drive, mountpoint });
    }
    
    /**
     * Show mount drive dialog
     * @param {object} drive - The drive to mount
     * @returns {Promise<string|null>} - Promise resolving to the mountpoint or null if cancelled
     */
    showMountDialog(drive) {
        return new Promise(resolve => {
            // Create modal backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop';
            document.body.appendChild(backdrop);
            
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Mount Drive ${drive.path}</h3>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="mount-form">
                            <div class="form-group">
                                <label for="mountpoint">Mount Point</label>
                                <input type="text" id="mountpoint" name="mountpoint" value="/mnt/${drive.name}" required>
                                <small>Directory where the drive will be mounted</small>
                            </div>
                            <div class="form-group">
                                <label for="mount-options">Mount Options</label>
                                <input type="text" id="mount-options" name="options" value="defaults">
                                <small>Comma-separated mount options</small>
                            </div>
                            <div class="form-group toggle-container">
                                <label for="mount-persistent">Mount Persistently (Add to fstab)</label>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="mount-persistent" name="persistent" checked>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary cancel-btn">Cancel</button>
                        <button class="btn btn-primary mount-btn">Mount</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Add event listeners
            const closeModal = () => {
                document.body.removeChild(modal);
                document.body.removeChild(backdrop);
                resolve(null);
            };
            
            modal.querySelector('.close-modal').addEventListener('click', closeModal);
            modal.querySelector('.cancel-btn').addEventListener('click', closeModal);
            
            modal.querySelector('.mount-btn').addEventListener('click', () => {
                const form = modal.querySelector('#mount-form');
                const mountpoint = form.mountpoint.value.trim();
                
                if (!mountpoint) {
                    alert('Mountpoint is required');
                    return;
                }
                
                document.body.removeChild(modal);
                document.body.removeChild(backdrop);
                resolve(mountpoint);
            });
        });
    }
    
    /**
     * Show format drive dialog
     * @param {object} drive - The drive to format
     * @returns {Promise<object|null>} - Promise resolving to format options or null if cancelled
     */
    showFormatDialog(drive) {
        return new Promise(resolve => {
            // Create modal backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop';
            document.body.appendChild(backdrop);
            
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Format Drive ${drive.path}</h3>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="format-warning">
                            <i class="fas fa-exclamation-triangle"></i>
                            <p>Warning: Formatting will permanently delete all data on this drive. This action cannot be undone.</p>
                        </div>
                        <form id="format-form">
                            <div class="form-group">
                                <label for="filesystem">Filesystem Type</label>
                                <select id="filesystem" name="filesystem">
                                    <option value="ext4">ext4 (Linux)</option>
                                    <option value="xfs">XFS (Linux)</option>
                                    <option value="ntfs">NTFS (Windows/Linux)</option>
                                    <option value="exfat">exFAT (Portable)</option>
                                    <option value="vfat">FAT32 (Portable, legacy)</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="label">Volume Label</label>
                                <input type="text" id="label" name="label" value="${drive.label || 'MEDIA'}">
                            </div>
                            <div class="confirmation-check">
                                <input type="checkbox" id="confirm-format" required>
                                <label for="confirm-format">I understand that all data on this drive will be permanently deleted</label>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary cancel-btn">Cancel</button>
                        <button class="btn btn-danger format-btn" disabled>Format Drive</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Add event listeners
            const closeModal = () => {
                document.body.removeChild(modal);
                document.body.removeChild(backdrop);
                resolve(null);
            };
            
            modal.querySelector('.close-modal').addEventListener('click', closeModal);
            modal.querySelector('.cancel-btn').addEventListener('click', closeModal);
            
            // Enable/disable format button based on confirmation
            const confirmCheck = modal.querySelector('#confirm-format');
            const formatBtn = modal.querySelector('.format-btn');
            
            confirmCheck.addEventListener('change', () => {
                formatBtn.disabled = !confirmCheck.checked;
            });
            
            formatBtn.addEventListener('click', () => {
                const form = modal.querySelector('#format-form');
                const filesystem = form.filesystem.value;
                const label = form.label.value.trim();
                
                document.body.removeChild(modal);
                document.body.removeChild(backdrop);
                resolve({ filesystem, label });
            });
        });
    }
    
    /**
     * Show confirmation dialog
     * @param {string} title - The dialog title
     * @param {string} message - The dialog message
     * @returns {Promise<boolean>} - Promise resolving to true if confirmed, false otherwise
     */
    showConfirmDialog(title, message) {
        return new Promise(resolve => {
            // Create modal backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop';
            document.body.appendChild(backdrop);
            
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>${title}</h3>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary cancel-btn">Cancel</button>
                        <button class="btn btn-primary confirm-btn">Confirm</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Add event listeners
            const closeModal = (result) => {
                document.body.removeChild(modal);
                document.body.removeChild(backdrop);
                resolve(result);
            };
            
            modal.querySelector('.close-modal').addEventListener('click', () => closeModal(false));
            modal.querySelector('.cancel-btn').addEventListener('click', () => closeModal(false));
            modal.querySelector('.confirm-btn').addEventListener('click', () => closeModal(true));
        });
    }
    
    /**
     * Show notification
     * @param {string} title - The notification title
     * @param {string} message - The notification message
     * @param {string} type - The notification type
     */
    showNotification(title, message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        // Set icon based on type
        let icon;
        switch (type) {
            case 'success': icon = 'fa-check-circle'; break;
            case 'error': icon = 'fa-exclamation-triangle'; break;
            case 'warning': icon = 'fa-exclamation-circle'; break;
            default: icon = 'fa-info-circle';
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
     * Render network shares UI
     */
    renderNetworkSharesUI() {
        if (!this.networkSharesContainer) return;
        
        // Clear the container
        this.networkSharesContainer.innerHTML = '';
        
        // Add "Add Network Share" button
        const addShareBtn = document.createElement('button');
        addShareBtn.className = 'btn btn-primary add-network-share';
        addShareBtn.innerHTML = '<i class="fas fa-plus"></i> Add Network Share';
        addShareBtn.addEventListener('click', () => this.handleAddNetworkShare());
        
        this.networkSharesContainer.appendChild(addShareBtn);
        
        // Create shares container
        const sharesContainer = document.createElement('div');
        sharesContainer.className = 'network-shares';
        
        if (this.networkShares.length === 0) {
            sharesContainer.innerHTML = '<p class="no-shares-message">No network shares configured.</p>';
        } else {
            // Add shares
            this.networkShares.forEach(share => {
                const shareCard = this.createNetworkShareCard(share);
                sharesContainer.appendChild(shareCard);
            });
        }
        
        this.networkSharesContainer.appendChild(sharesContainer);
    }
    
    /**
     * Create a network share card element
     * @param {object} share - The share data
     * @returns {HTMLElement} - The share card element
     */
    createNetworkShareCard(share) {
        const card = document.createElement('div');
        card.className = `network-share-card ${share.status}`;
        card.dataset.id = share.id;
        
        const canMount = share.status === 'unmounted';
        const canUnmount = share.status === 'mounted';
        
        // Determine icon based on share type
        let icon = 'fa-network-wired';
        if (share.type === 'smb') icon = 'fa-windows';
        else if (share.type === 'nfs') icon = 'fa-server';
        
        // Create share card content
        card.innerHTML = `
            <div class="share-card-header">
                <div class="share-icon">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="share-title">
                    <h4>${share.name}</h4>
                    <span class="share-server">${share.server}:${share.share_name}</span>
                </div>
                <div class="share-status">
                    <span class="status-badge ${share.status}">${share.status}</span>
                </div>
            </div>
            <div class="share-card-details">
                <div class="detail-row">
                    <span class="detail-label">Type:</span>
                    <span class="detail-value">${share.type.toUpperCase()}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Server:</span>
                    <span class="detail-value">${share.server}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Share:</span>
                    <span class="detail-value">${share.share_name}</span>
                </div>
                ${share.mountpoint ? `
                <div class="detail-row">
                    <span class="detail-label">Mount:</span>
                    <span class="detail-value">${share.mountpoint}</span>
                </div>` : ''}
                ${share.username ? `
                <div class="detail-row">
                    <span class="detail-label">User:</span>
                    <span class="detail-value">${share.username}</span>
                </div>` : ''}
            </div>
            <div class="share-card-actions">
                ${canMount ? `
                <button class="btn btn-sm btn-primary mount-share" title="Mount Share">
                    <i class="fas fa-plug"></i> Mount
                </button>` : ''}
                ${canUnmount ? `
                <button class="btn btn-sm btn-warning unmount-share" title="Unmount Share">
                    <i class="fas fa-eject"></i> Unmount
                </button>` : ''}
                <button class="btn btn-sm btn-danger remove-share" title="Remove Share">
                    <i class="fas fa-trash"></i> Remove
                </button>
                <button class="btn btn-sm btn-success select-share" title="Select for Media">
                    <i class="fas fa-check"></i> Select
                </button>
            </div>
        `;
        
        // Add event listeners
        if (canMount) {
            card.querySelector('.mount-share').addEventListener('click', () => this.handleMountShare(share));
        }
        
        if (canUnmount) {
            card.querySelector('.unmount-share').addEventListener('click', () => this.handleUnmountShare(share));
        }
        
        card.querySelector('.remove-share').addEventListener('click', () => this.handleRemoveShare(share));
        card.querySelector('.select-share').addEventListener('click', () => this.handleSelectShare(share));
        
        return card;
    }
    
    /**
     * Handle add network share button click
     */
    async handleAddNetworkShare() {
        const shareConfig = await this.showAddShareDialog();
        
        if (shareConfig) {
            try {
                await this.addNetworkShare(shareConfig);
                this.showNotification('Share Added', `Network share ${shareConfig.name} has been added`, 'success');
            } catch (error) {
                this.showNotification('Add Failed', `Failed to add network share`, 'error');
            }
        }
    }
    
    /**
     * Handle mount share button click
     * @param {object} share - The share to mount
     */
    async handleMountShare(share) {
        try {
            // Use the drive mount API since it's the same concept
            await this.mountDrive(`${share.type}://${share.server}/${share.share_name}`, share.mountpoint);
            this.showNotification('Share Mounted', `Share ${share.name} has been mounted`, 'success');
            await this.refreshNetworkShares();
        } catch (error) {
            this.showNotification('Mount Failed', `Failed to mount share ${share.name}`, 'error');
        }
    }
    
    /**
     * Handle unmount share button click
     * @param {object} share - The share to unmount
     */
    async handleUnmountShare(share) {
        const confirmed = await this.showConfirmDialog('Unmount Share', `Are you sure you want to unmount ${share.name}?`);
        
        if (confirmed) {
            try {
                await this.unmountDrive(share.mountpoint);
                this.showNotification('Share Unmounted', `Share ${share.name} has been unmounted`, 'success');
                await this.refreshNetworkShares();
            } catch (error) {
                this.showNotification('Unmount Failed', `Failed to unmount share ${share.name}`, 'error');
            }
        }
    }
    
    /**
     * Handle remove share button click
     * @param {object} share - The share to remove
     */
    async handleRemoveShare(share) {
        const confirmed = await this.showConfirmDialog('Remove Share', `Are you sure you want to remove ${share.name}?`);
        
        if (confirmed) {
            try {
                await this.removeNetworkShare(share.id);
                this.showNotification('Share Removed', `Share ${share.name} has been removed`, 'success');
            } catch (error) {
                this.showNotification('Remove Failed', `Failed to remove share ${share.name}`, 'error');
            }
        }
    }
    
    /**
     * Handle select share button click
     * @param {object} share - The selected share
     */
    handleSelectShare(share) {
        const mountpoint = share.mountpoint || `/mnt/networkshare/${share.name.toLowerCase().replace(/\s+/g, '_')}`;
        
        // Update media directory inputs
        const mediaDir = document.getElementById('media-directory');
        const downloadsDir = document.getElementById('downloads-directory');
        
        if (mediaDir) mediaDir.value = `${mountpoint}/media`;
        if (downloadsDir) downloadsDir.value = `${mountpoint}/downloads`;
        
        this.dispatchEvent('shareSelected', { share, mountpoint });
    }
    
    /**
     * Show add network share dialog
     * @returns {Promise<object|null>} - Promise resolving to share config or null if cancelled
     */
    showAddShareDialog() {
        return new Promise(resolve => {
            // Create modal backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop';
            document.body.appendChild(backdrop);
            
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Add Network Share</h3>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="share-form">
                            <div class="form-group">
                                <label for="share-name">Share Name</label>
                                <input type="text" id="share-name" name="name" required>
                                <small>Display name for this share</small>
                            </div>
                            <div class="form-group">
                                <label for="share-type">Share Type</label>
                                <select id="share-type" name="type">
                                    <option value="smb">SMB/CIFS (Windows Share)</option>
                                    <option value="nfs">NFS (Linux/Unix)</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="server">Server</label>
                                <input type="text" id="server" name="server" placeholder="192.168.1.100" required>
                                <small>IP address or hostname of the server</small>
                            </div>
                            <div class="form-group">
                                <label for="share-name">Share Path/Name</label>
                                <input type="text" id="share-path" name="share_name" placeholder="media" required>
                                <small>Share name or path on the server</small>
                            </div>
                            <div class="form-group">
                                <label for="mountpoint">Mount Point</label>
                                <input type="text" id="mountpoint" name="mountpoint" placeholder="/mnt/networkshare/media" required>
                                <small>Local directory where the share will be mounted</small>
                            </div>
                            <div id="smb-auth" class="auth-section">
                                <div class="form-group">
                                    <label for="username">Username</label>
                                    <input type="text" id="username" name="username">
                                    <small>Leave blank for anonymous access</small>
                                </div>
                                <div class="form-group">
                                    <label for="password">Password</label>
                                    <input type="password" id="password" name="password">
                                </div>
                            </div>
                            <div id="nfs-options" class="options-section hidden">
                                <div class="form-group">
                                    <label for="nfs-options">NFS Options</label>
                                    <input type="text" id="nfs-options" name="options" value="noatime,soft">
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary cancel-btn">Cancel</button>
                        <button class="btn btn-primary add-btn">Add Share</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Add event listeners
            const closeModal = () => {
                document.body.removeChild(modal);
                document.body.removeChild(backdrop);
                resolve(null);
            };
            
            modal.querySelector('.close-modal').addEventListener('click', closeModal);
            modal.querySelector('.cancel-btn').addEventListener('click', closeModal);
            
            // Show/hide authentication based on share type
            const shareType = modal.querySelector('#share-type');
            const smbAuth = modal.querySelector('#smb-auth');
            const nfsOptions = modal.querySelector('#nfs-options');
            
            shareType.addEventListener('change', () => {
                if (shareType.value === 'smb') {
                    smbAuth.classList.remove('hidden');
                    nfsOptions.classList.add('hidden');
                } else {
                    smbAuth.classList.add('hidden');
                    nfsOptions.classList.remove('hidden');
                }
            });
            
            modal.querySelector('.add-btn').addEventListener('click', () => {
                const form = modal.querySelector('#share-form');
                const shareConfig = {
                    name: form.name.value.trim(),
                    type: form.type.value,
                    server: form.server.value.trim(),
                    share_name: form.share_name.value.trim(),
                    mountpoint: form.mountpoint.value.trim()
                };
                
                // Add authentication for SMB
                if (form.type.value === 'smb' && form.username.value.trim()) {
                    shareConfig.username = form.username.value.trim();
                    shareConfig.password = form.password.value;
                }
                
                // Add options for NFS
                if (form.type.value === 'nfs' && form.options) {
                    shareConfig.options = form.options.value.trim();
                }
                
                document.body.removeChild(modal);
                document.body.removeChild(backdrop);
                resolve(shareConfig);
            });
        });
    }
    
    /**
     * Render media paths UI
     */
    renderMediaPathsUI() {
        if (!this.mediaPathsContainer) return;
        
        // Clear the container
        this.mediaPathsContainer.innerHTML = '';
        
        // Create media paths form
        const form = document.createElement('form');
        form.id = 'media-paths-form';
        form.className = 'media-paths-form';
        
        // Define media path types
        const mediaTypes = [
            { id: 'tv', name: 'TV Shows', icon: 'fa-tv' },
            { id: 'movies', name: 'Movies', icon: 'fa-film' },
            { id: 'music', name: 'Music', icon: 'fa-music' },
            { id: 'books', name: 'Books', icon: 'fa-book' },
            { id: 'audiobooks', name: 'Audiobooks', icon: 'fa-headphones' },
            { id: 'games', name: 'Games', icon: 'fa-gamepad' },
            { id: 'downloads', name: 'Downloads', icon: 'fa-download' }
        ];
        
        // Add fields for each media type
        mediaTypes.forEach(type => {
            const value = this.mediaPaths[type.id] || '';
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            formGroup.innerHTML = `
                <label for="path-${type.id}">
                    <i class="fas ${type.icon}"></i> ${type.name} Directory
                </label>
                <div class="path-input-group">
                    <input type="text" id="path-${type.id}" name="${type.id}" value="${value}">
                    <button type="button" class="btn btn-sm btn-outline browse-btn" data-path-id="${type.id}">
                        <i class="fas fa-folder-open"></i>
                    </button>
                </div>
                <small>Path for your ${type.name.toLowerCase()}</small>
            `;
            form.appendChild(formGroup);
        });
        
        // Add custom path section
        const customPathSection = document.createElement('div');
        customPathSection.className = 'custom-path-section';
        customPathSection.innerHTML = `
            <div class="section-header">
                <h4>Add Custom Path</h4>
                <button type="button" class="btn btn-sm btn-primary add-custom-path">
                    <i class="fas fa-plus"></i> Add Path
                </button>
            </div>
            <div class="custom-paths-container"></div>
        `;
        
        form.appendChild(customPathSection);
        
        // Add save button
        const saveBtn = document.createElement('button');
        saveBtn.type = 'button';
        saveBtn.className = 'btn btn-primary save-paths-btn';
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Paths';
        saveBtn.addEventListener('click', () => this.handleSavePaths(form));
        
        form.appendChild(saveBtn);
        
        this.mediaPathsContainer.appendChild(form);
        
        // Add event listeners
        form.querySelectorAll('.browse-btn').forEach(btn => {
            btn.addEventListener('click', () => this.handleBrowsePath(btn.dataset.pathId));
        });
        
        form.querySelector('.add-custom-path').addEventListener('click', () => this.handleAddCustomPath());
    }
    
    /**
     * Handle save paths button click
     * @param {HTMLFormElement} form - The form element
     */
    async handleSavePaths(form) {
        // Collect path values
        const paths = {};
        mediaTypes.forEach(type => {
            const input = form.querySelector(`#path-${type.id}`);
            if (input && input.value.trim()) {
                paths[type.id] = input.value.trim();
            }
        });
        
        // Add custom paths
        form.querySelectorAll('.custom-path-row').forEach(row => {
            const nameInput = row.querySelector('.custom-path-name');
            const pathInput = row.querySelector('.custom-path-value');
            
            if (nameInput && pathInput && nameInput.value.trim() && pathInput.value.trim()) {
                const id = nameInput.value.trim().toLowerCase().replace(/\s+/g, '_');
                paths[id] = pathInput.value.trim();
            }
        });
        
        try {
            await this.updateMediaPaths(paths);
            this.showNotification('Paths Saved', 'Media paths have been updated', 'success');
        } catch (error) {
            this.showNotification('Save Failed', 'Failed to update media paths', 'error');
        }
    }
    
    /**
     * Handle browse path button click
     * @param {string} pathId - The path ID to browse for
     */
    handleBrowsePath(pathId) {
        // For now, just show a dialog with available drives and network shares
        this.showBrowseDialog(pathId);
    }
    
    /**
     * Show browse dialog
     * @param {string} pathId - The path ID being browsed for
     */
    showBrowseDialog(pathId) {
        const input = document.getElementById(`path-${pathId}`);
        if (!input) return;
        
        return new Promise(resolve => {
            // Create modal backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop';
            document.body.appendChild(backdrop);
            
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'modal browse-modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Select Path for ${pathId}</h3>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="location-tabs">
                            <button class="tab-btn active" data-tab="drives">Drives</button>
                            <button class="tab-btn" data-tab="network">Network</button>
                            <button class="tab-btn" data-tab="custom">Custom</button>
                        </div>
                        <div class="tab-content">
                            <div class="tab-pane active" id="drives-tab">
                                <div class="browse-drives-list">
                                    ${this.renderBrowseDrivesList()}
                                </div>
                            </div>
                            <div class="tab-pane" id="network-tab">
                                <div class="browse-network-list">
                                    ${this.renderBrowseNetworkList()}
                                </div>
                            </div>
                            <div class="tab-pane" id="custom-tab">
                                <div class="custom-path-input">
                                    <input type="text" id="custom-path" class="form-control" placeholder="/custom/path/${pathId}">
                                    <button class="btn btn-primary use-custom-path">Use Path</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Add event listeners
            const closeModal = () => {
                document.body.removeChild(modal);
                document.body.removeChild(backdrop);
                resolve();
            };
            
            modal.querySelector('.close-modal').addEventListener('click', closeModal);
            
            // Tab switching
            modal.querySelectorAll('.tab-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    // Update active tab button
                    modal.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    
                    // Show selected tab
                    const tabId = btn.dataset.tab + '-tab';
                    modal.querySelectorAll('.tab-pane').forEach(tab => tab.classList.remove('active'));
                    modal.querySelector(`#${tabId}`).classList.add('active');
                });
            });
            
            // Drive selection
            modal.querySelectorAll('.select-browse-drive').forEach(btn => {
                btn.addEventListener('click', () => {
                    const mountpoint = btn.dataset.mountpoint;
                    input.value = `${mountpoint}/${pathId}`;
                    closeModal();
                });
            });
            
            // Network share selection
            modal.querySelectorAll('.select-browse-share').forEach(btn => {
                btn.addEventListener('click', () => {
                    const mountpoint = btn.dataset.mountpoint;
                    input.value = `${mountpoint}/${pathId}`;
                    closeModal();
                });
            });
            
            // Custom path
            modal.querySelector('.use-custom-path').addEventListener('click', () => {
                const customPath = modal.querySelector('#custom-path').value.trim();
                if (customPath) {
                    input.value = customPath;
                    closeModal();
                }
            });
        });
    }
    
    /**
     * Render drives list for browse dialog
     * @returns {string} - HTML for the drives list
     */
    renderBrowseDrivesList() {
        if (this.drives.length === 0) {
            return '<p class="no-drives-message">No drives found.</p>';
        }
        
        const drivesHtml = this.drives
            .filter(drive => drive.status === 'mounted')
            .map(drive => `
                <div class="browse-item">
                    <div class="browse-icon">
                        <i class="fas ${drive.type === 'usb' ? 'fa-usb' : 'fa-hdd'}"></i>
                    </div>
                    <div class="browse-info">
                        <div class="browse-name">${drive.label || drive.name}</div>
                        <div class="browse-path">${drive.mountpoint}</div>
                    </div>
                    <button class="btn btn-sm btn-primary select-browse-drive" data-mountpoint="${drive.mountpoint}">
                        Select
                    </button>
                </div>
            `).join('');
            
        return drivesHtml || '<p class="no-drives-message">No mounted drives found.</p>';
    }
    
    /**
     * Render network shares list for browse dialog
     * @returns {string} - HTML for the network shares list
     */
    renderBrowseNetworkList() {
        if (this.networkShares.length === 0) {
            return '<p class="no-shares-message">No network shares found.</p>';
        }
        
        const sharesHtml = this.networkShares
            .filter(share => share.status === 'mounted')
            .map(share => `
                <div class="browse-item">
                    <div class="browse-icon">
                        <i class="fas ${share.type === 'smb' ? 'fa-windows' : 'fa-server'}"></i>
                    </div>
                    <div class="browse-info">
                        <div class="browse-name">${share.name}</div>
                        <div class="browse-path">${share.mountpoint}</div>
                    </div>
                    <button class="btn btn-sm btn-primary select-browse-share" data-mountpoint="${share.mountpoint}">
                        Select
                    </button>
                </div>
            `).join('');
            
        return sharesHtml || '<p class="no-shares-message">No mounted network shares found.</p>';
    }
    
    /**
     * Handle add custom path button click
     */
    handleAddCustomPath() {
        const container = document.querySelector('.custom-paths-container');
        if (!container) return;
        
        const index = container.children.length + 1;
        
        const row = document.createElement('div');
        row.className = 'custom-path-row';
        row.innerHTML = `
            <div class="path-input-group">
                <input type="text" class="custom-path-name" placeholder="Path Name">
                <input type="text" class="custom-path-value" placeholder="/custom/path">
                <button type="button" class="btn btn-sm btn-danger remove-custom-path">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        container.appendChild(row);
        
        // Add event listener for remove button
        row.querySelector('.remove-custom-path').addEventListener('click', () => {
            container.removeChild(row);
        });
    }
    
    /**
     * Format a file size in bytes to a human-readable format
     * @param {number} bytes - The size in bytes
     * @returns {string} - The formatted size string
     */
    formatSize(bytes) {
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
    }
}

// Create a singleton instance
const driveManager = new DriveManager();