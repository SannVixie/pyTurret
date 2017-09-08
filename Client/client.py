import pygame
import time
import socket
import threading
import sys
import struct


class Client:
    server_address = "127.0.0.1"
    camera_feed_port = 6000
    camera_feed_buffer_size = 1024*2048
    camera_resolution = (640, 480)
    window = None
    current_camera_still = None
    force_thread_quit = False

    def __init__(self):
        pygame.init()

    def start(self):
        print("Client started.")

        # Set up thread to poll server for camera data.
        camera_thread = threading.Thread(target=self.setup_camera_feed)
        camera_thread.start()

        # Create initial interface.
        display_info = pygame.display.Info()
        self.window = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
        pygame.display.set_caption("Turret Command Centre")

        while True:
            self.draw_ui()

    def draw_ui(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                self.force_thread_quit = True
                pygame.quit()
                sys.exit()

        if self.current_camera_still is not None:
            self.window.blit(self.current_camera_still, (0, 0))

        pygame.display.update()
        time.sleep(0.016)

    def setup_camera_feed(self):
        while not self.force_thread_quit:
            print("Attempting to connect to server...")
            camera_feed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                camera_feed_socket.connect((self.server_address, self.camera_feed_port))
                print("Connection successful. Receiving camera data...")
                while not self.force_thread_quit:
                    data = bytes()
                    packet_length = struct.unpack("I", camera_feed_socket.recv(4))[0]

                    while not self.force_thread_quit and len(data) < packet_length:
                        buffer_length = self.camera_feed_buffer_size
                        diff = packet_length - len(data)
                        if diff < self.camera_feed_buffer_size:
                            buffer_length = diff
                        data += camera_feed_socket.recv(buffer_length)

                    try:
                        display_info = pygame.display.Info()
                        image = pygame.image.fromstring(data, self.camera_resolution, "RGB")
                        image = pygame.transform.scale(image, (display_info.current_w, display_info.current_h))
                        self.current_camera_still = image
                    except ValueError:
                        print("Error: Camera snapshot data was corrupt or incomplete.")
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError):
                print("Error: The connection was refused or reset.")
                time.sleep(1)


if __name__ == "__main__":
    client = Client()
    client.start()
