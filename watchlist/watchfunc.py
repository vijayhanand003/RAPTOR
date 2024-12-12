import socket
import threading
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("dharun.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

def handle_search(stock_name):
    print(f"Searching for stocks starting with: {stock_name}")
    stocks_collection = db.collection('stock_id')

    # Convert stock_name to uppercase to ensure consistency if stored as uppercase
    stock_name_upper = stock_name.upper()
    
    # Set up filters to capture the range of names starting with stock_name
    query = stocks_collection.where('stock_name', '>=', stock_name_upper).where('stock_name', '<', stock_name_upper + '\uf8ff')
    
    # Fetch matching stocks
    matching_stocks = list(query.stream())  # Convert to list to check for emptiness

    if not matching_stocks:
        return "No matching stocks found."
    
    # Prepare the response using the correct field name
    stock_list = [stock.to_dict()['stock_name'] for stock in matching_stocks]  # Ensure field name matches
    return ', '.join(stock_list)


def handle_fetch_watchlist(email):
    try:
        # Fetch the user's document from the 'client' collection based on the email
        user_doc = db.collection('client').where('email', '==', email).get()
        
        if not user_doc:
            return "User does not exist."
        
        # Get the 'watchlist' field which contains a list of stock symbols
        for doc in user_doc:
            user_data = doc.to_dict()
            watchlist = user_data.get('watchlist', [])
        
        if not watchlist:
            return "No stocks in watchlist."
        
        stock_data = []

        # Fetch each stock's price from the 'stocks' collection
        for stock_symbol in watchlist:
            stock_ref = db.collection('stocks').document(stock_symbol)
             # Fetch the document
            doc = stock_ref.get()

            if doc.exists:
                data = doc.to_dict()
                #print(data)
                # Retrieve the 'date' map field
                date_map = data
        
                if date_map:
                    # Sort the keys (dates) in descending order
                    sorted_dates = sorted(date_map.keys(), reverse=True)

                    # Get the latest date and its corresponding close value
                    latest_date = sorted_dates[0]
                    latest_close = date_map[latest_date]['close']
                    
                    stock_data.append(f"{stock_symbol},{latest_close}")
        
        # Return the watchlist with stock names and prices as a semicolon-separated string
        return ",".join(stock_data)
    
    except Exception as e:
        return f"Error fetching watchlist: {e}"