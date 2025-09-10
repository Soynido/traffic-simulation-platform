type WSOptions = {
  url?: string;
  protocols?: string | string[];
  onOpen?: (ev: Event) => void;
  onMessage?: (ev: MessageEvent) => void;
  onError?: (ev: Event) => void;
  onClose?: (ev: CloseEvent) => void;
  reconnect?: boolean;
  reconnectDelayMs?: number;
};

export function connectWebSocket(path = '/ws', opts: WSOptions = {}) {
  const base = process.env.NEXT_PUBLIC_WS_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  // Convert http(s) base to ws(s)
  const baseUrl = new URL(base);
  baseUrl.protocol = baseUrl.protocol.replace('http', 'ws');

  const target = opts.url || `${baseUrl.origin}${path}`;

  let ws: WebSocket | null = null;
  let closedByClient = false;
  const reconnect = opts.reconnect ?? true;
  const delay = opts.reconnectDelayMs ?? 1500;

  function open() {
    ws = new WebSocket(target, opts.protocols);

    ws.onopen = (ev) => opts.onOpen?.(ev);
    ws.onmessage = (ev) => opts.onMessage?.(ev);
    ws.onerror = (ev) => opts.onError?.(ev);
    ws.onclose = (ev) => {
      opts.onClose?.(ev);
      if (!closedByClient && reconnect) {
        setTimeout(open, delay);
      }
    };
  }

  open();

  return {
    send: (data: string | ArrayBufferLike | Blob | ArrayBufferView) => ws?.send(data),
    close: () => {
      closedByClient = true;
      ws?.close();
    },
    get socket() {
      return ws;
    },
  };
}

