"""CD Chat server program."""
import logging
import selectors
import socket
import json



from .protocol import CDProto, CDProtoBadFormat




logging.basicConfig(filename="server.log", level=logging.DEBUG)

class Server:
    """Chat Server process."""
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sel = selectors.DefaultSelector()
        self.sock.bind(('localhost', 2020))
        self.sock.listen(5)
        self.sel.register(self.sock,selectors.EVENT_READ,self.accept)
        print("-------SERVER CREATED-------")
        logging.debug('-------SERVER CREATED-------')
        self.listMembers = {} #channel -> connections in that channel
        self.CDProto = CDProto
        self.connectionsName = {} 


    
    def accept(self,sock, mask):
        conn, addr = sock.accept()  # Should be ready
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)

    def read(self,conn, mask):
        cabecalho = int.from_bytes(conn.recv(2),"big")
        try:
            msg  = json.loads(conn.recv(cabecalho).decode('utf-8'))
        except ValueError as e:
            msg=''
        
        if msg:
            if (msg["command"] == "register"): #REGISTAR A CONEXÃO
                username = msg["user"]
                self.connectionsName[conn] = username
                print(f'CLIENT {username} is in the server')
                self.listMembers[conn] = [None] # QUANO HÁ UM REGISTO O CLIENTE ENTRA SEMPRE NO CANAL NONE

            elif (msg["command"] == "join"): #ENTRAR NUM CANAL
                channel = msg["channel"]
                canaisAtivos = self.listMembers.get(conn) #lista
    
                if canaisAtivos==[None]:
                    self.listMembers[conn]=[msg["channel"]]
                else: 
                    canaisAtivos.append(msg["channel"])

            elif (msg["command"] == "message"): #MANDAR UMA MENSAGEM DE TEXTO
                conteudoMensagem = msg["message"]
                channel = msg["channel"]
                print(f'{channel} channel: {msg}')
                enviteString = f'{self.connectionsName[conn]} disse {conteudoMensagem}'
                messageObject = CDProto.message(enviteString,channel)
                logging.debug('received "%s' , messageObject.__repr__)
                
                for conexao, listChannel in self.listMembers.items():      
                    if (conexao != conn and channel in listChannel):
                            CDProto.send_msg(conexao,messageObject)
                
        else: 
            try:
                print('CLIENT', self.connectionsName[conn], 'left the server')
                logging.debug('CLIENT %s left the server',self.connectionsName[conn])
                del self.connectionsName[conn]   
            except KeyError as e:
                if (len(self.connectionsName)==1):
                    self.connectionsName={}
            self.sel.unregister(conn)
            conn.close
    
    def loop(self):
        """Loop indefinetely."""
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask) 