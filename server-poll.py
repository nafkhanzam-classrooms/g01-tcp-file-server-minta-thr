import socket
import select
import os

HOST = '0.0.0.0'
PORT = 9002
FILES_DIR = 'server_files'
BUFFER_SIZE = 4096

os.makedirs(FILES_DIR, exist_ok=True)

fd_to_sock = {} 
fd_to_addr = {}   
client_state = {}   
send_queue = {}   
clients = []
poller = None

def process(fd, message):
    if message == '/list':
        files = os.listdir(FILES_DIR)
        response = ("\n".join(files)) if files else "No files on server."
        return response.encode('utf-8')

    elif message.startswith('/upload '):
        filename = message[8:].strip()
        client_state[fd] = {'type': 'upload_size', 'filename': filename}
        return b"READY"

    elif message.startswith('/download '):
        filename = message[10:].strip()
        filepath = os.path.join(FILES_DIR, filename)
        if not os.path.exists(filepath):
            return b"ERROR: File not found."
        file_size = os.path.getsize(filepath)
        client_state[fd] = {'type': 'download_ack', 'filename': filename}
        return f"SIZE {file_size}".encode('utf-8')

def remove_client(fd):
    print(f"[POLL] Disconnected: {fd_to_addr.get(fd)}")
    poller.unregister(fd)                  
    sock = fd_to_sock.pop(fd, None)
    fd_to_addr.pop(fd, None)
    client_state.pop(fd, None)
    send_queue.pop(fd, None)
    if fd in clients:
        clients.remove(fd)
    if sock:
        sock.close()

def main():
    global poller

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    server.setblocking(False)
    print(f"Server listening on {HOST}:{PORT}")

    poller = select.poll()
    poller.register(server.fileno(), select.POLLIN)

    server_fd = server.fileno()
    fd_to_sock[server_fd] = server

    while True:
        events = poller.poll(1000)

        for fd, event in events:

            if fd == server_fd:
                conn, addr = server.accept()
                conn.setblocking(False)
                cfd = conn.fileno()

                poller.register(cfd, select.POLLIN)

                fd_to_sock[cfd] = conn
                fd_to_addr[cfd] = addr
                client_state[cfd] = None
                send_queue[cfd] = []
                clients.append(cfd)
                print(f"[POLL] Connected: {addr}")

            elif event & (select.POLLHUP | select.POLLERR):
                remove_client(fd)

            elif event & select.POLLIN:
                sock = fd_to_sock[fd]
                try:
                    data = sock.recv(BUFFER_SIZE)
                except Exception:
                    data = None

                if not data:
                    remove_client(fd)
                else:
                    state = client_state.get(fd)

                    if state and state['type'] == 'upload_size':
                        file_size = int(data.decode('utf-8').strip())
                        filename = state['filename']
                        filepath = os.path.join(FILES_DIR, filename)
                        client_state[fd] = {
                            'type': 'upload',
                            'filename': filename,
                            'size': file_size,
                            'received': 0,
                            'file': open(filepath, 'wb')
                        }
                        send_queue[fd].append(b"SIZE_OK")
                        poller.modify(fd, select.POLLIN | select.POLLOUT)

                    elif state and state['type'] == 'upload':
                        state['file'].write(data)
                        state['received'] += len(data)
                        if state['received'] >= state['size']:
                            state['file'].close()
                            client_state[fd] = None
                            send_queue[fd].append(
                                f"Upload successful: {state['filename']}".encode('utf-8')
                            )
                            poller.modify(fd, select.POLLIN | select.POLLOUT)

                    elif state and state['type'] == 'download_ack':
                        if data.strip() == b"SIZE_OK":
                            filename = state['filename']
                            filepath = os.path.join(FILES_DIR, filename)
                            client_state[fd] = None
                            with open(filepath, 'rb') as f:
                                while True:
                                    chunk = f.read(BUFFER_SIZE)
                                    if not chunk:
                                        break
                                    send_queue[fd].append(chunk)
                            poller.modify(fd, select.POLLIN | select.POLLOUT)

                    else:
                        message  = data.decode('utf-8').strip()
                        print(f"[POLL] {fd_to_addr[fd]}: {message}")
                        response = process(fd, message)
                        if response:
                            send_queue[fd].append(response)
                            poller.modify(fd, select.POLLIN | select.POLLOUT)

            elif event & select.POLLOUT:
                if send_queue.get(fd):
                    data = send_queue[fd].pop(0)
                    try:
                        fd_to_sock[fd].sendall(data)
                    except Exception:
                        remove_client(fd)
                        continue

                if not send_queue.get(fd):
                    poller.modify(fd, select.POLLIN)

if __name__ == '__main__':
    main()
