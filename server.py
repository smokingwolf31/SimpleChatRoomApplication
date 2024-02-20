from socket import *
import pickle
import threading
import account

userBase = [account.Account]
userBaseLock = threading.Lock

requests = ["SignUp*******","logIn********","WhoIsOnline**","LogOut*******"]

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
        

def clientHandler(clientSocket):
    message = clientSocket.recv(4028).decode()

    while True:
        message = pickle.load(clientSocket.recv(4028).decode())
        command = message[0:13]
        message = message[13:]
        user = account.Account
        if (command == requests[0]):
            while userBaseLock:
                if(not alreadyAUser(message)):
                    user.accUsername = message
                    user.status = account.Status.Online
                    userBase.append()
                    clientSocket.sendall(pickle.dumps(user))
                else:
                    clientSocket.sendall(pickle.dumps(("UsernameTaken")))
        elif (command == requests[1]):
            if(userBase.count(message) == 1):
                clientSocket.sendall(pickle.dumps(getAccount(message)))
            else:
                clientSocket.sendall(pickle.dumps("UserNotFound*"))
        elif (command == requests[3]):
            updateUserBase(message)
            clientSocket.close()
            break

def main():    
    postNumber = 31000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',postNumber))
    serverSocket.listen(5)

    while True:
        connectionSocket, clientAddr = serverSocket.accept()
        clientHandlerThread = threading.Thread(target=clientHandler, args=connectionSocket)
        clientHandlerThread.start()

if __name__ == "main":
    main()

        
