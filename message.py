import account

"""
Class representing a message in the system.

Attributes:
    request (str): The type of request or action associated with the message.
    text (str): The text content of the message.
    account (account.Account): The account associated with the message.
    fileData: Data associated with a file, if applicable.
    arrayToSend (list): An array of data to be sent.
    result: Result of an operation, if applicable.
    ipAddress (str): The IP address associated with the message.
    portNumber (int): The port number associated with the message.

Methods:
    withAccount: Method to associate the message with a specific account.

"""
class Message:
    def __init__(self, request="spaceHolder",text="spaceHolder", account=None, fileData=None,result=None,ipAddress="spaceHolder", portNumber=-1):
        self.request = request
        self.text = text
        self.account = account
        self.fileData = fileData
        self.arrayToSend = []
        self.result = result
        self.ipAddress = ipAddress
        self.portNumber = portNumber

    def withAccount(self, account):
        self.account=account
        return self