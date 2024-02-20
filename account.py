import enum

class Status(enum.Enum):
    OFFLINE = "Offline"
    ONLINE = "Online"
    AWAY = "Away"

class Account:
    def __init__(self, accUsername="spaceHolder", status=Status.OFFLINE):
        self.accUsername = accUsername
        self.inbox = {}
        self.status = status

