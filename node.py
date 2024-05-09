import socket
from threading import Thread
import time

QUEUE_SIZE = 1012
IP = '127.0.0.1'
PORT = int(input("enter port for node:"))
DIRECTORY_IP = ('127.0.0.1', 25050)


def ping_directory():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(DIRECTORY_IP)
        client_socket.send(f'{PORT}'.encode())
        time.sleep(1)
        while True:
            client_socket.send('ping'.encode())
            print('ping')
            time.sleep(1)
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    ping_directory()
    ping_thread = Thread(target=ping_directory)
    ping_thread.start()


if __name__ == "__main__":
    # Call the main handler function
    main()
