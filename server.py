from socket import *
import pickle
import threading
import account


userBase = []
userBaseLock = threading.Lock()

requests = ["SignUp*******","LogIn********","WhoIsOnline**","LogOut*******"]


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
    user = pickle.loads(clientSocket.recv(4028))
    print(user.accUsername)
    if(not alreadyAUser(user.accUsername)):
        with userBaseLock:
            userBase.append(user)
        user.status = account.Status.ONLINE
        clientSocket.sendall(pickle.dumps(user))
    else:
        clientSocket.sendall(pickle.dumps(user))

def logIn(clientSocket):
    user = pickle.loads(clientSocket.recv(4028))
    if (alreadyAUser(user.accUsername)):
        user = getAccount(user.accUsername)
        user.status = account.Status.ONLINE
        clientSocket.sendall(pickle.dumps(user))
    else:
        clientSocket.sendall(pickle.dumps(user))

def whoIsOnline(clientSocket):
    result = [user.accUsername for user in userBase if user.status == account.Status.ONLINE]
    clientSocket.sendall(pickle.dumps(result))

def logOut(clientSocket):
    user = pickle.loads(clientSocket.recv(4028))
    clientSocket.close()
    user.status = account.Status.OFFLINE
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
        
        # List online users
        elif (message == requests[2]):
            whoIsOnline(clientSocket)

        # Log Out
        elif (message == requests[3]):
            logOut(clientSocket)
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

        
