import socket
import threading
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase connection
cred = credentials.Certificate("dharun.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to verify client by email
def verifyClientPassword(email, password):
    try:
        # Verify password for the specified email
        field_filter = firestore.FieldFilter("email", "==", email)
        docRef = db.collection('client').where(filter=field_filter)
        docs = docRef.stream()

        found = False
        for doc in docs:
            doc_data = doc.to_dict()
            if doc_data.get('clientPassword') == password:
                found = True
                break
        
        if found:
            print("Login successful")

            return True
        else:
            print("Login failed")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Function to generate unique clientId
def generate_unique_client_id():
    clients = db.collection('client').stream()
    client_count = sum(1 for _ in clients)
    return f"client_{client_count + 1:03d}"

# Function to handle signup
# Function to handle signup and create portfolio
def handle_signup(name, email, password):
    try:
        # Check if the email already exists
        field_filter = firestore.FieldFilter("email", "==", email)
        docRef = db.collection('client').where(filter=field_filter)
        docs = docRef.stream()

        if any(True for _ in docs):
            return "Email already exists"
        
        # Generate unique clientId
        clientId = generate_unique_client_id()

        # Add new client to Firestore
        db.collection('client').document(clientId).set({
            'clientId': clientId,
            'clientName': name,
            'email': email,
            'clientPassword': password,
            'watchlist': ['AAME']  # Default watchlist item, can be customized later
        })

        # Add a portfolio document for the client in the Portfolio collection
        db.collection('Portfolio').document(clientId).set({
            'clientId': clientId,
            'clientName': name,
            'Holdings': []  # Empty holdings initially
        })

        return "Signup successful"
    except Exception as e:
        return f"An error occurred during signup: {e}"
