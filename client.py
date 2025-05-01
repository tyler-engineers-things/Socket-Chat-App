from socket import *
import argparse
import threading
import datetime
import sys

# Argument parsing to determine server, port, username, inputted passcode, etc.
###
parser = argparse.ArgumentParser("Client")
parser.add_argument('-join', action = 'store_true')
parser.add_argument('-host', '--hostname')
parser.add_argument('-port', '--port')
parser.add_argument('-username', '--username')
parser.add_argument('-passcode', '--passcode')
obtained_args = parser.parse_args()
###

# Values obtained from command arguments
###
server = obtained_args.hostname
port = int(obtained_args.port)
user = obtained_args.username
passcode = obtained_args.passcode
###

# Creates socket
clientSocket = socket(AF_INET, SOCK_STREAM)

# Value for ending second thread
thread_end = 0

# Function for data capture thread
###
def receive_data():
    while thread_end == 0:
        try:
            text = clientSocket.recv(1024).decode()
            if thread_end == 0:
                print(text)
                sys.stdout.flush()
        except:
            return
###

# Main function
###
if __name__ == "__main__":
    # Ensures inputted values are valid
    if len(passcode) <= 5 and len(user) <= 8:

        # Connects socket to server to allow data transfer
        clientSocket.connect((server, port))

        # Passcode handling; Ensures correct passcode was entered and doesn't allow connection if otherwise
        ###
        user_data = str(user + " " + passcode)
        clientSocket.send(user_data.encode())
        passcode_check = clientSocket.recv(1024)
        if passcode_check.decode() == '0':
            print("Incorrect passcode")
            sys.stdout.flush()
        ###

        # Creates data receiving thread and allows for messages to be sent
        ###
        else:
            print("Connected to", server, "on port", port)
            sys.stdout.flush()
            # Creates thread for receiving data
            chat_update = threading.Thread(target=receive_data, name="chat_thread")
            chat_update.start()
            while thread_end == 0:
                # User input to send messages
                send_text = str(input())

                # Message formatting; clients the message goes to will be determined by server
                ###
                current_time = datetime.datetime.now()
                one_hour = current_time + datetime.timedelta(hours=1)
                send_text = send_text.replace(":)", "[Feeling Joyful]")
                send_text = send_text.replace(":(", "[Feeling Unhappy]")
                send_text = send_text.replace(":mytime", current_time.strftime("%Y %b %d %X %a"))
                send_text = send_text.replace(":+1hr", one_hour.strftime("%Y %b %d %X %a"))
                ###

                # Checks for exit
                if send_text.lower().find(":exit") == 0:
                    thread_end = 1
                # Sends message to server
                clientSocket.send(send_text.encode())
        ###
    else:
        print("Incorrect passcode")
        sys.stdout.flush()
    clientSocket.close()
###