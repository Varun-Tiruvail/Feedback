import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PyQt6.QtCore import Qt
import sqlite3
import os
from FeedbackApp import SurveyApp
from analysisnew3 import AnalysisApp

class MainApp(QMainWindow):
    def __init__(self, username, is_manager):
        super().__init__()
        self.username = username
        self.is_manager = is_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Feedback System")
        self.setMinimumSize(1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create navigation sidebar
        sidebar = QWidget()
        sidebar.setMaximumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)

        # Add user info
        user_label = QLabel(f"User: {self.username}")
        system_user = os.getlogin()
        system_label = QLabel(f"System: {system_user}")

        sidebar_layout.addWidget(user_label)
        sidebar_layout.addWidget(system_label)
        sidebar_layout.addSpacing(20)

        # Add navigation buttons
        self.feedback_btn = QPushButton("Feedback")
        self.feedback_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.analysis_btn = QPushButton("Score Chart")
        self.analysis_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        sidebar_layout.addWidget(self.feedback_btn)
        sidebar_layout.addWidget(self.analysis_btn)
        sidebar_layout.addStretch()

        # Create stacked widget for main content
        self.stack = QStackedWidget()
        self.survey_app = SurveyApp(self.username)
        self.analysis_app = AnalysisApp(self.username, self.is_manager)

        self.stack.addWidget(self.survey_app)
        self.stack.addWidget(self.analysis_app)

        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        # Check if analysis should be visible
        self.update_analysis_visibility()

    def update_analysis_visibility(self):
        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM responses 
            WHERE user_id = ?
        """, (self.username,))
        
        count = cursor.fetchone()[0]
        conn.close()

        self.analysis_btn.setVisible(count >= 5 or self.is_manager)