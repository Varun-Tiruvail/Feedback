import sys
import os
import sqlite3
import hashlib
import platform
import uuid
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt

def get_system_id():
    """Get unique system identifier"""
    system_id = ':'.join([
        platform.node(),
        platform.machine(),
        str(uuid.getnode())  # MAC address
    ])
    return hashlib.sha256(system_id.encode()).hexdigest()

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setup_db()
        self.init_ui()

    def setup_db(self):
        """Initialize user database"""
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            system_username TEXT,
            password TEXT,
            system_id TEXT,
            is_manager INTEGER,
            manager_id TEXT
        )''')
        
        conn.commit()
        conn.close()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        
        signup_btn = QPushButton("Sign Up")
        signup_btn.clicked.connect(self.show_signup)
        
        layout.addWidget(QLabel("Login"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        layout.addWidget(signup_btn)
        
        self.setLayout(layout)

    def login(self):
        username = self.username.text()
        password = self.password.text()
        system_id = get_system_id()
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT system_id, is_manager FROM users WHERE username=? AND password=?",
            (username, hashlib.sha256(password.encode()).hexdigest())
        )
        result = cursor.fetchone()
        
        if result:
            stored_system_id, is_manager = result
            if stored_system_id == system_id:
                self.open_main_app(username, is_manager == 1)
            else:
                QMessageBox.warning(self, "Error", "Cannot login from this system")
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")
        
        conn.close()

    def show_signup(self):
        self.signup_window = SignupWindow()
        self.signup_window.show()
        self.close()

    def open_main_app(self, username, is_manager):
        from main_app import MainApp  # Import here to avoid circular imports
        self.main_app = MainApp(username, is_manager)
        self.main_app.show()
        self.close()

# ...existing code...

class SignupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign Up")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm Password")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.manager_username = QLineEdit()
        self.manager_username.setPlaceholderText("Manager Username (Optional)")

        signup_btn = QPushButton("Sign Up")
        signup_btn.clicked.connect(self.signup)

        back_btn = QPushButton("Back to Login")
        back_btn.clicked.connect(self.back_to_login)

        layout.addWidget(QLabel("Sign Up"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.confirm_password)
        layout.addWidget(self.manager_username)
        layout.addWidget(signup_btn)
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def signup(self):
        username = self.username.text()
        password = self.password.text()
        confirm_password = self.confirm_password.text()
        manager_username = self.manager_username.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all required fields")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        system_id = get_system_id()
        system_username = os.getlogin()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        try:
            # Check if username already exists
            cursor.execute("SELECT 1 FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Error", "Username already exists")
                return

            # Check if manager exists if specified
            is_manager = 0
            if manager_username:
                cursor.execute("SELECT 1 FROM users WHERE username=?", (manager_username,))
                if not cursor.fetchone():
                    QMessageBox.warning(self, "Error", "Specified manager does not exist")
                    return

            # Insert new user
            cursor.execute("""
                INSERT INTO users 
                (username, system_username, password, system_id, is_manager, manager_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                username,
                system_username,
                hashlib.sha256(password.encode()).hexdigest(),
                system_id,
                is_manager,
                manager_username if manager_username else None
            ))

            conn.commit()
            QMessageBox.information(self, "Success", "Account created successfully!")
            self.back_to_login()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
        finally:
            conn.close()

    def back_to_login(self):
        self.login_window = AuthWindow()
        self.login_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())