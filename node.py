import logging
import socket
from threading import Thread
import time
import sys
from protocol import *

QUEUE_SIZE = 10
IP = '127.0.0.1'
PORT = int(sys.argv[1])
DIRECTORY_IP = ('127.0.0.1', 22353)
MAX_PACKET = 4096
TEST_MODE = True
# Configuration for logging
LOG_FORMAT = f'%(asctime)s | NODE{PORT} |  %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_FILE = 'TorNetwork.log'


def delay(sec):
    if TEST_MODE:
        time.sleep(sec)


def handle_connection(client_socket, client_address):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    try:
        print(client_address[0] + ':' + str(client_address[1]) + ' is connected')

        data = client_socket.recv(MAX_PACKET).decode()  # protocol CONNECT IP:PORT
        logging.debug(f'from {client_address} received {data}')
        if 'CONNECT' not in data:
            logging.debug(f'connecting to next device failed')
            client_socket.send(f'connection failed PROTOCOL NOT GOOD'.encode())
        port_to_send = data.split()[1]
        port_to_send = (port_to_send.split(':')[0], int(port_to_send.split(':')[1]))
        forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            logging.debug(f'connecting to {port_to_send}')
            forward_socket.connect(port_to_send)
            delay(0.05)
        except socket.error as err:
            logging.debug(f'connecting to {port_to_send} failed')
            client_socket.send(f'connection failed {str(err)}'.encode())
        try:
            logging.debug(f'sending OK back to {client_address}')
            client_socket.send('OK'.encode())
            delay(0.05)
            while True:
                data = client_socket.recv(MAX_PACKET)  # msg from before
                if data.decode() == '':
                    break
                logging.debug(f'from {client_address} received {data.decode()}')
                delay(0.05)
                logging.debug(f'sending encoded {data.decode()} to {port_to_send}')
                forward_socket.send(data)  # forward to next
                delay(0.05)
                ret = forward_socket.recv(MAX_PACKET)
                logging.debug(f'from {port_to_send} received {ret.decode()}')
                delay(0.05)
                logging.debug(f'returned encoded {ret.decode()} to {client_address}')
                client_socket.send(ret)  # return answer
                delay(0.05)
        except socket.error as err:
            print('received socket exception - ' + str(err))
            logging.debug(f'received exception {str(err)}')
        finally:
            forward_socket.close()
            logging.debug(f'closed socket connected to {port_to_send}')

        print(port_to_send)
        print(data)

    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        client_socket.close()
        logging.debug(f'closed socket connected to {client_address}')


def ping_directory():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(DIRECTORY_IP)
        client_socket.send(f'{PORT}'.encode())
        time.sleep(1)
        while True:
            client_socket.send('ping'.encode())
            time.sleep(1)
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    ping_thread = Thread(target=ping_directory)
    ping_thread.start()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)
        while True:
            client_socket, client_address = server_socket.accept()
            logging.debug(f'received connection from {client_address}')
            thread = Thread(target=handle_connection,
                            args=(client_socket, client_address))
            thread.start()

    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format=LOG_FORMAT)
    main()
