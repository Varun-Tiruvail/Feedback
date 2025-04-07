import sys
import sqlite3
import datetime
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QLabel, QRadioButton, QButtonGroup, QScrollArea,
                            QPushButton, QLineEdit, QFormLayout, QMessageBox,
                            QGroupBox)
from PyQt6.QtCore import Qt

class SurveyApp(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Feedback Survey Form")
        self.resize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        # Load questions from Excel
        try:
            self.questions_df = pd.read_excel('survey_questions.xlsx')
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "survey_questions.xlsx file not found!")
            return

        main_layout = QVBoxLayout()
        
        # Create tabs for different categories
        self.tabs = QTabWidget()
        self.categories = ["Cultural", "Development", "Ways of Working"]
        self.responses = {}
        
        for category in self.categories:
            tab = self.create_category_tab(category)
            self.tabs.addTab(tab, category)
            
        # Submit button
        self.submit_button = QPushButton("Submit Feedback")
        self.submit_button.clicked.connect(self.submit_survey)
        
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.submit_button)
        self.setLayout(main_layout)

    def create_category_tab(self, category):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Filter questions for this category
        category_questions = self.questions_df[
            self.questions_df['Category'] == category
        ]
        
        for _, row in category_questions.iterrows():
            q_id = row['QuestionID']
            question_text = row['Question']
            
            group_box = QGroupBox(question_text)
            group_layout = QVBoxLayout()
            
            # Create radio buttons for options
            option_group = QButtonGroup(self)
            self.responses[q_id] = None
            
            for i in range(1, 5):
                option_text = row[f'Option{i}']
                radio = QRadioButton(option_text)
                radio.setObjectName(f"{q_id}_{i}")
                radio.toggled.connect(self.on_radio_toggled)
                option_group.addButton(radio)
                group_layout.addWidget(radio)
            
            group_box.setLayout(group_layout)
            layout.addWidget(group_box)
        
        scroll.setWidget(container)
        return scroll

    def on_radio_toggled(self):
        sender = self.sender()
        if sender.isChecked():
            q_id, value = sender.objectName().split('_')
            self.responses[q_id] = int(value)

    def submit_survey(self):
        # Check for unanswered questions
        unanswered = [q_id for q_id, resp in self.responses.items() if resp is None]
        
        if unanswered:
            msg = f"You have {len(unanswered)} unanswered questions. Continue anyway?"
            reply = QMessageBox.question(self, "Incomplete Survey", msg,
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Save to database
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            question_id TEXT,
            category TEXT,
            response INTEGER,
            timestamp TEXT
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            manager_id TEXT
        )''')
        
        try:
            # Insert responses
            for q_id, response in self.responses.items():
                q_row = self.questions_df[
                    self.questions_df['QuestionID'] == q_id
                ].iloc[0]
                category = q_row['Category']
                
                cursor.execute("""
                    INSERT INTO feedback_responses 
                    (username, question_id, category, response, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    self.username,
                    q_id,
                    category,
                    response if response is not None else -1,
                    timestamp
                ))
            
            conn.commit()
            QMessageBox.information(self, "Success", "Feedback submitted successfully!")
            self.responses = {q_id: None for q_id in self.responses.keys()}
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
        finally:
            conn.close()