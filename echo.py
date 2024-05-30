import os
import socket
import threading
import logging


IP = '127.0.0.1'
PORT = 65432
MAX_PACKET = 4096
# Configuration for logging
LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | ECHO |  %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_FILE = 'TorNetwork.log'


# Function to handle client connections
def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")
    with client_socket:
        while True:
            # Receive data from the client
            data = client_socket.recv(MAX_PACKET)
            if not data:
                break
            print(f"Received {data.decode()} from {client_address}")
            logging.debug(f'received {data} from {client_address}')
            # Echo the data back to the client
            logging.debug(f'sending {data} to {client_address}')
            client_socket.sendall(data)

    print(f"Connection from {client_address} closed")


def start_server(host=IP, port=PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            # Create a new thread to handle the client connection
            logging.debug(f'received new connection from {client_address}')
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server shutting down")
    finally:
        server_socket.close()


if __name__ == "__main__":
    logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format=LOG_FORMAT)
    start_server()
