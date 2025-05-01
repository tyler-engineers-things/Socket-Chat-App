from socket import *
import argparse
import sys
import threading

# Argument parsing to determine server, port, username, inputted passcode, etc.
###
parser = argparse.ArgumentParser("Server")
parser.add_argument('-start', action = 'store_true')
parser.add_argument('-port', '--port')
parser.add_argument('-passcode', '--passcode')
obtained_args = parser.parse_args()
###

# Extracting inputted server information into variables
###
port = int(obtained_args.port)
passcode = obtained_args.passcode
###

# Value for maintaining or closing server
server_end = 0
# Thread dictionary for sending messages to each client
send_socket_dict = {}
# Thread dictionary for receiving messages from each client
recv_thread_dict = {}
# Queue of strings representing messages to be processed and sent to clients; Associated clients in client queue
message_queue = []
client_queue = []
# Message being sent at any given time
sent_message = ""
# Creates server and connection sockets
serverSocket = socket(AF_INET, SOCK_STREAM)

# Creates a thread to host receiving connection from a client
###
def recv_client_instance(client_socket, addr, user):
    try:
        while server_end == 0:
            message_queue.append(client_socket.recv(1024).decode())
            client_queue.append(user)
    except:
        return
###

# Creates thread for accepting new socket connections
###
def socket_accept(event):
    while server_end == 0:
        try:
            connectionSocket, addr = serverSocket.accept()

            # Passcode handling; Takes client's user and passcode and checks if passcode is correct. Then continues connection or sends break to client.
            ###
            c_user, c_pass = connectionSocket.recv(1024).decode().split(" ")
            if c_pass != passcode:
                c_pass = '0'
                connectionSocket.send(c_pass.encode())
                connectionSocket.close()
            else:
                c_pass = '1'
                connectionSocket.send(c_pass.encode())
                # Notifies all clients of new user
                message_queue.insert(0, c_user + " joined the chatroom")
                event.wait()
                # Stores each socket object, then creates and starts each connection thread
                send_socket_dict[c_user] = connectionSocket
                recv_thread_dict[c_user] = threading.Thread(target=recv_client_instance, args=(connectionSocket, addr, c_user))
                recv_thread_dict[c_user].start()
        ###
        except:
            print("Server has been closed.")
            sys.stdout.flush()
###

# Main function
###
if __name__ == "__main__" and len(passcode) <= 5:
    # Binds server to port, and then listens for clients
    serverSocket.bind(('127.0.0.1', port))
    serverSocket.listen(5) # number in here represents max number of connections
    print("Server started on port", str(port) + ". Accepting connections")
    sys.stdout.flush()

    # Event handler to ensure threads occur in correct order
    event_handle = threading.Event()

    # Creates new client acceptance thread
    client_accept = threading.Thread(target=socket_accept, args=(event_handle, ))
    client_accept.start()

    # Loop to check if any client has sent a message
    ###
    try:
        while server_end == 0:
            # Ensures new users aren't sent their own connection message
            event_handle.clear()

            # If statement used for outputting server announcements
            ###
            if len(message_queue) != len(client_queue):
                sent_message = str(message_queue.pop(0))
                print(sent_message)
                sys.stdout.flush()
                for outbound_socket in send_socket_dict.values():
                    outbound_socket.send(sent_message.encode())
                event_handle.set()
            ###
        
            # If statement used for messages
            elif len(message_queue) > 0 and len(client_queue) > 0:
                event_handle.set()
                sent_message = str(message_queue.pop(0))
                sender = str(client_queue.pop(0))
                
                # Handles direct messages from one individual to another
                ###
                if sent_message.lower().find(":dm") == 0:
                    extra_data, recipient, sent_message = sent_message.split(" ", maxsplit=2)
                    output_message = sender + ": " + sent_message
                    print(sender, "to", str(recipient + ":"), sent_message)
                    sys.stdout.flush()
                    outbound_socket = send_socket_dict[recipient]
                    outbound_socket.send(output_message.encode())
                ###

                # Handles users leaving the server
                ###
                elif sent_message.lower().find(":exit") == 0:
                    curr_socket = send_socket_dict.pop(sender)
                    curr_socket.close()
                    output_message = str(sender + " left the chatroom")
                    print(output_message)
                    sys.stdout.flush()
                    for outbound_socket in send_socket_dict.values():
                        outbound_socket.send(output_message.encode())
                ###

                # Handles normal messages to the server
                ###
                else:
                    output_message = str(sender + ": " + sent_message)
                    print(output_message)
                    sys.stdout.flush()
                    for outbound_socket in send_socket_dict.values():
                        outbound_socket.send(output_message.encode())
                ###
            ###
    except:
        server_end = 1
    ###
    serverSocket.close()
###
else:
    print("Passcode is invalid. Input a shorter passcode.")

