"""Protocol for chat server - Computação Distribuida Assignment 1."""
import json
import errno
from datetime import datetime
from socket import socket



class Message:
    """Message Type."""
    def __init__(self,command):
        self.command = command


class JoinMessage(Message):
    """Message to join a chat channel."""
    def __init__(self,command,channel):
        super().__init__(command)
        self.channel = channel

    def __repr__(self):
        return f'{{"command": "join", "channel": "{self.channel}"}}'
    
class RegisterMessage(Message):
    """Message to register username in the server."""
    def __init__(self, command,username):
        super().__init__(command)
        self.username=username
        self.channel= None

    def __repr__(self):
        return f'{{"command": "register", "user": "{self.username}"}}'
        

class TextMessage(Message):
    """Message to chat with other clients."""
    def __init__(self, command,message,channel,timestamp):
        super().__init__(command)
        self.message=message
        self.channel=channel
        self.timestamp=timestamp

    def __repr__(self):
        if self.channel: 
            return f'{{"command": "message", "message": "{self.message}", "channel": "{self.channel}", "ts": {self.timestamp}}}'
        else:
            return f'{{"command": "message", "message": "{self.message}", "ts": {self.timestamp}}}'


class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""
        return RegisterMessage("Register", username)

    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""
        return JoinMessage("Join",channel)

    @classmethod
    def message(cls, message: str, channel: str = None) -> TextMessage:
        """Creates a TextMessage object."""
        return TextMessage("message: ",message,channel,int(datetime.now().timestamp()))

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        """Sends through a connection a Message object."""
        if (type(msg) is RegisterMessage):
            jsonText=json.dumps({"command": "register", "user": msg.username }).encode('utf-8')
        elif (type(msg) is JoinMessage):
            jsonText=json.dumps({"command": "join", "channel": msg.channel }).encode('utf-8')
        else:
            jsonText=json.dumps({"command": "message", "message": msg.message, "channel": msg.channel, "ts": int(datetime.now().timestamp())}).encode('utf-8')
        
        header = len(jsonText).to_bytes(2, "big")
        try:
            connection.send(header+jsonText)
        except IOError as e:
            if e.errno == errno.EPIPE:
                pass
                

       
        


    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        header = int.from_bytes(connection.recv(2),"big")
        try:
            jsonString= connection.recv(header).decode('utf-8')
            mensagem = json.loads(jsonString)
        except json.JSONDecodeError as err:
            raise CDProtoBadFormat(jsonString)

        
        if (mensagem["command"] == "register"):
            username = mensagem["user"]
            return CDProto.register(username)
        elif (mensagem["command"] == "join"):
            channel = mensagem["channel"]
            return CDProto.join(channel)
        elif (mensagem["command"] == "message"):
            msg = mensagem["message"]
            if (mensagem.get("channel")):
                channel = mensagem["channel"]
                return CDProto.message(msg,channel)
            else:
                return CDProto.message(msg)
            


class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto."""

    def __init__(self, original_msg: bytes=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")
