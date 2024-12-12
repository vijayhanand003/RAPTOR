import sys
from tkinter import messagebox
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
import firebase_admin
from firebase_admin import credentials, firestore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime
import mplfinance as mpf
import mplcursors
import pandas as pd
import socket
import json
from buySell.buysell import buy_sell,bank_transaction
cred = credentials.Certificate(r"stock-fe319-10e86b8008ac.json")  # Path to the service account key

db = firestore.client()
from qtpy.QtWidgets import QInputDialog, QMessageBox

colors = {
    "background": "#E0F7FA",
    "primary": "#00796B",
    "secondary": "#004D40",
    "grid": "#B2DFDB",
    "text": "#333333"
}

def send_request(self, client_data):
    try:
        self.client_socket.send(client_data.encode('utf-8'))
        response = self.client_socket.recv(12347).decode('utf-8')
        return response  # Return the response for further processing
        
    except Exception as e:
        print(f"Error: {e}")
        return ""

def get_stock_data(self, symbol):
    # Prepare the request in the format GET_STOCK_DATA:SYMBOL
    request_data = f"GET_STOCK_DATA,{symbol}"
    response = send_request(self, request_data)

    if response:
        return json.loads(response)  # Handle the received string response
    else:
        return None

def get_historical_stock_data(self, symbol):
    stock_ref = db.collection("stocks").document(symbol)
    stock_data = stock_ref.get()

    if stock_data.exists:
        data_dict = stock_data.to_dict()
        historical_data = []
        for date_key, data in data_dict.items():
            if isinstance(data, dict) and "date" in data:
                historical_data.append((datetime.strptime(date_key, '%Y-%m-%d'), data))
        historical_data.sort(key=lambda x: x[0])
        return historical_data[-100:]  # Return the last 100 entries
    else:
        return None


class StockDashboard(QMainWindow):
    def __init__(self, symbol,email,previous_window=None):

        super().__init__()

        self.client_socket = None
        self.connect_to_server()
        self.email=email
        self.symbol = symbol
        self.previous_window = previous_window  # Save the reference to the previous window
        self.price=0
        self.setWindowTitle(f"Real-Time Stock Dashboard - {self.symbol}")
        self.setGeometry(100, 100, 1080, 720)  # Increased the height for larger plot area

        self.current_plot = "candle"  # Track current plot type (candle or line_chart)

        main_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(20, 20, 20, 20)

        self.back_button = QPushButton("Back", self)  # Back Button
        self.back_button.setFixedHeight(40)
        self.back_button.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                font-size: 16px;
                background-color: {colors['primary']};
                color: white;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {colors['secondary']};
            }}
        """)
        self.back_button.clicked.connect(self.go_back)
        search_layout.addWidget(self.back_button)

        self.toggle_button = QPushButton("Switch to line_chart", self)  # Button to switch plots
        self.toggle_button.setFixedHeight(40)
        self.toggle_button.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                font-size: 16px;
                background-color: {colors['primary']};
                color: white;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {colors['secondary']};
            }}
        """)
        self.toggle_button.clicked.connect(self.toggle_plot)
        search_layout.addWidget(self.toggle_button)

        main_layout.addLayout(search_layout)

        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)  # Adjusted spacer height
        main_layout.addSpacerItem(spacer)

        self.stock_data_label = QLabel(self)
        self.stock_data_label.setAlignment(Qt.AlignCenter)
        self.stock_data_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                padding: 20px;
                color: {colors['secondary']};
                border: 1px solid {colors['primary']};
                border-radius: 10px;
                background-color: {colors['background']};
            }}
        """)
        main_layout.addWidget(self.stock_data_label)

        self.buttons_layout = QHBoxLayout()

        self.buy_button = QPushButton("BUY", self)
        self.buy_button.setFixedHeight(50)
        self.buy_button.setFixedWidth(200)
        self.buy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #28a745;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
        """)
        self.buy_button.clicked.connect(self.buy_stock)

        self.sell_button = QPushButton("SELL", self)
        self.sell_button.setFixedHeight(50)
        self.sell_button.setFixedWidth(200)
        self.sell_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #dc3545;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: #c82333;
            }}
        """)
        self.sell_button.clicked.connect(self.sell_stock)

        self.buttons_layout.addWidget(self.buy_button)
        self.buttons_layout.addWidget(self.sell_button)

        main_layout.addLayout(self.buttons_layout)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(900, 700)  # Increased minimum height
        self.canvas.setStyleSheet("background-color: white;")
        main_layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Fetch the stock data automatically when window opens
        self.fetch_stock_data()

    def connect_to_server(self):
        """Establish connection to the server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("127.0.0.1", 12347))
        except Exception as e:
            messagebox.critical(self, "Connection Error", f"Failed to connect to server: {e}")
            self.close()

    def fetch_stock_data(self):
        symbol = self.symbol.upper()

        stock_data = get_stock_data(self,symbol)
        if stock_data:
            self.display_stock_data(symbol, stock_data)
        else:
            self.stock_data_label.setText(f"No data available for {symbol}")

        historical_data = get_historical_stock_data(self,symbol)
        if historical_data:
            self.display_stock_graph(symbol, historical_data)
        else:
            self.ax.clear()
            self.ax.set_title("No historical data available")
            self.canvas.draw()

    def display_stock_data(self, symbol, stock_data):
        latest_entry = list(stock_data.values())[-1]
        self.stock_data_label.setText(
            f"Stock: {symbol}\n"
            f"Price: ${latest_entry['close']}\n"
            f"Volume: {latest_entry['volume']}\n"
            f"Open: ${latest_entry['open']}\n"
            f"High: ${latest_entry['high']}\n"
            f"Low: ${latest_entry['low']}\n"
            f"Close: ${latest_entry['close']}\n"
        )
        self.price=latest_entry['open']

    def buy_stock(self):
    # Ask the user for the quantity of stocks to buy
        quantity, ok = QInputDialog.getInt(self, "Buy Stock", "Enter quantity:", 1, 1)

        if ok:
            # Assume the following variables are set in the class or passed to this function
            email = self.email  # User's email
            stock = self.symbol  # Stock symbol
            price = self.price  # Current stock price
            transaction_type = "buy"  # This is a buy transaction
            
            # Call the buy_sell function with the input values
            result = buy_sell(email, stock, quantity, price, transaction_type)

            # Display the return value of buy_sell in a message box
            QMessageBox.information(self, "Transaction Result", f"Result: {result}")

            # Update the stock data label to reflect the buy order
            self.stock_data_label.setText(f"{result}")

    def sell_stock(self):
        # Ask the user for the quantity of stocks to sell
        quantity, ok = QInputDialog.getInt(self, "Sell Stock", "Enter quantity:", 1, 1)

        if ok:
            # Assume the following variables are set in the class or passed to this function
            email = self.email  # User's email
            stock = self.symbol  # Stock symbol
            price = self.price  # Current stock price
            transaction_type = "sell"  # This is a sell transaction
            
            # Call the buy_sell function with the input values
            result = buy_sell(email, stock, quantity, price, transaction_type)

            # Display the return value of buy_sell in a message box
            QMessageBox.information(self, "Transaction Result", f"Result: {result}")

            # Update the stock data label to reflect the sell order
            self.stock_data_label.setText(f"{result}")
            
    def display_stock_graph(self, symbol, historical_data):
        self.ax.clear()

        dates = [data[0] for data in historical_data]
        opens = [data[1]['open'] for data in historical_data]
        highs = [data[1]['high'] for data in historical_data]
        lows = [data[1]['low'] for data in historical_data]
        closes = [data[1]['close'] for data in historical_data]
        volumes = [data[1]['volume'] for data in historical_data]

        stock_data = pd.DataFrame({
            'Date': dates,
            'Open': opens,
            'High': highs,
            'Low': lows,
            'Close': closes,
            'Volume': volumes
        })
        stock_data.set_index('Date', inplace=True)

        if self.current_plot == "candle":
            self.plot_candlestick(stock_data, symbol)
        else:
            self.plot_line_chart(stock_data, symbol)

        self.canvas.draw()

    def plot_candlestick(self, stock_data, symbol):
        self.ax = self.figure.add_subplot(1, 1, 1)  # Make it a single plot

        mpf.plot(
            stock_data,
            type='candle',
            ax=self.ax,
            style='yahoo',
            show_nontrading=True
        )

        self.ax.grid(True, linestyle='--', linewidth=0.5, color=colors["grid"])
        self.ax.set_title(f"{symbol} Stock Price (Last 100 Entries)", fontsize=14, color=colors["secondary"])
        self.ax.set_xlabel("Date", fontsize=12, color=colors["text"])
        self.ax.set_ylabel("Price ($)", fontsize=12, color=colors["text"])

        mplcursors.cursor(self.ax.collections).connect("add", lambda sel: sel.annotation.set_text(
            f'Date: {stock_data.index[sel.index]}\nClose: ${stock_data["Close"].iloc[sel.index]}\nVolume: {stock_data["Volume"].iloc[sel.index]}'
        ))

        self.figure.tight_layout(pad=3.0)

    def plot_line_chart(self, stock_data, symbol):
        self.ax.clear()

        self.ax.plot(stock_data.index, stock_data['Close'], color='green', linewidth=2)
        self.ax.fill_between(stock_data.index, stock_data['Close'], color='green', alpha=0.1)  # Green gradient fill

        self.ax.set_title(f"{symbol} Closing Price Trend", fontsize=14, color=colors["secondary"])
        self.ax.set_xlabel("Date", fontsize=12, color=colors["text"])
        self.ax.set_ylabel("Price ($)", fontsize=12, color=colors["text"])
        self.ax.grid(True, linestyle='--', linewidth=0.5, color=colors["grid"])

        self.figure.tight_layout(pad=3.0)

    def toggle_plot(self):
        if self.current_plot == "candle":
            self.current_plot = "line_chart"
            self.toggle_button.setText("Switch to Candlestick")
        else:
            self.current_plot = "candle"
            self.toggle_button.setText("Switch to line_chart")

        # Fetch and update the plot with the current data
        historical_data = get_historical_stock_data(self,self.symbol)
        if historical_data:
            self.display_stock_graph(self.symbol, historical_data)

    def go_back(self):
        if self.previous_window:
            self.previous_window.show()  # Show the previous window
        self.close()  # Close the current dashboard window
