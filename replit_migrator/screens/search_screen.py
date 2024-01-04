import os
import re
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import tkcalendar
import datetime

class SearchScreen:
    def __init__(self, root, data_handler):
        self.root = root
        self.data = data_handler.read_projects()

        self.create_gui();


    def create_gui(self):
        """Creates Tkinter GUI."""

        # Create frame that wraps this screen.
        self.frame = tk.Frame(self.root)

        # Entry widget for the search string.
        self.search_entry = tk.Entry(self.frame, width=30)
        self.search_entry.grid(row=0, column=0, columnspan=2, pady=10)

        # Combobox widget to select the search type.
        self.search_type_combo = ttk.Combobox(self.frame, width=27)
        self.search_type_combo['values'] = ('File Name', 'File Content', 'Last Modified Date')
        self.search_type_combo.current(1)
        self.search_type_combo.bind('<<ComboboxSelected>>', self.update_search_type)
        self.search_type_combo.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # Calendar labels and widgets which are initially hidden.
        self.start_date_label = tk.Label(self.frame, text='Start Date')
        self.start_date_label.grid(row=2, column=0)
        self.start_date_label.grid_remove()
        self.start_date_calendar = tkcalendar.DateEntry(self.frame, width=12)
        self.start_date_calendar.grid(row=3, column=0)
        self.start_date_calendar.grid_remove()
        self.end_date_label = tk.Label(self.frame, text='End Date')
        self.end_date_label.grid(row=2, column=1)
        self.end_date_label.grid_remove()
        self.end_date_calendar = tkcalendar.DateEntry(self.frame, width=12)
        self.end_date_calendar.grid(row=3, column=1)
        self.end_date_calendar.grid_remove()

        # Button to start the search.
        self.search_button = tk.Button(self.frame, text="Search", command=self.search_files)
        self.search_button.grid(row=4, column=0, columnspan=2, pady=10)

        # ScrolledText widget to display the results
        self.result_text = scrolledtext.ScrolledText(self.frame, width=80, height=20)
        self.result_text.grid(row=5, column=0, columnspan=2, pady=10)


    def update_search_type(self, e):
        """Handles reorganization of widgets based on search type combobox selection."""

        search_type = self.search_type_combo.get()
        if search_type == 'Last Modified Date':
            # Show calendar widgets.
            self.start_date_label.grid()
            self.start_date_calendar.grid()
            self.end_date_label.grid()
            self.end_date_calendar.grid()
        else:
            # Hide calendar widgets.
            self.start_date_label.grid_remove()
            self.start_date_calendar.grid_remove()
            self.end_date_label.grid_remove()
            self.end_date_calendar.grid_remove()




    def search_files(self):
        """Searches for files based on the selected search type."""

        search_type = self.search_type_combo.get()
        if search_type == 'File Name':
            self.search_files_by_name()
        elif search_type == 'File Content':
            self.search_files_by_content()
        elif search_type == 'Last Modified Date':
            self.search_files_by_date()


    def search_files_by_name(self):
        """Search for files which match the given search string."""

        # Clear previous results
        self.result_text.delete(1.0, tk.END)

        # Search through the files in the output directory for the search_string.
        search_string = self.search_entry.get()
        search_dir = os.path.join(os.getcwd(), 'output/')
        for root, dirs, files in os.walk(search_dir):
            for file_name in files:
                file_path = os.path.normpath(os.path.join(root, file_name))
                if re.search(search_string, file_name):
                    result = f"File: {file_path}\n\n"
                    self.result_text.insert(tk.END, result)


    def search_files_by_content(self):
        """Search for files which contain lines that match the given search string."""

        # Clear previous results
        self.result_text.delete(1.0, tk.END)

        # Search through the files in the output directory for the search_string.
        search_string = self.search_entry.get()
        search_dir = os.path.join(os.getcwd(), 'output/')
        for root, dirs, files in os.walk(search_dir):
            for file_name in files:
                file_path = os.path.normpath(os.path.join(root, file_name))
                # Search through the specific file using regular expressions.
                with open(file_path, 'r') as file:
                    try:
                        for line_number, line in enumerate(file):
                            if re.search(search_string, line):
                                result = f"File: {file_path}\nLine: {line_number}\n\n"
                                self.result_text.insert(tk.END, result)
                    except UnicodeDecodeError:
                        # Not a readable file (perhaps an image or binary file), skip.
                        pass


    def search_files_by_date(self):
        """Search for files which were modified in the given date interval."""

        # Clear previous results
        self.result_text.delete(1.0, tk.END)
        
        # Get the start and end dates.
        start_date = self.start_date_calendar.get_date()
        end_date = self.end_date_calendar.get_date()

        # Search through all projects and display those which were last modified in the given interval.
        for name in self.data:
            project = self.data[name]
            raw_date_string = project['last_modified']
            project_date = self.string_to_date(raw_date_string)
            if start_date <= project_date <= end_date:
                result = f"Project: {name}\nLast Modified: {project['last_modified']}\n\n"
                self.result_text.insert(tk.END, result)

    

    def string_to_date(self, raw_date):
        """
        Converts a layman representation of a date (ex. '4 weeks ago') to a datetime object.

        Assumes a format of '<magnitude> <unit> ago' where unit is one of 'days', 'weeks', 'months', 'years'.
        Given ambiguity in the date, the most recent possible date is returned.
        """

        # Get the current date.
        cur_date = datetime.date.today()

        # Interpret the raw_date string and subtract the relevant interval from the current date.
        bits = raw_date.split()
        magnitude = int(bits[0])
        actual_date = None
        if bits[1] == 'days':
            actual_date = cur_date - datetime.timedelta(days=magnitude)
        elif bits[1] == 'weeks':
            actual_date = cur_date - datetime.timedelta(weeks=magnitude)
        elif bits[1] == 'months':
            # Assume a month is 30 days.
            actual_date = cur_date - datetime.timedelta(days=magnitude*30)
        elif bits[1] == 'years':
            actual_date = cur_date - datetime.timedelta(days=magnitude*365)

        return actual_date
    