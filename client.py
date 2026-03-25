import socket
import threading
import sys
import os

BUFFER_SIZE = 4096
DOWNLOADS_DIR = 'downloads'

os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def receive_loop(sock, stop_event):
    while not stop_event.is_set():
        try:
            sock.settimeout(0.5)
            data = sock.recv(BUFFER_SIZE)
            if not data:
                print("\nServer closed the connection.")
                stop_event.set()
                break
            print(f"\r{data.decode('utf-8', errors='replace')}")
            print("> ", end='', flush=True)
        except socket.timeout:
            continue
        except Exception:
            if not stop_event.is_set():
                print("\nConnection lost.")
            stop_event.set()
            break

def send_upload(sock, filename):
    if not os.path.exists(filename):
        print(f"Local file not found: {filename}")
        return

    sock.sendall(f"/upload {os.path.basename(filename)}".encode('utf-8'))

    resp = sock.recv(BUFFER_SIZE)
    if resp.strip() != b"READY":
        print(f"Server not ready: {resp.decode()}")
        return

    file_size = os.path.getsize(filename)
    sock.sendall(str(file_size).encode('utf-8'))

    ack = sock.recv(BUFFER_SIZE)
    if ack.strip() != b"SIZE_OK":
        print(f"Unexpected ack: {ack.decode()}")
        return

    sent = 0
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendall(chunk)
            sent += len(chunk)
    print(f"Uploaded '{filename}' ({sent} bytes)")


def send_download(sock, filename):
    sock.sendall(f"/download {filename}".encode('utf-8'))

    resp = sock.recv(BUFFER_SIZE).decode('utf-8').strip()
    if resp.startswith("ERROR"):
        print(f"{resp}")
        return
    if not resp.startswith("SIZE "):
        print(f"Unexpected response: {resp}")
        return

    file_size = int(resp.split()[1])

    sock.sendall(b"SIZE_OK")

    received = 0
    save_path = os.path.join(DOWNLOADS_DIR, filename)
    with open(save_path, 'wb') as f:
        while received < file_size:
            chunk = sock.recv(min(BUFFER_SIZE, file_size - received))
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
    print(f"Downloaded '{filename}' → {save_path} ({received} bytes)")

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(f"Could not connect to {host}:{port}")
        sys.exit(1)

    print(f"[+] Connected to {host}:{port}")
    print("Commands: /list  /upload <file>  /download <file>  /quit\n")

    stop_event = threading.Event()
    recv_thread = threading.Thread(target=receive_loop, args=(sock, stop_event), daemon=True)
    recv_thread.start()

    try:
        while not stop_event.is_set():
            try:
                user_input = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nDisconnecting")
                break

            if not user_input:
                continue

            if user_input in ('/quit', '/exit'):
                print("Disconnecting")
                break

            elif user_input == '/list':
                sock.sendall(b"/list")

            elif user_input.startswith('/upload '):
                filename = user_input[8:].strip()
                send_upload(sock, filename)

            elif user_input.startswith('/download '):
                filename = user_input[10:].strip()
    
                stop_event.set() 
                recv_thread.join()
    
                send_download(sock, filename)
    
                stop_event.clear()
                recv_thread = threading.Thread(target=receive_loop, args=(sock, stop_event), daemon=True)
                recv_thread.start()

            else:
                sock.sendall(user_input.encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        stop_event.set()
        sock.close()
        print("Connection closed.")

if __name__ == '__main__':
    main()
