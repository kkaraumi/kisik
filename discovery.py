import socket
import time

from config import BROADCAST_ADDRESS, DISCOVERY_PORT, DISCOVERY_PREFIX, GAME_PORT


def get_computer_name():
    return socket.gethostname() or "Без имени"


def make_announcement(name):
    return DISCOVERY_PREFIX + ":" + str(GAME_PORT) + ":" + name


def parse_announcement(text):
    parts = text.split(":", 2)
    if len(parts) != 3:
        return None
    if parts[0] != DISCOVERY_PREFIX or parts[1] != str(GAME_PORT):
        return None
    return parts[2] or "Без имени"


def broadcast_until(stop_event):
    message = make_announcement(get_computer_name())
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while not stop_event.is_set():
            send_announcement(udp_socket, message)
            stop_event.wait(1)


def send_announcement(udp_socket, message):
    try:
        udp_socket.sendto(message.encode(), (BROADCAST_ADDRESS, DISCOVERY_PORT))
    except OSError:
        pass


def find_servers(timeout):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind(("", DISCOVERY_PORT))
            return collect_announcements(udp_socket, timeout)
    except OSError:
        return {}


def collect_announcements(udp_socket, timeout):
    servers = {}
    deadline = time.time() + timeout
    while time.time() < deadline:
        udp_socket.settimeout(max(deadline - time.time(), 0.1))
        try:
            data, address = udp_socket.recvfrom(1024)
        except socket.timeout:
            break
        name = parse_announcement(data.decode(errors="ignore"))
        if name is not None:
            servers[address[0]] = name
    return servers
