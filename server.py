"""Inicialização do servidor e sua interface GUI"""
import os
import threading
import pychat.Server as Server
import pychat.utils as utils
import tkinter as tk
from tkinter import *


BG_GRAY = "#92ccb6"
BG_COLOR = "#8e8ca3"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"


def start_server(host, window):
    window.destroy()
    if host == '':
        host = 'localhost'
    server = Server.ServerRedirect(host, 1060)
    server.start()

    exit = threading.Thread(target=utils.exit, args=(server,))
    exit.start()


if __name__ == "__main__":
    window = tk.Tk()
    window.title('PyChat: Servidor')
    window.resizable(height=False, width=False)
    host_input = tk.Entry(
        master=window,
        width='100',
        borderwidth=30,
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        relief=tk.FLAT,
        font=FONT,
    )

    host_input.pack(fill=tk.BOTH, expand=True)
    host_input.bind("<Return>", lambda x: start_server(host_input.get(), window))
    host_input.insert(0, "Digite o endereço de host: (sugerido localhost)")
    host_input.bind("<Button-1>", lambda x: host_input.delete(0, tk.END))

    width = 500
    heigth = 75
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (heigth // 2)
    window.geometry('{}x{}+{}+{}'.format(width, heigth, x, y))

    window.mainloop()
