import queue
import socket
import threading

import customtkinter as ctk

from config import (
    APP_TITLE,
    CARD_COLOR,
    CONNECT_TIMEOUT,
    CORNER_RADIUS,
    GAME_PORT,
    GREEN_COLOR,
    MENU_HEIGHT,
    MENU_WIDTH,
    MUTED_TEXT_COLOR,
    PADDING,
    POLL_INTERVAL,
    RED_COLOR,
    SEARCH_TIMEOUT,
    TEXT_COLOR,
    TEXT_FONT,
    TITLE_FONT,
    YELLOW_COLOR,
)
from discovery import find_servers
from network import close_connection, prepare_connection
from ui import make_button, open_screen, set_status, show_game


def connect_to_server(ip):
    try:
        connection = socket.create_connection((ip, GAME_PORT), timeout=CONNECT_TIMEOUT)
    except (OSError, ValueError):
        return None
    prepare_connection(connection)
    return connection


def search_servers(results):
    results.put(find_servers(SEARCH_TIMEOUT))


def connect_by_ip(ip, results):
    results.put((ip, connect_to_server(ip)))


def make_bottom_buttons(root, frame, go_back):
    buttons = ctk.CTkFrame(frame, fg_color="transparent")
    buttons.pack()
    search_button = make_button(buttons, "Искать снова", lambda: show_client_screen(root, go_back), primary=False)
    search_button.pack(side="left", padx=PADDING // 2)
    manual_button = make_button(buttons, "Ввести IP вручную", lambda: show_manual_screen(root, go_back))
    manual_button.pack(side="left", padx=PADDING // 2)
    back_button = make_button(buttons, "Назад", go_back, primary=False)
    back_button.pack(side="left", padx=PADDING // 2)


def show_client_screen(root, go_back):
    frame = open_screen(root, APP_TITLE + " — клиент", MENU_WIDTH, MENU_HEIGHT)
    title = ctk.CTkLabel(frame, text="Поиск игры", font=TITLE_FONT, text_color=TEXT_COLOR)
    title.pack()
    card = ctk.CTkFrame(frame, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
    card.pack(fill="both", expand=True, pady=PADDING)
    status = ctk.CTkLabel(card, text="", font=TEXT_FONT)
    status.pack(pady=(60, 10))
    hint = ctk.CTkLabel(
        card,
        text="Оба ноутбука должны быть в одной Wi-Fi сети",
        font=TEXT_FONT,
        text_color=MUTED_TEXT_COLOR,
    )
    hint.pack()
    make_bottom_buttons(root, frame, go_back)
    set_status(status, "Ищу игры в сети…", YELLOW_COLOR)
    results = queue.Queue()
    threading.Thread(target=search_servers, args=(results,), daemon=True).start()
    check_search(root, status, results, go_back)


def check_search(root, status, results, go_back):
    if results.empty():
        root.after(POLL_INTERVAL, check_search, root, status, results, go_back)
        return
    servers = results.get()
    if not status.winfo_exists():
        return
    if servers:
        show_server_list(root, servers, go_back)
    else:
        set_status(status, "Сервер не найден", RED_COLOR)


def show_server_list(root, servers, go_back):
    frame = open_screen(root, APP_TITLE + " — клиент", MENU_WIDTH, MENU_HEIGHT)
    title = ctk.CTkLabel(frame, text="Найденные игры", font=TITLE_FONT, text_color=TEXT_COLOR)
    title.pack()
    status = ctk.CTkLabel(frame, text="", font=TEXT_FONT)
    status.pack()
    set_status(status, "Найдено игр: " + str(len(servers)) + ". Выберите свою", GREEN_COLOR)
    server_list = ctk.CTkScrollableFrame(frame, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
    server_list.pack(fill="both", expand=True, pady=PADDING)
    for ip, name in sorted(servers.items()):
        make_server_button(root, server_list, ip, name, status, go_back)
    make_bottom_buttons(root, frame, go_back)


def make_server_button(root, parent, ip, name, status, go_back):
    button = make_button(parent, name + "   •   " + ip, lambda: start_connect(root, ip, status, go_back))
    button.pack(fill="x", padx=PADDING // 2, pady=6)


def show_manual_screen(root, go_back):
    frame = open_screen(root, APP_TITLE + " — клиент", MENU_WIDTH, MENU_HEIGHT)
    title = ctk.CTkLabel(frame, text="Подключение по IP", font=TITLE_FONT, text_color=TEXT_COLOR)
    title.pack()
    card = ctk.CTkFrame(frame, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
    card.pack(fill="both", expand=True, pady=PADDING)
    hint = ctk.CTkLabel(
        card,
        text="IP-адрес показан в окне сервера",
        font=TEXT_FONT,
        text_color=MUTED_TEXT_COLOR,
    )
    hint.pack(pady=(40, 10))
    entry = ctk.CTkEntry(
        card,
        placeholder_text="Например, 192.168.0.10",
        font=TEXT_FONT,
        width=280,
        height=40,
        corner_radius=CORNER_RADIUS,
    )
    entry.pack()
    status = ctk.CTkLabel(card, text="", font=TEXT_FONT)
    status.pack(pady=10)
    buttons = ctk.CTkFrame(frame, fg_color="transparent")
    buttons.pack()
    connect_button = make_button(
        buttons,
        "Подключиться",
        lambda: start_manual_connect(root, entry, status, go_back),
    )
    connect_button.pack(side="left", padx=PADDING // 2)
    back_button = make_button(buttons, "Назад", go_back, primary=False)
    back_button.pack(side="left", padx=PADDING // 2)
    entry.bind("<Return>", lambda event: start_manual_connect(root, entry, status, go_back))
    entry.focus()


def start_manual_connect(root, entry, status, go_back):
    ip = entry.get().strip()
    if not ip:
        set_status(status, "Введите IP-адрес сервера", RED_COLOR)
        return
    start_connect(root, ip, status, go_back)


def start_connect(root, ip, status, go_back):
    set_status(status, "Подключаюсь к " + ip + "…", YELLOW_COLOR)
    results = queue.Queue()
    threading.Thread(target=connect_by_ip, args=(ip, results), daemon=True).start()
    check_connection(root, status, results, go_back)


def check_connection(root, status, results, go_back):
    if results.empty():
        root.after(POLL_INTERVAL, check_connection, root, status, results, go_back)
        return
    ip, connection = results.get()
    if not status.winfo_exists():
        if connection is not None:
            close_connection(connection)
        return
    if connection is None:
        set_status(status, "Не удалось подключиться к " + ip, RED_COLOR)
    else:
        show_game(root, connection, False, go_back)
