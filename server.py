from socket import *
import pickle
import threading
import account

userBase = [account.Account]
currentConnections = {}

currentConnectionsLock = threading.Lock
requests = ["SignUp*******","logIn********","WhoIsOnline**"]

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
        
        

def clientHandler(clientSocket):
    message = clientSocket.recv(4028).decode()
    while currentConnectionsLock:
        currentConnections.append(clientSocket)

    while True:
        message = pickle.load(clientSocket.recv(4028).decode())
        command = message[0:13]
        message = message[13:]
        user = account.Account
        if (command == requests[0]):
            if(not alreadyAUser(message)):
                user.accUsername = message
                userBase.append(user)
                clientSocket.sendall(pickle.dumps(user))
            else:
                clientSocket.sendall(pickle.dumps(("UsernameTaken")))
        elif (command == requests[1]):
            if(userBase.count(message) == 1):
                
                clientSocket.send()

        while currentConnectionsLock:
            currentConnectionsLock.remove(clientSocket)
    clientSocket.close()

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

        
