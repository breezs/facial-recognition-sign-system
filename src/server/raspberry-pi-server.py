import pickle
import socket
import struct
import threading
import cv2

class RaspberryPiServer:
    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))

        self.server_socket.listen(1)
        print(f"服务器启动，监听 {host}:{port}")
        self.capture = cv2.VideoCapture(0)  # 打开默认摄像头

    def set_threshold(self, threshold):
        try:
            self.threshold = int(threshold)
            print(f'收到开门标志: {self.threshold}')
        except ValueError:
            print('无效的标志')

    def encode_image(self):  # 图像编码
        ret, frame = self.capture.read()
        cv2.waitKey(1)
        if ret:
            _, img_encoded = cv2.imencode('.jpg', frame)
            return img_encoded.tobytes()
        return None

    def send_data(self, client_socket):  # 发送数据
        image_data = self.encode_image()
        # img.frombuffer(image_data).show()
        if image_data:
            # data里面传输数据,字典方式
            data = {"image": image_data}
            packed_data = pickle.dumps(data)
            client_socket.sendall(struct.pack(">L", len(packed_data)))
            client_socket.sendall(packed_data)
            client_socket.recv(1024)  # 等待客户端确认

    def handle_client(self, client_socket):
        while True:
            try:
                # 发送图像数据
                self.send_data(client_socket)

                # 非阻塞地检查是否有来自客户端的数据
                client_socket.settimeout(0.1)  # 设置短暂超时
                try:
                    request = client_socket.recv(1024).decode()
                    if request.startswith("SET_THRESHOLD"):
                        new_threshold = request.split(":")[1]
                        self.set_threshold(new_threshold)
                except socket.timeout:
                    pass  # 没有接收到数据，继续下一次循环
            except Exception as e:
                print(f"处理客户端请求时出错: {e}")
                break
        client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"接收到来自 {addr} 的连接")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

if __name__ == '__main__':
    server = RaspberryPiServer('127.0.0.1', 6958)
    server.start()
