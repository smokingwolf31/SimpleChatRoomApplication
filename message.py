import account

class Message:
    def __init__(self, request="spaceHolder",text="spaceHolder", account=None, ipAddress="spaceHolder", portNumber=-1):
        self.request = request
        self.text = text
        self.account = account
        self.arrayToSend = []
        self.ipAddress = ipAddress
        self.portNumber = portNumber

    def withAccount(self, account):
        self.account=account
        return self