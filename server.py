from socket import *
import pickle
import threading
import requests
import account
import message as msg
import sys


userBase = []
userBaseLock = threading.Lock()

currentGroups = {}

requests = ["SignUp*******","LogIn********","ConnectToAcc*", "MsgOfflineAcc","WhoIsOnline**","LogOut*******", "DoesUserExist", "IsUserOnline*", "DoesGroupExist", "AddToGroup***","SendToGroup**"]

"""
    Checks if a user with the given username already exists.

    Parameters:
        userName (str): The username to check.

    Returns:
        bool: True if the user already exists, False otherwise.
"""
def alreadyAUser(userName) -> bool:
    result = False
    for currentUser in userBase:
        if(currentUser.accUsername == userName):
            result = True
            break
    return result

"""
    Retrieves an account object based on the given username.

    Parameters:
        userName (str): The username associated with the account.

    Returns:
        account.Account: The account object.
"""
def getAccount(userName) -> account.Account:
    result = account.Account()
    for currentUser in userBase:
        if(currentUser.accUsername == userName):
            result = currentUser
    return result

"""
    Updates the userBase list with the information from the given user.

    Parameters:
        userToUpdate (account.Account): The user object with updated information.
"""
def updateUserBase(userToUpdate):
    for currentUser in userBase:
        if (currentUser.accUsername == userToUpdate.accUsername):
            currentUser.status = userToUpdate.status
            currentUser.privateInbox = userToUpdate.privateInbox
            currentUser.groupInbox = userToUpdate.groupInbox
            currentUser.address = userToUpdate.address
            currentUser.port = userToUpdate.port
            break

"""
    Handles the sign-up process for a new user.

    Parameters:
        clientSocket (socket): The client socket.
        messageRecieved (message.Message): The message object received from the client.
        clientAddr (tuple): The client's address.
""" 
def signUp(clientSocket, messageRecieved, clientAddr):
    username = messageRecieved.text[:messageRecieved.text.index(" ")]
    password = messageRecieved.text[messageRecieved.text.index(" ")+1:]
    if(not alreadyAUser(username)):
        user = account.Account()
        user.accUsername = username
        user.password = password
        user.status = account.Status.ONLINE
        user.address, user.port = clientAddr
        print("User: " + user.accUsername + " " +user.address+ " joined")
        user.port = 16000 + len(userBase)
        with userBaseLock:
            userBase.append(user)
        messageToSend = msg.Message().withAccount(user)
        clientSocket.sendall(pickle.dumps(messageToSend))
    else:
        clientSocket.sendall(pickle.dumps(msg.Message().withAccount(account.Account())))

"""
    Handles the log-in process for an existing user.

    Parameters:
        clientSocket (socket): The client socket.
        messageRecieved (message.Message): The message object received from the client.
        clientAddr (tuple): The client's address.
"""
def logIn(clientSocket, messageRecieved, clientAddr):
    accUsername = messageRecieved.text[:messageRecieved.text.index(" ")]
    password = messageRecieved.text[messageRecieved.text.index(" ")+1:]
    if (alreadyAUser(accUsername)):
        user = getAccount(accUsername)
        if user.password == password:
            if(user.status == account.Status.OFFLINE):
                user.status = account.Status.ONLINE
                user.address, _ = clientAddr
                clientSocket.sendall(pickle.dumps(msg.Message().withAccount(user)))
                updateUserBase(user)
            else:
                user.status = account.Status.AWAY
                clientSocket.sendall(pickle.dumps(msg.Message().withAccount(user)))
            return
    clientSocket.sendall(pickle.dumps(msg.Message().withAccount(account.Account())))

"""
    Handles the process of connecting to another user.

    Parameters:
        clientSocket (socket): The client socket.
        messageRecieved (message.Message): The message object received from the client.
"""
def connectToAcc(clientSocket, messageRecieved):
    messageToSend   = msg.Message()
    accUsername = messageRecieved.text  
    accToConnectTo = getAccount(accUsername)
    messageToSend.ipAddress = accToConnectTo.address
    messageToSend.portNumber = accToConnectTo.port
    clientSocket.sendall(pickle.dumps(messageToSend))

"""
    Handles sending messages to offline users.

    Parameters:
        clientSocket (socket): The client socket.
        messageRecieved (message.Message): The message object received from the client.
"""
def sendMsgToOfflineAcc(clientSocket, messageRecieved):
    accNamesAndMessage = messageRecieved.text
    accUsernameToSendFrom = accNamesAndMessage[:accNamesAndMessage.index(' ')]
    accNamesAndMessage = accNamesAndMessage[accNamesAndMessage.index(' ')+1:]
    accUsernameToSendTo = accNamesAndMessage[:accNamesAndMessage.index(' ')]
    actualMessage = accNamesAndMessage[accNamesAndMessage.index(' ')+1:]
    accToConnectTo = getAccount(accUsernameToSendTo)
    accToConnectTo.privateInbox.setdefault(accUsernameToSendFrom, [0]).append(accUsernameToSendFrom + ": " + actualMessage)
    accToConnectTo.privateInbox[accUsernameToSendFrom][0] = 1 + accToConnectTo.privateInbox[accUsernameToSendFrom][0]
    updateUserBase(accToConnectTo)

"""
    Handles the process of listing online users.

    Parameters:
        clientSocket (socket): The client socket.
        messageRecieved (message.Message): The message object received from the client.
"""
def whoIsOnline(clientSocket, messageRecieved):
    messageTosend = msg.Message()
    messageTosend.arrayToSend = [user.accUsername for user in userBase if user.status == account.Status.ONLINE]
    clientSocket.sendall(pickle.dumps(messageTosend))

"""
    Handles the log-out process for a user.

    Parameters:
        clientSocket (socket): The client socket.
        messageSent (message.Message): The message object sent from the client.
"""
def logOut(clientSocket, messageSent):
    user = messageSent.account
    user.address = ""
    user.currentlyInbox = None
    user.status = account.Status.OFFLINE
    updateUserBase(user)
    clientSocket.close()

"""
    Handles sending a message to a group.

    Parameters:
        groupName (str): The name of the group.
        sender (str): The sender of the message.
        actualMessage (str): The content of the message.
"""
def sendMessageToGroup(groupName, sender, actualMessage):
    groupMembers = currentGroups[groupName]
    messageToSend = msg.Message()
    for currentMember in groupMembers:
        if currentMember == sender:
            continue
        currentMemberAcc = getAccount(currentMember)
        if currentMemberAcc.status == account.Status.ONLINE:
            messageToSend.text = "Group** " + sender + " " + groupName + " " + actualMessage
            socketToMember = socket(AF_INET, SOCK_DGRAM)
            socketToMember.connect((currentMemberAcc.address, currentMemberAcc.port))
            socketToMember.sendall(pickle.dumps(messageToSend))
        else:
            currentMemberAcc.groupInbox.setdefault(groupName, [0]).append(sender+": "+actualMessage)
            currentMemberAcc.groupInbox[groupName][0] = 1 + currentMemberAcc.groupInbox[groupName][0] 
            updateUserBase(currentMemberAcc)

"""
    Handles the communication with a client.

    Parameters:
        clientSocket (socket): The client socket.
        clientAddr (tuple): The client's address.
"""
def clientHandler(clientSocket, clientAddr):
    while True:
        messageRecieved = pickle.loads(clientSocket.recv(4028)) 
        message = messageRecieved.request

        # Sign Up
        if (message == requests[0]):
            signUp(clientSocket, messageRecieved, clientAddr)

        # Log In
        elif (message == requests[1]):
            logIn(clientSocket, messageRecieved, clientAddr)
        
        #Connect with another user
        elif (message == requests[2]):
            connectToAcc(clientSocket, messageRecieved)

        #Send messages to offline users 
        elif (message == requests[3]):
            sendMsgToOfflineAcc(clientSocket, messageRecieved)

        # List online users
        elif (message == requests[4]):
            whoIsOnline(clientSocket, messageRecieved)

        # Log Out
        elif (message == requests[5]):
            logOut(clientSocket, messageRecieved)
            break

        # Does this user exit
        elif (message == requests[6]):
            messageToSend = msg.Message()
            messageToSend.result = alreadyAUser(messageRecieved.text)
            clientSocket.sendall(pickle.dumps(messageToSend))


        # Is This User Online
        elif (message == requests[7]):
            userName = messageRecieved.text
            accToCheck = getAccount(userName)
            messageToSend = msg.Message()
            if accToCheck.status == account.Status.ONLINE:
                messageToSend.result = True
                clientSocket.sendall(pickle.dumps(messageToSend))
            else:
                messageToSend.result = False
                clientSocket.sendall(pickle.dumps(messageToSend))

        # Does the group exist
        elif (message == requests[8]):
            messageToSend = msg.Message()
            if currentGroups.get(messageRecieved.text) is None:
                messageToSend.result = False
            else:
                messageToSend.result = True
            clientSocket.sendall(pickle.dumps(messageToSend))
            
        # Add member to group
        elif (message == requests[9]):
            accnameToAdd = messageRecieved.text
            groupName = accnameToAdd[:accnameToAdd.index(" ")]
            accnameToAdd = accnameToAdd[accnameToAdd.index(" ")+1:]
            currentGroups.setdefault(groupName, []).append(accnameToAdd)

        # Send message to group
        elif (message == requests[10]):
            actualMessage = messageRecieved.text
            groupName = actualMessage[:actualMessage.index(" ")]
            actualMessage = actualMessage[actualMessage.index(" ")+1:]
            sender = actualMessage[:actualMessage.index(" ")]
            actualMessage = actualMessage[actualMessage.index(" ")+1:]
            sendMessageToGroup(groupName, sender, actualMessage)
            

def main():
    portNumber = int(sys.argv[1])
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',portNumber))
    serverSocket.listen(1) 

    while True:
        clientSocket, clientAddr = serverSocket.accept()
        clientHandlerThread = threading.Thread(target=clientHandler, args=(clientSocket,clientAddr))
        clientHandlerThread.start()

if __name__ == "__main__":
    main()
