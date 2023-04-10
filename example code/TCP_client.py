from socket import *
from datetime import datetime
import sys

# parse command line arguments
serverName = sys.argv[2]
serverPort = int(sys.argv[3])
resetCounter = 0
connectionID = sys.argv[4] 
resetFlag = True

clientSocket = socket(AF_INET, SOCK_STREAM)

while resetFlag:
    # Handle socket timeout
    try:
        # Set client timeout to 15 seconds
        clientSocket.settimeout(15)

        message = sys.argv[1] + " " + connectionID # message + connectionID

        # connect to server
        clientSocket.connect((serverName,serverPort))



        # Send message to server
        clientSocket.send(message.encode())

        modifiedMessage = clientSocket.recv(2048)

        returnCode = modifiedMessage.decode().split()

        # Handle server return code
        if(returnCode[0] == "OK"):
            response = "Connection established {} {} {} on {}".format(connectionID, serverName, serverPort, datetime.now())
            print(response)
            resetFlag = False # Stop loop since we have finished the connection
            clientSocket.close()

        else:
            # If we have tried more than 3 times to establish a connection
            if(resetCounter > 2):
                response = "Connection failure on {}".format(datetime.now())
                print(response)
                resetFlag = False
                clientSocket.close()
            else:
                response = "Connection error {} on {}".format(sys.argv[4],datetime.now())
                print(response)
                print("Please enter a new connectionID:")
                connectionID = input().strip()
                resetCounter += 1
                clientSocket.close()

    # If we waited longer than 15 seconds for the server to respond
    except timeout:
        if(resetCounter > 2):
            response = "Connection failure on {}".format(datetime.now())
            print(response)
            resetFlag = False
            clientSocket.close()
        else:
            response = "Connection error {} on {}".format(sys.argv[4],datetime.now())
            print(response)
            print("Please enter a new connectionID:")
            connectionID = input().strip()
            resetCounter += 1
            clientSocket.close()

    # Handle connection failure, i.e. if the server is not up/avaiable
    except ConnectionRefusedError:
        print("Connection failure")
        resetFlag = False
        clientSocket.close()


        

