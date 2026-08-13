"""
termichat_server.py
Run this on the computer that will WAIT for the other one to connect.

Usage:
    python3 termichat_server.py

It will listen on port 5555 by default. Change PORT below if you want.
"""

import socket
import sys
import threading

HOST = "0.0.0.0"   # listen on all network interfaces
PORT = 5555         # pick any free port number

connected = True


def get_local_ips() -> list[str]:
    """Returns a list of local IP addresses bound to network interfaces on this machine."""
    ips: list[str] = []
    # Attempt UDP socket connect trick to find primary outgoing LAN IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
        if primary_ip and not primary_ip.startswith("127."):
            ips.append(primary_ip)
    except Exception:
        pass

    # Fallback / additional interface IPs
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


def receive_messages(conn):
    """Runs in the background, prints messages as they arrive."""
    global connected
    while connected:
        try:
            data = conn.recv(1024)
            if not data:
                if connected:
                    print("\n[Other side disconnected] (Press Enter to exit)", flush=True)
                    connected = False
                break
            text = data.decode("utf-8", errors="replace")
            print(f"\nThem: {text}\nYou: ", end="", flush=True)
        except (OSError, ConnectionResetError):
            if connected:
                print("\n[Connection closed] (Press Enter to exit)", flush=True)
                connected = False
            break


def main():
    global connected
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Enable address reuse so restarting server doesn't throw "Address already in use"
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
        server.listen(1)
        
        local_ips = get_local_ips()
        print("=" * 50)
        print("  Termichat Server Started!")
        print("  Give one of these IP addresses to the client:")
        for ip in local_ips:
            print(f"    -> {ip}")
        print(f"    -> 127.0.0.1 (if client is on the same machine)")
        print(f"  Port: {PORT}")
        print("=" * 50)
        print(f"\nWaiting for a connection on port {PORT}...")
        conn, addr = server.accept()
    except (KeyboardInterrupt, EOFError):
        print("\nServer stopped.")
        server.close()
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        server.close()
        sys.exit(1)

    print(f"Connected to {addr}. Start chatting! (type 'quit' to exit)\n")

    # Start a background thread that listens and prints incoming messages
    thread = threading.Thread(target=receive_messages, args=(conn,), daemon=True)
    thread.start()

    # Main thread handles typing and sending
    try:
        while connected:
            msg = input("You: ")
            if not connected or msg.lower() == "quit":
                break
            if not msg:
                continue
            try:
                conn.sendall(msg.encode("utf-8"))
            except (BrokenPipeError, OSError):
                print("[Failed to send message: Connection closed]")
                break
    except (KeyboardInterrupt, EOFError):
        print("\nExiting chat...")
    finally:
        connected = False
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        conn.close()
        server.close()


if __name__ == "__main__":
    main()
