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
        

def clientHandler(clientSocket):
    while True:
        message = pickle.loads(clientSocket.recv(4028))
        command = message[0:13]
        message = message[13:]
        print(message+" bruj")

        # Sign Up
        if (command == requests[0]):
            with userBaseLock:
                print("just enterd\n")
                user = account.Account(accUsername=message, status=account.Status.OFFLINE)
                if(message == "UsernameTaken"):
                    user.accUsername = "NotValidUserName"
                    print("dump invalid user\n")
                    clientSocket.sendall(pickle.dumps(user))
                elif(not alreadyAUser(message)):
                    userBase.append(user)
                    user.status = account.Status.ONLINE
                    print("dump new user\n")
                    clientSocket.sendall(pickle.dumps(user))
                else:
                    user.accUsername = "UsernameTaken"
                    print("dump existing user\n")
                    clientSocket.sendall(pickle.dumps(user))

        # Log In
        elif (command == requests[1]):
            if (alreadyAUser(message)):
                clientSocket.sendall(pickle.dumps(getAccount(message)))
            else:
                clientSocket.sendall(pickle.dumps("UserNotFound*"))


        # Log Out
        elif (command == requests[3]):
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

        
