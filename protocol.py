"""
Author: Rugh1
Date: 31.05.2024
Description: protocol for .7 work
"""
import socket


def send(connected_socket, msg):
    """
    Send a message over the connected socket.

    :param connected_socket: The connected socket to send the message through.
    :type connected_socket: socket.socket

    :param msg: The message to be sent.
    :type msg: str

    :return: None
    :rtype: None
    """
    # Check if the last character of the 'msg' string is a space
    if msg[-1] == ' ':
        # If the last character is a space, remove it from the 'msg' string
        msg = msg[:-1]

    # Convert the length of the 'msg' string to hexadecimal representation, excluding the '0x' prefix
    msg = hex(len(msg))[2:] + '!' + '!'.join(msg.split())

    # Encode the modified 'msg' string and send it through the 'connected_socket'
    connected_socket.send(msg.encode())


def recv(connected_socket):
    """
    Receive a message from the connected socket.

    :param connected_socket: The connected socket to receive the message from.
    :type connected_socket: socket.socket

    :return: A list containing the split components of the received message.
    :rtype: list[str]
    """
    # Receive the length of the message in hexadecimal
    length_hex = ''
    while '!' not in length_hex:
        length_hex += connected_socket.recv(1).decode()
    length_hex = length_hex[:-1]

    # Convert the length to an integer
    length = int(length_hex, 16)

    # Receive the message until the expected length is reached
    received_msg = ''
    while len(received_msg) < length:
        received_msg += connected_socket.recv(1).decode()

    # Split the received message using '!!' as the separator
    return received_msg.split('!')


if __name__ == '__main__':
    pass