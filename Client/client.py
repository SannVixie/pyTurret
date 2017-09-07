import pygame
import time
import socket
import threading
import sys


class Client:
    server_address = "127.0.0.1"
    camera_feed_port = 6000
    camera_buffer_size = 921600
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
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
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

        pygame.display.flip()

    def setup_camera_feed(self):
        while not self.force_thread_quit:
            print("Attempting to connect to server...")
            camera_feed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                camera_feed_socket.connect((self.server_address, self.camera_feed_port))
                print("Connection successful. Receiving camera data...")
                while not self.force_thread_quit:
                    data = bytes()

                    while not self.force_thread_quit:
                        buffer = camera_feed_socket.recv(1024)
                        data += buffer
                        if len(buffer) == 0:
                            print(data)
                            break

                    try:
                        pass
                        #self.current_camera_still = pygame.image.fromstring(data, self.camera_resolution, "RGB")
                    except ValueError:
                        raise
                        print("Error: Camera snapshot data was corrupt or incomplete.")
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError):
                print("Error: The connection was refused or reset.")
                time.sleep(1)


if __name__ == "__main__":
    client = Client()
    client.start()
