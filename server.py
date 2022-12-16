"""Inicialização do servidor e sua interface GUI"""
import os
import sqlite3
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
    server = Server.ServerRedirect(host, 1025)
    server.start()

    exit = threading.Thread(target=utils.exit, args=(server,))
    exit.start()


if __name__ == "__main__":
    try:
        sqliteConnection = sqlite3.connect('.port_alocation.db')
        sqlite_drop_table = '''DROP table IF EXISTS tbl_ports;'''
        sqlite_create_table_query = '''CREATE TABLE tbl_ports (
                                    id INTEGER PRIMARY KEY,
                                    connections INTEGER NOT NULL);'''

        cursor = sqliteConnection.cursor()
        print('Preparando Configurações de banco de dados...')
        cursor.execute(sqlite_drop_table)
        cursor.execute(sqlite_create_table_query)
        sqliteConnection.commit()

        cursor.close()

    except sqlite3.Error as error:
        print("Erro ao preparar o banco de dados ", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('Banco de dados configurado!')

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
