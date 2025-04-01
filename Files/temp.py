import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QRadioButton, 
                             QButtonGroup, QFileDialog, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt

class SurveyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Survey Application")
        self.setMinimumSize(700, 500)
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Button to load Excel file
        self.load_button = QPushButton("Load Survey Questions from Excel")
        self.load_button.clicked.connect(self.load_excel_file)
        self.main_layout.addWidget(self.load_button)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs for each section
        self.tabs = {
            "cultural": QWidget(),
            "development": QWidget(),
            "ways of working": QWidget()
        }
        
        # Set up layouts for each tab
        self.tab_layouts = {}
        for section_name, tab in self.tabs.items():
            layout = QVBoxLayout(tab)
            
            # Add scrollable content area for questions
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            layout.addWidget(content_widget)
            
            # Store the content layout for later adding questions
            self.tab_layouts[section_name] = content_layout
            
            # Add the tab to the tab widget with a capitalized name
            display_name = section_name.title()
            self.tab_widget.addTab(tab, display_name)
        
        # Submit button
        self.submit_button = QPushButton("Submit Survey")
        self.submit_button.clicked.connect(self.submit_survey)
        self.main_layout.addWidget(self.submit_button)
        
        # Initialize variables
        self.questions = {}  # Dictionary to store questions by section
        self.user_answers = {}  # Dictionary to store user answers
        self.option_groups = {}  # Dictionary to store button groups
        
        # Disable submit button until questions are loaded
        self.submit_button.setEnabled(False)
    
    def load_excel_file(self):
        """Load questions from an Excel file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)"
        )
        
        if not file_path:
            return
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Validate required columns
            required_columns = ['Question', 'Option1', 'Option2', 'Option3', 'Option4', 'Section']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"Excel file must contain columns: {', '.join(required_columns)}")
            
            # Convert section names to lowercase for consistency
            df['Section'] = df['Section'].str.lower()
            
            # Validate sections
            valid_sections = list(self.tabs.keys())
            invalid_sections = df[~df['Section'].isin(valid_sections)]['Section'].unique()
            if len(invalid_sections) > 0:
                raise ValueError(f"Invalid sections found: {', '.join(invalid_sections)}. "
                                f"Valid sections are: {', '.join(valid_sections)}")
            
            # Clear previous questions
            self.questions = {section: [] for section in self.tabs.keys()}
            self.user_answers = {}
            
            # Group questions by section
            for section in self.tabs.keys():
                section_questions = df[df['Section'].str.lower() == section].to_dict('records')
                self.questions[section] = section_questions
            
            # Display questions in each tab
            self.display_questions()
            
            # Enable submit button
            self.submit_button.setEnabled(True)
            
            # Show message with question count
            total_questions = sum(len(questions) for questions in self.questions.values())
            QMessageBox.information(self, "Success", f"Loaded {total_questions} questions from the Excel file.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load questions: {str(e)}")
    
    def display_questions(self):
        """Display questions in their respective tabs"""
        # Clear all existing questions from tabs
        for section, layout in self.tab_layouts.items():
            # Remove all widgets from the layout
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        self.option_groups = {}
        
        # Add questions to each tab
        for section, questions in self.questions.items():
            if not questions:
                # Add a placeholder if no questions in this section
                label = QLabel(f"No questions available for the {section.title()} section.")
                label.setAlignment(Qt.AlignCenter)
                self.tab_layouts[section].addWidget(label)
                continue
            
            # Add questions to this section
            for q_idx, question_data in enumerate(questions):
                # Create a container for this question
                question_widget = QWidget()
                question_layout = QVBoxLayout(question_widget)
                
                # Add the question text
                question_label = QLabel(f"Q{q_idx+1}: {question_data['Question']}")
                question_label.setWordWrap(True)
                question_layout.addWidget(question_label)
                
                # Create button group for this question
                question_id = f"{section}_{q_idx}"
                button_group = QButtonGroup(self)
                self.option_groups[question_id] = button_group
                
                # Add options as radio buttons
                for i in range(1, 5):
                    option_key = f'Option{i}'
                    radio_button = QRadioButton(question_data[option_key])
                    button_group.addButton(radio_button, i)
                    question_layout.addWidget(radio_button)
                
                # Connect button group to save answer
                button_group.buttonClicked.connect(
                    lambda btn, qid=question_id: self.save_answer(qid, btn)
                )
                
                # Add some spacing between questions
                question_layout.addSpacing(20)
                
                # Add this question to the tab
                self.tab_layouts[section].addWidget(question_widget)
            
            # Add stretch to push questions to the top
            self.tab_layouts[section].addStretch()
    
    def save_answer(self, question_id, button):
        """Save the user's answer for a question"""
        selected_option = self.option_groups[question_id].id(button)
        self.user_answers[question_id] = selected_option
    
    def submit_survey(self):
        """Process and display the survey results"""
        if not any(self.questions.values()):
            QMessageBox.warning(self, "Warning", "No questions loaded!")
            return
        
        # Calculate response rates for each section
        results = {}
        total_questions = 0
        total_answered = 0
        
        for section, questions in self.questions.items():
            section_total = len(questions)
            section_answered = sum(1 for q_idx in range(section_total) 
                                if f"{section}_{q_idx}" in self.user_answers)
            
            if section_total > 0:
                section_rate = (section_answered / section_total) * 100
            else:
                section_rate = 0
                
            results[section] = {
                "total": section_total,
                "answered": section_answered,
                "rate": section_rate
            }
            
            total_questions += section_total
            total_answered += section_answered
        
        # Overall completion rate
        overall_rate = (total_answered / total_questions) * 100 if total_questions > 0 else 0
        
        # Format results message
        result_message = "Survey Results:\n\n"
        for section, data in results.items():
            if data["total"] > 0:
                result_message += f"{section.title()} Section:\n"
                result_message += f"- Completed: {data['answered']}/{data['total']} questions ({data['rate']:.1f}%)\n\n"
        
        result_message += f"Overall Completion: {total_answered}/{total_questions} ({overall_rate:.1f}%)"
        
        # Show results
        QMessageBox.information(self, "Survey Results", result_message)
        
        # Ask if they want to export results
        reply = QMessageBox.question(self, "Export Results", 
                                    "Would you like to export the survey responses?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.export_results()
    
    def export_results(self):
        """Export survey responses to an Excel file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "survey_results.xlsx", "Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            # Prepare data for export
            results_data = []
            
            for section, questions in self.questions.items():
                for q_idx, question in enumerate(questions):
                    question_id = f"{section}_{q_idx}"
                    selected_option = self.user_answers.get(question_id, None)
                    
                    # Get the text of the selected option
                    selected_text = None
                    if selected_option is not None:
                        option_key = f"Option{selected_option}"
                        selected_text = question.get(option_key, "")
                    
                    results_data.append({
                        "Section": section.title(),
                        "Question": question["Question"],
                        "Selected Option": selected_option,
                        "Selected Text": selected_text
                    })
            
            # Create DataFrame and export
            results_df = pd.DataFrame(results_data)
            results_df.to_excel(file_path, index=False)
            
            QMessageBox.information(self, "Export Successful", 
                                   f"Survey responses have been exported to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results: {str(e)}")

if __name__ == "__main__":
    # Use try/except to handle both PyQt and PySide imports
    try:
        # First try with PySide6
        app = QApplication(sys.argv)
        window = SurveyApp()
        window.show()
        sys.exit(app.exec())
    except ImportError:
        # If PySide6 not available, try PyQt6
        try:
            from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                        QHBoxLayout, QLabel, QPushButton, QRadioButton, 
                                        QButtonGroup, QFileDialog, QMessageBox, QTabWidget)
            from PyQt6.QtCore import Qt
            
            app = QApplication(sys.argv)
            window = SurveyApp()
            window.show()
            sys.exit(app.exec())
        except ImportError:
            print("Error: Neither PySide6 nor PyQt6 is installed.")
            print("Please install one using pip: pip install PySide6 or pip install PyQt6")
            sys.exit(1)