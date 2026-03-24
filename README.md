[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Hazza Danta Hermandanu               | 5025241117           | D          |
|                |            |           |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program
1. server-sync.py
   ```python
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
send_queue = {}   # conn -> list of data yang antri dikirim

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

        # ─── HANDLE READABLE ───────────────────────────
        for sock in readable:
            if sock is server:
                #ada client baru connect
                conn, addr = server.accept()
                conn.setblocking(False)
                rlist.append(conn)   # pantau bacanya
                xlist.append(conn)   # pantau errornya
                clients.append(conn)
                client_state[conn] = None
                send_queue[conn] = []
                print(f"[SELECT] Connected: {addr}")

            else:
                # ada data masuk dari client
                try:
                    data = conn.recv(BUFFER_SIZE)
                except Exception:
                    data = None

                if not data:
                    # client disconnect
                    remove_client(sock, rlist, wlist, xlist)
                else:
                    message = data.decode('utf-8').strip()
                    print(f"[SELECT] {sock.getpeername()}: {message}")

                    # proses perintah, simpan response ke send_queue
                    response = process(sock, message)
                    if response:
                        send_queue[sock].append(response)
                        if sock not in wlist:
                            wlist.append(sock)  # daftarkan ke wlist

        # ─── HANDLE WRITABLE ───────────────────────────
        for sock in writable:
            if send_queue.get(sock):
                # ambil data pertama dari antrian
                data = send_queue[sock].pop(0)
                try:
                    sock.sendall(data)
                except Exception:
                    remove_client(sock, rlist, wlist, xlist)
            else:
                # tidak ada data → keluarkan dari wlist
                wlist.remove(sock)

        # ─── HANDLE EXCEPTIONAL ────────────────────────
        for sock in exceptional:
            print(f"[SELECT] Error on {sock.getpeername()}")
            remove_client(sock, rlist, wlist, xlist)


def process(conn, message):
    """proses perintah dan return response dalam bytes"""
    if message == '/list':
        files = os.listdir(FILES_DIR)
        response = ("Files on server:\n" + "\n".join(files)) if files else "No files on server."
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

    else:
        broadcast(message, exclude=conn)
        return b"[Server] Message broadcast."


def broadcast(message, exclude=None):
    for c in clients:
        if c is not exclude:
            if c in send_queue:
                send_queue[c].append(f"[Broadcast] {message}".encode('utf-8'))


def remove_client(sock, rlist, wlist, xlist):
    print(f"[SELECT] Disconnected: {sock.getpeername()}")
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


if __name__ == '__main__':
    main()
   ```

## Screenshot Hasil
