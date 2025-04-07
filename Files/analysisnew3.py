import sys
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                            QLabel, QPushButton, QMessageBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AnalysisApp(QWidget):
    def __init__(self, username, is_manager):
        super().__init__()
        self.username = username
        self.is_manager = is_manager
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Cultural", "Development", "Ways of Working"])
        self.category_combo.currentTextChanged.connect(self.update_section_analysis)
        
        self.question_combo = QComboBox()
        self.question_combo.currentTextChanged.connect(self.update_question_analysis)
        
        controls_layout.addWidget(QLabel("Category:"))
        controls_layout.addWidget(self.category_combo)
        controls_layout.addWidget(QLabel("Question:"))
        controls_layout.addWidget(self.question_combo)
        
        # Charts
        self.section_figure = plt.figure(figsize=(8, 4))
        self.section_canvas = FigureCanvas(self.section_figure)
        
        self.question_figure = plt.figure(figsize=(8, 4))
        self.question_canvas = FigureCanvas(self.question_figure)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.section_canvas)
        layout.addWidget(self.question_canvas)
        
        self.setLayout(layout)

    def load_data(self):
        try:
            # Load questions
            self.questions_df = pd.read_excel('survey_questions.xlsx')
            
            # Ensure tables exist
            conn = sqlite3.connect('feedback.db')
            cursor = conn.cursor()
            
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
            
            conn.commit()
            
            # Load responses
            query = """
                SELECT f.*, u.manager_id 
                FROM feedback_responses f
                JOIN users u ON f.username = u.username
                WHERE 1=1
            """
            
            if not self.is_manager:
                query += f" AND f.username = '{self.username}'"
            else:
                query += f" AND (u.manager_id = '{self.username}' OR f.username = '{self.username}')"
            
            self.responses_df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Merge questions and responses
            self.merged_data = pd.merge(
                self.responses_df,
                self.questions_df,
                on='question_id'
            )
            
            # Update question combo box
            self.update_question_list()
            
            # Initial updates
            self.update_section_analysis(self.category_combo.currentText())
            self.update_question_analysis(self.question_combo.currentText())
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading data: {str(e)}")

    def update_question_list(self):
        category = self.category_combo.currentText()
        questions = self.questions_df[
            self.questions_df['Category'] == category
        ]['Question'].tolist()
        
        self.question_combo.clear()
        self.question_combo.addItems(questions)

    def update_section_analysis(self, category):
        if self.merged_data is None or not category:
            return
            
        try:
            self.section_canvas.figure.clear()
            ax = self.section_canvas.figure.add_subplot(111)
            
            # Calculate average scores by question
            category_data = self.merged_data[
                self.merged_data['Category'] == category
            ]
            
            avg_scores = category_data.groupby('Question')['response'].mean()
            
            # Create bar chart
            avg_scores.plot(kind='bar', ax=ax)
            ax.set_title(f'Average Scores - {category}')
            ax.set_ylabel('Score')
            ax.set_xlabel('Questions')
            plt.xticks(rotation=45, ha='right')
            
            self.section_canvas.figure.tight_layout()
            self.section_canvas.draw()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error updating section analysis: {str(e)}")

    def update_question_analysis(self, question_text):
        if self.merged_data is None or not question_text:
            return
            
        try:
            self.question_canvas.figure.clear()
            ax = self.question_canvas.figure.add_subplot(111)
            
            # Get response distribution
            question_data = self.merged_data[
                self.merged_data['Question'] == question_text
            ]
            
            response_counts = question_data['response'].value_counts()
            
            # Create pie chart
            plt.pie(response_counts.values, labels=response_counts.index,
                   autopct='%1.1f%%')
            ax.set_title(f'Response Distribution - {question_text}')
            
            self.question_canvas.figure.tight_layout()
            self.question_canvas.draw()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error updating question analysis: {str(e)}")