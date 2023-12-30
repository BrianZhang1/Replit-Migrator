import tkinter as tk
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class ReportScreen:
    def __init__(self, root, data_handler):
        self.root = root
        self.data = data_handler.read()

        self.pdf_canvas = None  # Canvas for PDF document, initialized when needed.
        self.line_begin = inch  # Tracks the y coordinate of the beginning of the next line to be drawn.

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
        self.pdf_canvas = canvas.Canvas('report.pdf', pagesize=letter)

        self.draw_text("Repl.it Report", font_size=20, line_spacing=10)
        self.draw_text(f"Total Projects: {len(self.data)}")

        # Save the PDF
        self.pdf_canvas.save()


    def draw_text(self, text, font_size=12, line_spacing=4, x=inch, y=None):
        """
        Draws text on the canvas, assuming a coordinate system where the
        origin is at the top left, given font size and top left corner coordinates.
        """

        # If y is not specified, use the current line.
        if y is None:
            y = self.line_begin

        self.pdf_canvas.setFont("Helvetica", font_size)
        actual_y = letter[1] - font_size - y
        self.pdf_canvas.drawString(x, actual_y, text)

        # Move next line down.
        self.line_begin += font_size + line_spacing
