import socket
from threading import Thread
import pickle

QUEUE_SIZE = 10
IP = '127.0.0.1'
PORT = 22353
NODES_UP = []
SOCKET_TIMEOUT = 3
GET_LIST_CMD = 'GET LIST'
MAX_PACKET = 4096


def handle_connection(client_socket, client_address):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    try:
        print(client_address[0] + ':' + str(client_address[1]) + ' is connected')
        data = client_socket.recv(MAX_PACKET).decode()
        if data == GET_LIST_CMD:
            nodes_up = pickle.dumps(NODES_UP)
            client_socket.send(nodes_up)
        else:
            port = data
            NODES_UP.append(port)
            print(port)
            print(NODES_UP)
            client_socket.settimeout(SOCKET_TIMEOUT)
            try:
                while True:
                    print(NODES_UP)
                    data = client_socket.recv(MAX_PACKET).decode()
                    if data == '':
                        break
                    print(NODES_UP, end="\r")
                    print('aa')
            except Exception as err:
                print(err)
            print('\n')
            NODES_UP.remove(port)
        # handle the communication

    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)
        while True:
            client_socket, client_address = server_socket.accept()

            thread = Thread(target=handle_connection,
                            args=(client_socket, client_address))
            thread.start()

    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    main()
