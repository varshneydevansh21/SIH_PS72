type MessageHandler = (data: any) => void;

class NowcastWebSocketClient {
  private socket: WebSocket | null = null;
  private url: string;
  private handlers: Set<MessageHandler> = new Set();
  private reconnectIntervalMs: number = 3000;
  private isExplicitlyClosed: boolean = false;

  constructor(url?: string) {
    if (url) {
      this.url = url;
    } else {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.hostname;
      const port = window.location.port ? ':8001' : '';
      this.url = `${protocol}//${host}${port}/ws/nowcast`;
    }
  }

  public connect() {
    this.isExplicitlyClosed = false;
    try {
      this.socket = new WebSocket(this.url);

      this.socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.handlers.forEach((h) => h(parsed));
        } catch {
          this.handlers.forEach((h) => h(event.data));
        }
      };

      this.socket.onclose = () => {
        if (!this.isExplicitlyClosed) {
          setTimeout(() => this.connect(), this.reconnectIntervalMs);
        }
      };

      this.socket.onerror = () => {
        if (this.socket) {
          this.socket.close();
        }
      };
    } catch {
      if (!this.isExplicitlyClosed) {
        setTimeout(() => this.connect(), this.reconnectIntervalMs);
      }
    }
  }

  public subscribe(handler: MessageHandler): () => void {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }

  public send(data: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const payload = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(payload);
    }
  }

  public disconnect() {
    this.isExplicitlyClosed = true;
    if (this.socket) {
      this.socket.close();
    }
  }
}

export const wsClient = new NowcastWebSocketClient();
