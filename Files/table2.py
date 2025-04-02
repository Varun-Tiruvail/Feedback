import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QWidget, QMessageBox
)
from PyQt5.QtGui import QClipboard
import polars as pl

class ExcelTableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Table Paster")

        # Required headers
        self.required_headers = ["Question", "Option1", "Option2"]

        # Create table widget
        self.table_widget = QTableWidget()
        
        # Create buttons
        self.paste_button = QPushButton("Paste Table")
        self.paste_button.clicked.connect(self.paste_table)
        
        self.convert_button = QPushButton("Convert to Polars DataFrame")
        self.convert_button.clicked.connect(self.convert_to_polars)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addWidget(self.paste_button)
        layout.addWidget(self.convert_button)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def paste_table(self):
        clipboard = QApplication.clipboard()
        data = clipboard.text()  # Get clipboard text
        rows = data.strip().split("\n")

        if not rows:
            self.show_error_message("Clipboard is empty or contains invalid data.")
            return

        # Populate the table
        self.table_widget.setRowCount(len(rows))
        self.table_widget.setColumnCount(len(rows[0].split("\t")))

        for i, row in enumerate(rows):
            columns = row.split("\t")
            for j, cell in enumerate(columns):
                self.table_widget.setItem(i, j, QTableWidgetItem(cell))

    def convert_to_polars(self):
        # Extract table headers
        cols = self.table_widget.columnCount()
        headers = [
            self.table_widget.item(0, j).text() if self.table_widget.item(0, j) else ""
            for j in range(cols)
        ]

        # Validate headers
        missing_headers = [h for h in self.required_headers if h not in headers]
        extra_headers = [h for h in headers if h not in self.required_headers]

        if missing_headers or extra_headers:
            error_message = ""
            if missing_headers:
                error_message += f"Missing columns: {', '.join(missing_headers)}\n"
            if extra_headers:
                error_message += f"Extra columns: {', '.join(extra_headers)}"
            self.show_error_message(error_message)
            return

        # Extract data
        rows = self.table_widget.rowCount()
        data = []
        for i in range(1, rows):  # Skip the first row (headers)
            row_data = []
            for j in range(cols):
                item = self.table_widget.item(i, j)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Create Polars DataFrame
        dataframe = pl.DataFrame(data, schema=headers)

        # Print DataFrame to terminal
        print("Polars DataFrame:")
        print(dataframe)

    def show_error_message(self, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Invalid Table Format")
        msg_box.setText(message)
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelTableApp()
    window.show()
    sys.exit(app.exec_())