import socket
import json

# Server configuration
HOST = 'localhost'
PORT = 12345

def receive_message(client_socket):
    return client_socket.recv(1024).decode('utf-8')

def send_message(client_socket, message):
    client_socket.send(message.encode('utf-8'))

def main():
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Send client's name
    username = input("Enter your name: ")
    send_message(client_socket, username)

    while True:
        # Receive the menu options from the server
        menu = receive_message(client_socket)
        print(menu)

        choice = input("Choose an option: ")
        send_message(client_socket, choice)

        if choice == '1':  # Headlines
            category = input("Enter a category (business, general, health, etc.): ")
            send_message(client_socket, category)
            results = receive_message(client_socket)
            print("Headlines:", results)

            # Request details for a selected headline
            selected = input("Select a headline (number): ")
            send_message(client_socket, selected)
            details = receive_message(client_socket)
            print("Headline Details:", details)

        elif choice == '2':  # Sources
            country = input("Enter a country (au, ca, jp, etc.): ")
            send_message(client_socket, country)
            results = receive_message(client_socket)
            print("Sources:", results)

            # Request details for a selected source
            selected = input("Select a source (number): ")
            send_message(client_socket, selected)
            details = receive_message(client_socket)
            print("Source Details:", details)

        elif choice == '3':  # Quit
            print(receive_message(client_socket))
            break

    client_socket.close()

if __name__ == "__main__":
    main()
