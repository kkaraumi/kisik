import queue
import socket
import threading


def prepare_connection(connection):
    connection.settimeout(None)
    connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


def send_line(connection, line):
    try:
        connection.sendall((line + "\n").encode())
        return True
    except OSError:
        return False


def receive_lines(connection, lines):
    buffer = ""
    while True:
        data = read_chunk(connection)
        if not data:
            lines.put(None)
            return
        buffer += data.decode(errors="ignore")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            lines.put(line.strip())


def read_chunk(connection):
    try:
        return connection.recv(1024)
    except OSError:
        return b""


def start_receiving(connection):
    lines = queue.Queue()
    thread = threading.Thread(target=receive_lines, args=(connection, lines), daemon=True)
    thread.start()
    return lines


def close_connection(connection):
    try:
        connection.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    connection.close()
