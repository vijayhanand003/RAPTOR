import socket
import firebase_admin
from firebase_admin import firestore
import json
from datetime import datetime
from datetime import datetime
# Initialize Firebase Admin SDK
cred = firebase_admin.credentials.Certificate("dharun.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

def convert_date_to_int(data):
    for key, value in data.items():
        if isinstance(value, dict) and 'date' in value:
            value['date'] = 1
    return data

# Convert dates in the stock_data dictionary

def convert_date_to_int1(data):
    # Assuming 'data' is a list of tuples [(date_key, data_dict), ...]
    converted_data = []
    for date_key, value in data:
        if isinstance(value, dict) and 'date' in value:
            value['date'] = 1  # Or whatever logic you want
        converted_data.append((date_key, value))
    return converted_data


def get_stock_data(symbol):
    stock_ref = db.collection('stocks').document(symbol)
    stock_doc = stock_ref.get()

    if stock_doc.exists:
        stock_data = stock_doc.to_dict()
        converted_stock_data = convert_date_to_int(stock_data)
        return converted_stock_data
    else:
        return None


import json

def get_historical_stock_data(symbol):
    stock_ref = db.collection("stocks").document(symbol)
    stock_data = stock_ref.get()

    if stock_data.exists:
        data_dict = stock_data.to_dict()
        historical_data = []

        # Iterate through all records and assign values from 1 to 100 to the "date" key
        for idx, (date_key, data) in enumerate(data_dict.items()):
            if isinstance(data, dict):
                # Assign an integer value from 1 to 100 to the "date" key
                data['date'] = idx + 1  # Replace the "date" key value with idx + 1
                historical_data.append(data)

        # Keep only the last 100 entries if there are more than 100
        historical_data = historical_data[-100:]

        # Prepare the data to send to the client
        client_data = [{"date": data['date'], "data": data} for data in historical_data]

        # Return the data in JSON format
        return json.dumps(client_data)  # Send JSON formatted data to the client
    else:
        return json.dumps({"error": f"No document found for symbol: {symbol}"})


# Handle buy/sell/display funds requests from the main server
def handle_bank_transaction(data):
    try:
        parts = data.split(',')
        transaction_type = parts[0]  # Extract transaction type first
        print("requested: ",transaction_type)
        # Handle display_funds request
        if transaction_type == 'display_funds':
            if len(parts) != 2:
                return "INVALID_REQUEST_FORMAT"
            client_id = parts[1]

            # Retrieve user's bank details using client_id
            bank_ref = db.collection('accounts').document(client_id)
            bank_account = bank_ref.get().to_dict()

            if not bank_account:
                return "BANK_ACCOUNT_NOT_FOUND"

            current_balance = bank_account.get('available_money', None)
            if current_balance is None:
                return "ACCOUNT_BALANCE_NOT_FOUND"

            return current_balance

        elif(transaction_type == 'GET_STOCK_DATA'):
            symbol = data.split(",")[1]
            stock_data = get_stock_data(symbol)
            
            response = stock_data if stock_data else "No data found"
            return response
    
        elif(transaction_type == 'GET_HISTORICAL_DATA'):
            symbol = data.split(",")[1]
            historical_data = get_historical_stock_data(symbol)
            
            response = historical_data if historical_data else "No historical data found"
            return response
        # Handle buy/sell requests
        else:
            if len(parts) != 3:
                return "INVALID_REQUEST_FORMAT"
            transaction_type, client_id, amount = parts
            amount = float(amount)

            # Retrieve user's bank details using client_id
            bank_ref = db.collection('accounts').document(client_id)
            bank_account = bank_ref.get().to_dict()

            if not bank_account:
                return "BANK_ACCOUNT_NOT_FOUND"

            current_balance = bank_account.get('available_money', None)
            if current_balance is None:
                return "ACCOUNT_BALANCE_NOT_FOUND"

            # Handle buy request
            if transaction_type == 'buy':
                if current_balance >= amount:
                    # Deduct the amount and update bank balance
                    bank_ref.update({'available_money': firestore.Increment(-amount)})
                    return "SUCCESS"
                else:
                    return "INSUFFICIENT_FUNDS"

            # Handle sell request
            elif transaction_type == 'sell':
                # Add the sale amount to user's balance
                bank_ref.update({'available_money': firestore.Increment(amount)})
                return "SUCCESS"

            return "INVALID_TRANSACTION_TYPE"

    except Exception as e:
        return f"Error: {e}"

# Function to handle each bank server request
def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(12347).decode('utf-8')
            if not data:
                break

            print(f"Received data: {data}")
            # Process the bank transaction
            response = handle_bank_transaction(data)
            client_socket.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")
            break

    client_socket.close()

# Main banking server code
def start_banking_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('10.160.0.4', 12347))
    server_socket.listen(5)
    print("Banking server is listening on port 12347...")

    while True:
        client_socket, _ = server_socket.accept()
        handle_client(client_socket)

if __name__ == "__main__":
    start_banking_server()
