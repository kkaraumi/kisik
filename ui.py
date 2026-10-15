import tkinter as tk

import customtkinter as ctk

from config import (
    ACCENT_COLOR,
    ACCENT_HOVER_COLOR,
    APP_TITLE,
    AXIS_SIZE,
    BACKGROUND_COLOR,
    BOARD_SIZE,
    CARD_COLOR,
    CARD_HOVER_COLOR,
    CELL_SIZE,
    COLUMN_LETTERS,
    CORNER_RADIUS,
    GAME_HEIGHT,
    GAME_WIDTH,
    GREEN_COLOR,
    GRID_COLOR,
    LABEL_FONT,
    MISS_COLOR,
    MUTED_TEXT_COLOR,
    PADDING,
    POLL_INTERVAL,
    RED_COLOR,
    TEXT_COLOR,
    TEXT_FONT,
    TITLE_FONT,
    YELLOW_COLOR,
)
from game import Board
from network import close_connection, send_line, start_receiving


def get_scaling(root):
    return ctk.ScalingTracker.get_window_scaling(root)


def center_window(root, width, height):
    scaling = get_scaling(root)
    x = int((root.winfo_screenwidth() - width * scaling) / 2)
    y = int((root.winfo_screenheight() - height * scaling) / 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def open_screen(root, title, width, height):
    for widget in root.winfo_children():
        widget.destroy()
    root.title(title)
    center_window(root, width, height)
    frame = ctk.CTkFrame(root, fg_color=BACKGROUND_COLOR, corner_radius=0)
    frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
    return frame


def make_button(parent, text, command, primary=True):
    color = ACCENT_COLOR if primary else CARD_COLOR
    hover_color = ACCENT_HOVER_COLOR if primary else CARD_HOVER_COLOR
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        font=TEXT_FONT,
        height=40,
        corner_radius=CORNER_RADIUS,
        fg_color=color,
        hover_color=hover_color,
        text_color=TEXT_COLOR,
    )


def set_status(label, text, color):
    label.configure(text="●  " + text, text_color=color)


def show_game(root, connection, is_server, go_back):
    role = "сервер" if is_server else "клиент"
    frame = open_screen(root, APP_TITLE + " — " + role, GAME_WIDTH, GAME_HEIGHT)
    game = {
        "root": root,
        "connection": connection,
        "lines": start_receiving(connection),
        "board": Board(),
        "enemy_marks": {},
        "turn": "mine" if is_server else "theirs",
        "last_shot": None,
        "cell": round(CELL_SIZE * get_scaling(root)),
        "axis": round(AXIS_SIZE * get_scaling(root)),
        "go_back": go_back,
    }
    make_top_bar(game, frame)
    make_boards(game, frame)
    make_bottom_bar(game, frame)
    redraw(game)
    if is_server:
        update_turn(game, "Вы ходите первым, стреляйте по полю соперника")
    else:
        update_turn(game, "Соперник ходит первым")
    check_messages(game)


def make_top_bar(game, frame):
    top = ctk.CTkFrame(frame, fg_color="transparent")
    top.pack(fill="x")
    texts = ctk.CTkFrame(top, fg_color="transparent")
    texts.pack(side="left")
    game["status"] = ctk.CTkLabel(texts, text="", font=TITLE_FONT, anchor="w")
    game["status"].pack(anchor="w")
    game["info"] = ctk.CTkLabel(texts, text="", font=TEXT_FONT, text_color=MUTED_TEXT_COLOR, anchor="w")
    game["info"].pack(anchor="w")
    game["connection_label"] = ctk.CTkLabel(top, text="", font=TEXT_FONT)
    game["connection_label"].pack(side="right", anchor="n")
    set_status(game["connection_label"], "Подключено", GREEN_COLOR)


def make_boards(game, frame):
    boards = ctk.CTkFrame(frame, fg_color="transparent")
    boards.pack(pady=PADDING)
    game["own_canvas"] = make_board_card(game, boards, "Ваше поле")
    game["enemy_canvas"] = make_board_card(game, boards, "Поле соперника")
    game["enemy_canvas"].bind("<Button-1>", lambda event: on_enemy_click(game, event))


def make_board_card(game, parent, title):
    card = ctk.CTkFrame(parent, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
    card.pack(side="left", padx=PADDING // 2)
    label = ctk.CTkLabel(card, text=title, font=TEXT_FONT, text_color=TEXT_COLOR)
    label.pack(pady=(PADDING // 2, 0))
    size = game["axis"] + BOARD_SIZE * game["cell"] + 1
    canvas = tk.Canvas(card, width=size, height=size, bg=CARD_COLOR, highlightthickness=0)
    canvas.pack(padx=PADDING, pady=(0, PADDING))
    return canvas


def make_bottom_bar(game, frame):
    bottom = ctk.CTkFrame(frame, fg_color="transparent")
    bottom.pack(fill="x")
    game["replace_button"] = make_button(
        bottom,
        "Расставить заново",
        lambda: replace_ships(game),
        primary=False,
    )
    game["replace_button"].pack(side="left")
    game["menu_button"] = make_button(bottom, "Играть снова", lambda: leave_game(game))


def redraw(game):
    draw_board(game, game["own_canvas"], own_states(game["board"]))
    draw_board(game, game["enemy_canvas"], game["enemy_marks"])


def own_states(board):
    states = {}
    for cell in board.ship_cells():
        states[cell] = "ship"
    for x, y in board.shots:
        states[(x, y)] = "hit" if board.has_ship(x, y) else "miss"
    return states


def draw_board(game, canvas, states):
    canvas.delete("all")
    draw_axes(game, canvas)
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            draw_cell(game, canvas, x, y, states.get((x, y), "water"))


def draw_axes(game, canvas):
    cell = game["cell"]
    axis = game["axis"]
    for i in range(BOARD_SIZE):
        middle = axis + i * cell + cell // 2
        draw_label(canvas, middle, axis // 2, COLUMN_LETTERS[i])
        draw_label(canvas, axis // 2, middle, str(i + 1))


def draw_label(canvas, x, y, text):
    canvas.create_text(x, y, text=text, fill=MUTED_TEXT_COLOR, font=LABEL_FONT)


def draw_cell(game, canvas, x, y, state):
    cell = game["cell"]
    left = game["axis"] + x * cell
    top = game["axis"] + y * cell
    canvas.create_rectangle(left, top, left + cell, top + cell, fill=CARD_COLOR, outline=GRID_COLOR)
    if state == "ship":
        draw_square(canvas, left, top, cell, ACCENT_COLOR)
    elif state == "hit":
        draw_square(canvas, left, top, cell, RED_COLOR)
        draw_cross(canvas, left, top, cell)
    elif state == "miss":
        draw_dot(canvas, left, top, cell)


def draw_square(canvas, left, top, cell, color):
    canvas.create_rectangle(left + 3, top + 3, left + cell - 3, top + cell - 3, fill=color, outline="")


def draw_dot(canvas, left, top, cell):
    radius = cell // 9
    left_edge = left + cell // 2 - radius
    top_edge = top + cell // 2 - radius
    size = radius * 2
    canvas.create_oval(left_edge, top_edge, left_edge + size, top_edge + size, fill=MISS_COLOR, outline="")


def draw_cross(canvas, left, top, cell):
    gap = cell // 4
    canvas.create_line(left + gap, top + gap, left + cell - gap, top + cell - gap, fill=TEXT_COLOR, width=2)
    canvas.create_line(left + cell - gap, top + gap, left + gap, top + cell - gap, fill=TEXT_COLOR, width=2)


def update_turn(game, info):
    if game["turn"] == "theirs":
        game["status"].configure(text="Ход соперника", text_color=YELLOW_COLOR)
        game["enemy_canvas"].configure(cursor="arrow")
    else:
        game["status"].configure(text="Ваш ход", text_color=GREEN_COLOR)
        game["enemy_canvas"].configure(cursor="crosshair")
    game["info"].configure(text=info)


def replace_ships(game):
    game["board"].place_ships_randomly()
    redraw(game)


def lock_ships(game):
    game["replace_button"].configure(state="disabled")


def on_enemy_click(game, event):
    if game["turn"] != "mine":
        return
    x = (event.x - game["axis"]) // game["cell"]
    y = (event.y - game["axis"]) // game["cell"]
    if not is_on_board(x, y):
        return
    if (x, y) in game["enemy_marks"]:
        game["info"].configure(text="Сюда вы уже стреляли, выберите другую клетку")
        return
    game["turn"] = "waiting"
    game["last_shot"] = (x, y)
    lock_ships(game)
    send(game, f"shot {x} {y}")


def is_on_board(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE


def send(game, line):
    if not send_line(game["connection"], line):
        show_disconnected(game)


def check_messages(game):
    if not game["status"].winfo_exists() or game["turn"] == "over":
        return
    while not game["lines"].empty():
        line = game["lines"].get()
        if line is None:
            show_disconnected(game)
            return
        handle_line(game, line)
        if game["turn"] == "over":
            return
    game["root"].after(POLL_INTERVAL, check_messages, game)


def handle_line(game, line):
    parts = line.split()
    if len(parts) == 3 and parts[0] == "shot" and parts[1].isdigit() and parts[2].isdigit():
        handle_shot(game, int(parts[1]), int(parts[2]))
    elif len(parts) == 2 and parts[0] == "result":
        handle_result(game, parts[1])


def handle_shot(game, x, y):
    if game["turn"] != "theirs" or not is_on_board(x, y):
        return
    lock_ships(game)
    board = game["board"]
    result = board.receive_shot(x, y)
    if result == "sunk" and board.all_sunk():
        result = "win"
    redraw(game)
    send(game, "result " + result)
    if game["turn"] == "over":
        return
    if result == "win":
        finish_game(game, "Поражение", RED_COLOR, "Соперник потопил все ваши корабли")
    elif result == "miss":
        game["turn"] = "mine"
        update_turn(game, "Соперник промахнулся по " + cell_name(x, y) + ", ваш ход")
    elif result == "hit":
        update_turn(game, "Соперник попал в " + cell_name(x, y))
    else:
        update_turn(game, "Соперник потопил ваш корабль на " + cell_name(x, y))


def handle_result(game, result):
    if game["turn"] != "waiting" or result not in ["miss", "hit", "sunk", "win"]:
        return
    x, y = game["last_shot"]
    game["enemy_marks"][(x, y)] = "miss" if result == "miss" else "hit"
    redraw(game)
    if result == "win":
        finish_game(game, "Победа!", GREEN_COLOR, "Вы потопили все корабли соперника")
    elif result == "miss":
        game["turn"] = "theirs"
        update_turn(game, cell_name(x, y) + ": мимо, ход переходит к сопернику")
    elif result == "hit":
        game["turn"] = "mine"
        update_turn(game, cell_name(x, y) + ": попадание! Стреляйте ещё")
    else:
        game["turn"] = "mine"
        update_turn(game, cell_name(x, y) + ": корабль потоплен! Стреляйте ещё")


def cell_name(x, y):
    return COLUMN_LETTERS[x] + str(y + 1)


def finish_game(game, title, color, info):
    game["turn"] = "over"
    game["status"].configure(text=title, text_color=color)
    game["info"].configure(text=info)
    game["enemy_canvas"].configure(cursor="arrow")
    lock_ships(game)
    game["menu_button"].configure(text="Играть снова")
    game["menu_button"].pack(side="right")


def show_disconnected(game):
    if game["turn"] == "over":
        return
    set_status(game["connection_label"], "Соединение потеряно", RED_COLOR)
    finish_game(game, "Соперник отключился", RED_COLOR, "Игра прервана, можно начать заново")
    game["menu_button"].configure(text="Вернуться к выбору роли")


def leave_game(game):
    close_connection(game["connection"])
    game["go_back"]()
