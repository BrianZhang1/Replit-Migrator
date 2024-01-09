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

        self.create_gui()


    def create_gui(self):
        """Creates Tkinter GUI."""

        # Create frame that wraps this screen.
        self.frame = tk.Frame(self.root)

        self.search_details_frame = tk.Frame(self.frame)
        self.search_label = tk.Label(self.search_details_frame, text='Search')
        self.search_item_combo = ttk.Combobox(self.search_details_frame, width=12)
        self.search_item_combo['values'] = ('Projects', 'Files')
        self.search_item_combo.current(0)
        self.search_item_combo.bind('<<ComboboxSelected>>', self.update_search_item)
        self.search_by_label = tk.Label(self.search_details_frame, text='by')
        self.search_type_combo = ttk.Combobox(self.search_details_frame, width=15)
        self.search_type_combo.bind('<<ComboboxSelected>>', self.update_search_type)

        self.search_entry_frame = tk.Frame(self.frame)
        self.search_entry = tk.Entry(self.search_entry_frame, width=30)
        self.search_button = tk.Button(self.search_entry_frame, text="Search", command=self.search)

        # Calendar labels and widgets.
        self.search_calendar_frame = tk.Frame(self.frame)
        self.start_date_label = tk.Label(self.search_calendar_frame, text='Start Date')
        self.start_date_calendar = tkcalendar.DateEntry(self.search_calendar_frame, width=12)
        self.end_date_label = tk.Label(self.search_calendar_frame, text='End Date')
        self.end_date_calendar = tkcalendar.DateEntry(self.search_calendar_frame, width=12)

        # ScrolledText widget to display the results
        self.result_text = scrolledtext.ScrolledText(self.frame, width=80, height=20)

        # Place all widgets.
        self.search_details_frame.grid(row=0, column=0, sticky='w')
        self.search_entry_frame.grid(row=1, column=0, sticky='w')
        self.search_calendar_frame.grid(row=2, column=0, sticky='w')
        self.search_calendar_frame.grid_remove()    # Hide calendar widgets by default.
        self.result_text.grid(row=3, column=0, sticky='w')

        self.search_label.pack(side='left')
        self.search_item_combo.pack(side='left')
        self.search_by_label.pack(side='left')
        self.search_type_combo.pack(side='left')
        self.search_entry.pack(side='left')
        self.search_button.pack(side='left')
        self.start_date_label.grid(row=0, column=0)
        self.start_date_calendar.grid(row=1, column=0)
        self.end_date_label.grid(row=0, column=1)
        self.end_date_calendar.grid(row=1, column=1)

        self.update_search_item(None)   # Update search type combobox to default value.
        self.search_type_combo.current(0)


    def update_search_item(self, e):
        """Updates search type combobox based on search item combobox selection."""

        search_item = self.search_item_combo.get()
        if search_item == 'Projects':
            self.search_type_combo['values'] = ('Project Name', 'Last Modified Date')
            self.search_type_combo.current(0)
            self.update_search_type(None)
        elif search_item == 'Files':
            self.search_type_combo['values'] = ('File Name', 'File Content')
            self.search_type_combo.current(0)
            self.update_search_type(None)


    def update_search_type(self, e):
        """Handles reorganization of widgets based on search type combobox selection."""

        search_type = self.search_type_combo.get()
        if search_type == 'Last Modified Date':
            # Show calendar widgets.
            self.search_calendar_frame.grid()
        else:
            # Hide calendar widgets.
            self.search_calendar_frame.grid_remove()


    def search(self):
        """Searches for files based on the selected search item and type."""

        search_item = self.search_item_combo.get()
        search_type = self.search_type_combo.get()

        if search_item == 'Projects':
            if search_type == 'Project Name':
                self.search_projects_by_name()
            elif search_type == 'Last Modified Date':
                self.search_projects_by_date()
        elif search_item == 'Files':
            if search_type == 'File Name':
                self.search_files_by_name()
            elif search_type == 'File Content':
                self.search_files_by_content()


    def search_projects_by_name(self):
        """Search for projects with names that match the given search string."""

        # Clear previous results
        self.result_text.delete(1.0, tk.END)

        # Get the search string.
        target_name = self.search_entry.get()
        
        # Search through all projects and display those which were last modified in the given interval.
        for name in self.data:
            if target_name in name:
                self.display_project_in_textbox(name)


    def search_projects_by_date(self):
        """Search for projects which were modified in the given date interval."""

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
                self.display_project_in_textbox(name)


    def display_project_in_textbox(self, name):
        """Displays a project's details in the textbox."""

        # Get the project's details.
        project_details = self.data[name]
        formatted_path = os.path.normpath(f"output/{project_details['path']}{name}/")
        output = ''
        output += f'Project: {name}\n'
        output += f'Path: {formatted_path}\n'
        output += f'Last Modified: {project_details["last_modified"]}\n'
        output += f'Size: {project_details["size"]}\n'
        output += '\n'
        self.result_text.insert(tk.END, output)

    
    def search_files_by_name(self):
        """Search for files with naems that match the given search string."""

        # Clear previous results
        self.result_text.delete(1.0, tk.END)

        # Search through the files in the output directory for the search_string.
        search_string = self.search_entry.get()
        search_dir = os.path.join(os.getcwd(), 'output/')
        for root, dirs, files in os.walk(search_dir):
            for file_name in files:
                if re.search(search_string, file_name):
                    self.display_file_in_textbox(root, file_name, search_dir)


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
                                self.display_file_in_textbox(root, file_name, search_dir, (line_number, line.strip()))
                    except UnicodeDecodeError:
                        # Not a readable file (perhaps an image or binary file), skip.
                        pass
    

    def display_file_in_textbox(self, root, file_name, search_dir, line_data=None):
        absolute_file_path = os.path.normpath(os.path.join(root, file_name))
        relative_file_path = os.path.relpath(absolute_file_path, search_dir)
        formatted_path = os.path.normpath(f"output/{relative_file_path}")
        result = ''
        result += f'File: {file_name}\n'
        result += f'Path: {formatted_path}\n'
        if line_data is not None:
            line_number, line_preview = line_data
            if len(line_preview) > 50:
                line_preview = line_preview[:50] + '...'
            result += f'Line: {line_number}\n'
            result += f'Preview: {line_preview}\n'
        result += '\n'
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
    