import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 9003
FILES_DIR = 'server_files'
BUFFER_SIZE = 4096

os.makedirs(FILES_DIR, exist_ok=True)

clients_lock = threading.Lock()
clients = {}

def handle_client(conn, addr):
    print(f"Connected: {addr} (thread {threading.current_thread().name})")
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            message = data.decode('utf-8').strip()
            print(f"{addr}: {message}")

            if message == '/list':
                files = os.listdir(FILES_DIR)
                response = ("\n".join(files)) if files else "No files on server."
                conn.sendall(response.encode('utf-8'))

            elif message.startswith('/upload '):
                filename = message[8:].strip()
                conn.sendall(b"READY")
                size_data = conn.recv(BUFFER_SIZE).decode('utf-8').strip()
                file_size = int(size_data)
                conn.sendall(b"SIZE_OK")
                received = 0
                filepath = os.path.join(FILES_DIR, filename)
                with open(filepath, 'wb') as f:
                    while received < file_size:
                        chunk = conn.recv(min(BUFFER_SIZE, file_size - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                print(f"Received '{filename}' ({received} bytes) from {addr}")
                conn.sendall(f"Upload success: {filename}".encode('utf-8'))
                broadcast(f"File '{filename}' uploaded by {addr}", exclude=conn)

            elif message.startswith('/download '):
                filename = message[10:].strip()
                filepath = os.path.join(FILES_DIR, filename)
                if not os.path.exists(filepath):
                    conn.sendall(b"ERROR: File not found.")
                else:
                    file_size = os.path.getsize(filepath)
                    conn.sendall(f"SIZE {file_size}".encode('utf-8'))
                    ack = conn.recv(BUFFER_SIZE)
                    if ack.strip() == b"SIZE_OK":
                        with open(filepath, 'rb') as f:
                            while True:
                                chunk = f.read(BUFFER_SIZE)
                                if not chunk:
                                    break
                                conn.sendall(chunk)
                        print(f"Sent '{filename}' to {addr}")

    except (ConnectionResetError, BrokenPipeError, ValueError):
        pass
    finally:
        with clients_lock:
            clients.pop(conn, None)
        conn.close()
        print(f"Disconnected: {addr}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(10)
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            with clients_lock:
                clients[conn] = addr
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
            print(f"Active clients: {threading.active_count() - 1}")

if __name__ == '__main__':
    main()
