import enum

class Status(enum):
    OFFLINE = "Offline"
    Online = "Online"
    AWAY = "Away"

class Account:
    accUsername = ""
    inbox = {}
    status = Status.OFFLINE

