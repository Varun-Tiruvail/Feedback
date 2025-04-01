import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QComboBox, QFileDialog, QMessageBox, QTabWidget,
                             QListWidget, QStackedWidget, QRadioButton, QButtonGroup,
                             QGroupBox, QCheckBox, QSplitter, QFrame)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QColor

# Set style for plots
plt.style.use('ggplot')
sns.set_style("whitegrid")

class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas class for embedding charts in Qt"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(self.fig)

class SurveyDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Survey Results Dashboard")
        self.setMinimumSize(1200, 800)
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        
        # Header widget
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Title and data loading section
        title_label = QLabel("Survey Results Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        load_button = QPushButton("Load Survey Results Folder")
        load_button.clicked.connect(self.load_survey_data)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(load_button)
        
        main_layout.addWidget(header_widget)
        
        # Create a splitter for the main content area
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter, 1)
        
        # Left panel for controls
        self.control_panel = QWidget()
        control_layout = QVBoxLayout(self.control_panel)
        
        # Analysis level selection
        level_group = QGroupBox("Analysis Level")
        level_layout = QVBoxLayout()
        
        self.level_combo = QComboBox()
        self.level_combo.addItems(["Overall Analysis", "Section Level Analysis", "Question Level Analysis"])
        self.level_combo.currentIndexChanged.connect(self.update_analysis_view)
        level_layout.addWidget(self.level_combo)
        
        level_group.setLayout(level_layout)
        control_layout.addWidget(level_group)
        
        # Section selection - visible when section/question level is selected
        self.section_group = QGroupBox("Section Filter")
        section_layout = QVBoxLayout()
        
        self.section_combo = QComboBox()
        self.section_combo.currentIndexChanged.connect(self.update_section_filter)
        section_layout.addWidget(self.section_combo)
        
        self.section_group.setLayout(section_layout)
        control_layout.addWidget(self.section_group)
        self.section_group.hide()
        
        # Question selection - visible only when question level is selected
        self.question_group = QGroupBox("Question Filter")
        question_layout = QVBoxLayout()
        
        self.question_list = QListWidget()
        self.question_list.currentRowChanged.connect(self.update_question_filter)
        question_layout.addWidget(self.question_list)
        
        self.question_group.setLayout(question_layout)
        control_layout.addWidget(self.question_group)
        self.question_group.hide()
        
        # Chart type selection
        chart_group = QGroupBox("Chart Type")
        chart_layout = QVBoxLayout()
        
        self.chart_combo = QComboBox()
        self.chart_combo.addItems([
            "Pie Chart", "Bar Chart", "Horizontal Bar Chart", 
            "Stacked Bar Chart", "Line Chart", "Heatmap"
        ])
        self.chart_combo.currentIndexChanged.connect(self.update_chart_type)
        chart_layout.addWidget(self.chart_combo)
        
        chart_group.setLayout(chart_layout)
        control_layout.addWidget(chart_group)
        
        # Additional filters group
        filter_group = QGroupBox("Additional Filters")
        filter_layout = QVBoxLayout()
        
        # Time period filter (if timestamps available)
        self.time_period_combo = QComboBox()
        self.time_period_combo.addItem("All Time")
        filter_layout.addWidget(QLabel("Time Period:"))
        filter_layout.addWidget(self.time_period_combo)
        
        # Summary statistics option
        self.show_stats_check = QCheckBox("Show Summary Statistics")
        self.show_stats_check.setChecked(True)
        self.show_stats_check.stateChanged.connect(self.toggle_statistics)
        filter_layout.addWidget(self.show_stats_check)
        
        # Show/Hide labels
        self.show_labels_check = QCheckBox("Show Data Labels")
        self.show_labels_check.setChecked(True)
        self.show_labels_check.stateChanged.connect(self.update_chart)
        filter_layout.addWidget(self.show_labels_check)
        
        # Show percentages instead of counts
        self.show_percent_check = QCheckBox("Show Percentages")
        self.show_percent_check.setChecked(True)
        self.show_percent_check.stateChanged.connect(self.update_chart)
        filter_layout.addWidget(self.show_percent_check)
        
        # Apply button at bottom of controls
        self.apply_button = QPushButton("Apply Filters")
        self.apply_button.clicked.connect(self.update_chart)
        filter_layout.addWidget(self.apply_button)
        
        filter_group.setLayout(filter_layout)
        control_layout.addWidget(filter_group)
        
        # Add stretch to push controls to top
        control_layout.addStretch()
        
        # Add export button at bottom
        export_button = QPushButton("Export Dashboard")
        export_button.clicked.connect(self.export_dashboard)
        control_layout.addWidget(export_button)
        
        # Add control panel to splitter
        self.main_splitter.addWidget(self.control_panel)
        
        # Right panel for visualization
        self.vis_panel = QWidget()
        vis_layout = QVBoxLayout(self.vis_panel)
        
        # Tab widget for different views
        self.view_tabs = QTabWidget()
        
        # Create tabs for charts and statistics
        self.chart_widget = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_widget)
        
        # Create matplotlib canvas for the chart
        self.chart_canvas = MatplotlibCanvas(width=5, height=4, dpi=100)
        self.chart_layout.addWidget(self.chart_canvas)
        
        # Statistics panel
        self.stats_widget = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_widget)
        self.stats_label = QLabel("No data loaded yet")
        self.stats_layout.addWidget(self.stats_label)
        
        # Add widgets to tabs
        self.view_tabs.addTab(self.chart_widget, "Visualization")
        self.view_tabs.addTab(self.stats_widget, "Statistics")
        
        vis_layout.addWidget(self.view_tabs)
        
        # Add visualization panel to splitter
        self.main_splitter.addWidget(self.vis_panel)
        
        # Set splitter proportions
        self.main_splitter.setSizes([300, 900])
        
        # Initialize data structures
        self.survey_data = pd.DataFrame()
        self.sections = []
        self.questions = {}
        self.current_level = "Overall Analysis"
        self.current_section = ""
        self.current_question = ""
        self.current_chart_type = "Pie Chart"
        
        # Set up an initial empty chart
        self.setup_empty_chart()
    
    def setup_empty_chart(self):
        """Display an empty chart with a message"""
        self.chart_canvas.axes.clear()
        self.chart_canvas.axes.text(0.5, 0.5, "No data loaded. Please load survey results.",
                                   horizontalalignment='center', verticalalignment='center',
                                   fontsize=12)
        self.chart_canvas.axes.axis('off')
        self.chart_canvas.draw()
    
    def load_survey_data(self):
        """Load survey results from multiple Excel files in a folder"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder with Survey Results")
        
        if not folder_path:
            return
        
        try:
            # Find all Excel files in the folder
            excel_files = [f for f in os.listdir(folder_path) 
                         if f.endswith('.xlsx') or f.endswith('.xls')]
            
            if not excel_files:
                QMessageBox.warning(self, "No Files Found", 
                                  "No Excel files found in the selected folder.")
                return
            
            # Load and concatenate all Excel files
            all_data = []
            
            for file in excel_files:
                file_path = os.path.join(folder_path, file)
                try:
                    # Extract timestamp from filename if possible (for time filtering)
                    timestamp = None
                    try:
                        # Try to extract date from filename (assuming format like survey_YYYY-MM-DD.xlsx)
                        filename = os.path.basename(file)
                        date_part = filename.split('_')[-1].split('.')[0]
                        timestamp = pd.to_datetime(date_part)
                    except:
                        # If can't extract, use file modification time
                        mod_time = os.path.getmtime(file_path)
                        timestamp = pd.to_datetime(mod_time, unit='s')
                    
                    # Read the Excel file
                    df = pd.read_excel(file_path)
                    
                    # Add file metadata
                    df['Source File'] = file
                    df['Timestamp'] = timestamp
                    
                    all_data.append(df)
                except Exception as e:
                    print(f"Error loading {file}: {str(e)}")
            
            if not all_data:
                QMessageBox.warning(self, "Loading Error", 
                                  "Could not load any valid survey data from the files.")
                return
            
            # Combine all data
            self.survey_data = pd.concat(all_data, ignore_index=True)
            
            # Update UI with available sections and questions
            self.update_filters()
            
            # Generate initial visualization
            self.update_chart()
            
            # Show success message
            QMessageBox.information(self, "Data Loaded", 
                                  f"Successfully loaded {len(excel_files)} survey result files with "
                                  f"{len(self.survey_data)} responses.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load survey data: {str(e)}")
    
    def update_filters(self):
        """Update the filter options based on loaded data"""
        if self.survey_data.empty:
            return
        
        # Get unique sections
        self.sections = sorted(self.survey_data['Section'].unique())
        
        # Update section dropdown
        self.section_combo.clear()
        self.section_combo.addItems(self.sections)
        
        # Get questions for each section
        self.questions = {}
        for section in self.sections:
            section_questions = self.survey_data[self.survey_data['Section'] == section]['Question'].unique()
            self.questions[section] = sorted(section_questions)
        
        # Update question list for initial section
        self.update_question_list(self.sections[0] if self.sections else "")
        
        # Update time periods if available
        if 'Timestamp' in self.survey_data.columns:
            self.survey_data['Year-Month'] = self.survey_data['Timestamp'].dt.strftime('%Y-%m')
            time_periods = sorted(self.survey_data['Year-Month'].unique())
            
            self.time_period_combo.clear()
            self.time_period_combo.addItem("All Time")
            self.time_period_combo.addItems(time_periods)
    
    def update_question_list(self, section):
        """Update the question list when section changes"""
        self.question_list.clear()
        if section in self.questions:
            self.question_list.addItems(self.questions[section])
            if self.questions[section]:
                self.question_list.setCurrentRow(0)
    
    def update_analysis_view(self):
        """Update the visible controls based on analysis level selection"""
        level = self.level_combo.currentText()
        self.current_level = level
        
        # Show/hide section and question filters based on level
        if level == "Overall Analysis":
            self.section_group.hide()
            self.question_group.hide()
        elif level == "Section Level Analysis":
            self.section_group.show()
            self.question_group.hide()
        else:  # Question Level Analysis
            self.section_group.show()
            self.question_group.show()
        
        self.update_chart()
    
    def update_section_filter(self):
        """Handle section selection change"""
        section = self.section_combo.currentText()
        self.current_section = section
        self.update_question_list(section)
        self.update_chart()
    
    def update_question_filter(self):
        """Handle question selection change"""
        selected_items = self.question_list.selectedItems()
        if selected_items:
            self.current_question = selected_items[0].text()
            self.update_chart()
    
    def update_chart_type(self):
        """Handle chart type change"""
        self.current_chart_type = self.chart_combo.currentText()
        self.update_chart()
    
    def toggle_statistics(self):
        """Toggle visibility of statistics panel"""
        if self.show_stats_check.isChecked():
            self.update_statistics()
        
    def update_statistics(self):
        """Update the statistics panel with current data"""
        if self.survey_data.empty:
            self.stats_label.setText("No data loaded yet")
            return
        
        # Filter data based on current selections
        filtered_data = self.get_filtered_data()
        
        if filtered_data.empty:
            self.stats_label.setText("No data available for the selected filters")
            return
        
        # Generate statistics based on analysis level
        stats_text = ""
        
        if self.current_level == "Overall Analysis":
            # Overall response statistics
            total_responses = len(filtered_data['Source File'].unique())
            total_questions = filtered_data['Question'].nunique()
            total_sections = filtered_data['Section'].nunique()
            
            # Response rates by section
            section_counts = filtered_data.groupby('Section').size()
            section_percents = section_counts / section_counts.sum() * 100
            
            stats_text += f"<h3>Overall Survey Statistics</h3>"
            stats_text += f"<p>Total Survey Responses: {total_responses}</p>"
            stats_text += f"<p>Number of Sections: {total_sections}</p>"
            stats_text += f"<p>Number of Questions: {total_questions}</p>"
            
            stats_text += f"<h4>Response Distribution by Section</h4>"
            stats_text += "<table border='1' cellpadding='5'>"
            stats_text += "<tr><th>Section</th><th>Count</th><th>Percentage</th></tr>"
            
            for section, count in section_counts.items():
                percent = section_percents[section]
                stats_text += f"<tr><td>{section}</td><td>{count}</td><td>{percent:.1f}%</td></tr>"
            
            stats_text += "</table>"
            
        elif self.current_level == "Section Level Analysis":
            # Section level statistics
            section = self.current_section
            section_data = filtered_data[filtered_data['Section'] == section]
            
            total_questions = section_data['Question'].nunique()
            response_counts = section_data.groupby(['Question', 'Selected Text']).size().unstack()
            
            stats_text += f"<h3>Section Analysis: {section}</h3>"
            stats_text += f"<p>Number of Questions: {total_questions}</p>"
            
            # Top response patterns
            if 'Selected Text' in section_data.columns:
                option_counts = section_data['Selected Text'].value_counts()
                stats_text += f"<h4>Top Responses</h4>"
                stats_text += "<table border='1' cellpadding='5'>"
                stats_text += "<tr><th>Response</th><th>Count</th><th>Percentage</th></tr>"
                
                for option, count in option_counts.head(5).items():
                    percent = count / len(section_data) * 100
                    stats_text += f"<tr><td>{option}</td><td>{count}</td><td>{percent:.1f}%</td></tr>"
                
                stats_text += "</table>"
            
        else:  # Question Level Analysis
            # Question level statistics
            section = self.current_section
            question = self.current_question
            
            question_data = filtered_data[
                (filtered_data['Section'] == section) & 
                (filtered_data['Question'] == question)
            ]
            
            stats_text += f"<h3>Question Analysis</h3>"
            stats_text += f"<p>Section: {section}</p>"
            stats_text += f"<p>Question: {question}</p>"
            
            # Response distribution
            if 'Selected Text' in question_data.columns:
                option_counts = question_data['Selected Text'].value_counts()
                total_responses = len(question_data)
                
                stats_text += f"<h4>Response Distribution</h4>"
                stats_text += f"<p>Total Responses: {total_responses}</p>"
                stats_text += "<table border='1' cellpadding='5'>"
                stats_text += "<tr><th>Response</th><th>Count</th><th>Percentage</th></tr>"
                
                for option, count in option_counts.items():
                    percent = count / total_responses * 100
                    stats_text += f"<tr><td>{option}</td><td>{count}</td><td>{percent:.1f}%</td></tr>"
                
                stats_text += "</table>"
        
        self.stats_label.setText(stats_text)
    
    def get_filtered_data(self):
        """Get data filtered according to current selections"""
        if self.survey_data.empty:
            return pd.DataFrame()
        
        filtered_data = self.survey_data.copy()
        
        # Apply time period filter if selected
        time_period = self.time_period_combo.currentText()
        if time_period != "All Time" and 'Year-Month' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['Year-Month'] == time_period]
        
        # Filter based on analysis level
        if self.current_level == "Section Level Analysis":
            if self.current_section:
                filtered_data = filtered_data[filtered_data['Section'] == self.current_section]
        
        elif self.current_level == "Question Level Analysis":
            if self.current_section and self.current_question:
                filtered_data = filtered_data[
                    (filtered_data['Section'] == self.current_section) & 
                    (filtered_data['Question'] == self.current_question)
                ]
        
        return filtered_data
    
    def update_chart(self):
        """Update the chart based on current selections"""
        if self.survey_data.empty:
            self.setup_empty_chart()
            return
        
        # Get filtered data
        filtered_data = self.get_filtered_data()
        
        if filtered_data.empty:
            self.chart_canvas.axes.clear()
            self.chart_canvas.axes.text(0.5, 0.5, "No data available for the selected filters",
                                       horizontalalignment='center', verticalalignment='center',
                                       fontsize=12)
            self.chart_canvas.axes.axis('off')
            self.chart_canvas.draw()
            return
        
        # Clear previous chart
        self.chart_canvas.axes.clear()
        
        # Prepare data based on analysis level
        if self.current_level == "Overall Analysis":
            # For overall, show section distribution
            plot_data = filtered_data.groupby('Section').size()
            title = "Overall Response Distribution by Section"
            
        elif self.current_level == "Section Level Analysis":
            # For section level, show question distribution
            plot_data = filtered_data.groupby('Question').size()
            title = f"Response Count by Question in {self.current_section} Section"
            
        else:  # Question Level Analysis
            # For question level, show response distribution
            if 'Selected Text' in filtered_data.columns:
                plot_data = filtered_data['Selected Text'].value_counts()
                title = f"Response Distribution for: {self.current_question}"
            else:
                plot_data = filtered_data.groupby('Selected Option').size()
                title = f"Response Distribution for: {self.current_question}"
        
        # Convert to percentages if needed
        show_percent = self.show_percent_check.isChecked()
        if show_percent:
            plot_data_percent = plot_data / plot_data.sum() * 100
        else:
            plot_data_percent = plot_data
        
        # Create the appropriate chart type
        chart_type = self.current_chart_type
        show_labels = self.show_labels_check.isChecked()
        
        if chart_type == "Pie Chart":
            # Create pie chart
            self.chart_canvas.axes.pie(
                plot_data, 
                labels=plot_data.index if show_labels else None,
                autopct='%1.1f%%' if show_labels else None,
                startangle=90,
                shadow=False
            )
            self.chart_canvas.axes.axis('equal')
            
            # Add legend if not showing labels
            if not show_labels:
                self.chart_canvas.axes.legend(plot_data.index, loc='best')
            
        elif chart_type == "Bar Chart":
            # Create vertical bar chart
            bars = self.chart_canvas.axes.bar(plot_data.index, plot_data)
            
            # Add data labels if requested
            if show_labels:
                for bar in bars:
                    height = bar.get_height()
                    self.chart_canvas.axes.text(
                        bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}' if not show_percent else f'{height:.1f}%',
                        ha='center', va='bottom', rotation=0
                    )
            
            # Format x-axis labels
            self.chart_canvas.axes.set_xticklabels(plot_data.index, rotation=45, ha='right')
            
        elif chart_type == "Horizontal Bar Chart":
            # Create horizontal bar chart
            bars = self.chart_canvas.axes.barh(plot_data.index, plot_data)
            
            # Add data labels if requested
            if show_labels:
                for bar in bars:
                    width = bar.get_width()
                    self.chart_canvas.axes.text(
                        width, bar.get_y() + bar.get_height()/2.,
                        f'{width:.0f}' if not show_percent else f'{width:.1f}%',
                        ha='left', va='center'
                    )
            
        elif chart_type == "Line Chart":
            # For line chart, we need time dimension
            if self.current_level == "Question Level Analysis" and 'Timestamp' in filtered_data.columns:
                # Group by time and option
                time_series = filtered_data.groupby([
                    pd.Grouper(key='Timestamp', freq='M'), 'Selected Text'
                ]).size().unstack()
                
                # Plot each option as a line
                time_series.plot(ax=self.chart_canvas.axes, marker='o')
                
                # Format x-axis as dates
                self.chart_canvas.axes.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m'))
                plt.setp(self.chart_canvas.axes.xaxis.get_majorticklabels(), rotation=45)
                
                # Add legend
                self.chart_canvas.axes.legend(title="Response")
                
                # Update title
                title = f"Trend Analysis for: {self.current_question}"
            else:
                # Fallback to bar chart if time dimension not appropriate
                bars = self.chart_canvas.axes.bar(plot_data.index, plot_data)
                
                # Add data labels if requested
                if show_labels:
                    for bar in bars:
                        height = bar.get_height()
                        self.chart_canvas.axes.text(
                            bar.get_x() + bar.get_width()/2., height,
                            f'{height:.0f}' if not show_percent else f'{height:.1f}%',
                            ha='center', va='bottom'
                        )
                
                # Format x-axis labels
                self.chart_canvas.axes.set_xticklabels(plot_data.index, rotation=45, ha='right')
        
        elif chart_type == "Stacked Bar Chart":
            # This works best for question level analysis with time dimension
            if 'Timestamp' in filtered_data.columns:
                # Group by time period (month)
                filtered_data['month'] = pd.to_datetime(filtered_data['Timestamp']).dt.strftime('%Y-%m')
                
                # Group by month and response
                pivot_data = filtered_data.pivot_table(
                    index='month', 
                    columns='Selected Text', 
                    values='Source File', 
                    aggfunc='count', 
                    fill_value=0
                )
                
                # Plot stacked bar
                pivot_data.plot(kind='bar', stacked=True, ax=self.chart_canvas.axes)
                
                # Update title
                title = f"Response Distribution Over Time"
            else:
                # Fallback to simple bar chart
                bars = self.chart_canvas.axes.bar(plot_data.index, plot_data)
                
                if show_labels:
                    for bar in bars:
                        height = bar.get_height()
                        self.chart_canvas.axes.text(
                            bar.get_x() + bar.get_width()/2., height,
                            f'{height:.0f}' if not show_percent else f'{height:.1f}%',
                            ha='center', va='bottom'
                        )
        
        elif chart_type == "Heatmap":
            # Heatmap works well for section-question analysis
            if self.current_level == "Overall Analysis" or self.current_level == "Section Level Analysis":
                # Create a pivot table of responses by question and option
                if self.current_level == "Overall Analysis":
                    # Group by section and response
                    heatmap_data = pd.crosstab(
                        filtered_data['Section'], 
                        filtered_data['Selected Text'] if 'Selected Text' in filtered_data.columns 
                        else filtered_data['Selected Option']
                    )
                else:
                    # Group by question and response
                    heatmap_data = pd.crosstab(
                        filtered_data['Question'], 
                        filtered_data['Selected Text'] if 'Selected Text' in filtered_data.columns 
                        else filtered_data['Selected Option']
                    )
                
                # Calculate percentages by row
                if show_percent:
                    heatmap_data = heatmap_data.div(heatmap_data.sum(axis=1), axis=0) * 100
                
                # Plot heatmap
                im = self.chart_canvas.axes.imshow(heatmap_data.values, cmap="YlGnBu")
                
                # Add colorbar
                cbar = self.chart_canvas.fig.colorbar(im, ax=self.chart_canvas.axes)
                cbar.set_label('Response Count' if not show_percent else 'Percentage (%)')
                
                # Add labels
                self.chart_canvas.axes.set_xticks(np.arange(len(heatmap_data.columns)))
                self.chart_canvas.axes.set_yticks(np.arange(len(heatmap_data.index)))
                self.chart_canvas.axes.set_xticklabels(heatmap_data.columns)
                self.chart_canvas.axes.set_yticklabels(heatmap_data.index)
                
                # Rotate x labels
                plt.setp(self.chart_canvas.axes.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
                
                # Add text annotations if requested
                if show_labels:
                    for i in range(len(heatmap_data.index)):
                        for j in range(len(heatmap_data.columns)):
                            value = heatmap_data.iloc[i, j]
                            text_color = "white" if value > heatmap_data.values.max() / 2 else "black"
                            self.chart_canvas.axes.text(
                                j, i, f"{value:.0f}" if not show_percent else f"{value:.1f}%",
                                ha="center", va="center", color=text_color
                            )
            else:
                # Fallback to bar chart for question level analysis
                bars = self.chart_canvas.axes.bar(plot_data.index, plot_data)
                
                if show_labels:
                    for bar in bars:
                        height = bar.get_height()
                        self.chart_canvas.axes.text(
                            bar.get_x() + bar.get_width()/2., height,
                            f'{height:.0f}' if not show_percent else f'{height:.1f}%',
                            ha='center', va='bottom'
                        )
        
        # Set chart title and labels
        self.chart_canvas.axes.set_title(title)
        
        if chart_type not in ["Pie Chart", "Heatmap"]:
            y_label = "Percentage (%)" if show_percent else "Count"
            self.chart_canvas.axes.set_ylabel(y_label)
            
            if chart_type != "Horizontal Bar Chart":
                x_label = "Section"