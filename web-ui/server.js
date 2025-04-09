/**
 * Pi-PVARR Web UI Server
 * Serves the web interface for Pi-PVARR
 */

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 8080;

// Create HTTP server
const server = http.createServer(app);

// Create WebSocket server
const wss = new WebSocket.Server({ server });

// Store connected clients
const clients = new Set();

// WebSocket connection handler
wss.on('connection', (ws) => {
    // Add the new client to our set
    clients.add(ws);
    console.log(`WebSocket client connected. Total clients: ${clients.size}`);
    
    // Send initial welcome message
    ws.send(JSON.stringify({
        type: 'connection_established',
        data: { message: 'Connected to Pi-PVARR WebSocket server', timestamp: Date.now() }
    }));
    
    // Handle incoming messages
    ws.on('message', (message) => {
        try {
            // Try to parse the message as JSON
            const parsedMessage = JSON.parse(message);
            console.log('Received message:', parsedMessage);
            
            // Handle specific message types
            if (parsedMessage.type === 'ping') {
                ws.send(JSON.stringify({
                    type: 'pong',
                    data: { timestamp: Date.now() }
                }));
            }
            // Add more message type handlers as needed
            
        } catch (e) {
            console.error('Error handling WebSocket message:', e);
        }
    });
    
    // Handle disconnection
    ws.on('close', () => {
        clients.delete(ws);
        console.log(`WebSocket client disconnected. Total clients: ${clients.size}`);
    });
    
    // Handle errors
    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        clients.delete(ws);
    });
});

/**
 * Broadcast a message to all connected WebSocket clients
 * @param {string} type - The message type
 * @param {object} data - The message data
 */
function broadcastMessage(type, data) {
    const message = JSON.stringify({
        type,
        data,
        timestamp: Date.now()
    });
    
    clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
}

// Static files middleware
app.use(express.static(path.join(__dirname)));

// Parse JSON bodies
app.use(express.json());

// Allow CORS for development
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
});

// Mock installation status
let installationStatus = {
    current_stage: "pre_check",
    current_stage_name: "System Compatibility Check",
    stage_progress: 0,
    overall_progress: 0,
    status: "not_started",
    logs: [],
    errors: [],
    start_time: null,
    end_time: null,
    elapsed_time: null
};

// API proxy to avoid CORS issues
app.use('/api', async (req, res) => {
    try {
        // For installation status endpoint
        if (req.path === '/install/status' && req.method === 'GET') {
            return res.json(installationStatus);
        }
        
        // For compatibility check endpoint
        if (req.path === '/install/compatibility' && req.method === 'GET') {
            return res.json({
                status: "success",
                compatible: true,
                system_info: {
                    memory: { total_gb: 4, free_gb: 3.2 },
                    disk: { total_gb: 32, free_gb: 25 },
                    docker_installed: true,
                    is_raspberry_pi: true,
                    model: "Raspberry Pi 4 Model B Rev 1.2"
                },
                checks: {
                    memory: {
                        value: 4,
                        unit: "GB",
                        compatible: true,
                        recommended: 2,
                        message: "Memory: 4GB"
                    },
                    disk_space: {
                        value: 25,
                        unit: "GB",
                        compatible: true,
                        recommended: 10,
                        message: "Free Disk Space: 25GB"
                    },
                    docker: {
                        installed: true,
                        message: "Docker: Installed"
                    }
                }
            });
        }
        
        // Endpoint to start installation
        if (req.path === '/install/run' && req.method === 'POST') {
            // Simulate starting an installation process
            installationStatus = {
                current_stage: "pre_check",
                current_stage_name: "System Compatibility Check",
                stage_progress: 0,
                overall_progress: 0,
                status: "in_progress",
                logs: ["Starting installation process..."],
                errors: [],
                start_time: Date.now() / 1000,
                end_time: null,
                elapsed_time: null
            };
            
            // Broadcast the status update to all WebSocket clients
            broadcastMessage('installation_status', installationStatus);
            
            // Start mock installation progress simulation
            simulateInstallation();
            
            return res.json({
                status: "success",
                message: "Installation started successfully"
            });
        }
        
        // Handle drive management endpoints
        if (req.path.startsWith('/drives')) {
            if (req.method === 'GET') {
                // Get all drives
                return res.json({
                    status: 'success',
                    drives: [
                        {
                            name: 'sda',
                            path: '/dev/sda1',
                            type: 'internal',
                            size: 1099511627776, // 1TB
                            used_percent: 25,
                            mountpoint: '/mnt/data',
                            filesystem: 'ext4',
                            label: 'DATA',
                            model: 'WD10EZEX',
                            serial: 'WD-WCC3F7HL1234',
                            removable: false,
                            status: 'mounted'
                        },
                        {
                            name: 'sdb',
                            path: '/dev/sdb1',
                            type: 'usb',
                            size: 549755813888, // 512GB
                            used_percent: 10,
                            mountpoint: null,
                            filesystem: null,
                            label: null,
                            model: 'SanDisk Ultra',
                            serial: '4C530001231234',
                            removable: true,
                            status: 'unmounted'
                        },
                        {
                            name: 'sdc',
                            path: '/dev/sdc1',
                            type: 'usb',
                            size: 32212254720, // 30GB
                            used_percent: 5,
                            mountpoint: '/mnt/backup',
                            filesystem: 'ext4',
                            label: 'BACKUP',
                            model: 'Kingston DataTraveler',
                            serial: '5921ABF341',
                            removable: true,
                            status: 'mounted'
                        },
                        {
                            name: 'sdd',
                            path: '/dev/sdd',
                            type: 'usb',
                            size: 16106127360, // 15GB
                            used_percent: 0,
                            mountpoint: null,
                            filesystem: null,
                            label: null,
                            model: 'Generic Flash Disk',
                            serial: 'FI93JZO492',
                            removable: true,
                            status: 'unformatted'
                        }
                    ]
                });
            } else if (req.path === '/drives/mount' && req.method === 'POST') {
                // Mount a drive
                const { drive, mountpoint, options } = req.body;
                return res.json({
                    status: 'success',
                    message: `Drive ${drive} mounted at ${mountpoint}`,
                    mountpoint: mountpoint
                });
            } else if (req.path === '/drives/unmount' && req.method === 'POST') {
                // Unmount a drive
                const { drive } = req.body;
                return res.json({
                    status: 'success',
                    message: `Drive ${drive} unmounted successfully`
                });
            } else if (req.path === '/drives/format' && req.method === 'POST') {
                // Format a drive
                const { drive, filesystem, label } = req.body;
                return res.json({
                    status: 'success',
                    message: `Drive ${drive} formatted as ${filesystem} with label ${label}`
                });
            }
        }
        
        // Handle network share endpoints
        if (req.path.startsWith('/network/shares')) {
            if (req.method === 'GET') {
                // Get all network shares
                return res.json({
                    status: 'success',
                    shares: [
                        {
                            id: 'share1',
                            name: 'Media Share',
                            type: 'smb',
                            server: '192.168.1.100',
                            share_name: 'media',
                            mountpoint: '/mnt/networkshare/media',
                            username: 'user',
                            status: 'mounted'
                        },
                        {
                            id: 'share2',
                            name: 'Backup Share',
                            type: 'nfs',
                            server: '192.168.1.101',
                            share_name: '/volume1/backup',
                            mountpoint: '/mnt/networkshare/backup',
                            options: 'ro,noatime',
                            status: 'unmounted'
                        }
                    ]
                });
            } else if (req.method === 'POST') {
                // Add a network share
                const { name, type, server, share_name, mountpoint, username, password, options } = req.body;
                return res.json({
                    status: 'success',
                    message: 'Network share added successfully',
                    id: 'share' + Math.floor(Math.random() * 1000)
                });
            } else if (req.method === 'DELETE') {
                // Remove a network share
                const { id } = req.body;
                return res.json({
                    status: 'success',
                    message: `Network share ${id} removed successfully`
                });
            }
        }
        
        // For media path management
        if (req.path === '/paths' && req.method === 'GET') {
            return res.json({
                status: 'success',
                paths: {
                    tv: '/mnt/media/tv',
                    movies: '/mnt/media/movies',
                    music: '/mnt/media/music',
                    books: '/mnt/media/books',
                    audiobooks: '/mnt/media/audiobooks',
                    games: '/mnt/media/games',
                    downloads: '/mnt/downloads'
                }
            });
        } else if (req.path === '/paths' && req.method === 'PUT') {
            // Update paths
            const { paths } = req.body;
            return res.json({
                status: 'success',
                message: 'Paths updated successfully',
                paths: paths
            });
        }
        
        // For all other POST endpoints, return success for development
        if (req.method === 'POST') {
            return res.json({
                status: "success",
                message: "Operation completed successfully"
            });
        }
        
        // Default response for unhandled endpoints
        res.status(404).json({ error: "Endpoint not found" });
        
    } catch (error) {
        console.error('API proxy error:', error);
        res.status(500).json({ error: "Internal server error" });
    }
});

/**
 * Simulate an installation process
 */
function simulateInstallation() {
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
    
    let currentStageIndex = 0;
    let stageProgress = 0;
    
    // Update progress every 500ms
    const progressInterval = setInterval(() => {
        const currentStage = stages[currentStageIndex];
        
        // Update stage progress
        stageProgress += 5;
        
        if (stageProgress > 100) {
            // Move to next stage
            stageProgress = 0;
            currentStageIndex++;
            
            // Add log message about completing the previous stage
            installationStatus.logs.push(`Completed: ${currentStage.name}`);
            
            // If all stages are complete, finish the installation
            if (currentStageIndex >= stages.length) {
                clearInterval(progressInterval);
                
                // Set final status
                installationStatus.status = "completed";
                installationStatus.current_stage = "finalization";
                installationStatus.current_stage_name = "Installation Complete";
                installationStatus.stage_progress = 100;
                installationStatus.overall_progress = 100;
                installationStatus.end_time = Date.now() / 1000;
                installationStatus.elapsed_time = installationStatus.end_time - installationStatus.start_time;
                installationStatus.logs.push("Installation completed successfully!");
                
                // Add service URLs for the completion screen
                installationStatus.service_urls = {
                    sonarr: "http://localhost:8989",
                    radarr: "http://localhost:7878",
                    jellyfin: "http://localhost:8096",
                    prowlarr: "http://localhost:9696",
                    transmission: "http://localhost:9091",
                    portainer: "http://localhost:9000"
                };
                
                // Broadcast final status
                broadcastMessage('installation_status', installationStatus);
                broadcastMessage('installation_complete', {
                    message: "Installation completed successfully!",
                    elapsed_time: installationStatus.elapsed_time.toFixed(2)
                });
                
                return;
            }
            
            // Update for the new stage
            const newStage = stages[currentStageIndex];
            installationStatus.current_stage = newStage.id;
            installationStatus.current_stage_name = newStage.name;
            installationStatus.logs.push(`Starting: ${newStage.name}`);
        }
        
        // Update installation status
        installationStatus.stage_progress = stageProgress;
        installationStatus.overall_progress = ((currentStageIndex / stages.length) * 100) + 
                                             ((stageProgress / 100) * (100 / stages.length));
        
        // Add occasional log messages
        if (stageProgress % 20 === 0) {
            installationStatus.logs.push(`Progress: ${installationStatus.current_stage_name} - ${stageProgress}%`);
        }
        
        // Add occasional simulated error (but don't interrupt the installation)
        if (Math.random() < 0.05 && installationStatus.errors.length < 3) {
            const errorMessage = `Non-critical warning in ${installationStatus.current_stage_name}`;
            installationStatus.errors.push(errorMessage);
            installationStatus.logs.push(`WARNING: ${errorMessage}`);
        }
        
        // Update elapsed time
        installationStatus.elapsed_time = (Date.now() / 1000) - installationStatus.start_time;
        
        // Broadcast the status update to all WebSocket clients
        broadcastMessage('installation_status', installationStatus);
        
    }, 500);
}

// Serve the main page for all routes to enable client-side routing
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start the server
server.listen(PORT, () => {
    console.log(`Pi-PVARR Web UI server running on port ${PORT}`);
    console.log(`Open http://localhost:${PORT} in your browser`);
});