"""CD Chat client program"""
import logging
import sys
import socket
import selectors
import os
import fcntl

from .protocol import CDProto, CDProtoBadFormat, Message, TextMessage

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        self.name=name
        self.channel=None
        self.sel = selectors.DefaultSelector()
        self.conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.addr=('localhost',2020)
        self.CDProto=CDProto()

    def connect(self):
        """Connect to chat server and setup stdin flags."""
        self.conn.connect(self.addr)
        print(f"{self.name} Connected to {self.addr[0]} | {self.addr[1]}")
        self.sel.register(self.conn, selectors.EVENT_READ, self.read)
        regist = CDProto.register(self.name)
        self.CDProto.send_msg(self.conn,regist)



    def read(self,conn,mask):
        messageObject=self.CDProto.recv_msg(self.conn)
        logging.debug('received "%s' , messageObject.__repr__)
        print(f'{messageObject.message}')


        
        
    def got_keyboard_data(self,stdin, mask):         
        rtnmsg = stdin.read()     
        if (rtnmsg == "exit\n"):
            self.sel.unregister(self.conn)
            self.conn.close
            sys.exit(f"Ending {self.name} in {self.addr[0]} | {self.addr[1]}")
        elif (rtnmsg[:5] == "/join"):
            self.channel= rtnmsg[6:-1]
            print(f'-------{self.name} joined {self.channel}-------')
            joinMessageObject = self.CDProto.join(self.channel)
            self.CDProto.send_msg(self.conn, joinMessageObject)
        else: 
            msg = self.CDProto.message(rtnmsg[:-1],self.channel)
            self.CDProto.send_msg(self.conn, msg)



    def loop(self):
        """Loop indefinetely."""
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK) 
        self.sel.register(sys.stdin, selectors.EVENT_READ, self.got_keyboard_data) 
        while True:
            sys.stdout.write(f'> ')
            sys.stdout.flush()
            for k, mask in self.sel.select():
                callback = k.data
                callback(k.fileobj,mask)