import socket
import threading
import firebase_admin
from firebase_admin import credentials, firestore

# Import necessary functions
from authentication.auth import handle_signup, verifyClientPassword
from watchlist.watchfunc import handle_search
from Portfolio.portfolio import display_portfolio
from buySell.buysell import buy_sell
from buySell.displayFunds import display_funds

from authentication.auth import handle_signup, verifyClientPassword
from watchlist.watchfunc import handle_search,handle_fetch_watchlist


# Initialize Firebase connection
cred = credentials.Certificate("dharun.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to handle the type of client data received
def handle_client_data(data):
    try:
        # Split the request type and client info
        request_type, *client_info = data.split(',')
        print("Requested:", request_type)

        # Handle signup
        if request_type == "signup" and len(client_info) == 3:
            name, email, password = client_info
            return handle_signup(name, email, password)

        # Handle login and return user's watchlist
        elif request_type == "login" and len(client_info) == 2:
            email, password = client_info
            if verifyClientPassword(email, password):
                user_ref = db.collection('users').document(email)
                user_doc = user_ref.get()
                if user_doc.exists:
                    return f"Login successful, {user_doc.to_dict().get('watchlist', [])}"
                else:
                    return "Login successful, []"
            else:
                return "Login failed"

        # Handle stock search
        elif request_type == "search" and len(client_info) == 1:
            stock_name = client_info[0]
            return handle_search(stock_name)

        # Handle adding to watchlist
        elif request_type == "add_to_watchlist" and len(client_info) == 2:
            email, stock_name = client_info
            user_ref = db.collection('client').where('email', '==', email).limit(1).get()
            if user_ref:
                doc_ref = user_ref[0].reference
                doc_ref.update({'watchlist': firestore.ArrayUnion([stock_name])})
                return f"Added {stock_name} to watchlist."
            else:
                return "User not found."

        # Handle portfolio request
        elif request_type == 'Portfolio' and len(client_info) == 1:
            clientId = client_info[0]
            return display_portfolio(clientId)
        
        elif request_type == "buy" or request_type == "sell":
            email, stock, quantity, price = client_info
            quantity = int(quantity)
            price = float(price) if price else None  # None indicates market price

            # Call the buy_sell function
            return buy_sell(email, stock, quantity, price, request_type)

        # Handle funds display request
        elif request_type == 'display_funds':
            email = client_info[0]
            return display_funds(email)

        else:
            return "Invalid data format or request type"

    except Exception as e:
        return f"Error handling client: {e}"


def handle_second_client_data(data):
    try:
        # Split the data by commas and identify the request type
        request_type, *client_info = data.split(',')
        print(f"Requested: {request_type}")
    
        # Handle fetching the user's watchlist
        if request_type == "fetch_watchlist" and len(client_info) == 1:
            email = client_info[0]
            return handle_fetch_watchlist(email)
        
        else:
            return "Invalid request format or missing data."

    except Exception as e:
        return f"Error handling client data: {e}"

def handle_second_client(client_socket, address):
    print(f"Second connection established with {address}")
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            response = handle_second_client_data(data)  # Use a separate handler for second connection
            #print(response)
            client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"Error in second connection: {e}")
            break
    client_socket.close()


# Function to handle each client connection
def handle_client(client_socket, address):
    print(f"Connection established with {address}")
    while True:
        try:
            # Receive data from client
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            # Process client data and send response
            response = handle_client_data(data)
            client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
            break
    client_socket.close()

# Main server code with manual test case
def start_server():
    # Create the first socket
    server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket1.bind(('127.0.0.1', 12345))
    server_socket1.listen(5)
    print("Server is listening on port 12345 for first connection...")

    # Create the second socket
    server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket2.bind(('127.0.0.1', 12346))  # Different port for second connection
    server_socket2.listen(5)
    print("Server is listening on port 12346 for second connection...")

    while True:
        # Accept connections on the first socket
        client_socket1, address1 = server_socket1.accept()
        client_handler1 = threading.Thread(target=handle_client, args=(client_socket1, address1))
        client_handler1.start()

        # Accept connections on the second socket
        client_socket2, address2 = server_socket2.accept()
        client_handler2 = threading.Thread(target=handle_second_client, args=(client_socket2, address2))
        client_handler2.start()

if __name__ == "__main__":
    start_server()
