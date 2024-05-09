import socket
from threading import Thread
import pickle

QUEUE_SIZE = 10
IP = '127.0.0.1'
PORT = 25050
NODES_UP = []
SOCKET_TIMEOUT = 3
GET_LIST_CMD = 'GET LIST'


def recv(connected_socket):
    data = connected_socket.recv(100).decode()
    msg = data
    while data != '':
        data = connected_socket.recv(1).decode()
        msg += data
        print(msg)
    return msg


def handle_connection(client_socket, client_address):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    try:
        print(client_address[0] + ':' + str(client_address[1]) + ' is connected')
        data = client_socket.recv(100).decode()
        if data == GET_LIST_CMD:
            nodes_up = pickle.dumps(NODES_UP)
            client_socket.send(nodes_up)
        else:
            port = data
            NODES_UP.append(port)
            client_socket.settimeout(SOCKET_TIMEOUT)
            try:
                while True:
                    data = client_socket.recv(100).decode()
                    if data == '':
                        break
                    print(NODES_UP, end="\r")

            except Exception as err:
                print(err)
            print('\n')
            NODES_UP.remove(port)
        # handle the communication'

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