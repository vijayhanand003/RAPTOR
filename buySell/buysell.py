import firebase_admin
from firebase_admin import firestore
from Portfolio.portfolio import update_portfolio
import socket
from datetime import datetime

db = firestore.client()

def buy_sell(email, stock, quantity, price, transaction_type):
    try:
        # Retrieve the client ID using the email
        client_ref = db.collection('client').where('email', '==', email).get()
        if not client_ref:
            return "Client not found"
        
        # Extract client ID from the document
        client_id = client_ref[0].id
        print(client_id)

        # Get stock details
        stock_ref = db.collection('stocks').document(stock)
        stock_data = stock_ref.get().to_dict()

        if not stock_data:
            return "Stock not found"

        # Retrieve the latest stock date entry
        stock_dates = stock_data.keys()
        latest_date = max(stock_dates)
        latest_data = stock_data[latest_date]

        current_volume = latest_data['volume']
        market_price = latest_data['open']  # Current market price

        # If price is None, use market price
        price = price or market_price

        # Calculate timestamp for the new record
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare the new data (copy previous data except for 'volume' and 'open')
        new_data = latest_data.copy()  # Copy existing data
        new_data['volume'] = current_volume - quantity if transaction_type == "buy" else current_volume + quantity
        new_data['open'] = market_price + (0.001 * quantity) if transaction_type == "buy" else market_price - 0.01
        new_data['timestamp'] = timestamp  # Optionally include a timestamp field in the new record

        if transaction_type == "buy":
            if quantity > current_volume or price < market_price:
                return "Insufficient volume or price too low"

            # Calculate total cost
            total_cost = quantity * price

            # Contact banking server for payment verification using client_id
            if not bank_transaction(client_id, total_cost):
                return "Insufficient funds"

            # Update stock volume and price
            stock_ref.update({timestamp: new_data})  # Add new data with updated 'volume' and 'open' fields

            # Update user's portfolio
            update_portfolio(email, stock, quantity, price, market_price)

            return f"Buy transaction successful. New record added with timestamp {timestamp}"

        elif transaction_type == "sell":
            # Assume client portfolio holds details for quantity and stock
            portfolio_ref = db.collection('Portfolio').document(client_id)
            portfolio = portfolio_ref.get().to_dict()

            if not portfolio:
                return "Portfolio not found"

            holdings = portfolio.get('Holdings', [])
            for item in holdings:
                if item['stock_name'] == stock:
                    if item['quantity'] < quantity:
                        return "Not enough stock to sell"

                    total_sale = quantity * price

                    # Add stock to market volume and update price
                    stock_ref.update({timestamp: new_data})  # Add new data with updated 'volume' and 'open' fields

                    # Update the portfolio
                    item['quantity'] -= quantity
                    if item['quantity'] == 0:
                        holdings.remove(item)
                    portfolio_ref.update({'Holdings': holdings})

                    # Contact banking server to deposit sale amount
                    bank_transaction(client_id, total_sale, transaction_type='sell')

                    return f"Sell transaction successful. New record added with timestamp {timestamp}"

            return "Stock not found in portfolio"

    except Exception as e:
        return f"Error processing transaction: {e}"

def bank_transaction(client_id, amount, transaction_type='buy'):
    try:
        # Establish connection with the banking server
        banking_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        banking_socket.connect(('10.160.0.4', 12347))  # Set your banking server details

        # Send the client_id and amount to the banking server
        data = f"{transaction_type},{client_id},{amount}"
        banking_socket.send(data.encode('utf-8'))
        print(f"Data sent to bank server: {data}")
        
        # Receive response from banking server
        response = banking_socket.recv(1024).decode('utf-8')  # Reduced recv buffer size
        banking_socket.close()
        print(f"Response received from bank server: {response}")

        return response.strip() == "SUCCESS"  # Strip any whitespace and compare

    except Exception as e:
        print(f"Bank transaction error: {e}")
        return False
