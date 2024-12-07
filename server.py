import socket
import threading
import requests
import json
import os
import ssl

# Server configuration
HOST = 'localhost'
PORT = 12345
MAX_CONNECTIONS = 3
API_KEY = "df53d52f41de447d8ec156ca19eedf3a"  # API KEY

# Create a directory to store the JSON files
if not os.path.exists('client_data'):
    os.makedirs('client_data')

# Define a function to handle client requests
def handle_client(client_socket, client_address):
    print(f"New connection: {client_address}")
    
    # Ask for the client's name
    client_name = client_socket.recv(1024).decode('utf-8')
    print(f"Client name: {client_name}")

    # Send a menu to the client
    menu = """
    Main Menu:
    1. Search Headlines
    2. List Sources
    3. Quit
    """
    client_socket.send(menu.encode('utf-8'))

    while True:
        # Receive client's choice
        choice = client_socket.recv(1024).decode('utf-8')

        # Initialize group_id at the start of the loop
        group_id = 1  # Default group_id, modify as needed

        if choice == '1':  # Headlines option
            client_socket.send("Choose a category: business, general, health, science, sports, technology.".encode('utf-8'))
            category = client_socket.recv(1024).decode('utf-8')
            # Fetch data from API
            response = requests.get(f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={API_KEY}")
            headlines = response.json().get('articles', [])
            results = [{'source': h['source']['name'], 'title': h['title']} for h in headlines[:15]]
            
            # Save the data into a JSON file
            json_filename = f'client_data/{client_name}_{choice}_{group_id}.json'
            with open(json_filename, 'w') as f:
                json.dump(results, f, indent=4)
            
            # Send list of headlines to client
            client_socket.send(json.dumps(results).encode('utf-8'))
            # Client selects a headline for detailed info
            client_socket.send("Select a headline by number to view details:".encode('utf-8'))
            selected = client_socket.recv(1024).decode('utf-8')

            # Ensure the selected value is a valid integer index
            try:
                selected_index = int(selected)
                if 0 <= selected_index < len(headlines):
                    selected_headline = headlines[selected_index]
                    client_socket.send(json.dumps(selected_headline).encode('utf-8'))
                else:
                    client_socket.send("Invalid index. Please select a number between 0 and {0}.".format(len(headlines) - 1).encode('utf-8'))
            except ValueError:
                client_socket.send("Invalid input. Please enter a valid number.".encode('utf-8'))

        elif choice == '2':  # Sources option
            client_socket.send("Choose a country: au, ca, jp, ae, sa, kr, us, ma.".encode('utf-8'))
            country = client_socket.recv(1024).decode('utf-8')
            # Fetch sources data from API
            response = requests.get(f"https://newsapi.org/v2/sources?country={country}&apiKey={API_KEY}")
            sources = response.json().get('sources', [])
            results = [{'source': s['name']} for s in sources[:15]]
            
            # Save the data into a JSON file
            json_filename = f'client_data/{client_name}_{choice}_{group_id}.json'
            with open(json_filename, 'w') as f:
                json.dump(results, f, indent=4)

            # Send list of sources to client
            client_socket.send(json.dumps(results).encode('utf-8'))
            # Client selects a source for detailed info
            client_socket.send("Select a source by number to view details:".encode('utf-8'))
            selected = client_socket.recv(1024).decode('utf-8')

            # Ensure the selected value is a valid integer index
            try:
                selected_index = int(selected)
                if 0 <= selected_index < len(sources):
                    selected_source = sources[selected_index]
                    client_socket.send(json.dumps(selected_source).encode('utf-8'))
                else:
                    client_socket.send("Invalid index. Please select a number between 0 and {0}.".format(len(sources) - 1).encode('utf-8'))
            except ValueError:
                client_socket.send("Invalid input. Please enter a valid number.".encode('utf-8'))

        elif choice == '3':  # Quit option
            client_socket.send("Goodbye!".encode('utf-8'))
            break

    client_socket.close()
    print(f"Connection with {client_address} closed.")

# Set up the server socket
def start_server():
    try:
        # Attempt to load SSL/TLS certificates
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")  # Replace with your certificate and key files
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secure_server_socket = context.wrap_socket(server_socket, server_side=True)
        secure_server_socket.bind((HOST, PORT))
        secure_server_socket.listen(MAX_CONNECTIONS)
        print(f"SSL/TLS server started on {HOST}:{PORT}, waiting for clients...")
    except FileNotFoundError:
        print("SSL certificates not found. Running server in normal mode.")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CONNECTIONS)
        print(f"Server started on {HOST}:{PORT} (no encryption), waiting for clients...")
    
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
