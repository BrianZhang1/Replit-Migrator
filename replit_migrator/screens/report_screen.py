import tkinter as tk
from tkinter import ttk
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import os

class ReportScreen:
    def __init__(self, root, change_screen, data_handler):
        self.root = root
        self.change_screen = change_screen
        self.data = data_handler.read_projects()

        self.pdf_canvas = None  # Canvas for PDF document, initialized when needed.
        self.line_begin = inch  # Tracks the y coordinate of the beginning of the next line to be drawn.
        self.report_options = {
            'Total Metrics': True,
            'Average Metrics': True,
            'Line Counts': True,
            'Project Index': True
        }

        self.create_gui()


    def create_gui(self):
        """Creates Tkinter GUI."""

        # Create frame that wraps this screen.
        self.frame = ttk.Frame(self.root)

        # Create title label.
        self.title_label = ttk.Label(self.frame, text='Report Generator', style='Header1.TLabel')
        self.title_label.pack()

        # Create instructions label.
        self.instructions_label = ttk.Label(self.frame, text='Unselect the options you would like to exclude from the report.')
        self.instructions_label.pack(pady=(self.root.winfo_reqheight()/2-150, 10))

        # Create checkboxes for each report option.
        self.option_widgets = {}
        for option in self.report_options:
            option_enabled = self.report_options[option]
            option_checkbox = ttk.Checkbutton(self.frame, text=option, command=lambda option=option: self.update_option(option), state='selected')
            if option_enabled:
                option_checkbox.state(['selected'])
            option_checkbox.pack()
            self.option_widgets[option] = option_checkbox

        # Create button to generate report.
        self.generate_button = ttk.Button(self.frame, text="Generate Report", command=self.generate_report)
        self.generate_button.pack(pady=20)

        # Create back button.
        self.back_button = ttk.Button(self.frame, text="Back", command=lambda: self.change_screen('home'))
        self.back_button.place(x=30, y=510)


    def update_option(self, option):
        clicked_checkbox = self.option_widgets[option]
        if clicked_checkbox.instate(['selected']):
            self.report_options[option] = True
        else:
            self.report_options[option] = False

    
    def generate_report(self):
        """Generates a PDF report of repl data."""

        # Create PDF document.
        self.pdf_canvas = canvas.Canvas('report.pdf', pagesize=letter)

        # Gather data.
        file_type_count, file_count = self.count_files_and_types()
        total_lines = sum(file_type_count.values())
        total_size = sum([float(self.data[project]['size'].split(' ')[0]) for project in self.data])

        self.draw_text('Repl.it Report', font_size=20, line_spacing=20)
        if self.report_options['Line Counts']:
            self.draw_pie_chart(file_type_count.values(), file_type_count.keys(), 'File Types', 3.5*inch)
        if self.report_options['Total Metrics']:
            self.draw_text(f'Total projects: {len(self.data)}')
            self.draw_text(f'Total files: {file_count}')
            self.draw_text(f'Total lines of code: {total_lines}')
            self.draw_text(f'Total size: {round(total_size, 2)} MiB')
            self.draw_text('', font_size=0, line_spacing=10)
        if self.report_options['Average Metrics']:
            self.draw_text(f'Average files per project: {round(len(self.data)/file_count, 2)}')
            self.draw_text(f'Average lines per file: {round(total_lines/file_count, 2)}')
            self.draw_text(f'Average size per file: {round(total_size/file_count, 2)} MiB')
            self.draw_text('', font_size=0, line_spacing=10)
        if self.report_options['Line Counts']:
            for file_type in file_type_count:
                self.draw_text(f'Lines of {file_type}: {file_type_count[file_type]}')
        if self.report_options['Project Index']:
            self.next_page()
            self.draw_text('Project Index', font_size=15, line_spacing=20)
            self.draw_project_details(None, header=True)
            for project_name in self.data:
                self.draw_project_details(project_name)

        # Save the PDF.
        self.pdf_canvas.save()

        # Reset the line begin y-coordinate for proper formatting in consecutive report generation.
        self.line_begin = inch


    def draw_text(self, text, font_size=12, line_spacing=4, x=inch, y=None):
        """
        Draws text on the canvas, assuming a coordinate system where the
        origin is at the top left, given font size and top left corner coordinates.
        """

        # If y is not specified, use the current line.
        y_inputted = False if y is None else True
        if not y_inputted:
            y = self.line_begin

        self.pdf_canvas.setFont('Helvetica', font_size)
        actual_y = letter[1] - font_size - y
        self.pdf_canvas.drawString(x, actual_y, text)

        if not y_inputted:
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


    def next_page(self):
        """Finishes the current page and resets the line begin coordinate."""

        self.pdf_canvas.showPage()
        self.line_begin = inch


    def draw_project_details(self, project_name, header=False):
        temp = None
        if header:
            project_name = 'Name'
            try:
                temp = self.data['Name']
            except KeyError:
                pass
            self.data['Name'] = {
                'last_modified': 'Last Modified',
                'size': 'Size',
                'path': 'Path'
            }

        cur_x = inch
        self.draw_text(project_name, x=cur_x, y=self.line_begin)
        cur_x += inch*1.5
        self.draw_text(self.data[project_name]['last_modified'], x=cur_x, y=self.line_begin)
        cur_x += inch*1.5
        self.draw_text(self.data[project_name]['size'], x=cur_x, y=self.line_begin)
        cur_x += inch*1.5
        self.draw_text(self.data[project_name]['path'], x=cur_x, y=self.line_begin)
        self.draw_text('')

        if header:
            if temp is not None:
                self.data['Name'] = temp
            else:
                del self.data['Name']


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
