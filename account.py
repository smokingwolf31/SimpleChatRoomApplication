import enum
import socket

class Status(enum.Enum):
    OFFLINE = "Offline"
    ONLINE = "Online"
    AWAY = "Away"

class Account:
    def __init__(self, accUsername="spaceHolder", status=Status.OFFLINE, socket=None):
        self.accUsername = accUsername
        self.inbox = {}
        self.status = status
        self.socket = socket

