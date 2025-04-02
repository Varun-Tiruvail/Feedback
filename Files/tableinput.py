import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtGui import QClipboard
import polars as pl  # Import Polars

class ExcelTableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Table Paster")

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
        self.table_widget.setRowCount(len(rows))
        self.table_widget.setColumnCount(len(rows[0].split("\t")))

        for i, row in enumerate(rows):
            columns = row.split("\t")
            for j, cell in enumerate(columns):
                self.table_widget.setItem(i, j, QTableWidgetItem(cell))

    def convert_to_polars(self):
        # Extract table data
        rows = self.table_widget.rowCount()
        cols = self.table_widget.columnCount()

        # Separate headers from data
        headers = []
        data = []

        for j in range(cols):
            header_item = self.table_widget.item(0, j)
            headers.append(header_item.text() if header_item else f"Column {j+1}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelTableApp()
    window.show()
    sys.exit(app.exec_())