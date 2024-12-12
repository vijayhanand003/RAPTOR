import sys
import socket
from qtpy.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
                            QMessageBox, QTabWidget, QListWidget, QHBoxLayout)
from qtpy.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5.QtCore import QTimer
from stockfunc.disstock import  StockDashboard


class WatchlistWindow(QWidget):
    def __init__(self, email, client_socket, watchlist, second_client_socket):
        super().__init__()

        self.client_socket = client_socket
        self.second_client_socket = second_client_socket
        self.current_user_email = email
        self.watchlist = watchlist

        self.setWindowTitle("Watchlist, Funds, and Portfolio")
        self.setGeometry(100, 100, 1080, 720)

        # Apply custom styles
        self.setStyleSheet("""
            QWidget {
                background-color: #2C2F33;
                color: #FFFFFF;
            }
            QTabWidget::pane {
                border: 1px solid #3F444A;
                background-color: #23272A;
            }
            QTabBar::tab {
                background: #2C2F33;
                color: #FFFFFF;
                padding: 10px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: #7289DA;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #7289DA;
                color: #FFFFFF;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #99AAB5;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #3F444A;
                border-radius: 5px;
                background-color: #23272A;
                color: #FFFFFF;
            }
            QTableWidget {
                background-color: #2C2F33;
                alternate-background-color: #3F444A;
                gridline-color: #7289DA;
            }
            QHeaderView::section {
                background-color: #7289DA;
                color: #FFFFFF;
                padding: 5px;
            }
            QListWidget {
                background-color: #23272A;
                color: #FFFFFF;
                border: 1px solid #3F444A;
                padding: 5px;
            }
        """)

        # Set up the tab widget
        self.tab_widget = QTabWidget(self)

        self.create_watchlist_tab()
        self.create_funds_tab()
        self.create_portfolio_tab()

        self.tab_widget.addTab(self.watchlist_tab, "Watchlist")
        self.tab_widget.addTab(self.funds_tab, "Funds")
        self.tab_widget.addTab(self.portfolio_tab, "Portfolio")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_widget)

    def send_second_request(self, client_data):
        try:
            self.second_client_socket.send(client_data.encode('utf-8'))
            response = self.second_client_socket.recv(1024).decode('utf-8')
            return response  # Return the response for further processing
        except Exception as e:
            QMessageBox.critical(self, "Second Connection Error", f"Error: {e}")
            return ""

    def create_watchlist_tab(self):
        self.watchlist_tab = QWidget()
        layout = QVBoxLayout(self.watchlist_tab)

        self.stock_search = QLineEdit(self)
        self.stock_search.setPlaceholderText("Search for stocks...")

        # Connect the textChanged signal to the search_stock method for real-time search
        self.stock_search.textChanged.connect(self.search_stock)
        layout.addWidget(self.stock_search)

        search_button = QPushButton("Search", self)
        search_button.clicked.connect(self.search_stock)  # In case user wants to search manually
        layout.addWidget(search_button)

        # Add a label for current watchlist
        current_watchlist_label = QLabel("Search results", self)
        layout.addWidget(current_watchlist_label)

        # Add a QTableWidget to display stock names and prices
        self.current_watchlist = QTableWidget(self)
        self.current_watchlist.setColumnCount(2)  # One column for stock names, one for prices
        self.current_watchlist.setHorizontalHeaderLabels(["Stock", "Price"])
        self.current_watchlist.cellClicked.connect(self.on_stock_clicked)  # Connect cellClicked signal

        # Fetch watchlist and start price updates
        self.fetch_watchlist()  # Initial fetch when the tab is created
        self.start_price_updates()  # Start periodic updates every 10 seconds

        # Watchlist display (for searched results)
        self.watchlist_display = QListWidget(self)
        layout.addWidget(self.watchlist_display)
        current_watchlist_label = QLabel("Current Watchlist", self)
        layout.addWidget(current_watchlist_label)
        layout.addWidget(self.current_watchlist)

        # Add stock to the watchlist button
        add_button = QPushButton("Add to Watchlist", self)
        add_button.clicked.connect(self.add_to_watchlist)
        layout.addWidget(add_button)

    def fetch_watchlist(self):
        """Fetch the watchlist for the current user from the server."""
        try:
            # Prepare request data for the server
            client_data = f"fetch_watchlist,{self.current_user_email}"
            
            # Send the request to the server using the first connection
            response = self.send_second_request(client_data)
            
            # Assuming the server response is a single string like: "stock1,price1,stock2,price2,..."
            if response:
                # Split the response by commas
                stock_data = response.split(',')
                print(stock_data)

                # Clear the current table contents before adding new items
                self.current_watchlist.setRowCount(0)
                
                if stock_data[0] == "User does not exist.":
                    row_count = self.current_watchlist.rowCount()
                    self.current_watchlist.insertRow(row_count)
                    self.current_watchlist.setItem(row_count, 0, QTableWidgetItem("No stocks in watchlist"))
                else:
                    # Iterate over the stock data in pairs (stock_name, stock_price)
                    for i in range(0, len(stock_data), 2):
                        stock_name = stock_data[i]
                        stock_price = stock_data[i + 1]
                        
                        row_count = self.current_watchlist.rowCount()
                        self.current_watchlist.insertRow(row_count)
                        self.current_watchlist.setItem(row_count, 0, QTableWidgetItem(stock_name))
                        self.current_watchlist.setItem(row_count, 1, QTableWidgetItem(f"${float(stock_price):.2f}"))
        except Exception as e:
            QMessageBox.critical(self, "Fetch Error", f"Error fetching watchlist: {e}")

    def start_price_updates(self):
        """Start periodic updates for stock prices every 10 seconds."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_watchlist)  # Fetch updated stock prices every 10 seconds
        self.timer.start(50000)  # 10,000 milliseconds = 10 seconds

    def create_portfolio_tab(self):
        self.portfolio_tab = QWidget()
        layout = QVBoxLayout(self.portfolio_tab)

        self.portfolio_display = QListWidget(self)
        layout.addWidget(self.portfolio_display)

        # Button to update and fetch the latest portfolio from the server
        update_portfolio_button = QPushButton("Update Portfolio", self)
        update_portfolio_button.clicked.connect(self.update_portfolio)
        layout.addWidget(update_portfolio_button)

    def update_portfolio(self):
        # Format the portfolio request as expected by the server: Portfolio,{clientId}
        client_data = f"Portfolio,{self.current_user_email}"
        
        # Send the formatted request to the server and handle the response
        response = self.send_request(client_data)

        if response.startswith("Error"):
            QMessageBox.critical(self, "Portfolio Error", response)
        else:
            self.portfolio_display.clear()
            portfolio_items = response.split(', ') 
            self.portfolio_display.addItems(portfolio_items)

    def create_funds_tab(self):
            """Create the funds tab with a button to update the user's funds from the server."""
            self.funds_tab = QWidget()
            layout = QVBoxLayout(self.funds_tab)

            # Label for current funds
            self.funds_label = QLabel("Funds: Loading...", self)
            layout.addWidget(self.funds_label)

            # Button to update funds
            update_funds_button = QPushButton("Update Funds", self)
            update_funds_button.clicked.connect(self.update_funds)  # Connect to the function
            layout.addWidget(update_funds_button)

    def update_funds(self):
        """Send a request to the server to fetch the user's funds."""
        try:
            # Format the funds request with the user's email as the parameter
            client_data = f"display_funds,{self.current_user_email}"
            
            # Send the request to the server via the primary connection
            response = self.send_request(client_data)

            # Handle the server's response, assuming it returns a simple float representing the funds
            if response.startswith("Error"):
                QMessageBox.critical(self, "Funds Error", response)
            else:
                self.funds_label.setText(f"Funds: ${float(response):.2f}")
        except Exception as e:
            QMessageBox.critical(self, "Funds Request Error", f"Error updating funds: {e}")


    def search_stock(self):
        stock_name = self.stock_search.text()
        if stock_name:
            client_data = f"search,{stock_name}"
            response = self.send_request(client_data)
            self.update_search_suggestions(response)

    def update_search_suggestions(self, response):
        stock_suggestions = response.split(', ')
        self.watchlist_display.clear()
        self.watchlist_display.addItems(stock_suggestions)

    def add_to_watchlist(self):
        selected_items = self.watchlist_display.selectedItems()
        
        if selected_items:
            stock_name = selected_items[0].text()
            client_data = f"add_to_watchlist,{self.current_user_email},{stock_name}"
            
            response = self.send_request(client_data)

            if response.startswith("Stock added successfully"):
                price = response.split(",")[1].strip()
                
                row_count = self.current_watchlist.rowCount()
                self.current_watchlist.insertRow(row_count)
                self.current_watchlist.setItem(row_count, 0, QTableWidgetItem(stock_name))
                self.current_watchlist.setItem(row_count, 1, QTableWidgetItem(f"${price}"))

                QMessageBox.information(self, "Server Response", f"{stock_name} added to watchlist with price ${price}")
            else:
                QMessageBox.warning(self, "Server Error", response)

    def send_request(self, client_data):
        try:
            self.client_socket.send(client_data.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            return response
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Error: {e}")
            return ""

    def on_stock_clicked(self, row, column):
        """Handle the event when a stock is clicked in the table."""
        stock_name = self.current_watchlist.item(row, 0).text()
        self.open_dashboard(stock_name)

    def open_dashboard(self,stock_name):
        """Opens the StockDashboard window."""
        self.dashboard_window = StockDashboard(stock_name,self.current_user_email,self)  # Initialize the dashboard
        self.dashboard_window.show()  # Show the StockDashboard window
        self.hide()