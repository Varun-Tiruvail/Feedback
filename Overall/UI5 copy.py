import sys
import os
import pandas as pd
import polars as pl
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                              QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                              QStackedWidget, QFileDialog, QTableWidget, 
                              QDateEdit, QMessageBox, QTableWidgetItem, 
                              QFormLayout, QDialog, QTabWidget)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QDropEvent, QDragEnterEvent
from PySide6.QtWidgets import QPlainTextEdit, QHeaderView
from PySide6.QtGui import QDoubleValidator
from io import StringIO  # Import StringIO for text conversion


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


# Updated XIPVWindow and related classes
class XIPVWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.data_entries = {}
        self.default_data_path = "default_tables.xlsx"  # Path to default data Excel file
        
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
        self.process_button.clicked.connect(self.start_process_sequence)
        
        # Table for displaying input data
        self.input_table = QTableWidget()
        self.input_table.setColumnCount(7)
        self.input_table.setHorizontalHeaderLabels([
            "File Path", "Date", "Adjustment 1", "Adjustment 2", 
            "Tables Imported", "Status", "Result"
        ])
        self.input_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Add widgets to layout
        main_layout.addWidget(title)
        main_layout.addWidget(self.process_button)
        main_layout.addWidget(self.input_table)
    
    def start_process_sequence(self):
        # Reset data for new processing
        self.data_entries = {
            'file_info': {},
            'tables': [None, None, None, None]  # Initialize with 4 None tables
        }
        
        # Show first dialog for file path, date, and adjustments
        self.show_file_info_dialog()
    
    def show_file_info_dialog(self):
        dialog = XIPVFileInfoDialog(self)
        if dialog.exec_():
            # Store file info
            self.data_entries['file_info'] = {
                'file_path': dialog.file_path_input.text(),
                'date': dialog.date_input.date().toString("yyyy-MM-dd"),
                'adjustment1': dialog.adjustment1_input.text(),
                'adjustment2': dialog.adjustment2_input.text()
            }
            
            # Add data to table
            row_position = self.input_table.rowCount()
            self.input_table.insertRow(row_position)
            self.input_table.setItem(row_position, 0, QTableWidgetItem(self.data_entries['file_info']['file_path']))
            self.input_table.setItem(row_position, 1, QTableWidgetItem(self.data_entries['file_info']['date']))
            self.input_table.setItem(row_position, 2, QTableWidgetItem(self.data_entries['file_info']['adjustment1']))
            self.input_table.setItem(row_position, 3, QTableWidgetItem(self.data_entries['file_info']['adjustment2']))
            self.input_table.setItem(row_position, 4, QTableWidgetItem("0/4"))
            self.input_table.setItem(row_position, 5, QTableWidgetItem("Processing..."))
            
            # Start table import sequence with table 1 (mandatory)
            self.current_row = row_position
            self.show_table1_dialog()
    
    def show_table1_dialog(self):
        # Table 1 is mandatory
        dialog = XIPVTableDialog(self, table_number=1, is_mandatory=True)
        if dialog.exec_():
            # Get table data and convert to polars DataFrame
            table_data = dialog.table_data
            if table_data:
                try:
                    # Parse the clipboard data into pandas DataFrame
                    pandas_df = pd.read_clipboard(sep='\t')
                    # Convert to polars
                    pl_df = pl.from_pandas(pandas_df)
                    
                    # Store the polars DataFrame
                    self.data_entries['tables'][0] = pl_df
                    
                    # Update table display
                    self.input_table.setItem(
                        self.current_row, 
                        4, 
                        QTableWidgetItem("1/4")
                    )
                    
                    # Now show dialog for remaining tables with default options
                    self.show_remaining_tables_dialog()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to parse table data: {str(e)}")
                    # Try again with table 1
                    self.show_table1_dialog()
            else:
                # No data provided, try again
                QMessageBox.warning(self, "Warning", "No table data provided. Please paste data from Excel.")
                self.show_table1_dialog()
        else:
            # Dialog cancelled, update status
            self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Cancelled"))

    def show_remaining_tables_dialog(self):
        # Load default data for remaining tables
        try:
            self.load_default_tables()
            
            # Show dialog for remaining tables
            dialog = XIPVRemainingTablesDialog(self, self.data_entries['tables'])
            if dialog.exec_():
                # Update tables with any changes
                self.data_entries['tables'] = dialog.tables
                
                # Save any changed default tables to Excel
                self.save_default_tables(dialog.modified_tables)
                
                # Update table display
                self.input_table.setItem(
                    self.current_row, 
                    4, 
                    QTableWidgetItem("4/4")
                )
                
                # Process all data
                self.process_data()
            else:
                # Dialog cancelled, update status
                self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Cancelled"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error with default tables: {str(e)}")
            self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Failed - Default tables error"))
    
    def load_default_tables(self):
        """Load default tables data from Excel file"""
        if os.path.exists(self.default_data_path):
            # Load tables 2-4 from Excel sheets
            for i in range(1, 4):  # Tables 2-4 (index 1-3)
                try:
                    pandas_df = pd.read_excel(self.default_data_path, sheet_name=f"Table{i+1}")
                    self.data_entries['tables'][i] = pl.from_pandas(pandas_df)
                except Exception as e:
                    print(f"Error loading default table {i+1}: {str(e)}")
                    # Create empty table as fallback
                    self.data_entries['tables'][i] = pl.DataFrame()
        else:
            # Create empty default tables
            for i in range(1, 4):
                self.data_entries['tables'][i] = pl.DataFrame()
            
            # Create default Excel file with empty sheets
            with pd.ExcelWriter(self.default_data_path) as writer:
                for i in range(1, 5):  # Create 4 sheets
                    pd.DataFrame().to_excel(writer, sheet_name=f"Table{i}", index=False)
    
    def save_default_tables(self, modified_indices):
        """Save modified default tables back to Excel"""
        if not os.path.exists(self.default_data_path):
            # Create Excel file if it doesn't exist
            with pd.ExcelWriter(self.default_data_path) as writer:
                for i in range(4):
                    pd.DataFrame().to_excel(writer, sheet_name=f"Table{i+1}", index=False)
        
        # Only save tables that were modified
        if modified_indices:
            with pd.ExcelWriter(self.default_data_path, mode='a', if_sheet_exists='replace') as writer:
                for i in modified_indices:
                    if i > 0:  # Only save tables 2-4 (index 1-3)
                        # Convert polars to pandas for Excel writing
                        pandas_df = self.data_entries['tables'][i].to_pandas()
                        pandas_df.to_excel(writer, sheet_name=f"Table{i+1}", index=False)
    
    def process_data(self):
        try:
            # Load data from file
            file_path = self.data_entries['file_info']['file_path']
            date = self.data_entries['file_info']['date']
            adjustment1 = float(self.data_entries['file_info']['adjustment1'])
            adjustment2 = float(self.data_entries['file_info']['adjustment2'])
            
            # Get all tables
            tables = self.data_entries['tables']
            
            if os.path.exists(file_path) and tables[0] is not None:
                # Determine file type and read into DataFrame
                file_ext = Path(file_path).suffix.lower()
                
                if file_ext == '.csv':
                    file_df = pl.read_csv(file_path)
                elif file_ext in ['.xlsx', '.xls']:
                    # Convert pandas to polars
                    pandas_df = pd.read_excel(file_path)
                    file_df = pl.from_pandas(pandas_df)
                else:
                    QMessageBox.warning(self, "Error", "Unsupported file format")
                    self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Failed - Bad file format"))
                    return
                
                # ====== ADD YOUR CUSTOM FUNCTION HERE ======
                # Process using all dataframes and parameters
                # Example: 
                # result = process_xipv_data(
                #     file_df, 
                #     date, 
                #     adjustment1, 
                #     adjustment2,
                #     tables[0],  # Table 1
                #     tables[1],  # Table 2
                #     tables[2],  # Table 3
                #     tables[3]   # Table 4
                # )
                result = 0
                # ============================================
                
                # Update table
                self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Completed"))
                self.input_table.setItem(self.current_row, 6, QTableWidgetItem(str(result)))
                
                QMessageBox.information(self, "Success", f"Data processed successfully. Result: {result}")
            else:
                QMessageBox.warning(self, "Error", "File not found or first table missing")
                self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Failed - Missing data"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Processing error: {str(e)}")
            self.input_table.setItem(self.current_row, 5, QTableWidgetItem(f"Failed - {str(e)[:20]}..."))


# Modified Dialog for XIPV table input (supports mandatory/optional)
class XIPVTableDialog(QDialog):
    def __init__(self, parent=None, table_number=1, is_mandatory=False):
        super().__init__(parent)
        self.setWindowTitle(f"XIPV Table {table_number} Input")
        self.setMinimumSize(600, 400)
        self.table_number = table_number
        self.is_mandatory = is_mandatory
        self.table_data = None
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            f"Paste Table {table_number} data from Excel (Ctrl+V).\n"
            "Make sure to copy the entire table including headers."
        )
        if is_mandatory:
            instructions.setText(instructions.text() + "\n(This table is mandatory)")
        instructions.setStyleSheet("font-weight: bold;")
        
        # Text area for pasted data
        self.data_text = QPlainTextEdit()
        self.data_text.setPlaceholderText("Paste Excel data here...")
        
        # Preview area
        preview_label = QLabel("Data Preview:")
        self.preview_table = QTableWidget()
        
        # Connect paste event
        self.data_text.textChanged.connect(self.update_preview)
        
        # Buttons
        button_box = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("Next")
        self.ok_button.clicked.connect(self.accept)
        
        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.ok_button)
        
        # Add to layout
        layout.addWidget(instructions)
        layout.addWidget(self.data_text)
        layout.addWidget(preview_label)
        layout.addWidget(self.preview_table)
        layout.addLayout(button_box)
        
        self.setLayout(layout)

    def update_preview(self):
        text = self.data_text.toPlainText()
        if text:
            try:
                # Convert the pasted text into a file-like object
                text_io = StringIO(text)

                # Try to parse the text as a DataFrame
                df = pd.read_csv(text_io, sep="\t")

                # Update preview table
                self.preview_table.setRowCount(min(5, len(df)))
                self.preview_table.setColumnCount(len(df.columns))
                self.preview_table.setHorizontalHeaderLabels(df.columns)

                # Fill preview data (first 5 rows)
                for i in range(min(5, len(df))):
                    for j in range(len(df.columns)):
                        item = QTableWidgetItem(str(df.iloc[i, j]))
                        self.preview_table.setItem(i, j, item)

                # Resize columns to content
                self.preview_table.resizeColumnsToContents()

                # Store the data
                self.table_data = text
            except Exception as e:
                # Handle parsing failures
                self.preview_table.setRowCount(0)
                self.preview_table.setColumnCount(0)
                self.table_data = None
                print(f"Error parsing data: {e}")
        else:
            # Clear preview if no text
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
            self.table_data = None


# New dialog for managing remaining tables
class XIPVRemainingTablesDialog(QDialog):

    def __init__(self, parent=None, tables=None):
        super().__init__(parent)
        self.setWindowTitle("Remaining Tables")
        self.setMinimumSize(800, 600)
        self.tables = tables if tables else [None, None, None, None]
        self.modified_tables = set()  # Track which tables have been modified
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Table 1 has been imported. Default data is loaded for Tables 2-4.\n"
            "You can view and modify the default data or import new data."
        )
        instructions.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(instructions)
        
        # Create tab widget for tables
        self.tab_widget = QTabWidget()
        
        # Add tabs for tables 2-4
        for i in range(1, 4):
            tab = self.create_table_tab(i+1, self.tables[i])
            self.tab_widget.addTab(tab, f"Table {i+1}")
        
        main_layout.addWidget(self.tab_widget)
        
        # Buttons
        button_box = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("Finish")
        self.ok_button.clicked.connect(self.accept)
        
        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.ok_button)
        main_layout.addLayout(button_box)
        
        self.setLayout(main_layout)
    
    def create_table_tab(self, table_num, table_data):
        """Create a tab for a table"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout()
        
        # Button to import new data
        import_button = QPushButton(f"Import New Data for Table {table_num}")
        import_button.clicked.connect(lambda: self.import_new_data(table_num-1))
        tab_layout.addWidget(import_button)
        
        # Table widget to display/edit data
        table_widget = QTableWidget()
        self.populate_table_widget(table_widget, table_data)
        table_widget.itemChanged.connect(lambda: self.handle_table_edit(table_num-1, table_widget))
        
        tab_layout.addWidget(QLabel("Default Data (editable):"))
        tab_layout.addWidget(table_widget)
        
        # Store reference to table widget
        setattr(self, f"table{table_num}_widget", table_widget)
        
        tab_widget.setLayout(tab_layout)
        return tab_widget
    
    def populate_table_widget(self, table_widget, table_data):
        """Populate a QTableWidget with data from a polars DataFrame"""
        if table_data is None or table_data.is_empty():
            table_widget.setRowCount(0)
            table_widget.setColumnCount(0)
            return
        
        # Convert polars to pandas for easier handling
        pandas_df = table_data.to_pandas()
        
        # Set table dimensions
        table_widget.setRowCount(len(pandas_df))
        table_widget.setColumnCount(len(pandas_df.columns))
        table_widget.setHorizontalHeaderLabels(pandas_df.columns)
        
        # Fill data
        for i in range(len(pandas_df)):
            for j in range(len(pandas_df.columns)):
                value = pandas_df.iloc[i, j]
                item = QTableWidgetItem(str(value))
                table_widget.setItem(i, j, item)
        
        # Resize columns to content
        table_widget.resizeColumnsToContents()
    
    def import_new_data(self, table_index):
        """Import new data for a table"""
        dialog = XIPVTableDialog(self, table_number=table_index+1)
        if dialog.exec_():
            table_data = dialog.table_data
            if table_data:
                try:
                    # Parse the clipboard data into pandas DataFrame
                    pandas_df = pd.read_clipboard(sep='\t')
                    # Convert to polars
                    pl_df = pl.from_pandas(pandas_df)
                    
                    # Update the table
                    self.tables[table_index] = pl_df
                    
                    # Update UI
                    table_widget = getattr(self, f"table{table_index+1}_widget")
                    self.populate_table_widget(table_widget, pl_df)
                    
                    # Mark as modified
                    self.modified_tables.add(table_index)
                    
                    QMessageBox.information(self, "Success", f"New data imported for Table {table_index+1}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to parse table data: {str(e)}")
    
    def handle_table_edit(self, table_index, table_widget):
        """Handle edits to the table widget"""
        try:
            # Get headers
            headers = []
            for j in range(table_widget.columnCount()):
                headers.append(table_widget.horizontalHeaderItem(j).text())
            
            # Get all data
            data = []
            for i in range(table_widget.rowCount()):
                row_data = []
                for j in range(table_widget.columnCount()):
                    item = table_widget.item(i, j)
                    value = item.text() if item else ""
                    row_data.append(value)
                data.append(row_data)
            
            # Create pandas DataFrame and convert to polars
            pandas_df = pd.DataFrame(data, columns=headers)
            pl_df = pl.from_pandas(pandas_df)
            
            # Update the table
            self.tables[table_index] = pl_df
            
            # Mark as modified
            self.modified_tables.add(table_index)
        except Exception as e:
            print(f"Error updating table data: {str(e)}")


# Dialog for XIPV file info input (first popup)
class XIPVFileInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("XIPV File Information")
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
        
        # Set placeholders and validators
        self.adjustment1_input.setPlaceholderText("Enter numeric value")
        self.adjustment2_input.setPlaceholderText("Enter numeric value")
        validator = QDoubleValidator()
        self.adjustment1_input.setValidator(validator)
        self.adjustment2_input.setValidator(validator)
        
        # Add to form layout
        layout.addRow("File Path:", file_layout)
        layout.addRow("Date:", self.date_input)
        layout.addRow("Adjustment 1:", self.adjustment1_input)
        layout.addRow("Adjustment 2:", self.adjustment2_input)
        
        # Buttons
        button_box = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("Next")
        self.ok_button.clicked.connect(self.validate_and_accept)
        
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
    
    def validate_and_accept(self):
        # Check if all fields are filled
        if not self.file_path_input.text():
            QMessageBox.warning(self, "Warning", "Please select a file.")
            return
        
        if not self.adjustment1_input.text() or not self.adjustment2_input.text():
            QMessageBox.warning(self, "Warning", "Please enter both adjustment values.")
            return
        
        self.accept()


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
        
        # Create a horizontal layout for the extraction and broil file buttons
        extraction_buttons_layout = QHBoxLayout()
        
        # Extract button
        self.extract_button = QPushButton("Extract from the Cube")
        self.extract_button.clicked.connect(self.extract_from_cube)
        
        # Generate broil file button
        self.broil_button = QPushButton("Generate Broil File")
        self.broil_button.clicked.connect(self.generate_broil_file)
        
        # Add buttons to horizontal layout
        extraction_buttons_layout.addWidget(self.extract_button)
        extraction_buttons_layout.addWidget(self.broil_button)
        
        # Create drag and drop area
        self.drag_drop_area = FileDragDropWidget()
        
        # Calculate button - now below drag and drop area
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)
        
        # Add widgets and layouts to main layout
        main_layout.addWidget(title)
        main_layout.addLayout(extraction_buttons_layout)  # Add the horizontal layout
        main_layout.addWidget(QLabel("Drag and drop file here:"))
        main_layout.addWidget(self.drag_drop_area)
        main_layout.addWidget(self.calculate_button)  # Moved below drag and drop area
    
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
    
    def generate_broil_file(self):
        date, ok = self.get_date_input()
        if ok:
            # ====== ADD YOUR BROIL FILE GENERATION FUNCTION HERE ======
            # Replace this comment with your broil file generation function
            # Example: result = generate_broil_file(date)
            # Currently just showing a message
            # ============================================
            
            QMessageBox.information(self, "Broil File Generation", f"Generated broil file for {date}")
    
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


# XReserves Window - Updated to use the XIPV table extraction method
class XReservesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.data_entries = {}
        self.default_data_path = "default_tables.xlsx"  # Same Excel file as XIPV but different sheets
        
    def init_ui(self):
        self.setWindowTitle("XReserves")
        self.setGeometry(200, 200, 800, 600)
        
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
        self.process_button = QPushButton("Process Data")
        self.process_button.clicked.connect(self.start_process_sequence)
        
        # Table for displaying input data
        self.input_table = QTableWidget()
        self.input_table.setColumnCount(7)
        self.input_table.setHorizontalHeaderLabels([
            "File Path", "Date", "Adjustment 1", "Adjustment 2", 
            "Tables Imported", "Status", "Result"
        ])
        self.input_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Add widgets to layout
        main_layout.addWidget(title)
        main_layout.addWidget(self.process_button)
        main_layout.addWidget(self.input_table)
    
    def start_process_sequence(self):
        # Reset data for new processing
        self.data_entries = {
            'file_info': {},
            'tables': [None, None, None, None]  # Initialize with 4 None tables
        }
        
        # Show first dialog for file path, date, and adjustments
        self.show_file_info_dialog()
    
    def show_file_info_dialog(self):
        dialog = XReservesFileInfoDialog(self)
        if dialog.exec_():
            # Store file info
            self.data_entries['file_info'] = {
                'file_path': dialog.file_path_input.text(),
                'date': dialog.date_input.date().toString("yyyy-MM-dd"),
                'adjustment1': dialog.adjustment1_input.text(),
                'adjustment2': dialog.adjustment2_input.text()
            }
            
            # Add data to table
            row_position = self.input_table.rowCount()
            self.input_table.insertRow(row_position)
            self.input_table.setItem(row_position, 0, QTableWidgetItem(self.data_entries['file_info']['file_path']))
            self.input_table.setItem(row_position, 1, QTableWidgetItem(self.data_entries['file_info']['date']))
            self.input_table.setItem(row_position, 2, QTableWidgetItem(self.data_entries['file_info']['adjustment1']))
            self.input_table.setItem(row_position, 3, QTableWidgetItem(self.data_entries['file_info']['adjustment2']))
            self.input_table.setItem(row_position, 4, QTableWidgetItem("0/4"))
            self.input_table.setItem(row_position, 5, QTableWidgetItem("Processing..."))
            
            # Start table import sequence with first mandatory table
            self.current_row = row_position
            self.show_table1_dialog()
    
    def show_table1_dialog(self):
        # First table is mandatory
        dialog = XReservesTableDialog(self, table_number=1, is_mandatory=True)
        if dialog.exec_():
            # Get table data and convert to polars DataFrame
            table_data = dialog.table_data
            if table_data:
                try:
                    # Parse the clipboard data into pandas DataFrame
                    pandas_df = pd.read_clipboard(sep='\t')
                    # Convert to polars
                    pl_df = pl.from_pandas(pandas_df)
                    
                    # Store the polars DataFrame
                    self.data_entries['tables'][0] = pl_df
                    
                    # Update table display
                    self.input_table.setItem(
                        self.current_row, 
                        4, 
                        QTableWidgetItem("1/4")
                    )
                    
                    # Show second mandatory table dialog
                    self.show_table2_dialog()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to parse table data: {str(e)}")
                    # Try again with table 1
                    self.show_table1_dialog()
            else:
                # No data provided, try again
                QMessageBox.warning(self, "Warning", "No table data provided. Please paste data from Excel.")
                self.show_table1_dialog()
        else:
            # Dialog cancelled, update status
            self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Cancelled"))
    
    def show_table2_dialog(self):
        # Second table is also mandatory
        dialog = XReservesTableDialog(self, table_number=2, is_mandatory=True)
        if dialog.exec_():
            # Get table data and convert to polars DataFrame
            table_data = dialog.table_data
            if table_data:
                try:
                    # Parse the clipboard data into pandas DataFrame
                    pandas_df = pd.read_clipboard(sep='\t')
                    # Convert to polars
                    pl_df = pl.from_pandas(pandas_df)
                    
                    # Store the polars DataFrame
                    self.data_entries['tables'][1] = pl_df
                    
                    # Update table display
                    self.input_table.setItem(
                        self.current_row, 
                        4, 
                        QTableWidgetItem("2/4")
                    )
                    
                    # Now show dialog for remaining tables with default options
                    self.show_remaining_tables_dialog()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to parse table data: {str(e)}")
                    # Try again with table 2
                    self.show_table2_dialog()
            else:
                # No data provided, try again
                QMessageBox.warning(self, "Warning", "No table data provided. Please paste data from Excel.")
                self.show_table2_dialog()
        else:
            # Dialog cancelled, update status
            self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Cancelled"))
    
    def show_remaining_tables_dialog(self):
        # Load default data for remaining tables
        try:
            self.load_default_tables()
            
            # Show dialog for remaining tables
            dialog = XReservesRemainingTablesDialog(self, self.data_entries['tables'])
            if dialog.exec_():
                # Update tables with any changes
                self.data_entries['tables'] = dialog.tables
                
                # Save any changed default tables to Excel
                self.save_default_tables(dialog.modified_tables)
                
                # Update table display
                self.input_table.setItem(
                    self.current_row, 
                    4, 
                    QTableWidgetItem("4/4")
                )
                
                # Process all data
                self.process_data()
            else:
                # Dialog cancelled, update status
                self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Cancelled"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error with default tables: {str(e)}")
            self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Failed - Default tables error"))
    
    def load_default_tables(self):
        """Load default tables data from Excel file"""
        if os.path.exists(self.default_data_path):
            # Load tables 3-4 from Excel sheets (XReserves specific sheets)
            for i in range(2, 4):  # Tables 3-4 (index 2-3)
                try:
                    pandas_df = pd.read_excel(self.default_data_path, sheet_name=f"XReserves_Table{i+1}")
                    self.data_entries['tables'][i] = pl.from_pandas(pandas_df)
                except Exception as e:
                    print(f"Error loading default XReserves table {i+1}: {str(e)}")
                    # Create empty table as fallback
                    self.data_entries['tables'][i] = pl.DataFrame()
        else:
            # Create empty default tables
            for i in range(2, 4):
                self.data_entries['tables'][i] = pl.DataFrame()
            
            # Create default Excel file with empty sheets if it doesn't exist
            with pd.ExcelWriter(self.default_data_path) as writer:
                for i in range(1, 5):  # Create 4 sheets for XIPV
                    pd.DataFrame().to_excel(writer, sheet_name=f"Table{i}", index=False)
                for i in range(3, 5):  # Create 2 sheets for XReserves (tables 3-4)
                    pd.DataFrame().to_excel(writer, sheet_name=f"XReserves_Table{i}", index=False)
    
    def save_default_tables(self, modified_indices):
        """Save modified default tables back to Excel"""
        if not os.path.exists(self.default_data_path):
            # Create Excel file if it doesn't exist
            with pd.ExcelWriter(self.default_data_path) as writer:
                for i in range(1, 5):  # Create 4 sheets for XIPV
                    pd.DataFrame().to_excel(writer, sheet_name=f"Table{i}", index=False)
                for i in range(3, 5):  # Create 2 sheets for XReserves (tables 3-4)
                    pd.DataFrame().to_excel(writer, sheet_name=f"XReserves_Table{i}", index=False)
        
        # Only save tables that were modified
        if modified_indices:
            with pd.ExcelWriter(self.default_data_path, mode='a', if_sheet_exists='replace') as writer:
                for i in modified_indices:
                    if i > 1:  # Only save tables 3-4 (index 2-3)
                        # Convert polars to pandas for Excel writing
                        pandas_df = self.data_entries['tables'][i].to_pandas()
                        pandas_df.to_excel(writer, sheet_name=f"XReserves_Table{i+1}", index=False)
    
    def process_data(self):
        try:
            # Load data from file
            file_path = self.data_entries['file_info']['file_path']
            date = self.data_entries['file_info']['date']
            adjustment1 = float(self.data_entries['file_info']['adjustment1'])
            adjustment2 = float(self.data_entries['file_info']['adjustment2'])
            
            # Get all tables
            tables = self.data_entries['tables']
            
            if os.path.exists(file_path) and tables[0] is not None and tables[1] is not None:
                # Determine file type and read into DataFrame
                file_ext = Path(file_path).suffix.lower()
                
                if file_ext == '.csv':
                    file_df = pl.read_csv(file_path)
                elif file_ext in ['.xlsx', '.xls']:
                    # Convert pandas to polars
                    pandas_df = pd.read_excel(file_path)
                    file_df = pl.from_pandas(pandas_df)
                else:
                    QMessageBox.warning(self, "Error", "Unsupported file format")
                    self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Failed - Bad file format"))
                    return
                
                # ====== ADD YOUR CUSTOM FUNCTION HERE ======
                # Process using all dataframes and parameters
                # Example: 
                # result = process_xreserves_data(
                #     file_df, 
                #     date, 
                #     adjustment1, 
                #     adjustment2,
                #     tables[0],  # Table 1 (mandatory)
                #     tables[1],  # Table 2 (mandatory)
                #     tables[2],  # Table 3 (default)
                #     tables[3]   # Table 4 (default)
                # )
                result = 0
                # ============================================
                
                # Update table
                self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Completed"))
                self.input_table.setItem(self.current_row, 6, QTableWidgetItem(str(result)))
                
                QMessageBox.information(self, "Success", f"Data processed successfully. Result: {result}")
            else:
                QMessageBox.warning(self, "Error", "File not found or mandatory tables missing")
                self.input_table.setItem(self.current_row, 5, QTableWidgetItem("Failed - Missing data"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Processing error: {str(e)}")
            self.input_table.setItem(self.current_row, 5, QTableWidgetItem(f"Failed - {str(e)[:20]}..."))


# Class for XReserves file info dialog (similar to XIPV)
class XReservesFileInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("XReserves File Information")
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
        
        # Set placeholders and validators
        self.adjustment1_input.setPlaceholderText("Enter numeric value")
        self.adjustment2_input.setPlaceholderText("Enter numeric value")
        validator = QDoubleValidator()
        self.adjustment1_input.setValidator(validator)
        self.adjustment2_input.setValidator(validator)
        
        # Add to form layout
        layout.addRow("File Path:", file_layout)
        layout.addRow("Date:", self.date_input)
        layout.addRow("Adjustment 1:", self.adjustment1_input)
        layout.addRow("Adjustment 2:", self.adjustment2_input)
        
        # Buttons
        button_box = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("Next")
        self.ok_button.clicked.connect(self.validate_and_accept)
        
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
    
    def validate_and_accept(self):
        # Check if all fields are filled
        if not self.file_path_input.text():
            QMessageBox.warning(self, "Warning", "Please select a file.")
            return
        
        if not self.adjustment1_input.text() or not self.adjustment2_input.text():
            QMessageBox.warning(self, "Warning", "Please enter both adjustment values.")
            return
        
        self.accept()


# Class for XReserves table dialog (similar to XIPV)
class XReservesTableDialog(QDialog):
    def __init__(self, parent=None, table_number=1, is_mandatory=False):
        super().__init__(parent)
        self.setWindowTitle(f"XReserves Table {table_number} Input")
        self.setMinimumSize(600, 400)
        self.table_number = table_number
        self.is_mandatory = is_mandatory
        self.table_data = None
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            f"Paste Table {table_number} data from Excel (Ctrl+V).\n"
            "Make sure to copy the entire table including headers."
        )
        if is_mandatory:
            instructions.setText(instructions.text() + "\n(This table is mandatory)")
        instructions.setStyleSheet("font-weight: bold;")
        
        # Text area for pasted data
        self.data_text = QPlainTextEdit()
        self.data_text.setPlaceholderText("Paste Excel data here...")
        
        # Preview area
        preview_label = QLabel("Data Preview:")
        self.preview_table = QTableWidget()
        
        # Connect paste event
        self.data_text.textChanged.connect(self.update_preview)
        
        # Buttons
        button_box = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("Next")
        self.ok_button.clicked.connect(self.accept)
        
        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.ok_button)
        
        # Add to layout
        layout.addWidget(instructions)
        layout.addWidget(self.data_text)
        layout.addWidget(preview_label)
        layout.addWidget(self.preview_table)
        layout.addLayout(button_box)
        
        self.setLayout(layout)

    def update_preview(self):
        text = self.data_text.toPlainText()
        if text:
            try:
                # Convert the pasted text into a file-like object
                text_io = StringIO(text)

                # Try to parse the text as a DataFrame
                df = pd.read_csv(text_io, sep="\t")

                # Update preview table
                self.preview_table.setRowCount(min(5, len(df)))
                self.preview_table.setColumnCount(len(df.columns))
                self.preview_table.setHorizontalHeaderLabels(df.columns)

                # Fill preview data (first 5 rows)
                for i in range(min(5, len(df))):
                    for j in range(len(df.columns)):
                        item = QTableWidgetItem(str(df.iloc[i, j]))
                        self.preview_table.setItem(i, j, item)

                # Resize columns to content
                self.preview_table.resizeColumnsToContents()

                # Store the data
                self.table_data = text
            except Exception as e:
                # Handle parsing failures
                self.preview_table.setRowCount(0)
                self.preview_table.setColumnCount(0)
                self.table_data = None
                print(f"Error parsing data: {e}")
        else:
            # Clear preview if no text
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
            self.table_data = None


# Class for remaining XReserves tables dialog (similar to XIPV)
class XReservesRemainingTablesDialog(QDialog):
    def __init__(self, parent=None, tables=None):
        super().__init__(parent)
        self.setWindowTitle("Remaining XReserves Tables")
        self.setMinimumSize(800, 600)
        self.tables = tables if tables else [None, None, None, None]
        self.modified_tables = set()  # Track which tables have been modified
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Tables 1 and 2 have been imported. Default data is loaded for Tables 3-4.\n"
            "You can view and modify the default data or import new data."
        )
        instructions.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(instructions)
        
        # Create tab widget for tables
        self.tab_widget = QTabWidget()
        
        # Add tabs for tables 3-4
        for i in range(2, 4):
            tab = self.create_table_tab(i+1, self.tables[i])
            self.tab_widget.addTab(tab, f"Table {i+1}")
        
        main_layout.addWidget(self.tab_widget)
        
        # Buttons
        button_box = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("Finish")
        self.ok_button.clicked.connect(self.accept)
        
        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.ok_button)
        main_layout.addLayout(button_box)
        
        self.setLayout(main_layout)
    
    def create_table_tab(self, table_num, table_data):
        """Create a tab for a table"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout()
        
        # Button to import new data
        import_button = QPushButton(f"Import New Data for Table {table_num}")
        import_button.clicked.connect(lambda: self.import_new_data(table_num-1))
        tab_layout.addWidget(import_button)
        
        # Table widget to display/edit data
        table_widget = QTableWidget()
        self.populate_table_widget(table_widget, table_data)
        table_widget.itemChanged.connect(lambda: self.handle_table_edit(table_num-1, table_widget))
        
        tab_layout.addWidget(QLabel("Default Data (editable):"))
        tab_layout.addWidget(table_widget)
        
        # Store reference to table widget
        setattr(self, f"table{table_num}_widget", table_widget)
        
        tab_widget.setLayout(tab_layout)
        return tab_widget
    
    def populate_table_widget(self, table_widget, table_data):
        """Populate a QTableWidget with data from a polars DataFrame"""
        if table_data is None or table_data.is_empty():
            table_widget.setRowCount(0)
            table_widget.setColumnCount(0)
            return
        
        # Convert polars to pandas for easier handling
        pandas_df = table_data.to_pandas()
        
        # Set table dimensions
        table_widget.setRowCount(len(pandas_df))
        table_widget.setColumnCount(len(pandas_df.columns))
        table_widget.setHorizontalHeaderLabels(pandas_df.columns)
        
        # Fill data
        for i in range(len(pandas_df)):
            for j in range(len(pandas_df.columns)):
                value = pandas_df.iloc[i, j]
                item = QTableWidgetItem(str(value))
                table_widget.setItem(i, j, item)
        
        # Resize columns to content
        table_widget.resizeColumnsToContents()
    
    def import_new_data(self, table_index):
        """Import new data for a table"""
        dialog = XReservesTableDialog(self, table_number=table_index+1)
        if dialog.exec_():
            table_data = dialog.table_data
            if table_data:
                try:
                    # Parse the clipboard data into pandas DataFrame
                    pandas_df = pd.read_clipboard(sep='\t')
                    # Convert to polars
                    pl_df = pl.from_pandas(pandas_df)
                    
                    # Update the table
                    self.tables[table_index] = pl_df
                    
                    # Update UI
                    table_widget = getattr(self, f"table{table_index+1}_widget")
                    self.populate_table_widget(table_widget, pl_df)
                    
                    # Mark as modified
                    self.modified_tables.add(table_index)
                    
                    QMessageBox.information(self, "Success", f"New data imported for Table {table_index+1}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to parse table data: {str(e)}")
    
    def handle_table_edit(self, table_index, table_widget):
        """Handle edits to the table widget"""
        try:
            # Get headers
            headers = []
            for j in range(table_widget.columnCount()):
                headers.append(table_widget.horizontalHeaderItem(j).text())
            
            # Get all data
            data = []
            for i in range(table_widget.rowCount()):
                row_data = []
                for j in range(table_widget.columnCount()):
                    item = table_widget.item(i, j)
                    value = item.text() if item else ""
                    row_data.append(value)
                data.append(row_data)
            
            # Create pandas DataFrame and convert to polars
            pandas_df = pd.DataFrame(data, columns=headers)
            pl_df = pl.from_pandas(pandas_df)
            
            # Update the table
            self.tables[table_index] = pl_df
            
            # Mark as modified
            self.modified_tables.add(table_index)
        except Exception as e:
            print(f"Error updating table data: {str(e)}")

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