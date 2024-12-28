import sys
import socket
from qtpy.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
                            QStackedWidget, QMessageBox, QTabWidget, QListWidget, QHBoxLayout,QSpacerItem,QSizePolicy)
from qtpy.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from watchlist.watchlistwindow import WatchlistWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modern Login & Signup")
        self.setGeometry(100, 100, 1080, 720)

        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                color: #333333;
                font-size: 16px;
            }
            QPushButton {
                background-color: #7289DA;
                color: #ffffff;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7289DA;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                padding: 10px;
                border-radius: 10px;
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
                color: #6c757d;
            }
        """)

        self.client_socket = None
        self.connect_to_server()

        self.second_client_socket = None
        self.connect_to_second_server()
        

        self.stacked_widget = QStackedWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)

        self.create_login_ui()
        self.create_signup_ui()
        self.stacked_widget.setCurrentIndex(0)

    def connect_to_server(self):
        """Establish connection to the server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("127.0.0.1", 12345))
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to server: {e}")
            self.close()

    def connect_to_second_server(self):
        """Establish connection to the second server."""
        try:
            self.second_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.second_client_socket.connect(("127.0.0.1", 12346))
        except Exception as e:
            QMessageBox.critical(self, "Second Connection Error", f"Failed to connect to second server: {e}")
            self.close()

    def create_login_ui(self):
        login_layout = QVBoxLayout()

        login_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add the title "Project Raptor" at the center of the window
        project_title = QLabel("Raptor", self)
        project_title.setAlignment(Qt.AlignCenter)
        project_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom:100px; color: #333333;")
        login_layout.addWidget(project_title, alignment=Qt.AlignCenter)

        # Center align fields
        self.login_email = QLineEdit(self)
        self.login_email.setPlaceholderText("Email")
        self.login_email.setFixedWidth(400)
        login_layout.addWidget(self.login_email, alignment=Qt.AlignCenter)

        self.login_password = QLineEdit(self)
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setFixedWidth(400)
        login_layout.addWidget(self.login_password, alignment=Qt.AlignCenter)

        login_button = QPushButton("Login", self)
        login_button.setFixedWidth(400)
        login_button.clicked.connect(self.login_user)
        login_layout.addWidget(login_button, alignment=Qt.AlignCenter)

        switch_to_signup_button = QPushButton("Don't have an account? Sign Up", self)
        switch_to_signup_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        switch_to_signup_button.setFixedWidth(400)
        login_layout.addWidget(switch_to_signup_button, alignment=Qt.AlignCenter)

        # Spacer at the bottom to center the content
        login_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        login_widget = QWidget()
        login_widget.setLayout(login_layout)
        self.stacked_widget.addWidget(login_widget)

    def create_signup_ui(self):
        signup_layout = QVBoxLayout()

        # Spacer at the top to center the content
        signup_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add the title "Project Raptor" at the center of the window
        project_title = QLabel("TradeX", self)
        project_title.setAlignment(Qt.AlignCenter)
        project_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 100px; color: #333333;")
        signup_layout.addWidget(project_title, alignment=Qt.AlignCenter)

        # title = QLabel("Sign Up", self)
        # title.setAlignment(Qt.AlignCenter)
        # title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333333;")
        # signup_layout.addWidget(title, alignment=Qt.AlignCenter)

        # Center align fields
        self.signup_name = QLineEdit(self)
        self.signup_name.setPlaceholderText("Name")
        self.signup_name.setFixedWidth(400)
        signup_layout.addWidget(self.signup_name, alignment=Qt.AlignCenter)

        self.signup_email = QLineEdit(self)
        self.signup_email.setPlaceholderText("Email")
        self.signup_email.setFixedWidth(400)
        signup_layout.addWidget(self.signup_email, alignment=Qt.AlignCenter)

        self.signup_password = QLineEdit(self)
        self.signup_password.setPlaceholderText("Password")
        self.signup_password.setEchoMode(QLineEdit.Password)
        self.signup_password.setFixedWidth(400)
        signup_layout.addWidget(self.signup_password, alignment=Qt.AlignCenter)

        signup_button = QPushButton("Sign Up", self)
        signup_button.setFixedWidth(400)
        signup_button.clicked.connect(self.signup_user)
        signup_layout.addWidget(signup_button, alignment=Qt.AlignCenter)

        switch_to_login_button = QPushButton("Already have an account? Login", self)
        switch_to_login_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        switch_to_login_button.setFixedWidth(400)
        signup_layout.addWidget(switch_to_login_button, alignment=Qt.AlignCenter)

        # Spacer at the bottom to center the content
        signup_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        signup_widget = QWidget()
        signup_widget.setLayout(signup_layout)
        self.stacked_widget.addWidget(signup_widget)



    def login_user(self):
        email = self.login_email.text()
        password = self.login_password.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Both fields are required.")
            return

        client_data = f"login,{email},{password}"
        response = self.send_request(client_data)
        
        if "Login successful" in response:
            # Open Watchlist window
            watchlist_data = response.split(',')
            self.open_watchlist_window(email, watchlist_data[1][1:-1].split(", "))  # Convert string to list
        else:
            QMessageBox.warning(self, "Login Failed", response)

    def signup_user(self):
        name = self.signup_name.text()
        email = self.signup_email.text()
        password = self.signup_password.text()

        if not name or not email or not password:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        client_data = f"signup,{name},{email},{password}"
        response = self.send_request(client_data)
        QMessageBox.information(self, "Server Response", response)

    def send_request(self, client_data):
        try:
            self.client_socket.send(client_data.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            return response  # Return the response for further processing
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Error: {e}")
            return ""

    
    def open_watchlist_window(self, email, watchlist):
        self.watchlist_window = WatchlistWindow(email, self.client_socket, watchlist,self.second_client_socket)
        self.watchlist_window.show()
        self.close()  # Close the login window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
