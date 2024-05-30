import pickle
import socket
import random

QUEUE_SIZE = 10
DIRECTORY_IP = ('127.0.0.1', 22353)
MAX_PACKET = 4096
GET_LIST_CMD = 'GET LIST'
ECHO_PORT = 65432
ROUTE_SIZE = 3


def random_route(nodes_up):
    return list(map(lambda x: int(x), random.sample(nodes_up, ROUTE_SIZE)))


def get_route(server):
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
        route.append(server)
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
    client_socket.connect(('127.0.0.1', route[0]))
    for i in range(1, len(route)):
        client_socket.send(f'CONNECT {route[i]}'.encode())
        data = client_socket.recv(MAX_PACKET).decode()
        print(route[i], data)
        if data != 'OK':
            return False
    return True


def main():
    server = int(input('enter port to connect:'))
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
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if set_route(client_socket, route):
            msg = input()
            while msg != 'close':
                client_socket.send(msg.encode())
                out = client_socket.recv(MAX_PACKET).decode()
                print(out)
                msg = input()
                while msg == '':
                    msg = input()
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        client_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    main()
