import sys
import os
import sqlite3
import hashlib
import uuid
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QMessageBox, QStackedWidget,
                             QDialog, QFormLayout, QGroupBox)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont

# Import your existing components
from feedback_form import SurveyApp
from analysis_dashboard import AnalysisApp

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.resize(300, 200)
        
        # Database setup
        self.db_conn = sqlite3.connect('feedback_users.db')
        self.create_tables()
        
        # UI Setup
        layout = QVBoxLayout()
        
        form_group = QGroupBox("Login")
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        
        form_group.setLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.authenticate)
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.show_register)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        
        layout.addWidget(form_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Settings for remembering login
        self.settings = QSettings("FeedbackApp", "LoginSettings")
        self.load_saved_credentials()
    
    def create_tables(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            is_developer BOOLEAN DEFAULT 0,
            device_id TEXT
        )
        ''')
        self.db_conn.commit()
    
    def hash_password(self, password, salt):
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def authenticate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        cursor = self.db_conn.cursor()
        cursor.execute('SELECT password_hash, salt, is_developer, device_id FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        if not result:
            QMessageBox.warning(self, "Error", "Invalid username or password")
            return
        
        stored_hash, salt, is_developer, device_id = result
        input_hash = self.hash_password(password, salt)
        
        if input_hash == stored_hash:
            # Check if this is the user's usual device
            current_device_id = self.get_device_id()
            is_usual_device = (device_id == current_device_id)
            
            # Save credentials if this is their usual device
            if is_usual_device:
                self.save_credentials(username, password)
            else:
                self.settings.remove("username")
                self.settings.remove("password")
            
            self.accept()  # Close the dialog with success
            return {
                'username': username,
                'is_developer': bool(is_developer),
                'is_usual_device': is_usual_device
            }
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")
            return None
    
    def show_register(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Register")
        dialog.resize(300, 250)
        
        layout = QVBoxLayout()
        
        form_group = QGroupBox("Register New User")
        form_layout = QFormLayout()
        
        self.new_username = QLineEdit()
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.developer_check = QCheckBox("Developer Account")
        
        form_layout.addRow("Username:", self.new_username)
        form_layout.addRow("Password:", self.new_password)
        form_layout.addRow("Confirm Password:", self.confirm_password)
        form_layout.addRow(self.developer_check)
        
        form_group.setLayout(form_layout)
        
        button_layout = QHBoxLayout()
        register_button = QPushButton("Register")
        register_button.clicked.connect(lambda: self.register_user(dialog))
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(register_button)
        button_layout.addWidget(cancel_button)
        
        layout.addWidget(form_group)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def register_user(self, dialog):
        username = self.new_username.text().strip()
        password = self.new_password.text().strip()
        confirm = self.confirm_password.text().strip()
        is_developer = self.developer_check.isChecked()
        
        if not username or not password:
            QMessageBox.warning(dialog, "Error", "Username and password are required")
            return
        
        if password != confirm:
            QMessageBox.warning(dialog, "Error", "Passwords do not match")
            return
        
        cursor = self.db_conn.cursor()
        
        # Check if username exists
        cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            QMessageBox.warning(dialog, "Error", "Username already exists")
            return
        
        # Generate salt and hash password
        salt = str(uuid.uuid4())
        password_hash = self.hash_password(password, salt)
        device_id = self.get_device_id()
        
        # Insert new user
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash, salt, is_developer, device_id) VALUES (?, ?, ?, ?, ?)',
                (username, password_hash, salt, is_developer, device_id)
            )
            self.db_conn.commit()
            QMessageBox.information(dialog, "Success", "Registration successful!")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Registration failed: {str(e)}")
    
    def get_device_id(self):
        # Generate a unique ID for this device
        # This is a simplified approach - in production you might want something more robust
        return str(uuid.getnode())
    
    def save_credentials(self, username, password):
        self.settings.setValue("username", username)
        self.settings.setValue("password", password)
    
    def load_saved_credentials(self):
        username = self.settings.value("username", "")
        password = self.settings.value("password", "")
        
        if username and password:
            self.username_input.setText(username)
            self.password_input.setText(password)
    
    def closeEvent(self, event):
        self.db_conn.close()
        super().closeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Feedback Application")
        self.resize(800, 600)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QVBoxLayout(central_widget)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Login screen
        self.login_screen = LoginWindow()
        self.stacked_widget.addWidget(self.login_screen)
        
        # Main application screen
        self.main_screen = QWidget()
        self.main_screen_layout = QVBoxLayout(self.main_screen)
        self.stacked_widget.addWidget(self.main_screen)
        
        # User info display
        self.user_info_group = QGroupBox("User Information")
        self.user_info_layout = QFormLayout()
        
        self.username_label = QLabel()
        self.user_type_label = QLabel()
        self.device_label = QLabel()
        
        self.user_info_layout.addRow("Username:", self.username_label)
        self.user_info_layout.addRow("User Type:", self.user_type_label)
        self.user_info_layout.addRow("Device Status:", self.device_label)
        
        self.user_info_group.setLayout(self.user_info_layout)
        self.main_screen_layout.addWidget(self.user_info_group)
        
        # Button area
        self.button_layout = QHBoxLayout()
        
        self.feedback_button = QPushButton("Feedback Form")
        self.feedback_button.clicked.connect(self.open_feedback_form)
        
        self.analysis_button = QPushButton("Review Feedback")
        self.analysis_button.clicked.connect(self.open_analysis)
        
        self.button_layout.addWidget(self.feedback_button)
        self.button_layout.addWidget(self.analysis_button)
        
        self.main_screen_layout.addLayout(self.button_layout)
        
        # Logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        self.main_screen_layout.addWidget(self.logout_button)
        
        # Initially show login screen
        self.stacked_widget.setCurrentIndex(0)
        self.login_screen.accepted.connect(self.handle_login)
    
    def handle_login(self):
        login_result = self.login_screen.authenticate()
        if login_result:
            self.current_user = login_result
            self.update_user_display()
            self.stacked_widget.setCurrentIndex(1)
            
            # Disable analysis button if not developer
            self.analysis_button.setEnabled(self.current_user['is_developer'])
    
    def update_user_display(self):
        self.username_label.setText(self.current_user['username'])
        user_type = "Developer" if self.current_user['is_developer'] else "Regular User"
        self.user_type_label.setText(user_type)
        
        device_status = "Usual Device" if self.current_user['is_usual_device'] else "New/Unrecognized Device"
        self.device_label.setText(device_status)
    
    def open_feedback_form(self):
        self.feedback_form = SurveyApp()
        self.feedback_form.show()
    
    def open_analysis(self):
        if self.current_user.get('is_developer', False):
            self.analysis_dashboard = AnalysisApp()
            self.analysis_dashboard.show()
        else:
            QMessageBox.warning(self, "Access Denied", "Only developers can access the analysis dashboard")
    
    def logout(self):
        self.stacked_widget.setCurrentIndex(0)
        self.login_screen.username_input.clear()
        self.login_screen.password_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style and font
    app.setStyle("Fusion")
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())