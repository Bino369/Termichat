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


def receive_messages(conn):
    """Runs in the background, prints messages as they arrive."""
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("\n[Other side disconnected]\nPress Enter to exit.")
                break
            text = data.decode("utf-8", errors="replace")
            print(f"\nThem: {text}\nYou: ", end="", flush=True)
        except (OSError, ConnectionResetError):
            print("\n[Connection closed by other side]\nPress Enter to exit.")
            break


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Enable address reuse so restarting server doesn't throw "Address already in use"
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
        server.listen(1)
        print(f"Waiting for a connection on port {PORT}...")
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
        while True:
            msg = input("You: ")
            if msg.lower() == "quit":
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
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        conn.close()
        server.close()


if __name__ == "__main__":
    main()
