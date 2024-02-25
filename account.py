import enum

class Status(enum.Enum):
    OFFLINE = "Offline"
    ONLINE = "Online"
    AWAY = "Away"

class Account:
    def __init__(self, accUsername="spaceHolder", status=Status.OFFLINE, address="", port=-1, currentlyInbox=None):
        self.accUsername = accUsername
        self.privateInbox = {}
        self.groupInbox = {}
        self.status = status
        self.address = address
        self.port = port
        self.currentlyInbox = currentlyInbox

