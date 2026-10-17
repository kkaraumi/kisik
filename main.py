import customtkinter as ctk

import client
import server
from config import (
    APP_TITLE,
    APP_VERSION,
    BACKGROUND_COLOR,
    CARD_COLOR,
    CARD_HOVER_COLOR,
    CORNER_RADIUS,
    LABEL_FONT,
    MENU_HEIGHT,
    MENU_WIDTH,
    MUTED_TEXT_COLOR,
    PADDING,
    TEXT_COLOR,
    TEXT_FONT,
    TITLE_FONT,
)
from ui import open_screen


def show_role_screen(root):
    frame = open_screen(root, APP_TITLE, MENU_WIDTH, MENU_HEIGHT)
    title = ctk.CTkLabel(frame, text=APP_TITLE, font=TITLE_FONT, text_color=TEXT_COLOR)
    title.pack()
    subtitle = ctk.CTkLabel(
        frame,
        text="Игра для двоих по локальной сети",
        font=TEXT_FONT,
        text_color=MUTED_TEXT_COLOR,
    )
    subtitle.pack()
    cards = ctk.CTkFrame(frame, fg_color="transparent")
    cards.pack(fill="both", expand=True, pady=PADDING)
    cards.rowconfigure(0, weight=1)
    cards.columnconfigure((0, 1), weight=1, uniform="card")
    make_role_card(cards, 0, "Сервер", "Создаёт новую игру", lambda: start_server(root))
    make_role_card(cards, 1, "Клиент", "Ищет игры в сети", lambda: start_client(root))
    version = ctk.CTkLabel(frame, text=APP_VERSION, font=LABEL_FONT, text_color=MUTED_TEXT_COLOR)
    version.pack()


def make_role_card(parent, column, title, caption, command):
    card = ctk.CTkFrame(parent, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS, cursor="hand2")
    card.grid(row=0, column=column, sticky="nsew", padx=PADDING // 2)
    title_label = ctk.CTkLabel(card, text=title, font=TITLE_FONT, text_color=TEXT_COLOR)
    title_label.pack(expand=True, anchor="s", pady=(0, 4))
    caption_label = ctk.CTkLabel(
        card,
        text=caption,
        font=TEXT_FONT,
        text_color=MUTED_TEXT_COLOR,
        wraplength=200,
    )
    caption_label.pack(expand=True, anchor="n", padx=PADDING)
    for widget in [card, title_label, caption_label]:
        widget.bind("<Button-1>", lambda event: command())
        widget.bind("<Enter>", lambda event: card.configure(fg_color=CARD_HOVER_COLOR))
        widget.bind("<Leave>", lambda event: card.configure(fg_color=CARD_COLOR))


def start_server(root):
    server.show_server_screen(root, lambda: show_role_screen(root))


def start_client(root):
    client.show_client_screen(root, lambda: show_role_screen(root))


def main():
    ctk.set_appearance_mode("dark")
    root = ctk.CTk(fg_color=BACKGROUND_COLOR)
    root.resizable(False, False)
    show_role_screen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
