from socket import *
import pickle
import threading
import account
import message as msg


userBase = []
userBaseLock = threading.Lock()

currentGroups = {}

requests = ["SignUp*******","LogIn********","ConnectToAcc*", "MsgOfflineAcc","WhoIsOnline**","LogOut*******", "DoesUserExist", "IsUserOnline*", "DoesGroupExist", "AddToGroup***","SendToGroup**"]


def alreadyAUser(userName) -> bool:
    result = False
    for currentUser in userBase:
        if(currentUser.accUsername == userName):
            result = True
            break
    return result


def getAccount(userName) -> account.Account:
    result = account.Account()
    for currentUser in userBase:
        if(currentUser.accUsername == userName):
            result = currentUser
    return result

def updateUserBase(userToUpdate):
    for currentUser in userBase:
        if (currentUser.accUsername == userToUpdate.accUsername):
            currentUser.status = userToUpdate.status
            currentUser.privateInbox = userToUpdate.privateInbox
            currentUser.groupInbox = userToUpdate.groupInbox
            currentUser.address = userToUpdate.address
            currentUser.port = userToUpdate.port
            break
        
def signUp(clientSocket, messageRecieved):
    username = messageRecieved.text
    password = input("Enter your password: ")  # Prompt for password during sign-up
    if not alreadyAUser(username):
        user = account.Account(accUsername=username, password=password, status=account.Status.ONLINE)
        user.address, _ = clientSocket.getsockname()
        user.port = 16000 + len(userBase)
        with userBaseLock:
            userBase.append(user)
        messageToSend = msg.Message().withAccount(user)
        clientSocket.sendall(pickle.dumps(messageToSend))
    else:
        clientSocket.sendall(pickle.dumps(msg.Message().withAccount(account.Account())))

def logIn(clientSocket, messageRecieved):
    username = messageRecieved.text
    password = input("Enter your password: ")  # Prompt for password during login
    if alreadyAUser(username):
        user = getAccount(username)
        if user.password == password:  # Password validation
            user.status = account.Status.ONLINE
            user.address, _ = clientSocket.getsockname()
            clientSocket.sendall(pickle.dumps(msg.Message().withAccount(user)))
            updateUserBase(user)
        else:
            # Password incorrect
            clientSocket.sendall(pickle.dumps(msg.Message().withAccount(account.Account())))
    else:
        # User not found
        clientSocket.sendall(pickle.dumps(msg.Message().withAccount(account.Account())))

def connectToAcc(clientSocket, messageRecieved):
    messageToSend = msg.Message()
    accUsername = messageRecieved.text
    accToConnectTo = getAccount(accUsername)
    messageToSend.ipAddress = accToConnectTo.address
    messageToSend.portNumber = accToConnectTo.port
    clientSocket.sendall(pickle.dumps(messageToSend))

def sendMsgToOfflineAcc(clientSocket, messageRecieved):
    accNamesAndMessage = messageRecieved.text
    accUsernameToSendFrom = accNamesAndMessage[:accNamesAndMessage.index(' ')]
    accNamesAndMessage = accNamesAndMessage[accNamesAndMessage.index(' ')+1:]
    accUsernameToSendTo = accNamesAndMessage[:accNamesAndMessage.index(' ')]
    actualMessage = accNamesAndMessage[accNamesAndMessage.index(' ')+1:]
    accToConnectTo = getAccount(accUsernameToSendTo)
    accToConnectTo.privateInbox.setdefault(accUsernameToSendFrom, []).append(accUsernameToSendFrom + ": " + actualMessage)
    updateUserBase(accToConnectTo)


def whoIsOnline(clientSocket, messageRecieved):
    messageTosend = msg.Message()
    messageTosend.arrayToSend = [user.accUsername for user in userBase if user.status == account.Status.ONLINE]
    clientSocket.sendall(pickle.dumps(messageTosend))

def logOut(clientSocket, messageSent):
    user = messageSent.account
    if user.status == account.Status.ONLINE:
        user.status = account.Status.OFFLINE
        user.address = ""
        user.port = -1
        user.currentlyInbox = None
        updateUserBase(user)
    clientSocket.close()

def sendMessageToGroup(groupName, sender, actualMessage):
    groupMembers = currentGroups[groupName]
    messageToSend = msg.Message()
    for currentMember in groupMembers:
        currentMemberAcc = getAccount(currentMember)
        if currentMemberAcc.status == account.Status.ONLINE:
            messageToSend.text = "Group** " + sender + " " + groupName + " " + actualMessage
            socketToMember = socket(AF_INET, SOCK_DGRAM)
            socketToMember.connect((currentMemberAcc.address, currentMemberAcc.port))
            socketToMember.sendall(pickle.dumps(messageToSend))
        else:
            currentMemberAcc.groupInbox.setdefault(groupName, []).append(sender+": "+actualMessage)
            updateUserBase(currentMemberAcc)


def clientHandler(clientSocket, clientAddr):
    while True:
        messageRecieved = pickle.loads(clientSocket.recv(4028)) #1st message recieved
        message = messageRecieved.request

        # Sign Up
        if (message == requests[0]): #request[0] = "SignUp*******"
            signUp(clientSocket, messageRecieved, clientAddr)

        # Log In
        elif (message == requests[1]):
            logIn(clientSocket, messageRecieved, clientAddr)
        
        #Connect with another user
        elif (message == requests[2]):
            connectToAcc(clientSocket, messageRecieved)

        #Send messages to offline users 
        elif (message == requests[3]):
            print("Second")
            sendMsgToOfflineAcc(clientSocket, messageRecieved)
            print("Third")

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
            print("enters elif")
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
            print(actualMessage)
            groupName = actualMessage[:actualMessage.index(" ")]
            actualMessage = actualMessage[actualMessage.index(" ")+1:]
            sender = actualMessage[:actualMessage.index(" ")]
            actualMessage = actualMessage[actualMessage.index(" ")+1:]
            sendMessageToGroup(groupName, sender, actualMessage)
            

def main():
    postNumber = 15048
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',postNumber))
    serverSocket.listen(1)

    while True:
        clientSocket, clientAddr = serverSocket.accept()
        clientHandlerThread = threading.Thread(target=clientHandler, args=(clientSocket,clientAddr))
        clientHandlerThread.start()

if __name__ == "__main__":
    main()
