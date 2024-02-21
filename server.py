from socket import *
import pickle
import threading
import account


userBase = []
userBaseLock = threading.Lock()

requests = ["SignUp*******","LogIn********","WhoIsOnline**","LogOut*******"]

def getAllOnlineClients() -> str:
    result = ""
    for currentUser in userBase:
        if currentUser.status == account.Status.Online:
            result = result + "\n" +str(currentUser.accUsername)
    return result

def alreadyAUser(userName) -> bool:
    result = False
    for currentUser in userBase:
        if(currentUser.accUsername == userName):
            result = True
            break
    return result

def getAccount(userName) -> account.Account:
    result = account.Account
    for currentUser in userBase:
        if(currentUser.accUsername == userName):
            result = currentUser
    return result

def updateUserBase(userToUpdate):
    for currentUser in userBase:
        if (currentUser.accUsername == userToUpdate.accUsername):
            currentUser = userToUpdate
            break
        
def signUp(clientSocket):
    user = pickle.loads(clientSocket.recv(4028))
    print(user.accUsername)
    if(not alreadyAUser(user.accUsername)):
        with userBaseLock:
            userBase.append(user)
        user.status = account.Status.ONLINE
        clientSocket.sendall(pickle.dumps(user))
    else:
        clientSocket.sendall(pickle.dumps(user))

def clientHandler(clientSocket):
    while True:
        message = pickle.loads(clientSocket.recv(4028))

        # Sign Up
        if (message == requests[0]):
            signUp(clientSocket)

        # Log In
        elif (message == requests[1]):
            if (alreadyAUser(message)):
                user = getAccount(message)
                user.status = account.Status.ONLINE
                clientSocket.sendall(pickle.dumps(user))
            else:
                user = account.Account()
                clientSocket.sendall(pickle.dumps("UserNotFound*"))


        # Log Out
        elif (message == requests[3]):
            message.status = account.Status.OFFLINE
            updateUserBase(message)
            clientSocket.close()
            break

def main():
    postNumber = 14000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',postNumber))
    serverSocket.listen(5)

    while True:
        connectionSocket, clientAddr = serverSocket.accept()
        clientHandlerThread = threading.Thread(target=clientHandler, args=(connectionSocket,))
        clientHandlerThread.start()

if __name__ == "__main__":
    main()

        
