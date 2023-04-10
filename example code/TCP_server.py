from socket import *
from datetime import datetime
import threading

serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
serverSocket.settimeout(120) # if socket listens for 2 minutes and gets no conenctions

connID_list = []
resetCounter = 0
resetFlag = True

while True:
     # Handle socket timeout
     try:
          connectionSocket, clientAddress = serverSocket.accept()

          # Automatic socket timeout if server waits over 2 minutes without any messages recived
          connectionSocket.settimeout(120)

          modifiedMessage = connectionSocket.recv(1024).decode().split()
          connectionID = modifiedMessage[1]
          modifiedMessage = modifiedMessage[0]

          # Check if connectionID is already connected
          if(connectionID not in connID_list):
               # If not connected, add to connection, start timer, and return OK code
               response = "OK {} {} {}".format(connectionID, clientAddress[0], serverPort)
               
               connID_list.append(connectionID)
               timer = threading.Timer(30, lambda : connID_list.remove(connectionID)) # Remove connID in 30 seconds
               timer.start()
               connectionSocket.send(response.encode())

          else:
               response = "RESET {}".format(connectionID)
               connectionSocket.send(response.encode())

     except timeout:
        resetFlag = False
        # Close socket if timeout reached
        connectionSocket.close()

