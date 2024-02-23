from socket import *
import pickle
import threading
import account
import message as msg


userBase = []
userBaseLock = threading.Lock()

requests = ["SignUp*******","LogIn********","ConnectToAcc*", "MsgOfflineAcc","WhoIsOnline**","LogOut*******", "DoesUserExist", "IsUserOnline*"]


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
            currentUser.inbox = userToUpdate.inbox
            currentUser.address = userToUpdate.address
            currentUser.port = userToUpdate.port
            break
        
def signUp(clientSocket, messageRecieved):
    if(not alreadyAUser(messageRecieved.text)):
        user = account.Account()
        user.accUsername = messageRecieved.text
        user.status = account.Status.ONLINE
        user.address, _ = clientSocket.getsockname()
        user.port = 16000 + len(userBase)
        with userBaseLock:
            userBase.append(user)
        messageToSend = msg.Message().withAccount(user)
        clientSocket.sendall(pickle.dumps(messageToSend)) #3rd Message sent
    else:
        clientSocket.sendall(pickle.dumps(msg.Message().withAccount(account.Account()))) #3rd Message Sent

def logIn(clientSocket, messageRecieved):
    accUsername = messageRecieved.text
    if (alreadyAUser(accUsername)):
        user = getAccount(accUsername)
        user.status = account.Status.ONLINE
        user.address, _ = clientSocket.getsockname()
        clientSocket.sendall(pickle.dumps(msg.Message().withAccount(user)))
        updateUserBase(user)
    else:
        clientSocket.sendall(pickle.dumps(msg.Message().withAccount(account.Account())))

def connectToAcc(clientSocket, messageRecieved):
    messageToSend = msg.Message()
    accUsername = messageRecieved.text
    accToConnectTo = getAccount(accUsername)
    messageToSend.ipAddress = accToConnectTo.address
    messageToSend.portNumber = accToConnectTo.port
    clientSocket.sendall(pickle.dumps(messageToSend))

def sendMsgToOfflineAcc(clientSocket, messageRecieved):
    print("Here Here")
    accNamesAndMessage = messageRecieved.text
    accUsernameToSendFrom = accNamesAndMessage[:accNamesAndMessage.index(' ')]
    accNamesAndMessage = accNamesAndMessage[accNamesAndMessage.index(' ')+1]
    accUsernameToSendTo = accNamesAndMessage[:accNamesAndMessage.index(' ')+1]
    actualMessage = accNamesAndMessage[accNamesAndMessage.index(' ')+1]
    accToConnectTo = getAccount(accUsernameToSendTo)
    if accToConnectTo.inbox.get(accUsernameToSendFrom) is None:
        accToConnectTo.inbox[accToConnectTo] = []
    accToConnectTo.inbox[accUsernameToSendFrom].append(accUsernameToSendFrom + ": " + actualMessage)
    updateUserBase(accToConnectTo)


def whoIsOnline(clientSocket, messageRecieved):
    messageTosend = msg.Message()
    messageTosend.arrayToSend = [user.accUsername for user in userBase if user.status == account.Status.ONLINE]
    clientSocket.sendall(pickle.dumps(messageTosend))

def logOut(clientSocket, messageSent):
    user = messageSent.account
    clientSocket.close()
    user.status = account.Status.OFFLINE
    user.socket = None
    updateUserBase(user)

def clientHandler(clientSocket):
    while True:
        messageRecieved = pickle.loads(clientSocket.recv(4028)) #1st message recieved
        message = messageRecieved.request

        # Sign Up
        if (message == requests[0]): #request[0] = "SignUp*******"
            signUp(clientSocket, messageRecieved)

        # Log In
        elif (message == requests[1]):
            logIn(clientSocket, messageRecieved)
        
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

        #Does this user exit
        elif (message == requests[6]):
            messageToSend = msg.Message()
            messageToSend.result = alreadyAUser(messageRecieved.text)
            clientSocket.sendall(pickle.dumps(messageToSend))

        #Is This User Online
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
            

def main():
    postNumber = 15034
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',postNumber))
    serverSocket.listen(1)

    while True:
        clientSocket, clientAddr = serverSocket.accept()
        clientHandlerThread = threading.Thread(target=clientHandler, args=(clientSocket,))
        clientHandlerThread.start()

if __name__ == "__main__":
    main()

        
