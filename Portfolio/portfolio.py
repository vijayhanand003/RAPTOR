import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("dharun.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

def get_client_id(email):
    try:
        # Query the 'client' collection to find the client ID based on the email
        client_ref = db.collection('client').where('email', '==', email).limit(1).get()
        if client_ref:
            client_id = client_ref[0].to_dict().get('clientId')
            return client_id
        else:
            return None
    except Exception as e:
        return f"An error occurred while retrieving the client ID: {e}"

def update_portfolio(email, stock_name, quantity, buy_price):
    try:
        # First, get the client ID using the email
        clientId = get_client_id(email)
        if not clientId:
            return "Client ID not found for this email."

        # Reference to the client's portfolio
        portfolio_ref = db.collection('Portfolio').document(clientId)

        # Get the current portfolio data
        portfolio = portfolio_ref.get().to_dict()
        holdings = portfolio.get('Holdings', []) if portfolio else []

        stock_found = False
        for stock in holdings:
            if stock['stock_name'] == stock_name:
                # Update stock quantity and calculate average price
                total_quantity = stock['quantity'] + quantity
                stock['buy_price'] = (stock['buy_price'] * stock['quantity'] + buy_price * quantity) / total_quantity
                stock['quantity'] = total_quantity
                stock_found = True
                break

        # If the stock is not found in holdings, add a new entry
        if not stock_found:
            holdings.append({
                'stock_name': stock_name,
                'quantity': quantity,
                'buy_price': buy_price
            })

        # Update the portfolio with new holdings
        portfolio_ref.set({'Holdings': holdings}, merge=True)

        return "Portfolio updated successfully"
    except Exception as e:
        return f"An error occurred while updating the portfolio: {e}"

def fetch_current_price(stock_name):
    """
    Fetch the latest stock price (open price) for the given stock_name from Firestore.
    We will navigate to the 'stocks' collection, find the stock document, and retrieve
    the most recent 'open' price.
    """
    try:
        # Reference to the 'stocks' collection and specific stock document by name
        stock_ref = db.collection('stocks').document(stock_name)
        stock_data = stock_ref.get().to_dict()

        if not stock_data:
            return f"Stock {stock_name} not found in the database."

        # Get all the date entries and find the last available date
        sorted_dates = sorted(stock_data.keys(), reverse=True)  # Sort the dates in descending order
        last_date = sorted_dates[0]  # The most recent date

        # Retrieve the 'open' price for the last date
        open_price = stock_data[last_date]['open']
        
        return open_price

    except Exception as e:
        return f"An error occurred while fetching the current price: {e}"


def display_portfolio(email):
    try:
        # First, get the client ID using the email
        clientId = get_client_id(email)
        if not clientId:
            return "Client ID not found for this email."

        # Reference to the client's portfolio
        portfolio_ref = db.collection('Portfolio').document(clientId)

        # Fetch the portfolio data
        portfolio = portfolio_ref.get().to_dict()

        if not portfolio:
            return "No portfolio data found for this client."

        # Get the holdings from the portfolio
        holdings = portfolio.get('Holdings', [])
        
        if not holdings:
            return "The portfolio is currently empty."

        # Format the portfolio data for display
        portfolio_display = []
        total_profit_loss = 0
        for stock in holdings:
            stock_name = stock['stock_name']
            quantity = stock['quantity']
            buy_price = stock['buy_price']
            
            # Fetch the current price dynamically (e.g., from an API)
            current_price = fetch_current_price(stock_name)
            
            # Calculate profit/loss for each stock
            profit_loss = (current_price - buy_price) * quantity
            total_profit_loss += profit_loss

            portfolio_display.append(
                f"Stock: {stock_name}, Quantity: {quantity}, Buy Price: {buy_price:.2f}, "
                f"Current Price: {current_price:.2f}, Profit/Loss: {profit_loss:.2f}"
            )

        # Add total profit/loss to the display
        portfolio_display.append(f"Total Portfolio Profit/Loss: {total_profit_loss:.2f}")

        # Return formatted portfolio data
        return "\n".join(portfolio_display)

    except Exception as e:
        return f"An error occurred while retrieving the portfolio: {e}"

