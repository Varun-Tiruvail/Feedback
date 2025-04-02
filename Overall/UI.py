import sys
import os
import pandas as pd
import polars as pl
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                              QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                              QStackedWidget, QFileDialog, QTableWidget, 
                              QDateEdit, QMessageBox, QTableWidgetItem, 
                              QFormLayout, QDialog)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QDropEvent, QDragEnterEvent

# Login window
class LoginWindow(QWidget):
    def __init__(self, excel_path="login_details.xlsx"):
        super().__init__()
        self.excel_path = excel_path
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Login")
        self.setGeometry(300, 300, 300, 200)
        
        layout = QVBoxLayout()
        
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
        
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        try:
            # Read Excel file with login credentials
            credentials_df = pd.read_excel(self.excel_path)
            
            # Check if credentials match
            valid_login = False
            for _, row in credentials_df.iterrows():
                if row['username'] == username and row['password'] == password:
                    valid_login = True
                    break
            
            if valid_login:
                self.hide()
                self.main_window = MainWindow()
                self.main_window.show()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login error: {str(e)}")


# Main window after login
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Monthly Automation Tool")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Create category buttons
        self.ipv_button = QPushButton("IPV")
        self.reserves_button = QPushButton("Reserves")
        
        # Add buttons to layout
        button_layout.addWidget(self.ipv_button)
        button_layout.addWidget(self.reserves_button)
        
        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Add widgets to stacked widget
        self.ipv_widget = IPVWidget()
        self.reserves_widget = ReservesWidget()
        
        self.stacked_widget.addWidget(self.ipv_widget)
        self.stacked_widget.addWidget(self.reserves_widget)
        
        # Connect buttons to switch views
        self.ipv_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.ipv_widget))
        self.reserves_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.reserves_widget))
        
        # Add layouts to main layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stacked_widget)


# IPV Widget
class IPVWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("IPV Categories")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Buttons
        self.xipv_button = QPushButton("XIPV")
        self.yipv_button = QPushButton("YIPV")
        
        # Connect buttons
        self.xipv_button.clicked.connect(self.open_xipv_window)
        self.yipv_button.clicked.connect(self.open_yipv_window)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.xipv_button)
        layout.addWidget(self.yipv_button)
        
        self.setLayout(layout)
        
    def open_xipv_window(self):
        self.xipv_window = XIPVWindow()
        self.xipv_window.show()
        
    def open_yipv_window(self):
        self.yipv_window = YIPVWindow()
        self.yipv_window.show()


# Reserves Widget
class ReservesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Reserves Categories")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Buttons
        self.xreserves_button = QPushButton("XReserves")
        self.yreserves_button = QPushButton("YReserves")
        
        # Connect buttons
        self.xreserves_button.clicked.connect(self.open_xreserves_window)
        self.yreserves_button.clicked.connect(self.open_yreserves_window)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.xreserves_button)
        layout.addWidget(self.yreserves_button)
        
        self.setLayout(layout)
        
    def open_xreserves_window(self):
        self.xreserves_window = XReservesWindow()
        self.xreserves_window.show()
        
    def open_yreserves_window(self):
        self.yreserves_window = YReservesWindow()
        self.yreserves_window.show()


# XIPV Window
class XIPVWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.data_entries = []
        
    def init_ui(self):
        self.setWindowTitle("XIPV")
        self.setGeometry(200, 200, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("XIPV Processing")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # Process button
        self.process_button = QPushButton("Process Data")
        self.process_button.clicked.connect(self.open_data_dialog)
        
        # Table for displaying input data
        self.input_table = QTableWidget()
        self.input_table.setColumnCount(4)
        self.input_table.setHorizontalHeaderLabels(["File Path", "Date", "Adjustment 1", "Adjustment 2"])
        
        # Add widgets to layout
        main_layout.addWidget(title)
        main_layout.addWidget(self.process_button)
        main_layout.addWidget(self.input_table)
    
    def open_data_dialog(self):
        dialog = XIPVDataDialog(self)
        if dialog.exec_():
            file_path = dialog.file_path_input.text()
            date = dialog.date_input.date().toString("yyyy-MM-dd")
            adjustment1 = dialog.adjustment1_input.text()
            adjustment2 = dialog.adjustment2_input.text()
            
            # Add data to table
            row_position = self.input_table.rowCount()
            self.input_table.insertRow(row_position)
            self.input_table.setItem(row_position, 0, QTableWidgetItem(file_path))
            self.input_table.setItem(row_position, 1, QTableWidgetItem(date))
            self.input_table.setItem(row_position, 2, QTableWidgetItem(adjustment1))
            self.input_table.setItem(row_position, 3, QTableWidgetItem(adjustment2))
            
            # Store data
            entry = {
                'file_path': file_path,
                'date': date,
                'adjustment1': adjustment1,
                'adjustment2': adjustment2
            }
            self.data_entries.append(entry)
            
            # Process data
            self.process_data(entry)
    
    def process_data(self, entry):
        try:
            # Load data from file into polars DataFrame
            if os.path.exists(entry['file_path']):
                # Determine file type and read into DataFrame
                file_ext = Path(entry['file_path']).suffix.lower()
                
                if file_ext == '.csv':
                    df = pl.read_csv(entry['file_path'])
                elif file_ext in ['.xlsx', '.xls']:
                    # Convert pandas to polars
                    pandas_df = pd.read_excel(entry['file_path'])
                    df = pl.from_pandas(pandas_df)
                else:
                    QMessageBox.warning(self, "Error", "Unsupported file format")
                    return
                
                # Here you would process the data
                # ====== ADD YOUR CUSTOM FUNCTION HERE ======
                # Replace this comment with your processing function
                # Example: result = process_xipv_data(df, entry['date'], 
                #                                     float(entry['adjustment1']), 
                #                                     float(entry['adjustment2']))
                # Currently just returning 0 as per requirements
                result = 0
                # ============================================
                
                QMessageBox.information(self, "Success", f"Data processed successfully. Result: {result}")
            else:
                QMessageBox.warning(self, "Error", "File not found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Processing error: {str(e)}")


# Dialog for XIPV data input
class XIPVDataDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("XIPV Data Input")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # File path input
        self.file_path_input = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(self.browse_button)
        
        # Date input
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        
        # Adjustment inputs
        self.adjustment1_input = QLineEdit()
        self.adjustment2_input = QLineEdit()
        
        # Add to form layout
        layout.addRow("File Path:", file_layout)
        layout.addRow("Date:", self.date_input)
        layout.addRow("Adjustment 1:", self.adjustment1_input)
        layout.addRow("Adjustment 2:", self.adjustment2_input)
        
        # Buttons
        button_box = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        
        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.ok_button)
        
        layout.addRow("", button_box)
        
        self.setLayout(layout)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.file_path_input.setText(file_path)


# YIPV Window
class YIPVWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("YIPV")
        self.setGeometry(200, 200, 600, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("YIPV Processing")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # Extract from cube button
        self.extract_button = QPushButton("Extract from the Cube")
        self.extract_button.clicked.connect(self.extract_from_cube)
        
        # Calculate button
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)
        
        # Create drag and drop area
        self.drag_drop_area = FileDragDropWidget()
        
        # Add widgets to layout
        main_layout.addWidget(title)
        main_layout.addWidget(self.extract_button)
        main_layout.addWidget(self.calculate_button)
        main_layout.addWidget(QLabel("Drag and drop file here:"))
        main_layout.addWidget(self.drag_drop_area)
    
    def extract_from_cube(self):
        date, ok = self.get_date_input()
        if ok:
            # ====== ADD YOUR EXTRACT FUNCTION HERE ======
            # Replace this comment with your extract function
            # Example: result = extract_from_cube(date)
            # Currently just returning None as per requirements
            result = None
            # ============================================
            
            QMessageBox.information(self, "Extraction", f"Extracted data for {date}")
    
    def calculate(self):
        if hasattr(self.drag_drop_area, 'file_path') and self.drag_drop_area.file_path:
            file_path = self.drag_drop_area.file_path
            
            # ====== ADD YOUR CALCULATE FUNCTION HERE ======
            # Replace this comment with your calculate function
            # Example: result = calculate_yipv(file_path)
            # Currently just returning 0 as per requirements
            result = 0
            # =============================================
            
            QMessageBox.information(self, "Calculation", f"Calculation complete. Result: {result}")
        else:
            QMessageBox.warning(self, "Error", "Please drag and drop a file first")
    
    def get_date_input(self):
        date_dialog = QDialog(self)
        date_dialog.setWindowTitle("Enter Date")
        
        layout = QVBoxLayout()
        
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        
        buttons = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        ok_button = QPushButton("OK")
        
        buttons.addWidget(cancel_button)
        buttons.addWidget(ok_button)
        
        layout.addWidget(QLabel("Select date:"))
        layout.addWidget(date_edit)
        layout.addLayout(buttons)
        
        date_dialog.setLayout(layout)
        
        ok_button.clicked.connect(date_dialog.accept)
        cancel_button.clicked.connect(date_dialog.reject)
        
        result = date_dialog.exec_()
        return date_edit.date().toString("yyyy-MM-dd"), result == QDialog.Accepted


# File drag and drop widget
class FileDragDropWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.file_path = None
        
    def init_ui(self):
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        self.setStyleSheet("border: 2px dashed #aaa; border-radius: 5px;")
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Drop file here")
        self.label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            self.file_path = url.toLocalFile()
            self.label.setText(f"File: {os.path.basename(self.file_path)}")
            event.acceptProposedAction()


# XReserves Window
class XReservesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("XReserves")
        self.setGeometry(200, 200, 600, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("XReserves Processing")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # Process button
        self.process_button = QPushButton("Process Tables")
        self.process_button.clicked.connect(self.process_tables)
        
        # Add widgets to layout
        main_layout.addWidget(title)
        main_layout.addWidget(self.process_button)
    
    def process_tables(self):
        # First table dialog
        table1_path = self.get_table_path("Select First Table")
        if not table1_path:
            return
        
        # Second table dialog
        table2_path = self.get_table_path("Select Second Table")
        if not table2_path:
            return
        
        try:
            # Load tables
            if os.path.exists(table1_path) and os.path.exists(table2_path):
                # Determine file types and read into DataFrames
                # Table 1
                file_ext1 = Path(table1_path).suffix.lower()
                if file_ext1 == '.csv':
                    df1 = pl.read_csv(table1_path)
                elif file_ext1 in ['.xlsx', '.xls']:
                    pandas_df1 = pd.read_excel(table1_path)
                    df1 = pl.from_pandas(pandas_df1)
                else:
                    QMessageBox.warning(self, "Error", "Unsupported file format for table 1")
                    return
                
                # Table 2
                file_ext2 = Path(table2_path).suffix.lower()
                if file_ext2 == '.csv':
                    df2 = pl.read_csv(table2_path)
                elif file_ext2 in ['.xlsx', '.xls']:
                    pandas_df2 = pd.read_excel(table2_path)
                    df2 = pl.from_pandas(pandas_df2)
                else:
                    QMessageBox.warning(self, "Error", "Unsupported file format for table 2")
                    return
                
                # ====== ADD YOUR FUNCTION HERE ======
                # Replace this comment with your processing function
                # Example: result = process_xreserves(df1, df2)
                # Currently just showing message as per requirements
                # =====================================
                
                QMessageBox.information(self, "Success", "Tables processed successfully")
            else:
                QMessageBox.warning(self, "Error", "One or both files not found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Processing error: {str(e)}")
    
    def get_table_path(self, title):
        return QFileDialog.getOpenFileName(
            self, title, "", "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )[0]


# YReserves Window
class YReservesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("YReserves")
        self.setGeometry(200, 200, 600, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("YReserves Processing")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # Process button
        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process_data)
        
        # Add widgets to layout
        main_layout.addWidget(title)
        main_layout.addWidget(self.process_button)
    
    def process_data(self):
        # ====== ADD YOUR FUNCTION HERE ======
        # Replace this comment with your processing function
        # Example: result = process_yreserves()
        # Currently just showing message as per requirements
        # =====================================
        
        QMessageBox.information(self, "Processing", "YReserves processing initiated")


# Main entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())