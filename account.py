import enum

class Status(enum.Enum):
    OFFLINE = "Offline"
    AWAY = "Away"
    ONLINE = "Online"

"""
    Class representing a user account.

    Attributes:
    accUsername (str): The account username.
    password (str): The account password.
    privateInbox (dict): Dictionary representing the user's private inbox.
    groupInbox (dict): Dictionary representing the user's group inbox.
    status (Status): The account status (OFFLINE, AWAY, ONLINE).
    address (str): The user's network address.
    port (int): The port used for network communication.
    currentlyInbox: A placeholder for the currently active inbox.

    Methods:
        __init__: Constructor method to initialize an Account object.
"""

class Account:
    def __init__(self, accUsername="spaceHolder",password="", status=Status.OFFLINE, address="", port=-1, currentlyInbox=None):
        self.accUsername = accUsername
        self.password = password
        self.privateInbox = {}
        self.groupInbox = {}
        self.status = status
        self.address = address
        self.port = port
        self.currentlyInbox = currentlyInbox