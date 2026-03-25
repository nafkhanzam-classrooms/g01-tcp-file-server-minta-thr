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
    - Import library Socket dan OS
    ```python
    import socket
    import os
    ```
    <br>

    - Deklarasi Host, Port, Direktori File, dan Buffer Size
    ```python
    HOST = '0.0.0.0'
    PORT = 9000
    FILES_DIR = 'server_files'
    BUFFER_SIZE = 4096
    ```
    <br>

    - Buat Direktori File, jika sudah ada set exist_ok ke ```True```
    ```python
    os.makedirs(FILES_DIR, exist_ok=True)
    ```
    <br>

    - Function ```handle_client``` dengan parameter conn (koneksi) dan addr (alamat client) untuk menghandle 1 client di 1 waktu
       - Deklarasi function dan print konektivitas
        ```python
        def handle_client(conn, addr):
            print(f"Connected: {addr}")
        ```
        <br>
        
       - Membaca message dari client
            - `try` untuk memulai error handling
            - Lakukan loop selama client masih terhubung
            - Lakukan block untuk client lain dan tunggu client saat ini mengirim data
            - Jika tidak ada data (kosong) maka `break`
            - Data akan terkirim dalam bentuk binary
            - Decode data yang diterima menjadi bentuk string lalu hapus space/newline di akhir string
            - Print alamat client dan apa yang dikirim
    
        ```python
        try:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                message = data.decode('utf-8').strip()
                print(f"{addr}: {message}")
        ```
        <br>
       
       - Membaca perintah `/list`
            - Cek apakah `message == '/list'`
            - Jika iya, baca direktori `FILES_DIR`, lalu assign ke `files`
            - Jika `files` tidak kosong, maka gabungkan semua nama file dengan newline dan assign ke `response`
            - Jika `files` kosong, set `response` dengan `No files on server.`
            - Encode string menjadi bytes lalu kirim ke client
          
        ```python
                if message == '/list':
                    files = os.listdir(FILES_DIR)
                    if files:
                        response = "\n".join(files)
                    else:
                        response = "No files on server."
                    conn.sendall(response.encode('utf-8'))
        ```
        <br>

        - Membaca perintah `/upload <filename>`
            - Cek apakah `message` diawali dengan string `/upload `
            - Jika iya, ambil nama file dengan mengambil string setelah indeks ke 8, lalu hapus space/newline
            - Beritahu client bahwa server sudah siap dengan mengirimkan `READY` dalam bentuk biner
            - Terima size file dari client lalu decode menjadi string
            - Convert string menjadi integer
            - Beritahu client bahwa ukuran telah diterima dengan mengirimkan `SIZE_OK` dalam bentuk biner
            - Deklarasi `received` sebagai counter dan `filepath` sebagai path
            - Buat file kosong di memory dengan `wb` dimana write untuk menulis dan binary artinya untuk semua jenis file
            - Loop saat `received < file_size`
            - Hitung berapa banyak bytes yang akan diterima dengan membandingkan nilai minimum dari `BUFFER_SIZE` dan `file_size - received`, lalu assign ke `chunk`
            - Jika chunk kosong, maka break
            - Tulis byte di file
            - Tambahkan panjang dari chunk ke `received`
            - Print file yang telah diupload, sizenya, dan client yang mengupload
            - Beritahu client bahwa file telah sukses diupload
        ```python
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
                    print(f"Received file '{filename}' ({received} bytes) from {addr}")
                    conn.sendall(f"Upload success: {filename}".encode('utf-8'))
        ```
        <br>

        - Membaca perintah `/download <filename>`
            - Cek apakah `message` diawali dengan string `/download `
            - Jika iya, ambil nama file dengan mengambil string setelah indeks ke 10, lalu hapus space/newline
            - Deklarasi `filepath` sebagai path file yang ingin didownload
            - Jika file/path tidak ada maka beritahu client bahwa `File not found.`
            - jika ada, dapatkan size file dengan `getsize`
            - Beritahu client ukuran file yang akan dikirim lalu tunggu konfirmasi client
            - Jika client menjawab `SIZE_OK`, maka buka file dengan rb dimana r adalah read dan b adalah binary
            - Loop sampai file habis
            - Baca file, jika file kosong/habis maka break
            - Kirimkan potongan (chunk) file ke client
            - Beritahu client bahwa file telah sukses didownload

        ```python
                elif message.startswith('/download '):
                    filename = message[10:].strip()
                    filepath = os.path.join(FILES_DIR, filename)
                    if not os.path.exists(filepath):
                        conn.sendall(b"ERROR: File not found.")
                    else:
                        file_size = os.path.getsize(filepath)
                        conn.sendall(f"SIZE {file_size}".encode('utf-8'))
                        ack = conn.recv(BUFFER_SIZE)
                        if ack == b"SIZE_OK":
                            with open(filepath, 'rb') as f: #open file untuk read
                                while True:
                                    chunk = f.read(BUFFER_SIZE)
                                    if not chunk:
                                        break
                                    conn.sendall(chunk)
                            print(f"Sent file '{filename}' to {addr}")
        ```
        <br>

        - Error handling
        ```python
        except (ConnectionResetError, BrokenPipeError):
            pass
        finally:
            conn.close()
            print(f"Disconnected: {addr}")
        ```
        <br>

        - Fungsi `main()`
            - Buat socket
            - Izinkan reuse port
            - Bind server ke alamat dan port
            - Server listen hanya ke 1 client
            - Loop untuk sampai client mengakhiri koneksi
            - Tunggu koneksi dari client
            - Block client lain selain dari client saat ini
        ```python
        def main():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind((HOST, PORT))
                server.listen(1)
                print(f"Server listening on {HOST}:{PORT}")
                while True:
                    conn, addr = server.accept()
                    handle_client(conn, addr)
        
        ```
        <br>

        - Handler untuk import file
        ```python
        if __name__ == '__main__':
            main()
       ```
        <br><br>

2. server-select.py
    - Import library
    ```python
        import socket
        import select
        import os
    ```
    <br>
    
    - Deklarasi Host, Port, Direktori File, dan Buffer Size
    ```python
    HOST = '0.0.0.0'
    PORT = 9001
    FILES_DIR = 'server_files'
    BUFFER_SIZE = 4096
    ```
    <br>

    - Buat Direktori File, jika sudah ada set exist_ok ke ```True```
    ```python
    os.makedirs(FILES_DIR, exist_ok=True)
    ```
    <br>

    - Deklarasi `clients` untuk menyimpan socket client yang terhubung, `client_state` untuk menyimpan state dari setiap client, dan `send_queue` untuk menyimpan antrian pengiriman data ke setiap client
    ```python
    clients = []
    client_state = {}
    send_queue = {}
    ```
    <br>

    - Function `process` dengan parameter `conn` dan `message` untuk menghandle proses dari setiap perintah client
        - Deklarasi function
        ```python
        def process(conn, message):
        ```
        <br>

        - Jika message `/list`
            - Assign file yang ada di `FILES_DIR` ke files
            - Jika `files` tidak kosong, maka gabungkan semua nama file dengan newline dan assign ke `response`
            - Jika `files` kosong, set `response` dengan `No files on server.`
            - Encode string menjadi bytes lalu return
        ```python
        if message == '/list':
            files = os.listdir(FILES_DIR)
            response = ("\n".join(files)) if files else "No files on server."
            return response.encode('utf-8')
        ```
        <br>

        - Jika message `/upload `
            - Ambil nama file dengan mengambil string setelah indeks ke 8, lalu hapus space/newline
            - Set `client_state` pada client saat ini dengan `type` : `upload_size` dan `filename` : `filename`
            - return `READY` yang telah diconvert ke biner 
        ```python
        elif message.startswith('/upload '):
            filename = message[8:].strip()
            client_state[conn] = {'type': 'upload_size', 'filename': filename}
            return b"READY"
        ```
        <br>

        - Jika message `/download `
            - Ambil nama file dengan mengambil string setelah indeks ke 10, lalu hapus space/newline
            - Assign `file_path` dari file ke `filepath`
            - Jika file/filepath tidak ada maka return `File not found` dalam bentuk biner
            - Dapatkan file size dengan `getsize`
            - Set `client state` pada client saat ini dengan `type` : `download_ack` dan `filename` : `filename`
            - Return `SIZE {file_size}` yang telah diencode
            ```python
            elif message.startswith('/download '):
                filename = message[10:].strip()
                filepath = os.path.join(FILES_DIR, filename)
                if not os.path.exists(filepath):
                    return b"ERROR: File not found."
                file_size = os.path.getsize(filepath)
                client_state[conn] = {'type': 'download_ack', 'filename': filename}
                return f"SIZE {file_size}".encode('utf-8')
            ```
            <br>

    - Function `remove_client` dengan parameter `sock`, `rlist`, `wlist`, dan `xlist` untuk meremove client saat client disconnect
    ```python
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
    ```
   <br>

   - Funcgsi `main()`
        - Setup
            - Buat socket
            - Izinkan reuse port
            - Bind server ke alamat dan port
            - Server listen maksimal ke 10 koneksi
            - Matikan blocking
        ```python
        def main():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((HOST, PORT))
            server.listen(10)
            server.setblocking(False)
            print(f"Server listening on {HOST}:{PORT}")
        ```
        <br>

        - List select
            - rlist untuk menyimpan socket yang siap untuk dibaca
            - wlist untuk menyimpan socket yang siap untuk ditulis
            - xlist untuk menyimpan socket untuk mendeteksi error
        ```python
        rlist = [server]
        wlist = []         
        xlist = [server]  
        ```
        <br>

        - Main loop
            - Loop terus dengan
                - `readable`: socket yang punya data masuk
                - `writable`: socket yang siap dikirim
                - `exceptional`: socket yang error
                - timeout 1 detik
            ```python
            while True:
                readable, writable, exceptional = select.select(rlist, wlist, xlist, 1.0)
            ```
            <br>
  
            - Readable handle
                ```python
                for sock in readable:
                ```
                <br>
                
                - Jika sock adalah server
                    - Loop jika ada `sock` di `readable`
                    - Jika `sock` adalah `server`, maka terima client dan tambahkan ke list select
                    - Tambahkan `conn` dari client ke `clients`, `client_state` menjadi `none`, dan `send_queue` dengan array kosong
                ```python
                    if sock is server:
                        conn, addr = server.accept()
                        conn.setblocking(False)
                        rlist.append(conn)
                        xlist.append(conn)
                        clients.append(conn)
                        client_state[conn] = None
                        send_queue[conn] = []
                        print(f"Connected: {addr}")
                ```
                <br>
    
                - Jika sock bukan server
                    - Terima data dari client
                    - Cek apakah data kosong/tidak
                    - Jika data kosong, maka remove client
                    - Jika tidak, maka dapatkan state client dengan `get`
                ```python
                else:
                    try:
                        data = sock.recv(BUFFER_SIZE)
                    except Exception:
                        data = None
        
                    if not data:
                        remove_client(sock, rlist, wlist, xlist)
                    else:
                        state = client_state.get(sock)
                ```
                <br>
    
                - State `upload_size`
                    - Cek state apakah `upload_size`
                    - Jika iya, assign `file_size` dengan mendecode data dan convert ke integer
                    - Assign `filename`, `filepath`, dan update `client_state` dengan socket client saat ini
                    - Tambahkan response `SIZE_OK` ke `send_queue` dengan socket client saat ini
                    - Jika tidak ditemukan socket di `wlist` maka tambahkan socket ke wlist
                ```python
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
                ```
                <br>
    
                - State 'upload`
                    - Cek state apakah `upload`
                    - Jika iya, write chunk ke memory lalu hitung data ter-received
                    - Jika data yang diterima >= data file, maka close file dan set `client_state` ke `None`
                    - Tambahkan `state['filename']` yang sudah diencode ke `send_queue`
                    - Jika socket tidak ada di `wlist`, tambahkan socket ke `wlist`
                ```python
                elif state and state['type'] == 'upload':
                    state['file'].write(data)
                    state['received'] += len(data)
                    if state['received'] >= state['size']:
                        state['file'].close()
                        client_state[sock] = None
                        send_queue[sock].append(f"Upload successful: {state['filename']}".encode('utf-8'))
                        if sock not in wlist:
                            wlist.append(sock)
                ```
                <br>

                - State `download_ack`
                    - Cek state apakah 'download_ack`
                    - Jika iya, cek apakah client mengirim `SIZE_OK`
                    - Jika iya, set `filename` dari state filename, `filepath`, set state dengan `None`
                    - Buka dan baca file menggunakan `rb`, r untuk read dan b untuk binary
                    - Loop sampai file berakhir
                    - Baca semua `chunk` lalu masukan ke `send_queue`
                    - Jika sudah tidak ada `chunk`, maka break
                    - Jika socket tidak ada di `wlist`, maka tambahkan socket di `wlist`
                ```python
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
                ```
                <br>
    
                - State `None`
                    - Jika tidak ada state aktif (`/list`, `/upload`, `/download`)
                    - Decode data dari client dan assign ke `message`
                    - Panggil fungsi `process` lalu assign nilainya ke `response`
                    - Jika `response` ada, maka tambahkan ke `send_queue`
                    - Jika socket tidak ada di `wlist`, maka tambahkan socket ke `wlist`
                ```python
                else:
                    message = data.decode('utf-8').strip()
                    print(f"{sock.getpeername()}: {message}")
                    response = process(sock, message)
                    if response:
                        send_queue[sock].append(response)
                        if sock not in wlist:
                            wlist.append(sock)
                ```
                <br>

            - Writable handler
                - Loop per socket yang ada di writable
                - Jika `send_queue` dari socket saat ini memiliki isi:
                    - Pop data pertama dan assign ke `data`
                    - Kirim data dari socket saat ini
                    - Jika error (client disconnect), maka remove client
                - Jika `send_queue` kosong, maka remove socket dari `wlist`
            ```python
            for sock in writable:
                if send_queue.get(sock):
                    data = send_queue[sock].pop(0)
                    try:
                        sock.sendall(data)
                    except Exception:
                        remove_client(sock, rlist, wlist, xlist)
                else:
                    wlist.remove(sock)
            ```
            <br>
  
            - Error handler
            ```python
            for sock in exceptional:
                print(f"Error on {sock.getpeername()}")
                remove_client(sock, rlist, wlist, xlist)
            ```
            <br>
        - Handler untuk import file
        ```
        if __name__ == '__main__':
            main() 
        ```
        <br><br>

3. server-poll.py
    - Import library
    ```python
    import socket
    import select
    import os
    ```
    <br>

    - Dekalarasi `HOST`, `HOST`, `PORT`, dan `BUFFER_SIZE`
    ```python
    HOST = '0.0.0.0'
    PORT = 9002
    FILES_DIR = 'server_files'
    BUFFER_SIZE = 4096
    ```
    <br>

    - Buat Direktori File, jika sudah ada set exist_ok ke ```True```
    ```python
    os.makedirs(FILES_DIR, exist_ok=True)
    ```
    <br>

    - Direct mapping file descriptor
        - `fd_to_sock`: fd-socket
        - `fd_to_addr`: fd-alamat client
    ```python
    fd_to_sock = {} 
    fd_to_addr = {}
    ```
    <br>

    - Deklarasi `clients` untuk menyimpan file descriptor client yang terhubung, `client_state` untuk menyimpan state dari setiap client, `send_queue` untuk menyimpan antrian pengiriman data ke setiap client, `poller` sebagai poll object dan diset ke `None`
    ```python
    client_state = {}   
    send_queue = {}   
    clients = []
    poller = None
    ```
    <br>

    - Function `process` dengan parameter `fd` dan `message` untuk menghandle proses dari setiap perintah client
        - Deklarasi function
        ```python
        def process(fd, message):
        ```
        <br>

        - Jika message `/list`
            - Assign file yang ada di `FILES_DIR` ke files
            - Jika `files` tidak kosong, maka gabungkan semua nama file dengan newline dan assign ke `response`
            - Jika `files` kosong, set `response` dengan `No files on server.`
            - Encode string menjadi bytes lalu return
        ```python
        if message == '/list':
            files = os.listdir(FILES_DIR)
            response = ("\n".join(files)) if files else "No files on server."
            return response.encode('utf-8')
       ```
        <br>

        - Jika message `/upload `
            - Ambil nama file dengan mengambil string setelah indeks ke 8, lalu hapus space/newline
            - Set `client_state` pada client saat ini dengan `type` : `upload_size` dan `filename` : `filename`
            - return `READY` yang telah diconvert ke biner
        ```python
        elif message.startswith('/upload '):
            filename = message[8:].strip()
            client_state[fd] = {'type': 'upload_size', 'filename': filename}
            return b"READY"
        ```
        <br>

        - Jika message `/download `
            - Ambil nama file dengan mengambil string setelah indeks ke 10, lalu hapus space/newline
            - Assign `file_path` dari file ke `filepath`
            - Jika file/filepath tidak ada maka return `File not found` dalam bentuk biner
            - Dapatkan file size dengan `getsize`
            - Set `client state` pada client saat ini dengan `type` : `download_ack` dan `filename` : `filename`
            - Return `SIZE {file_size}` yang telah diencode
        ```python
        elif message.startswith('/download '):
            filename = message[10:].strip()
            filepath = os.path.join(FILES_DIR, filename)
            if not os.path.exists(filepath):
                return b"ERROR: File not found."
            file_size = os.path.getsize(filepath)
            client_state[fd] = {'type': 'download_ack', 'filename': filename}
            return f"SIZE {file_size}".encode('utf-8')
        ```
        <br>

        - Function `remove_client` dengan parameter `fd` untuk meremove client saat client disconnect
        ```python
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
        ```
        <br>

    - Fungsi `main()`
        - Setup
            - Panggil `poller` sebagai variabel global
            - Buat socket
            - Izinkan reuse port
            - Bind server ke alamat dan port
            - Server listen maksimal ke 10 koneksi
            - Matikan blocking
        ```python
            def main():
                global poller

                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind((HOST, PORT))
                server.listen(10)
                server.setblocking(False)
                print(f"Server listening on {HOST}:{PORT}")
        ```
      <br>

        - Inisialisasi poll
            - `poller`: objek poll yang akan memantau semua file descriptor
            - Register server fd ke `poller`, lalu pantau event `POLLIN`
            - Simpan fd serber ke `server_fd`
            - Simpan server ke direct mapping
        ```python
            poller = select.poll()
            poller.register(server.fileno(), select.POLLIN)
        
            server_fd = server.fileno()
            fd_to_sock[server_fd] = server
        ```
        <br>

        - Loop utama
            - Event, timeout 1000ms (1 detik)
            - Loop ke setiap event
        ```python
                    while True:
                        events = poller.poll(1000)
                        for fd, event in events:
                    ```
                    <br>
                
                    - Jika `fd` = `server_fd` (Client mencoba untuk terhubung dengan server)
                        - Accept client
                        - Set block ke `false`
                        - Berikan client file descriptor
                    ```python
                    if fd == server_fd:
                        conn, addr = server.accept()
                        conn.setblocking(False)
                        cfd = conn.fileno()
        ```
       <br>
         
        - Register `cfd` untuk `POLLIN`
          ```python
                    poller.register(cfd, select.POLLIN)
          ```
           <br>
    
          - Simpan semua info client dengan key `fd`
            ```python
                    fd_to_sock[cfd] = conn
                    fd_to_addr[cfd] = addr
                    client_state[cfd] = None
                    send_queue[cfd] = []
                    clients.append(cfd)
                    print(f"[POLL] Connected: {addr}")
            ```
            <br>
      
            - Jika terjadi event dan client disconnect (POLLHUP) atau socket error (POLERR), maka remove client
               ```python
                    elif event & (select.POLLHUP | select.POLLERR):
                        remove_client(fd)
                ```
               <br>
      
            - Jika terjadi event dan ada data masuk yang siap dibaca (`POLLIN`):
                - Set sock berdasarkan `fd` yang sedang aktif
                - Terima data dari client
                - Jika data kosong, maka remove client
                - Jika tidak, maka dapatkan state client dengan `get`
                ```python
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
                ```
                <br>
    
                - State `upload_size`
                    - Cek state apakah `upload_size`
                    - Jika iya, assign `file_size` dengan mendecode data dan convert ke integer
                    - Assign `filename`, `filepath`, dan update `client_state` dengan `fd` client saat ini
                    - Tambahkan response `SIZE_OK` ke `send_queue` dengan socket client saat ini
                    - Modify `poller` dengan `POLLIN` atau `POLLOUT`
                ```python
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
                ```
                <br>
             
                - State 'upload`
                    - Cek state apakah `upload`
                    - Jika iya, write chunk ke memory lalu hitung data ter-received
                    - Jika data yang diterima >= data file, maka close file dan set `client_state` ke `None`
                    - Tambahkan `state['filename']` yang sudah diencode ke `send_queue`
                    - Modify `poller` dengan `POLLIN` atau `POLLOUT`
                ```python
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
                ```
                <br>
             
                - State `download_ack`
                    - Cek state apakah 'download_ack`
                    - Jika iya, cek apakah client mengirim `SIZE_OK`
                    - Jika iya, set `filename` dari state filename, `filepath`, set state dengan `None`
                    - Buka dan baca file menggunakan `rb`, r untuk read dan b untuk binary
                    - Loop sampai file berakhir
                    - Baca semua `chunk` lalu masukan ke `send_queue`
                    - Jika sudah tidak ada `chunk`, maka break
                    - Modify `poller` dengan `POLLIN` atau `POLLOUT`
                ```python
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
                ```
                <br>
        
                - State `None`
                    - Jika tidak ada state aktif (`/list`, `/upload`, `/download`)
                    - Decode data dari client dan assign ke `message`
                    - Panggil fungsi `process` lalu assign nilainya ke `response`
                    - Jika `response` ada, maka tambahkan ke `send_queue`
                    - Modify `poller` dengan `POLLIN` atau `POLLOUT`
                ```python
                            else:
                                message  = data.decode('utf-8').strip()
                                print(f"{fd_to_addr[fd]}: {message}")
                                response = process(fd, message)
                                if response:
                                    send_queue[fd].append(response)
                                    poller.modify(fd, select.POLLIN | select.POLLOUT)
                ```
                <br>
      
                - Jika terjadi event dan statusnya (`POLLOUT`):
                    - Jika `send_queue` dari `fd` saat ini memiliki isi:
                    - Pop data pertama dan assign ke `data`
                    - Kirim data dari socket saat ini
                    - Jika error (client disconnect), maka remove client dan continue
                    - Jika `send_queue` kosong, maka modify `poller` dengan `POLLIN`
                ```python
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
                ```
                <br>

    - Handler untuk import file
    ```python
        if __name__ == '__main__':
            main()
    ```
    <br><br>

4. server-thread.py
    - Import library
    ```python
    import socket
    import threading
    import os
    ```
    <br>

    - Deklarasi Host, Port, Direktori File, dan Buffer Size
    ```python
    HOST = '0.0.0.0'
    PORT = 9003
    FILES_DIR = 'server_files'
    BUFFER_SIZE = 4096
    ```
    <br>

    - Buat Direktori File, jika sudah ada set exist_ok ke ```True``` 
    ```python
    os.makedirs(FILES_DIR, exist_ok=True)
    ```
    <br>

    - Global variabel
        - `clients_lock`: mengunci threading client saat ini agar tidak bertabrakan saat melakukan proses
        - `clients`: list client yang terhubung
    ```python
    clients_lock = threading.Lock()
    clients = {}
    ```
    <br>

    - Function `handle_client` dengan parameter `conn` dan `addr` untuk menghandle proses dari setiap perintah client
        - Deklarasi function dan print konektivitas
    ```python
    def handle_client(conn, addr):
        print(f"Connected: {addr} (thread {threading.current_thread().name})")
    ```
    <br>

    - Membaca message dari client
            - `try` untuk memulai error handling
            - Lakukan loop selama client masih terhubung
            - Tunggu client saat ini mengirim data
            - Jika tidak ada data (kosong) maka `break`
            - Decode data yang diterima menjadi bentuk string lalu hapus space/newline di akhir string
            - Print alamat client dan apa yang dikirim
    ```python
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            message = data.decode('utf-8').strip()
            print(f"{addr}: {message}")
    ```
    <br>

    - Membaca perintah `/list`
            - Cek apakah `message == '/list'`
            - Jika iya, baca direktori `FILES_DIR`, lalu assign ke `files`
            - Jika `files` tidak kosong, maka gabungkan semua nama file dengan newline dan assign ke `response`
            - Jika `files` kosong, set `response` dengan `No files on server.`
            - Encode string menjadi bytes lalu kirim ke client
    ```python
    if message == '/list':
        files = os.listdir(FILES_DIR)
        response = ("\n".join(files)) if files else "No files on server."
        conn.sendall(response.encode('utf-8'))
    ```
    <br>

    - Membaca perintah `/upload <filename>`
            - Cek apakah `message` diawali dengan string `/upload `
            - Jika iya, ambil nama file dengan mengambil string setelah indeks ke 8, lalu hapus space/newline
            - Beritahu client bahwa server sudah siap dengan mengirimkan `READY` dalam bentuk biner
            - Terima size file dari client lalu decode menjadi string
            - Convert string menjadi integer
            - Beritahu client bahwa ukuran telah diterima dengan mengirimkan `SIZE_OK` dalam bentuk biner
            - Deklarasi `received` sebagai counter dan `filepath` sebagai path
            - Buat file kosong di memory dengan `wb` dimana write untuk menulis dan binary artinya untuk semua jenis file
            - Loop saat `received < file_size`
            - Hitung berapa banyak bytes yang akan diterima dengan membandingkan nilai minimum dari `BUFFER_SIZE` dan `file_size - received`, lalu assign ke `chunk`
            - Jika chunk kosong, maka break
            - Tulis byte di file
            - Tambahkan panjang dari chunk ke `received`
            - Print file yang telah diupload, sizenya, dan client yang mengupload
            - Beritahu client bahwa file telah sukses diupload
    ```python
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
    ```
    <br>

    - Membaca perintah `/download <filename>`
        - Cek apakah `message` diawali dengan string `/download `
        - Jika iya, ambil nama file dengan mengambil string setelah indeks ke 10, lalu hapus space/newline
        - Deklarasi `filepath` sebagai path file yang ingin didownload
        - Jika file/path tidak ada maka beritahu client bahwa `File not found.`
        - jika ada, dapatkan size file dengan `getsize`
        - Beritahu client ukuran file yang akan dikirim lalu tunggu konfirmasi client
        - Jika client menjawab `SIZE_OK`, maka buka file dengan rb dimana r adalah read dan b adalah binary
        - Loop sampai file habis
        - Baca file, jika file kosong/habis maka break
        - Kirimkan potongan (chunk) file ke client
        - Beritahu client bahwa file telah sukses didownload
    ```python
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
    ```
    <br>

    - Abaikan error
    ```python
    except (ConnectionResetError, BrokenPipeError, ValueError):
        pass
    ```
    <br>

    - Remove client
    ```python
    finally:
        with clients_lock:
            clients.pop(conn, None)
        conn.close()
        print(f"Disconnected: {addr}")
    ```
    <br>

    - Fungsi `main()`
        - Setup
            - Buat socket
            - Izinkan reuse port
            - Bind server ke alamat dan port
            - Server listen hanya ke maksimal 10 client
        ```python
        def main():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind((HOST, PORT))
                server.listen(10)
                print(f"Server listening on {HOST}:{PORT}")
        ```
        <br>

        - Loop utama
             - Loop sampai client mengakhiri koneks
             - Accept koneksi dari client
             - Gunakan lock karena data akan diakses banyak thread
             - Buat thread baru setiap ada client
             - Start threading
             - Print active client
        ```python
        while True:
            conn, addr = server.accept()
            with clients_lock:
                clients[conn] = addr
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
            print(f"Active clients: {threading.active_count() - 1}")
        ```
        <br>

    - Handler untuk import file
    ```python
    if __name__ == '__main__':
        main()
    ```
    <br><br>

5. client.py
    


## Screenshot Hasil
