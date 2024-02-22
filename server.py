from socket import *
import pickle
import threading
import account


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
            break
        
def signUp(clientSocket):
    accUsername = pickle.loads(clientSocket.recv(4028))
    if(not alreadyAUser(accUsername)):
        user = account.Account()
        user.status = account.Status.ONLINE
        user.socket = clientSocket
        with userBaseLock:
            userBase.append(user)
        clientSocket.sendall(pickle.dumps(user))
    else:
        clientSocket.sendall(pickle.dumps(account.Account()))

def logIn(clientSocket):
    accUsername = pickle.loads(clientSocket.recv(4028))
    if (alreadyAUser(accUsername)):
        user = getAccount(accUsername)
        user.status = account.Status.ONLINE
        user.socket = clientSocket
        clientSocket.sendall(pickle.dumps(user))
    else:
        clientSocket.sendall(account.Account())

def connectToAcc(clientSocket):
    accUsername = pickle.loads(clientSocket.recv(4028))
    accToConnectTo = getAccount(accUsername)
    clientSocket.sendall(pickle.dumps(accToConnectTo))

def sendMsgToOfflineAcc(clientSocket):
    accUsernameToSendFrom = pickle.loads(clientSocket.recv(4028))
    accUsernameToSendTo = pickle.loads(clientSocket.recv(4028))
    actualMessage = pickle.loads(clientSocket.recv(4028))
    accToConnectTo = getAccount(accUsernameToSendTo)
    if accToConnectTo.inbox.get(accUsernameToSendFrom) is not None:
        accToConnectTo.inbox[accUsernameToSendFrom].append(actualMessage)
    else:
        accToConnectTo.inbox[accToConnectTo] = [actualMessage]
    updateUserBase(accToConnectTo)


def whoIsOnline(clientSocket):
    result = [user.accUsername for user in userBase if user.status == account.Status.ONLINE]
    clientSocket.sendall(pickle.dumps(result))

def logOut(clientSocket):
    user = pickle.loads(clientSocket.recv(4028))
    clientSocket.close()
    user.status = account.Status.OFFLINE
    user.socket = None
    updateUserBase(user)

def clientHandler(clientSocket):
    while True:
        message = pickle.loads(clientSocket.recv(4028))

        # Sign Up
        if (message == requests[0]):
            signUp(clientSocket)

        # Log In
        elif (message == requests[1]):
            logIn(clientSocket)
        
        #Connect with another user
        elif (message == requests[2]):
            connectToAcc()

        #Send messages to offline users 
        elif (message == requests[3]):
            sendMsgToOfflineAcc()

        # List online users
        elif (message == requests[4]):
            whoIsOnline(clientSocket)

        # Log Out
        elif (message == requests[5]):
            logOut(clientSocket)
            break

        #Does this user exit
        elif (message == requests[6]):
            userName = pickle.loads(clientSocket.recv(4028))
            clientSocket.sendAll(pickle.dumps(alreadyAUser(userName)))

        #Is This User Online
        elif (message == requests[7]):
            userName = pickle.loads(clientSocket.recv(4028))
            accToCheck = getAccount(userName)
            if accToCheck.status == account.Status.ONLINE:
                clientSocket.sendAll(pickle.dumps(True))
            else:
                clientSocket.sendAll(pickle.dumps(False))
            

def main():
    postNumber = 14000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',postNumber))
    serverSocket.listen(5)

    while True:
        clientSocket, clientAddr = serverSocket.accept()
        clientHandlerThread = threading.Thread(target=clientHandler, args=(clientSocket,))
        clientHandlerThread.start()

if __name__ == "__main__":
    main()

        
