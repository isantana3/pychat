"""Configuração do servidor"""
import sqlite3
import socket
import random
import threading
from pychat.Server.ServerSocket import ServerSocket
from pychat import utils


class ServerRedirect(threading.Thread):
    """
    Suporta gerenciamento de conexões de servidor.

    Attributes:
            connections (list): Lista de objetos ServerSocket que representam as conexões ativas.
            host (str): Endereço IP do socket de escuta.
            port (int): Número da porta do socket de escuta.
    """

    def __init__(self, host, port):
        super().__init__()
        self.servers = []
        self.host = host
        self.port = port

    def _get_port(self):
        """
        Verifica no banco de dados se existe alguma porta com somente 1 conexão, caso exista,
        retorna a porta encontrada, caso contrário, sorteia uma nova prota.

        """
        sqliteConnection = sqlite3.connect('.port_alocation.db')
        cursor = sqliteConnection.cursor()
        select_disponible_connection = (
            '''SELECT id FROM tbl_ports WHERE connections<2 LIMIT 1;'''
        )
        select_all_connections = '''SELECT id FROM tbl_ports;'''
        cursor.execute(select_disponible_connection)
        query = cursor.fetchall()
        if len(query) != 0:
            # é chato, mas basicamente a query é isso: [(port,)], então precisa acessar a primeira posição da query e o primeiro elemento da tupla
            port = query[0][0]
            new_connection = False
            print(f'Novo Usuário redirecionado para a sala: {port}')
        else:
            cursor.execute(select_all_connections)
            query = cursor.fetchall()
            port = random.choice([i for i in range(1026, 9999) if i not in query])
            new_connection = True
            print(f'Sala {port} criada para novo usuário')

        cursor.close()
        sqliteConnection.close()
        return new_connection, port

    def run(self):
        """
        Cria o socket de escuta. O socket de escuta usará a opção SO_REUSEADDR para
        permitir a ligação a um endereço de socket usado anteriormente. Este é um aplicativo de pequena escala que
        suporta apenas uma conexão em espera por vez.
        Para cada nova conexão, um thread ServerSocket é iniciado para facilitar a comunicação com
        aquele cliente específico. Todos os objetos ServerSocket são armazenados no atributo connections.
        """
        # AF_INET: address family, for IP networking
        # SOCK_STREAM: socket type, for reliable flow-controlled data stream
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(1)
        print(f'Ouvindo em {sock.getsockname()}')

        # listen for new client connections
        while True:
            # new connection
            sc, sockname = sock.accept()
            print(f'Nova conexao de {sc.getpeername()} para {sc.getsockname()}')

            new_connection, new_port = self._get_port()
            sc.sendall(f'{new_port}'.encode('ascii'))
            if new_connection:
                server = Server(self.host, new_port)
                server.start()
                self.servers.append(server)

            # add thread to active connections
            print(f'Pronto para receber mensagens de {sc.getpeername()}')


class Server(threading.Thread):
    """
    Suporta gerenciamento de conexões de servidor.

    Attributes:
            connections (list): Lista de objetos ServerSocket que representam as conexões ativas.
            host (str): Endereço IP do socket de escuta.
            port (int): Número da porta do socket de escuta.
    """

    def __init__(self, host, port):
        super().__init__()
        # list of server sockets objects representing active client connections
        self.connections = []
        self.host = host
        self.port = port

    def _insert_port_connection(self, port: int):
        """
        Insere uma nova porta no banco de dados e inicializa como tendo somente 1 conexão

        Atributes:
            port: porta da conexão, varia de 1001 a 9999
        """

        sqliteConnection = sqlite3.connect('.port_alocation.db')
        cursor = sqliteConnection.cursor()
        insert_connection = (
            f'''INSERT INTO tbl_ports (id, connections) VALUES ({port},1);'''
        )
        cursor.execute(insert_connection)
        sqliteConnection.commit()
        cursor.close()
        sqliteConnection.close()
        return cursor.rowcount

    def _update_connection(self, port: int, conn: int):
        """
        Atualzia a quantidade de conexões numa porta, a quantidade atualizada de conexões pode ser 1 ou 2

        Atributes:
            port: porta da conexão, varia de 1001 a 9999
            port: Número de conexões na porta (1 ou 2)
        """
        sqliteConnection = sqlite3.connect('.port_alocation.db')
        cursor = sqliteConnection.cursor()
        update_connection = (
            f'''UPDATE tbl_ports SET connections = {conn} WHERE id = {port};'''
        )
        cursor.execute(update_connection)
        sqliteConnection.commit()
        cursor.close()
        sqliteConnection.close()
        return cursor.rowcount

    def _delete_connection(self, port: int):
        """
        Deleta porta no banco de dados

        Atributes:
            port: porta da conexão, varia de 1001 a 9999
        """

        sqliteConnection = sqlite3.connect('.port_alocation.db')
        cursor = sqliteConnection.cursor()
        delete_connection = f'''DELETE FROM tbl_ports WHERE id = {port};'''
        cursor.execute(delete_connection)
        sqliteConnection.commit()
        cursor.close()
        sqliteConnection.close()
        print('DELETE')
        return cursor.rowcount

    def run(self):
        """
        Cria o socket de escuta. O socket de escuta usará a opção SO_REUSEADDR para
        permitir a ligação a um endereço de socket usado anteriormente. Este é um aplicativo de pequena escala que
        suporta apenas uma conexão em espera por vez.
        Para cada nova conexão, um thread ServerSocket é iniciado para facilitar a comunicação com
        aquele cliente específico. Todos os objetos ServerSocket são armazenados no atributo connections.
        """
        # AF_INET: address family, for IP networking
        # SOCK_STREAM: socket type, for reliable flow-controlled data stream
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(1)
        print(f'Ouvindo em {sock.getsockname()}')

        # listen for new client connections
        while True:
            # new connection
            sc, sockname = sock.accept()
            if not self._update_connection(self.port, 2):
                self._insert_port_connection(self.port)
            print(f'Nova conexao de {sc.getpeername()} para {sc.getsockname()}')
            # new thread
            server_socket = ServerSocket(sc=sc, sockname=sockname, server=self)
            # start thread
            server_socket.start()

            # add thread to active connections
            self.connections.append(server_socket)
            print(f'Pronto para receber mensagens de {sc.getpeername()}')

    def broadcast(self, message, source):
        """
        Envia uma mensagem para todos os clientes conectados,
        exceto a origem da mensagem.

        Args:
                message (str): Mensagem a ser transmitida.
                source (tuple): Endereço de socket do cliente de origem.
        """
        for connection in self.connections:
            if connection.sockname != source:
                connection.send(message)

    def remove_connection(self, connection):
        """
        Remove uma thread ServerSocket do atributo connections.

        Args:
                connection (ServerSocket): Thread ServerSocket a ser removida.
        """
        if len(self.connections) > 1:
            self._update_connection(self.port, 1)
        else:
            self._delete_connection(self.port)
        self.connections.remove(connection)
