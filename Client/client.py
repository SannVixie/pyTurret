import pygame
import time
import socket
import threading
import sys
import struct
import pickle


class Client:
    window = None
    server_address = "127.0.0.1"
    camera_feed_port = 6000
    camera_feed_buffer_size = 1024*2048
    current_camera_still = None
    control_feed_port = 6001
    force_thread_quit = False

    def __init__(self):
        pygame.init()

    def start(self):
        print("Client started.")

        # Set up thread to receive camera data from server.
        camera_thread = threading.Thread(target=self.setup_camera_feed)
        #camera_thread.start()

        # Set up thread to send control data to server.
        control_thread = threading.Thread(target=self.setup_control_feed)
        control_thread.start()

        # Create initial interface.
        display_info = pygame.display.Info()
        #self.window = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
        self.window = pygame.display.set_mode((500, 500))
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
        time.sleep(0.032)

    def setup_control_feed(self):
        while not self.force_thread_quit:
            print("Control Feed Thread: Attempting to connect to server...")
            control_feed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                #control_feed_socket.connect((self.server_address, self.control_feed_port))
                print("Control Feed Thread: Connection successful. Listening for control data...")
                while not self.force_thread_quit:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_UP]:
                        print("UP PRESSED")
                        #packet_data = pickle.dumps(diff)
                        #packet_length = struct.pack("I", len(packet_data))
                        #control_feed_socket.send(packet_length)
                        #control_feed_socket.send(packet_data)
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError):
                print("Control Feed Thread: Error - The connection was refused or reset.")
                time.sleep(1)

    def setup_camera_feed(self):
        while not self.force_thread_quit:
            print("Camera Feed Thread: Attempting to connect to server...")
            camera_feed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                camera_feed_socket.connect((self.server_address, self.camera_feed_port))
                print("Camera Feed Thread: Connection successful. Receiving camera data...")
                while not self.force_thread_quit:
                    data = bytes()
                    packet_length = struct.unpack("I", camera_feed_socket.recv(4))[0]
                    camera_width = struct.unpack("I", camera_feed_socket.recv(4))[0]
                    camera_height = struct.unpack("I", camera_feed_socket.recv(4))[0]

                    while not self.force_thread_quit and len(data) < packet_length:
                        buffer_length = self.camera_feed_buffer_size
                        diff = packet_length - len(data)
                        if diff < self.camera_feed_buffer_size:
                            buffer_length = diff
                        data += camera_feed_socket.recv(buffer_length)

                    try:
                        display_info = pygame.display.Info()
                        image = pygame.image.fromstring(data, (camera_width, camera_height), "RGB")
                        image = pygame.transform.scale(image, (display_info.current_w, display_info.current_h))
                        self.current_camera_still = image
                    except ValueError:
                        print("Camera Feed Thread: Error - Camera snapshot data was corrupt or incomplete.")
                    except pygame.error:
                        print("Camera Feed Thread: Error - Screen object not available.")
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError):
                print("Camera Feed Thread: Error - The connection was refused or reset.")
                time.sleep(1)


if __name__ == "__main__":
    client = Client()
    client.start()
