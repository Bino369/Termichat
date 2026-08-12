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


def receive_messages(sock):
    """Runs in the background, prints messages as they arrive."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[Other side disconnected]\nPress Enter to exit.")
                break
            text = data.decode("utf-8", errors="replace")
            print(f"\nThem: {text}\nYou: ", end="", flush=True)
        except (OSError, ConnectionResetError):
            print("\n[Connection closed by other side]\nPress Enter to exit.")
            break


def main():
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
        while True:
            msg = input("You: ")
            if msg.lower() == "quit":
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
        try:
            client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client.close()


if __name__ == "__main__":
    main()
