import sys
import os
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                            QTabWidget)
from PyQt6.QtCore import Qt
from FeedbackApp import SurveyApp
from analysisnew3 import AnalysisApp
class MainApp(QMainWindow):
    def __init__(self, username, is_manager):
        super().__init__()
        self.username = username
        self.is_manager = is_manager
        self.init_ui()
        self.load_user_data()

    def init_ui(self):
        self.setWindowTitle("Feedback System")
        self.setMinimumSize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create navigation sidebar
        self.create_sidebar(main_layout)

        # Create main content area with tabs
        self.create_main_content(main_layout)

    def create_sidebar(self, main_layout):
        sidebar = QWidget()
        sidebar.setMaximumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)

        # User info section
        self.user_label = QLabel(f"User: {self.username}")
        self.system_label = QLabel(f"System: {os.getlogin()}")
        
        sidebar_layout.addWidget(self.user_label)
        sidebar_layout.addWidget(self.system_label)
        sidebar_layout.addSpacing(20)

        # Navigation buttons
        self.feedback_btn = QPushButton("Feedback")
        self.score_btn = QPushButton("Score Chart")
        
        self.feedback_btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(0))
        self.score_btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(1))

        sidebar_layout.addWidget(self.feedback_btn)
        sidebar_layout.addWidget(self.score_btn)
        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar)

    def create_main_content(self, main_layout):
        self.tab_widget = QTabWidget()
        
        # Feedback tab (direct)
        self.feedback_tab = QWidget()
        feedback_layout = QVBoxLayout(self.feedback_tab)
        self.feedback_widget = SurveyApp(self.username)
        feedback_layout.addWidget(self.feedback_widget)

        # Score chart tab (with direct/indirect sections if manager)
        self.score_tab = QWidget()
        score_layout = QVBoxLayout(self.score_tab)
        
        if self.is_manager:
            score_tabs = QTabWidget()
            
            # Direct scores
            direct_tab = AnalysisApp(self.username, False)
            score_tabs.addTab(direct_tab, "Direct Reports")
            
            # Indirect scores
            indirect_tab = AnalysisApp(self.username, True)
            score_tabs.addTab(indirect_tab, "Indirect Reports")
            
            score_layout.addWidget(score_tabs)
        else:
            self.analysis_widget = AnalysisApp(self.username, False)
            score_layout.addWidget(self.analysis_widget)

        self.tab_widget.addTab(self.feedback_tab, "Feedback")
        self.tab_widget.addTab(self.score_tab, "Score Chart")

        main_layout.addWidget(self.tab_widget)

    def load_user_data(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Check number of responses for score visibility
        cursor.execute("""
            SELECT COUNT(*) FROM responses WHERE username = ?
        """, (self.username,))
        
        response_count = cursor.fetchone()[0]
        
        # Hide score chart if less than 5 responses and not a manager
        if response_count < 5 and not self.is_manager:
            self.score_btn.hide()
            self.tab_widget.removeTab(1)
            
        conn.close()