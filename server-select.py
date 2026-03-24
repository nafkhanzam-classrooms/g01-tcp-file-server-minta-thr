import socket
import select
import os

HOST = '0.0.0.0'
PORT = 9001
FILES_DIR = 'server_files'
BUFFER_SIZE = 4096

os.makedirs(FILES_DIR, exist_ok=True)

clients = []
client_state = {}
send_queue = {}

def process(conn, message):
    if message == '/list':
        files = os.listdir(FILES_DIR)
        response = ("\n".join(files)) if files else "No files on server."
        return response.encode('utf-8')

    elif message.startswith('/upload '):
        filename = message[8:].strip()
        client_state[conn] = {'type': 'upload_size', 'filename': filename}
        return b"READY"

    elif message.startswith('/download '):
        filename = message[10:].strip()
        filepath = os.path.join(FILES_DIR, filename)
        if not os.path.exists(filepath):
            return b"ERROR: File not found."
        file_size = os.path.getsize(filepath)
        client_state[conn] = {'type': 'download_ack', 'filename': filename}
        return f"SIZE {file_size}".encode('utf-8')

def remove_client(sock, rlist, wlist, xlist):
    print(f"Disconnected: {sock.getpeername()}")
    if sock in rlist:
        rlist.remove(sock)
    if sock in wlist:
        wlist.remove(sock)
    if sock in xlist:
        xlist.remove(sock)
    if sock in clients:
        clients.remove(sock)
    send_queue.pop(sock, None)
    client_state.pop(sock, None)
    sock.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    server.setblocking(False)
    print(f"Server listening on {HOST}:{PORT}")

    rlist = [server]   #socket yang siap dibaca
    wlist = []         #socket yang siap ditulis
    xlist = [server]   #socket yang error

    while True:
        readable, writable, exceptional = select.select(rlist, wlist, xlist, 1.0)
        for sock in readable:
            if sock is server:
                conn, addr = server.accept()
                conn.setblocking(False)
                rlist.append(conn)
                xlist.append(conn)
                clients.append(conn)
                client_state[conn] = None
                send_queue[conn] = []
                print(f"Connected: {addr}")

            else:
                try:
                    data = sock.recv(BUFFER_SIZE)
                except Exception:
                    data = None

                if not data:
                    remove_client(sock, rlist, wlist, xlist)
                else:
                    state = client_state.get(sock)

                    #upload_size state
                    if state and state['type'] == 'upload_size':
                        file_size = int(data.decode('utf-8').strip())
                        filename = state['filename']
                        filepath = os.path.join(FILES_DIR, filename)
                        client_state[sock] = {
                            'type': 'upload',
                            'filename': filename,
                            'size': file_size,
                            'received': 0,
                            'file': open(filepath, 'wb')
                        }
                        send_queue[sock].append(b"SIZE_OK")
                        if sock not in wlist:
                            wlist.append(sock)

                    #upload state
                    elif state and state['type'] == 'upload':
                        state['file'].write(data)
                        state['received'] += len(data)
                        if state['received'] >= state['size']:
                            state['file'].close()
                            client_state[sock] = None
                            send_queue[sock].append(
                                f"Upload successful: {state['filename']}".encode('utf-8')
                            )
                            if sock not in wlist:
                                wlist.append(sock)

                    #download_ack state
                    elif state and state['type'] == 'download_ack':
                        if data.strip() == b"SIZE_OK":
                            filename = state['filename']
                            filepath = os.path.join(FILES_DIR, filename)
                            client_state[sock] = None
                            with open(filepath, 'rb') as f:
                                while True:
                                    chunk = f.read(BUFFER_SIZE)
                                    if not chunk:
                                        break
                                    send_queue[sock].append(chunk)
                            if sock not in wlist:
                                wlist.append(sock)
                    
                    #none state
                    else:
                        message = data.decode('utf-8').strip()
                        print(f"{sock.getpeername()}: {message}")
                        response = process(sock, message)
                        if response:
                            send_queue[sock].append(response)
                            if sock not in wlist:
                                wlist.append(sock)

        for sock in writable:
            if send_queue.get(sock):
                data = send_queue[sock].pop(0)
                try:
                    sock.sendall(data)
                except Exception:
                    remove_client(sock, rlist, wlist, xlist)
            else:
                wlist.remove(sock)

        for sock in exceptional:
            print(f"Error on {sock.getpeername()}")
            remove_client(sock, rlist, wlist, xlist)

if __name__ == '__main__':
    main()
