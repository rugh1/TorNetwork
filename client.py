"""
Author: rugh1
Date: 20.5.2024
Description: client for the TorNetwork project
"""
import pickle
import socket
import random
import logging

DIRECTORY_IP = ('127.0.0.1', 22353)
MAX_PACKET = 4096
GET_LIST_CMD = 'GET LIST'
ECHO_PORT = 65432
ROUTE_SIZE = 3

LOG_FORMAT = '%(asctime)s c| CLIENT |  %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_FILE = 'TorNetwork.log'


def random_route(nodes_up):
    """
        Generate a random route from the list of nodes.

        :param nodes_up: list of nodes available
        :return: a list representing the random route
    """
    return list(map(lambda x: x, random.sample(nodes_up, ROUTE_SIZE)))


def get_route(server):
    """
        Get the route from the directory server.

        :param server: the target server
        :return: the route or an error code
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(DIRECTORY_IP)
        client_socket.send(GET_LIST_CMD.encode())
        list_in_bytes = client_socket.recv(MAX_PACKET)
        print(list_in_bytes)
        nodes_up = pickle.loads(list_in_bytes)
        print(nodes_up)
        if len(nodes_up) < ROUTE_SIZE:
            return 1
        route = random_route(nodes_up)
        print(route)
        route.append(f'{server}')
        client_socket.close()
        return route
    except socket.error as err:
        print('received socket exception - ' + str(err))
        return 2
    except Exception as err:
        print('received  exception - ' + str(err))
        return 0
    finally:
        client_socket.close()


def set_route(client_socket, route):
    """
        Set the route for the client socket.

        :param client_socket: the client's socket
        :param route: the route to set
        :return: True if the route is set successfully, False otherwise
    """
    client_socket.connect((route[0].split(':')[0], int(route[0].split(':')[1])))
    print(route[0], 'OK')
    for i in range(1, len(route)):
        client_socket.send(f'CONNECT {route[i]}'.encode())
        data = client_socket.recv(MAX_PACKET).decode()
        print(route[i], data)
        if data != 'OK':
            return False
    return True


def main():
    """
        Main function to start the client, set the route, and handle user input.

        :return: None
    """
    server = input('enter ip:port to connect:')
    route = get_route(server)
    print(route)
    if route == 0:
        print('exception accorded while getting route')
        return

    if route == 1:
        print('amount of nodes up not enough for route size')
        return

    if route == 2:
        print('socket exception accorded while getting route')
        return
    logging.debug(f'route decided target is {server} route is {route}')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        logging.debug(f'setting route...')
        if set_route(client_socket, route):
            msg = input()
            while msg != 'close':
                client_socket.send(msg.encode())
                out = client_socket.recv(MAX_PACKET).decode()
                print(out)
                msg = input()
                while msg == '':
                    msg = input()
        else:
            print('setting route failed')
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        client_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format=LOG_FORMAT)
    main()
