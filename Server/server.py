import pygame.camera
import pygame
import socket
import struct
import time
import pickle

class Server:
    camera = None
    local_address = "127.0.0.1"
    camera_feed_port = 6000

    def __init__(self):
        pygame.init()
        pygame.camera.init()
        cameras = pygame.camera.list_cameras()
        if len(cameras) > 0:
            self.camera = pygame.camera.Camera(cameras[0])

    def start(self):
        if self.camera is None:
            print("No camera was found.")
            return

        print("Server started.")
        print("Camera found.")

        while True:
            connection, address = self.listen_for_client()
            print("Connected to client " + address[0] + ".")
            self.send_camera_feed(connection)

    def listen_for_client(self):
        print("Listening for client on port " + str(self.camera_feed_port) + "...")
        camera_feed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        camera_feed_socket.bind((self.local_address, self.camera_feed_port))
        camera_feed_socket.listen(1)
        return camera_feed_socket.accept()

    def send_camera_feed(self, connection):
        self.camera.start()
        while True:
            image = self.camera.get_image()
            packet_data = pygame.image.tostring(image, "RGB")
            packet_length = struct.pack("I", len(packet_data))
            camera_width = struct.pack("I", image.get_width())
            camera_height = struct.pack("I", image.get_height())
            try:
                connection.send(packet_length)
                connection.send(camera_width)
                connection.send(camera_height)
                connection.send(packet_data)
            except (ConnectionResetError, ConnectionAbortedError):
                print("Error: Connection has been reset or aborted.")
                self.camera.stop()
                break
            time.sleep(0.032)


if __name__ == "__main__":
    server = Server()
    server.start()
