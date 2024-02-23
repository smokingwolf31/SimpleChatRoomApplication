from socket import *
import pickle
import threading
import account
import message


userBase = []
userBaseLock = threading.Lock()

requests = ["SignUp*******"]


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
        
def signUp(clientSocket):
    print("Top") #debug
    username = pickle.loads(clientSocket.recv(4082)).text #2nd Message recieved. This is where it gets stuck. specifically clientSocket.recv(4028) does not end evaluating
    print("Buttom") #debug
    if(not alreadyAUser(username)):
        user = account.Account()
        user.accUsername = username
        user.status = account.Status.ONLINE
        with userBaseLock:
            userBase.append(user)
        messageToSend = message.Message().withAccount(user)
        clientSocket.sendall(pickle.dumps(messageToSend)) #3rd Message sent
    else:
        clientSocket.sendall(pickle.dumps(message.Message().withAccount(account.Account()))) #3rd Message Sent


def clientHandler(clientSocket):
    while True:
        messageSent = pickle.loads(clientSocket.recv(4028)) #1st message recieved
        message = messageSent.text

        # Sign Up
        if (message == requests[0]): #request[0] = "SignUp*******"
            signUp(clientSocket)
            

def main():
    postNumber = 15021
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',postNumber))
    serverSocket.listen(1)

    while True:
        clientSocket, clientAddr = serverSocket.accept()
        clientHandlerThread = threading.Thread(target=clientHandler, args=(clientSocket,))
        clientHandlerThread.start()

if __name__ == "__main__":
    main()

        
