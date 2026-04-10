import { useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook to handle WebSocket connection for real-time notifications.
 * @param {string} url - The WebSocket URL.
 * @param {function} onMessage - Callback for when a message is received.
 * @param {boolean} enabled - Whether to enable the connection.
 */
export default function useWebSockets(url, onMessage, enabled = true) {
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  const connect = useCallback(() => {
    if (!enabled) return;

    console.log('Connecting to WebSocket:', url);
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('WebSocket Connected');
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (err) {
        console.error('WebSocket message parsing error:', err);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };

    ws.current.onclose = (event) => {
      console.log('WebSocket Closed:', event.code, event.reason);
      if (enabled) {
        // Attempt to reconnect after 5 seconds
        reconnectTimeout.current = setTimeout(() => {
          connect();
        }, 5000);
      }
    };
  }, [url, onMessage, enabled]);

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [connect]);

  const sendMessage = useCallback((data) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    }
  }, []);

  return { sendMessage };
}
