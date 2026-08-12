"""
web_server.py - TermiChat Web & WebSocket Server
Runs a zero-dependency HTTP + WebSocket server in Python standard library.

Usage:
    python3 web_server.py
"""

import http.server
import socketserver
import socket
import select
import hashlib
import base64
import struct
import threading
import sys
import os

PORT = 8000
HOST = "0.0.0.0"
WS_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

clients = set()
clients_lock = threading.Lock()


def get_local_ips():
    """Returns a list of local IP addresses for this machine."""
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
        if primary_ip and not primary_ip.startswith("127."):
            ips.append(primary_ip)
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except Exception:
        pass

    if not ips:
        ips.append("127.0.0.1")

    return ips


def encode_ws_frame(message):
    """Encodes a string into an unmasked WebSocket text frame."""
    payload = message.encode("utf-8")
    length = len(payload)
    if length <= 125:
        header = struct.pack("!BB", 0x81, length)
    elif length <= 65535:
        header = struct.pack("!BBH", 0x81, 126, length)
    else:
        header = struct.pack("!BBQ", 0x81, 127, length)
    return header + payload


def decode_ws_frame(data):
    """Decodes a WebSocket frame (supports masked client frames)."""
    if len(data) < 2:
        return None, 0
    second_byte = data[1]
    is_masked = (second_byte & 0x80) != 0
    length = second_byte & 0x7F
    idx = 2
    if length == 126:
        if len(data) < 4:
            return None, 0
        length = struct.unpack("!H", data[2:4])[0]
        idx = 4
    elif length == 127:
        if len(data) < 10:
            return None, 0
        length = struct.unpack("!Q", data[2:10])[0]
        idx = 10

    if is_masked:
        if len(data) < idx + 4 + length:
            return None, 0
        mask = data[idx:idx+4]
        idx += 4
        raw = data[idx:idx+length]
        unmasked = bytearray(b ^ mask[i % 4] for i, b in enumerate(raw))
        return unmasked.decode("utf-8", errors="replace"), idx + length
    else:
        if len(data) < idx + length:
            return None, 0
        return data[idx:idx+length].decode("utf-8", errors="replace"), idx + length


def broadcast(message, sender_sock=None):
    """Broadcasts a WebSocket message to all connected clients."""
    frame = encode_ws_frame(message)
    with clients_lock:
        to_remove = set()
        for client in clients:
            try:
                client.sendall(frame)
            except OSError:
                to_remove.add(client)
        for client in to_remove:
            clients.remove(client)


class TermiChatHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle WebSocket Upgrade
        if self.headers.get("Upgrade", "").lower() == "websocket":
            self.handle_websocket()
            return
        
        # Default static file serving
        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        return super().do_GET()

    def handle_websocket(self):
        key = self.headers.get("Sec-WebSocket-Key")
        if not key:
            self.send_error(400, "Missing Sec-WebSocket-Key")
            return

        accept_val = base64.b64encode(
            hashlib.sha1((key.strip() + WS_MAGIC).encode("utf-8")).digest()
        ).decode("utf-8")

        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_val}\r\n\r\n"
        )
        self.wfile.write(response.encode("utf-8"))
        self.wfile.flush()

        sock = self.request
        with clients_lock:
            clients.add(sock)

        # Notify others
        addr = self.client_address[0]
        print(f"[WebSocket Connected] Client connected from {addr}")

        buffer = bytearray()
        try:
            while True:
                rlist, _, _ = select.select([sock], [], [], 1.0)
                if sock in rlist:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    buffer.extend(chunk)
                    while True:
                        msg, consumed = decode_ws_frame(buffer)
                        if msg is None:
                            break
                        buffer = buffer[consumed:]
                        if msg:
                            print(f"[Message Received] {msg}")
                            broadcast(msg, sender_sock=sock)
        except (OSError, ConnectionResetError):
            pass
        finally:
            with clients_lock:
                if sock in clients:
                    clients.remove(sock)
            print(f"[WebSocket Disconnected] Client {addr} disconnected")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    # Change working directory to directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    server = ThreadedTCPServer((HOST, PORT), TermiChatHandler)
    local_ips = get_local_ips()

    print("=" * 60)
    print("  🚀 TermiChat Web & WebSocket Server Running!")
    print("  Open this URL in your web browser (phone, PC, tablet):")
    for ip in local_ips:
        print(f"    👉 http://{ip}:{PORT}")
    print(f"    👉 http://localhost:{PORT}")
    print("=" * 60)

    try:
        server.serve_forever()
    except (KeyboardInterrupt, EOFError):
        print("\n[Server Stopping] Shutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
