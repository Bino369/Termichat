"""
termichat_client.py
Run this on the computer that will CONNECT to the other one.

Usage:
    python3 termichat_client.py

It will ask you for the server's IP address, then connect.
"""

import socket
import sys
import threading

PORT = 5555  # must match the port in termichat_server.py

connected = True


def receive_messages(sock: socket.socket) -> None:
    """Runs in background thread, listening and displaying incoming messages from server."""
    global connected
    while connected:
        try:
            data = sock.recv(1024)
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
    try:
        server_ip = input("Enter server IP address (e.g. 192.168.1.5): ").strip()
        if not server_ip:
            server_ip = "127.0.0.1"

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Connecting to {server_ip}:{PORT}...")
        client.connect((server_ip, PORT))
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    print("Connected! Start chatting. (type 'quit' to exit)\n")

    thread = threading.Thread(target=receive_messages, args=(client,), daemon=True)
    thread.start()

    try:
        while connected:
            msg = input("You: ")
            if not connected or msg.lower() == "quit":
                break
            if not msg:
                continue
            try:
                client.sendall(msg.encode("utf-8"))
            except (BrokenPipeError, OSError):
                print("[Failed to send message: Connection closed]")
                break
    except (KeyboardInterrupt, EOFError):
        print("\nExiting chat...")
    finally:
        connected = False
        try:
            client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client.close()


if __name__ == "__main__":
    main()
