import tkinter as tk
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class ReportScreen:
    def __init__(self, root, data_handler):
        self.root = root
        self.data = data_handler.read()

        self.create_gui()


    def create_gui(self):
        """Creates Tkinter GUI."""

        # Create frame that wraps this screen.
        self.frame = tk.Frame(self.root)

        # Create title label.
        self.title_label = tk.Label(self.frame, text="Report Generator", font=("Helvetica", 20))
        self.title_label.pack(pady=20)

        # Create button to generate report.
        self.generate_button = tk.Button(self.frame, text="Generate Report", command=self.generate_report)
        self.generate_button.pack()

    
    def generate_report(self):
        """Generates a PDF report of repl data."""

        # Create PDF document
        pdf_canvas = canvas.Canvas('report.pdf', pagesize=letter)

        # Add total project text
        self.draw_text(pdf_canvas, f"Total Projects: {len(self.data)}", 12, inch, inch)

        # Save the PDF
        pdf_canvas.save()


    def draw_text(self, pdf_canvas, text, font_size, x, y):
        """
        Draws text on the canvas, assuming a coordinate system where the
        origin is at the top left, given font size and top left corner coordinates.
        """

        pdf_canvas.setFont("Helvetica", font_size)
        actual_y = letter[1] - font_size - y
        pdf_canvas.drawString(x, actual_y, text)
