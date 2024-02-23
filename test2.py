from socket import *
import account
import message
import pickle
import sys

myAccount = account.Account(accUsername="spaceHolder", status=account.Status.OFFLINE)
serverName = "196.47.231.19"
serverPort = 15021
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

def signUp():
    while True:
        global myAccount
        userName = input("Please enter a user name you like or q to quit\n").strip()
        messageToSend = message.Message(userName) #sent messageToSend.text = usernName
        if userName == "q":
            break
        clientSocket.sendall(pickle.dumps(message.Message("SignUp*******"))) #1st message sent this messge is recieved in the main method on the server (used to identify the request i.e SignUp from SignIn for example)
        clientSocket.sendall(pickle.dumps(messageToSend)) #2nd message sent
        createdAcc = (pickle.loads(clientSocket.recv(4048))).account #3rd message recieved
        if(createdAcc.status == account.Status.OFFLINE):
            print("That username is taken\n")
        else:
            myAccount = createdAcc
            print("Account created your username is:\n"+myAccount.accUsername)
            break

def main():
    while True:
    
        #Sign Up
        if(myAccount.status == account.Status.OFFLINE):
            request = input("1. Sign Up\n")
            if request == "1":
                signUp()
            else:
                print("Enter valid option")

if __name__ == "__main__":
    main()