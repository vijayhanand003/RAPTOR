import socket
import firebase_admin
from firebase_admin import firestore

cred = firebase_admin.credentials.Certificate("dharun.json")  # Replace with your actual path
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Function to retrieve the client ID using their email
def get_client_id_by_email(email):
    try:
        # Fetch the document from 'clients' collection where email matches
        clients_ref = db.collection('client')  # Adjust 'clients' if the collection name differs
        query = clients_ref.where('email', '==', email).limit(1).stream()

        for doc in query:
            return doc.id  # Return the document ID as the client ID

        return None  # No client found for the given email

    except Exception as e:
        print(f"Error retrieving client ID: {e}")
        return None

# Function to connect to banking server and retrieve funds
def display_funds(email):
    try:
        # Retrieve client ID from the email
        client_id = get_client_id_by_email(email)
        if not client_id:
            return "CLIENT_NOT_FOUND"

        # Create a socket connection to the banking server
        banking_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        banking_socket.connect(('10.160.0.4', 12347))  # Banking server IP and port

        # Send a request to the banking server to check funds using client ID
        print('sending')
        request_data = f"display_funds,{client_id}"
        banking_socket.send(request_data.encode('utf-8'))

        # Receive the response from the banking server
        funds = banking_socket.recv(1024).decode('utf-8')
        banking_socket.close()
        print(funds)
        return funds  # Return the available funds

    except Exception as e:
        print(f"Error retrieving funds: {e}")
        return "Error"
