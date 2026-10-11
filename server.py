import os
import socket
import threading
import tkinter as tk

picture_folder = os.path.join(os.path.dirname(__file__), "pictures")
picture_files = sorted(name for name in os.listdir(picture_folder) if name.endswith(".png"))
picture_index = 0
displayed_index = -1


def run_server():
    global picture_index
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("0.0.0.0", 5050))
        server_socket.listen()
        while True:
            connection, address = server_socket.accept()
            with connection:
                command = connection.recv(1024).decode().strip()
                if command == "next" and picture_files:
                    picture_index = (picture_index + 1) % len(picture_files)


def update_picture():
    global displayed_index
    if not picture_files:
        picture_label.config(text="нет картинок")
    elif displayed_index != picture_index:
        displayed_index = picture_index
        photo = tk.PhotoImage(file=os.path.join(picture_folder, picture_files[picture_index]))
        picture_label.config(image=photo, text="")
        picture_label.image = photo
    root.after(100, update_picture)


root = tk.Tk()
root.title("Сервер")
picture_label = tk.Label(root)
picture_label.pack()
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
update_picture()
root.mainloop()