/**
 * Pi-PVARR WebSocket Client
 * Provides real-time communication for the Pi-PVARR web interface
 */

class WebSocketClient {
    /**
     * Creates a new WebSocket client
     * @param {string} url - The WebSocket server URL
     * @param {Object} options - Configuration options
     * @param {number} options.reconnectInterval - Interval in ms between reconnection attempts
     * @param {number} options.maxReconnectAttempts - Maximum number of reconnection attempts
     * @param {Function} options.onOpen - Callback when connection opens
     * @param {Function} options.onMessage - Callback when message is received
     * @param {Function} options.onClose - Callback when connection closes
     * @param {Function} options.onError - Callback when error occurs
     * @param {Function} options.onReconnect - Callback when reconnection is attempted
     */
    constructor(url, options = {}) {
        this.url = url;
        this.options = Object.assign({
            reconnectInterval: 2000,
            maxReconnectAttempts: 10,
            onOpen: () => {},
            onMessage: () => {},
            onClose: () => {},
            onError: () => {},
            onReconnect: () => {}
        }, options);
        
        this.socket = null;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.reconnectTimer = null;
        this.messageHandlers = new Map();
        
        // Bind methods to ensure 'this' refers to the class instance
        this.connect = this.connect.bind(this);
        this.reconnect = this.reconnect.bind(this);
        this.send = this.send.bind(this);
        this.close = this.close.bind(this);
        this.onOpen = this.onOpen.bind(this);
        this.onMessage = this.onMessage.bind(this);
        this.onClose = this.onClose.bind(this);
        this.onError = this.onError.bind(this);
    }
    
    /**
     * Connect to the WebSocket server
     */
    connect() {
        if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
            console.log('WebSocket already connected or connecting');
            return;
        }
        
        try {
            this.socket = new WebSocket(this.url);
            this.socket.addEventListener('open', this.onOpen);
            this.socket.addEventListener('message', this.onMessage);
            this.socket.addEventListener('close', this.onClose);
            this.socket.addEventListener('error', this.onError);
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.onError(error);
        }
    }
    
    /**
     * Reconnect to the WebSocket server
     */
    reconnect() {
        if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
            console.error(`Maximum reconnection attempts (${this.options.maxReconnectAttempts}) reached. Giving up.`);
            return;
        }
        
        this.reconnectAttempts++;
        clearTimeout(this.reconnectTimer);
        
        // Apply exponential backoff for reconnection
        const backoffTime = Math.min(
            this.options.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1),
            30000 // max 30 seconds
        );
        
        console.log(`Attempting to reconnect in ${backoffTime}ms (attempt ${this.reconnectAttempts}/${this.options.maxReconnectAttempts})`);
        
        if (this.options.onReconnect) {
            this.options.onReconnect(this.reconnectAttempts, backoffTime);
        }
        
        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, backoffTime);
    }
    
    /**
     * Send data through the WebSocket
     * @param {string|Object} data - The data to send
     * @param {string} eventType - Optional event type for structured messages
     */
    send(data, eventType = null) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.error('WebSocket not connected. Cannot send data.');
            return false;
        }
        
        try {
            // If eventType is provided, send as a structured message
            if (eventType) {
                const message = JSON.stringify({
                    type: eventType,
                    data: data,
                    timestamp: Date.now()
                });
                this.socket.send(message);
            } 
            // Otherwise, just send the data
            else {
                if (typeof data === 'object') {
                    this.socket.send(JSON.stringify(data));
                } else {
                    this.socket.send(data);
                }
            }
            return true;
        } catch (error) {
            console.error('Error sending data through WebSocket:', error);
            return false;
        }
    }
    
    /**
     * Register a handler for a specific message type
     * @param {string} eventType - The event type to listen for
     * @param {Function} handler - The handler function
     */
    on(eventType, handler) {
        this.messageHandlers.set(eventType, handler);
    }
    
    /**
     * Remove a handler for a specific message type
     * @param {string} eventType - The event type to remove handler for
     */
    off(eventType) {
        this.messageHandlers.delete(eventType);
    }
    
    /**
     * Close the WebSocket connection
     * @param {number} code - The close code
     * @param {string} reason - The reason for closing
     */
    close(code, reason) {
        if (this.socket) {
            this.socket.close(code, reason);
        }
        
        // Clear any reconnect timers
        clearTimeout(this.reconnectTimer);
    }
    
    /**
     * Handler for WebSocket open event
     * @param {Event} event - The open event
     */
    onOpen(event) {
        console.log('WebSocket connection established');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        if (this.options.onOpen) {
            this.options.onOpen(event);
        }
    }
    
    /**
     * Handler for WebSocket message event
     * @param {MessageEvent} event - The message event
     */
    onMessage(event) {
        let data = event.data;
        let parsedData;
        let eventType = null;
        
        // Try to parse the message as JSON
        try {
            parsedData = JSON.parse(data);
            
            // If the message is structured with a type, extract it
            if (parsedData && parsedData.type) {
                eventType = parsedData.type;
                data = parsedData.data;
            }
        } catch (e) {
            // Not JSON, use the raw data
            parsedData = data;
        }
        
        // If there's a specific handler for this event type, call it
        if (eventType && this.messageHandlers.has(eventType)) {
            this.messageHandlers.get(eventType)(data);
        }
        
        // Call the general onMessage callback
        if (this.options.onMessage) {
            this.options.onMessage(parsedData, eventType, event);
        }
    }
    
    /**
     * Handler for WebSocket close event
     * @param {CloseEvent} event - The close event
     */
    onClose(event) {
        console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
        this.isConnected = false;
        
        if (this.options.onClose) {
            this.options.onClose(event);
        }
        
        // Attempt to reconnect if it wasn't a normal closure
        if (event.code !== 1000) {
            this.reconnect();
        }
    }
    
    /**
     * Handler for WebSocket error event
     * @param {Event} event - The error event
     */
    onError(event) {
        console.error('WebSocket error:', event);
        
        if (this.options.onError) {
            this.options.onError(event);
        }
    }
}

// Create a singleton instance
const wsClient = new WebSocketClient(
    // Determine WebSocket URL based on current location
    typeof window !== 'undefined' 
        ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`
        : 'ws://localhost:8080/ws'
);

// Export for testing in Node.js environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WebSocketClient, wsClient };
}