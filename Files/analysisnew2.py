import tkinter as tk
from tkinter import ttk
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.pyplot as plt

# Create the main application window
class AnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Analysis App")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")  # Light background color

        # Create a frame for the graph
        self.graph_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.RAISED, bd=2)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.set_title("Dynamic Graph Animation", fontsize=14)
        self.ax.set_xlabel("X-axis")
        self.ax.set_ylabel("Y-axis")
        self.line, = self.ax.plot([], [], lw=2, color='blue')

        # Embed the matplotlib figure in the Tkinter app
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Create a frame for buttons
        self.button_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.button_frame.pack(fill=tk.X, pady=10)

        # Add styled buttons
        self.start_button = tk.Button(
            self.button_frame, text="Start Animation", command=self.start_animation,
            bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), relief=tk.RAISED,
            bd=2, activebackground="#45a049", activeforeground="white", highlightthickness=0
        )
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=5)

        self.stop_button = tk.Button(
            self.button_frame, text="Stop Animation", command=self.stop_animation,
            bg="#f44336", fg="white", font=("Arial", 12, "bold"), relief=tk.RAISED,
            bd=2, activebackground="#e53935", activeforeground="white", highlightthickness=0
        )
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=5)

        # Animation variables
        self.anim = None
        self.x_data = []
        self.y_data = []

    def start_animation(self):
        if self.anim is None:
            self.anim = FuncAnimation(self.fig, self.update_graph, frames=100, interval=100, repeat=True)
            self.canvas.draw()

    def stop_animation(self):
        if self.anim is not None:
            self.anim.event_source.stop()
            self.anim = None

    def update_graph(self, frame):
        self.x_data.append(frame)
        self.y_data.append(np.sin(frame * 0.1))
        self.line.set_data(self.x_data, self.y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = AnalysisApp(root)
    root.mainloop()