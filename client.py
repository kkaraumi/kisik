import socket
import sys
import tkinter as tk

ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"


def next_picture():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(2)
            client_socket.connect((ip, 5050))
            client_socket.sendall("next".encode())
    except OSError:
        print("сервер недоступен")


root = tk.Tk()
root.title("Пульт")
button = tk.Button(root, text="Следующая", command=next_picture, font=("Arial", 20), padx=20, pady=10)
button.pack(padx=20, pady=20)
root.mainloop()