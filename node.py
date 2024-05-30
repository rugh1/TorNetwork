import logging
import socket
from threading import Thread
import time
import sys

QUEUE_SIZE = 10
IP = '127.0.0.1'
PORT = int(sys.argv[1])
DIRECTORY_IP = ('127.0.0.1', 22353)
MAX_PACKET = 4096

# Configuration for logging
LOG_FORMAT = f'%(levelname)s | %(asctime)s | %(processName)s | NODE{PORT} |  %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_FILE = 'TorNetwork.log'


def handle_connection(client_socket, client_address):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    try:
        print(client_address[0] + ':' + str(client_address[1]) + ' is connected')

        data = client_socket.recv(MAX_PACKET).decode()  # protocol CONNECT PORT_TO_SEND
        print(data)
        logging.debug(f'from {client_address} received {data}')
        port_to_send = int(data.split()[1])
        forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            forward_socket.connect(('127.0.0.1', port_to_send))
            logging.debug(f'connected to {port_to_send}')
            client_socket.send('OK'.encode())
            logging.debug(f'sent OK back to {client_address}')
            while True:
                data = client_socket.recv(MAX_PACKET)  # msg from before
                logging.debug(f'from {client_address} received {data.decode()}')
                forward_socket.send(data)  # forward to next
                logging.debug(f'sent encoded {data.decode()} to {port_to_send}')
                ret = forward_socket.recv(MAX_PACKET)
                logging.debug(f'from {port_to_send} received {ret.decode()}')
                client_socket.send(ret)  # return answer
                logging.debug(f'returned encoded {ret.decode()} to {client_address}')
        except socket.error as err:
            print('received socket exception - ' + str(err))
            logging.debug(f'received exception {str(err)}')
        finally:
            forward_socket.close()
            logging.debug(f'closed socket connected to {port_to_send}')
            client_socket.close()
            logging.debug(f'closed socket connected to {client_address}')
        print(port_to_send)
        print(data)

    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        client_socket.close()


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
