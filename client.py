"""Inicialização do cliente e sua interface GUI"""
import os
import tkinter as tk
import pychat.Client as Client
from tkinter import *


BG_GRAY = "#92ccb6"
BG_COLOR = "#8e8ca3"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 12"
FONT_BOLD = "Helvetica 11 bold"

def main(host, port):
    """
    Configuração do cliente e inicializa a interface gráfica.

    Attributes:
            host (str): Endereço IP do socket.
            port (int): Número da porta do socket.
    """
    # Janela
    client = Client.Client(host, port)
    receive = client.start()
    window = tk.Tk()
    window.title('PyChat')
    window.resizable(height=False, width=False)
    window.config(background=BG_COLOR)

    # Componentes
    frm_messages = tk.Frame(master=window, bg=BG_COLOR)
    scrollbar = tk.Scrollbar(master=frm_messages)
    messages = tk.Listbox(
        master=frm_messages,
        yscrollcommand=scrollbar.set,
        fg=TEXT_COLOR,
        bg=BG_COLOR,
        borderwidth=0,
        highlightthickness=0,
        selectbackground="Red",
        highlightcolor="Green",
    )
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    client.messages = messages
    receive.messages = messages

    # Imagem & Formulario
    frm_messages.pack(fill='both', expand=True, padx=10, pady=10)

    # Input
    frm_entry = tk.Frame(master=window)
    text_input = tk.Entry(
        master=frm_entry,
        borderwidth=18,
        bg=BG_GRAY,
        fg='white',
        relief=tk.FLAT,
        font=FONT,
    )
    text_input.pack(fill=tk.BOTH, expand=True)
    text_input.bind("<Return>", lambda x: client.send(text_input))
    text_input.insert(0, "Digite algo e aperte enter.")
    text_input.bind("<Button-1>", lambda x: text_input.delete(0, tk.END))
    text_input.focus()

    # Pack ou Grid
    frm_entry.pack(fill='both')

    # Configs
    width = 450
    heigth = 550
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (heigth // 2)
    window.geometry('{}x{}+{}+{}'.format(width, heigth, x, y))

    window.mainloop()


def redirect(host, port, window):
    """
    Redireciona o usuário para a sala de bate-papo.

    Attributes:
            host (str): Endereço IP do socket.
            port (int): Número da porta do socket.
            window (tk.Frame): Objeto tk.Frame que contém a interface GUI que será destruida para criação da tela da sala de bate papo.
    """
    host = host_input.get()
    window.destroy()
    main(host, 1060)


if __name__ == "__main__":

    window = tk.Tk()
    window.title('Cliente - Conexão ao Host')
    window.resizable(height=False, width=False)
    host_input = tk.Entry(
        master=window,
        width='50',
        borderwidth=18,
        bg=BG_COLOR,
        relief=tk.FLAT,
        font=FONT,
    )
    host_input.pack(fill=tk.BOTH, expand=True)
    host_input.bind("<Return>", lambda x: redirect(host_input.get(), 1060, window))
    host_input.insert(
        0, "Host para conexão: (sugerido: localhost)"
    )
    host_input.bind("<Button-1>", lambda x: host_input.delete(0, tk.END))

    width = 450
    heigth = 50
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (heigth // 2)
    window.geometry('{}x{}+{}+{}'.format(width, heigth, x, y))

    window.mainloop()
