import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from FeedbackApp import SurveyApp
from analysisnew3 import AnalysisApp

class UnifiedApp(QMainWindow):
    def __init__(self, username, is_manager):
        super().__init__()
        self.setWindowTitle("Unified Feedback and Analysis App")
        self.resize(1000, 800)
        
        # Create a central widget with tabs
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.tabs = QTabWidget()
        
        # Add Survey tab
        self.survey_tab = SurveyApp(username)
        self.tabs.addTab(self.survey_tab, "Survey")
        
        # Add Analysis tab
        self.analysis_tab = AnalysisApp(username, is_manager)
        self.tabs.addTab(self.analysis_tab, "Analysis")
        
        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Replace with actual username and is_manager values
    username = "test_user"
    is_manager = False
    window = UnifiedApp(username, is_manager)
    window.show()
    sys.exit(app.exec())
