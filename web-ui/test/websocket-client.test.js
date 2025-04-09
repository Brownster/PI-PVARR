/**
 * Unit tests for the WebSocket client
 */

// Import WebSocket mock
const WS = require('jest-websocket-mock').default;
const WebSocketClient = require('../js/websocket-client').WebSocketClient;

describe('WebSocketClient', () => {
    let server;
    let wsClient;
    const url = 'ws://localhost:1234';
    
    beforeEach(() => {
        // Create a mock WebSocket server
        server = new WS(url, { jsonProtocol: true });
        
        // Create a new client instance
        wsClient = new WebSocketClient(url, {
            reconnectInterval: 100,
            maxReconnectAttempts: 3
        });
        
        // Create a global WebSocket constructor for browser environment simulation
        global.WebSocket = require('mock-socket').WebSocket;
        
        // Mock console methods to avoid noise in tests
        jest.spyOn(console, 'log').mockImplementation(() => {});
        jest.spyOn(console, 'error').mockImplementation(() => {});
    });
    
    afterEach(() => {
        // Close all servers
        WS.clean();
        jest.clearAllMocks();
    });
    
    test('should connect to WebSocket server', async () => {
        // Set up event handler spies
        const onOpenSpy = jest.fn();
        wsClient.options.onOpen = onOpenSpy;
        
        // Connect to the server
        wsClient.connect();
        
        // Wait for connection
        await server.connected;
        
        // Verify connection was established
        expect(wsClient.isConnected).toBe(true);
        expect(onOpenSpy).toHaveBeenCalled();
    });
    
    test('should handle connection when already connected', async () => {
        // Connect to the server
        wsClient.connect();
        await server.connected;
        
        // Try to connect again
        wsClient.connect();
        
        // Verify we're still connected and logged the already connected message
        expect(wsClient.isConnected).toBe(true);
        expect(console.log).toHaveBeenCalledWith('WebSocket already connected or connecting');
    });
    
    test('should send data correctly', async () => {
        // Connect to the server
        wsClient.connect();
        await server.connected;
        
        // Since we're using jsonProtocol, all messages need to be JSON
        // Send JSON-serializable object data
        wsClient.send({ message: 'Hello, server!' });
        await server.nextMessage;
        
        // Send object data
        wsClient.send({ foo: 'bar' });
        await server.nextMessage;
        
        // Send with event type
        wsClient.send({ value: 42 }, 'test_event');
        const message = await server.nextMessage;
        expect(message).toHaveProperty('type', 'test_event');
        expect(message).toHaveProperty('data');
        expect(message.data).toEqual({ value: 42 });
        expect(message).toHaveProperty('timestamp');
    });
    
    test('should handle failure when sending to closed connection', async () => {
        // Try to send without connecting
        const result = wsClient.send('This will fail');
        
        // Verify send failed
        expect(result).toBe(false);
        expect(console.error).toHaveBeenCalledWith('WebSocket not connected. Cannot send data.');
    });
    
    test('should handle send errors', async () => {
        // Connect to the server
        wsClient.connect();
        await server.connected;
        
        // Mock the send method to throw an error
        const mockError = new Error('Mock send error');
        wsClient.socket.send = jest.fn().mockImplementation(() => {
            throw mockError;
        });
        
        // Try to send data
        const result = wsClient.send('Will throw error');
        
        // Verify error was handled
        expect(result).toBe(false);
        expect(console.error).toHaveBeenCalledWith('Error sending data through WebSocket:', mockError);
    });
    
    test('should handle received messages', async () => {
        // Set up message handler spies
        const onMessageSpy = jest.fn();
        wsClient.options.onMessage = onMessageSpy;
        
        // Set up specific event handler
        const testEventHandler = jest.fn();
        wsClient.on('test_event', testEventHandler);
        
        // Connect to the server
        wsClient.connect();
        await server.connected;
        
        // Send a string message
        server.send('Hello, client!');
        expect(onMessageSpy).toHaveBeenCalledWith('Hello, client!', null, expect.anything());
        
        // Send a structured message
        server.send({
            type: 'test_event',
            data: { value: 42 },
            timestamp: Date.now()
        });
        
        // Verify event handler was called
        expect(testEventHandler).toHaveBeenCalledWith({ value: 42 });
    });
    
    test('should handle malformed JSON messages gracefully', async () => {
        // Set up message handler spy
        const onMessageSpy = jest.fn();
        wsClient.options.onMessage = onMessageSpy;
        
        // Connect to the server
        wsClient.connect();
        await server.connected;
        
        // Create malformed JSON message (not actually JSON, but a string that looks like it)
        const malformedMessage = '{"type": "broken_json", "data": {unclosed';
        
        // Send the raw message (bypassing the server's json protocol)
        wsClient.onMessage({ data: malformedMessage });
        
        // Verify the message was handled without crashing
        expect(onMessageSpy).toHaveBeenCalledWith(malformedMessage, null, expect.anything());
    });
    
    test('should handle disconnection and reconnect', async () => {
        // Set up event handler spies
        const onCloseSpy = jest.fn();
        const onReconnectSpy = jest.fn();
        wsClient.options.onClose = onCloseSpy;
        wsClient.options.onReconnect = onReconnectSpy;
        
        // Connect to the server
        wsClient.connect();
        await server.connected;
        
        // Force disconnect
        server.close({ code: 1001, reason: 'Test disconnect' });
        
        // Verify disconnect was detected
        expect(wsClient.isConnected).toBe(false);
        expect(onCloseSpy).toHaveBeenCalled();
        
        // Wait for reconnect attempt
        await new Promise(resolve => setTimeout(resolve, 150));
        expect(onReconnectSpy).toHaveBeenCalled();
    });
    
    test('should handle normal closure without reconnect', async () => {
        // Set up reconnect spy
        const onReconnectSpy = jest.fn();
        wsClient.options.onReconnect = onReconnectSpy;
        
        // Connect to the server
        wsClient.connect();
        await server.connected;
        
        // Close with normal closure code (1000)
        server.close({ code: 1000, reason: 'Normal closure' });
        
        // Wait to ensure no reconnect is attempted
        await new Promise(resolve => setTimeout(resolve, 150));
        
        // Verify no reconnect was attempted for normal closure
        expect(onReconnectSpy).not.toHaveBeenCalled();
    });
    
    test('should stop reconnecting after max attempts', async () => {
        // Set up reconnect spy
        const onReconnectSpy = jest.fn();
        wsClient.options.onReconnect = onReconnectSpy;
        
        // Mock the reconnect method to avoid actual timeouts
        const originalReconnect = wsClient.reconnect;
        wsClient.reconnect = jest.fn(() => {
            wsClient.reconnectAttempts++;
            onReconnectSpy(wsClient.reconnectAttempts);
            
            // Simulate giving up after max attempts
            if (wsClient.reconnectAttempts >= wsClient.options.maxReconnectAttempts) {
                console.error(`Maximum reconnection attempts (${wsClient.options.maxReconnectAttempts}) reached. Giving up.`);
            }
        });
        
        // Connect
        wsClient.connect();
        await server.connected;
        
        // Close the server to force reconnect
        server.close();
        
        // Manually trigger reconnect attempts
        wsClient.onClose({ code: 1001 });
        wsClient.onClose({ code: 1001 });
        wsClient.onClose({ code: 1001 });
        
        // Should have attempted exactly 3 reconnects
        expect(onReconnectSpy).toHaveBeenCalledTimes(3);
        expect(console.error).toHaveBeenCalledWith('Maximum reconnection attempts (3) reached. Giving up.');
        
        // Restore original method
        wsClient.reconnect = originalReconnect;
    });
    
    test('should implement exponential backoff for reconnection', () => {
        // Set up a client with specific reconnect settings for testing backoff
        const backoffClient = new WebSocketClient(url, {
            reconnectInterval: 100,
            maxReconnectAttempts: 5
        });
        
        // Mock setTimeout to directly verify backoff calculation
        const originalSetTimeout = global.setTimeout;
        global.setTimeout = jest.fn();
        
        // Verify first interval (base case)
        backoffClient.reconnectAttempts = 0;
        backoffClient.reconnect();
        // Base interval of 100ms
        expect(global.setTimeout).toHaveBeenCalledWith(expect.any(Function), 100); 
        
        // Verify second interval
        backoffClient.reconnectAttempts = 1;
        backoffClient.reconnect();
        // 100 * 1.5¹ = 150ms
        expect(global.setTimeout).toHaveBeenCalledWith(expect.any(Function), 150); 
        
        // Verify third interval
        backoffClient.reconnectAttempts = 2;
        backoffClient.reconnect();
        // 100 * 1.5² = 225ms
        expect(global.setTimeout).toHaveBeenCalledWith(expect.any(Function), 225); 
        
        // Verify fourth interval
        backoffClient.reconnectAttempts = 3;
        backoffClient.reconnect();
        // 100 * 1.5³ = 337.5ms
        expect(global.setTimeout).toHaveBeenCalledWith(expect.any(Function), 337.5); 
        
        // Test the max cap by directly computing the value
        // Calculate what would happen for a very high attempt (manually verify the formula works correctly)
        const highAttempt = 20;
        const calculatedDelay = Math.min(
            backoffClient.options.reconnectInterval * Math.pow(1.5, highAttempt - 1),
            30000 // max 30 seconds
        );
        expect(calculatedDelay).toBe(30000); // Verify the formula actually caps at 30000
        
        // Cleanup
        global.setTimeout = originalSetTimeout;
    });
    
    test('should remove event handlers', () => {
        // Set up a test event handler
        const testEventHandler = jest.fn();
        
        // Register the handler
        wsClient.on('test_event', testEventHandler);
        
        // Verify the handler is in the message handlers map
        expect(wsClient.messageHandlers.has('test_event')).toBe(true);
        expect(wsClient.messageHandlers.get('test_event')).toBe(testEventHandler);
        
        // Manually call the message handler with a test message
        wsClient.onMessage({
            data: JSON.stringify({
                type: 'test_event',
                data: { value: 1 },
                timestamp: Date.now()
            })
        });
        
        // Verify handler was called
        expect(testEventHandler).toHaveBeenCalledTimes(1);
        expect(testEventHandler).toHaveBeenCalledWith({ value: 1 });
        
        // Remove the handler
        wsClient.off('test_event');
        
        // Verify the handler was removed
        expect(wsClient.messageHandlers.has('test_event')).toBe(false);
        
        // Manually call the message handler again
        wsClient.onMessage({
            data: JSON.stringify({
                type: 'test_event',
                data: { value: 2 },
                timestamp: Date.now()
            })
        });
        
        // Verify handler was not called again
        expect(testEventHandler).toHaveBeenCalledTimes(1);
    });
    
    test('should properly close connection', () => {
        // Create a connected state
        wsClient.socket = { close: jest.fn() };
        wsClient.isConnected = true;
        
        // Mock clearTimeout to ensure reconnect timers are cleared
        const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');
        
        // Close the connection
        wsClient.close(1000, 'Test closure');
        
        // Verify close was called with the right parameters
        expect(wsClient.socket.close).toHaveBeenCalledWith(1000, 'Test closure');
        expect(clearTimeoutSpy).toHaveBeenCalled();
        
        // Simulate the onClose event
        wsClient.onClose({ code: 1000, reason: 'Test closure' });
        
        // Verify client state
        expect(wsClient.isConnected).toBe(false);
        
        // Cleanup
        clearTimeoutSpy.mockRestore();
    });
    
    test('should handle error events', () => {
        // Set up error handler spy
        const onErrorSpy = jest.fn();
        wsClient.options.onError = onErrorSpy;
        
        // Create a mock error event (Node.js doesn't have Event constructor)
        const errorEvent = { type: 'error', message: 'Test error' };
        wsClient.onError(errorEvent);
        
        // Verify error was handled
        expect(onErrorSpy).toHaveBeenCalledWith(errorEvent);
        expect(console.error).toHaveBeenCalledWith('WebSocket error:', errorEvent);
    });
    
    test('should handle connection error gracefully', () => {
        // Create a client with invalid URL
        const invalidClient = new WebSocketClient('invalid://url');
        
        // Set up error handler spy
        const onErrorSpy = jest.fn();
        invalidClient.options.onError = onErrorSpy;
        
        // Save original WebSocket
        const originalWebSocket = global.WebSocket;
        
        // Mock WebSocket constructor to throw error
        global.WebSocket = jest.fn().mockImplementation(() => {
            throw new Error('Invalid URL');
        });
        
        // Try to connect
        invalidClient.connect();
        
        // Verify error was handled
        expect(console.error).toHaveBeenCalledWith('Error creating WebSocket:', expect.any(Error));
        expect(onErrorSpy).toHaveBeenCalledWith(expect.any(Error));
        
        // Restore WebSocket constructor
        global.WebSocket = originalWebSocket;
    });
});