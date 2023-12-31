import tkinter as tk
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import os

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

        # Create PDF document.
        self.pdf_canvas = canvas.Canvas('report.pdf', pagesize=letter)

        # Gather data.
        file_type_count, file_count = self.count_files_and_types()
        total_lines = sum(file_type_count.values())

        self.draw_text('Repl.it Report', font_size=20, line_spacing=10)
        self.draw_text(f'Total projects: {len(self.data)}')
        self.draw_text(f'Total files: {file_count}')
        self.draw_text(f'Total lines of code: {total_lines}')
        self.draw_text(f'Average lines per file: {round(total_lines/file_count, 2)}')
        self.draw_text('', font_size=0, line_spacing=10)
        self.draw_pie_chart(file_type_count.values(), file_type_count.keys(), 'File Types', 4*inch)
        for file_type in file_type_count:
            self.draw_text(f'Lines of {file_type}: {file_type_count[file_type]}')

        # Save the PDF.
        self.pdf_canvas.save()


    def draw_text(self, text, font_size=12, line_spacing=4, x=inch, y=None):
        """
        Draws text on the canvas, assuming a coordinate system where the
        origin is at the top left, given font size and top left corner coordinates.
        """

        # If y is not specified, use the current line.
        if y is None:
            y = self.line_begin

        self.pdf_canvas.setFont('Helvetica', font_size)
        actual_y = letter[1] - font_size - y
        self.pdf_canvas.drawString(x, actual_y, text)

        # Move next line down.
        self.line_begin += font_size + line_spacing


    def draw_pie_chart(self, data, labels, title, x=inch, y=None):
        """
        Draws a pie chart on the canvas, assuming a coordinate system where the
        origin is at the top left, given top left corner coordinates.
        """

        # If y is not specified, use the current line.
        if y is None:
            y = self.line_begin

        # Plot the pie chart.
        width = 5
        height = 3
        plt.figure(figsize=(width, height))
        plt.pie(data, labels=labels)
        plt.title(title)
        plt.savefig('pie_chart.png')
        plt.close()

        # Draw the pie chart on the canvas.
        self.pdf_canvas.drawInlineImage('pie_chart.png', x, letter[1] - height*inch - y, width=width*inch, height=height*inch)

        # Delete temporary pie chart file.
        os.remove('pie_chart.png')


    def count_files_and_types(self):
        """
        Counts the total number of lines of each file type, by file extension,
        as well as the total number of code files (e.g. not images).
        """

        # Store the count of each file type in a dictionary.
        # Key: file extension, Value: count
        type_count = dict()
        code_file_count = 0

        # For each file, count the number of lines and add it to the count dictionary.
        search_dir = os.path.join(os.getcwd(), 'output/')
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                extension = file.split('.')[-1]
                file_path = os.path.normpath(os.path.join(root, file))
                file_line_count = self.count_lines(file_path)
                if file_line_count == -1:
                    # Not a readable file, perhaps an image or binary file. Skip this file.
                    continue
                type_count[extension] = type_count.get(extension, 0) + file_line_count
                code_file_count += 1

        return type_count, code_file_count


    def count_lines(self, file_path):
        """Counts the number of lines in a file."""

        count = 0
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    count += 1
        except UnicodeDecodeError:
            # Not a readable file, perhaps an image or binary file.
            return -1
        
        return count
