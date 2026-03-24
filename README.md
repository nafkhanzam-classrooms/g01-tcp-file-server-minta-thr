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


    - Deklarasi Host, Port, Direktori File, dan Buffer Size
    ```python
    HOST = '0.0.0.0'
    PORT = 9000
    FILES_DIR = 'server_files'
    BUFFER_SIZE = 4096
    ```

    - Buat Direktori File, jika sudah ada set exist_ok ke ```True```
    ```python
    os.makedirs(FILES_DIR, exist_ok=True)
    ```
    
    - Function ```handle_client``` dengan parameter conn (koneksi) dan addr (alamat client) untuk menghandle 1 client di 1 waktu
       - Deklarasi function dan print konektivitas
        ```python
        def handle_client(conn, addr):
            print(f"Connected: {addr}")
        ```

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
    
                elif message.startswith('/upload '):
                    filename = message[8:].strip()
                    conn.sendall(b"READY")
                    size_data = conn.recv(BUFFER_SIZE).decode('utf-8').strip()
                    file_size = int(size_data)
                    conn.sendall(b"SIZE_OK")
                    received = 0
                    filepath = os.path.join(FILES_DIR, filename)
                    with open(filepath, 'wb') as f: #open file untuk write dalam biner
                        while received < file_size:
                            chunk = conn.recv(min(BUFFER_SIZE, file_size - received))
                            if not chunk:
                                break
                            f.write(chunk) #tulis byte di file
                            received += len(chunk)
                    print(f"Received file '{filename}' ({received} bytes) from {addr}")
                    conn.sendall(f"Upload success: {filename}".encode('utf-8'))
    
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
    
        except (ConnectionResetError, BrokenPipeError):
            pass
        finally:
            conn.close()
            print(f"Disconnected: {addr}")
    
    def main():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((HOST, PORT))
            server.listen(1)
            print(f"Server listening on {HOST}:{PORT}")
            while True:
                conn, addr = server.accept()
                handle_client(conn, addr)
    
    
    if __name__ == '__main__':
        main()
       ```

## Screenshot Hasil
