import socket
import threading

import customtkinter as ctk

from config import (
    APP_TITLE,
    CARD_COLOR,
    CORNER_RADIUS,
    GAME_PORT,
    MENU_HEIGHT,
    MENU_WIDTH,
    MUTED_TEXT_COLOR,
    PADDING,
    POLL_INTERVAL,
    RED_COLOR,
    TEXT_COLOR,
    TEXT_FONT,
    TITLE_FONT,
    YELLOW_COLOR,
)
from discovery import broadcast_until, get_computer_name
from network import prepare_connection
from ui import make_button, open_screen, set_status, show_game


def get_local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        try:
            udp_socket.connect(("8.8.8.8", 80))
            return udp_socket.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def open_listening_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", GAME_PORT))
        server_socket.listen(1)
        server_socket.setblocking(False)
    except OSError:
        server_socket.close()
        return None
    return server_socket


def show_server_screen(root, go_back):
    frame = open_screen(root, APP_TITLE + " — сервер", MENU_WIDTH, MENU_HEIGHT)
    title = ctk.CTkLabel(frame, text="Создание игры", font=TITLE_FONT, text_color=TEXT_COLOR)
    title.pack()
    card = ctk.CTkFrame(frame, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
    card.pack(fill="both", expand=True, pady=PADDING)
    status = ctk.CTkLabel(card, text="", font=TEXT_FONT)
    status.pack(pady=(30, 10))
    ip_label = ctk.CTkLabel(card, text="Ваш IP: " + get_local_ip(), font=TITLE_FONT, text_color=TEXT_COLOR)
    ip_label.pack()
    name_label = ctk.CTkLabel(
        card,
        text="Имя компьютера: " + get_computer_name(),
        font=TEXT_FONT,
        text_color=TEXT_COLOR,
    )
    name_label.pack(pady=(4, 0))
    hint = ctk.CTkLabel(
        card,
        text="Соперник нажимает «Клиент» и выбирает эту игру в списке",
        font=TEXT_FONT,
        text_color=MUTED_TEXT_COLOR,
    )
    hint.pack(pady=10)
    server_socket = open_listening_socket()
    stop_event = threading.Event()
    back_button = make_button(frame, "Назад", lambda: stop_and_go_back(server_socket, stop_event, go_back))
    back_button.pack()
    if server_socket is None:
        set_status(status, "Порт " + str(GAME_PORT) + " занят, попробуйте ещё раз", RED_COLOR)
        return
    set_status(status, "Жду соперника…", YELLOW_COLOR)
    threading.Thread(target=broadcast_until, args=(stop_event,), daemon=True).start()
    check_for_client(root, status, server_socket, stop_event, go_back)


def check_for_client(root, status, server_socket, stop_event, go_back):
    if not status.winfo_exists():
        stop_server(server_socket, stop_event)
        return
    try:
        connection, address = server_socket.accept()
    except BlockingIOError:
        root.after(POLL_INTERVAL, check_for_client, root, status, server_socket, stop_event, go_back)
        return
    except OSError:
        stop_server(server_socket, stop_event)
        set_status(status, "Ошибка сервера, вернитесь назад", RED_COLOR)
        return
    stop_server(server_socket, stop_event)
    prepare_connection(connection)
    show_game(root, connection, True, go_back)


def stop_server(server_socket, stop_event):
    stop_event.set()
    if server_socket is not None:
        server_socket.close()


def stop_and_go_back(server_socket, stop_event, go_back):
    stop_server(server_socket, stop_event)
    go_back()
