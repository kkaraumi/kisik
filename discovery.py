import socket
import time

from config import BROADCAST_ADDRESS, DISCOVERY_MESSAGE, DISCOVERY_PORT


def broadcast_until(stop_event):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while not stop_event.is_set():
            send_announcement(udp_socket)
            stop_event.wait(1)


def send_announcement(udp_socket):
    try:
        udp_socket.sendto(DISCOVERY_MESSAGE.encode(), (BROADCAST_ADDRESS, DISCOVERY_PORT))
    except OSError:
        pass


def find_server(timeout):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind(("", DISCOVERY_PORT))
            return wait_for_announcement(udp_socket, timeout)
    except OSError:
        return None


def wait_for_announcement(udp_socket, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        udp_socket.settimeout(max(deadline - time.time(), 0.1))
        try:
            data, address = udp_socket.recvfrom(1024)
        except socket.timeout:
            return None
        if data.decode(errors="ignore") == DISCOVERY_MESSAGE:
            return address[0]
    return None
