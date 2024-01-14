# GUI modules.
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import tkcalendar

# Utility modules.
import datetime
import os
import re

from .screen_superclass import Screen


class SearchScreen(Screen):
    """
    The screen which allows the user to search for projects and files.
    """


    def __init__(self, root, change_screen, data_handler):
        # Call superclass constructor to initalize core functionality.
        super().__init__(root, change_screen, data_handler)

        # Get project data from the database.
        self.data = self.data_handler.read_projects()

        self.create_gui()


    def create_gui(self):
        """
        Create the Tkinter GUI to be displayed by the app handler.
        """

        # Create essential widgets by calling superclass method.
        super().create_gui()

        # Create title label.
        self.title_label = ttk.Label(self.frame, text='Search', style='Header1.TLabel')
        self.title_label.grid(row=0, column=0)

        # Create widgets for modifying search options.
        self.search_details_frame = ttk.Frame(self.frame)
        self.search_details_frame.grid(row=1, column=0, pady=(0, 20))
        self.search_label = ttk.Label(self.search_details_frame, text='Search for')
        self.search_label.pack(side='left')
        self.search_item_combo = ttk.Combobox(self.search_details_frame, width=12, state='readonly', values=('Projects', 'Files'))
        self.search_item_combo.current(0)
        self.search_item_combo.bind('<<ComboboxSelected>>', self.update_search_type_options)
        self.search_item_combo.pack(side='left', padx=5)
        self.search_by_label = ttk.Label(self.search_details_frame, text='by')
        self.search_by_label.pack(side='left')
        self.search_type_combo = ttk.Combobox(self.search_details_frame, width=15, state='readonly', values=('Project Name', 'Last Modified Date'))
        self.search_type_combo.bind('<<ComboboxSelected>>', self.update_input_widgets)
        self.search_type_combo.pack(side='left', padx=(5, 0))

        # Create widgets to allow user input through search box.
        self.search_entry_frame = ttk.Frame(self.frame)
        self.search_entry_frame.grid(row=2, column=0)
        self.search_entry_label = ttk.Label(self.search_entry_frame, text='Search Query:')
        self.search_entry_label.pack(side='left', padx=(0, 10))
        self.search_entry = ttk.Entry(self.search_entry_frame, width=30)
        self.search_entry.pack(side='right')

        # Create widgets to allow user input through calendar.
        self.search_calendar_frame = ttk.Frame(self.frame)
        self.start_date_frame = ttk.Frame(self.search_calendar_frame)
        self.start_date_frame.pack(side='left', padx=(0, 10))
        self.start_date_label = ttk.Label(self.start_date_frame, text='Start Date')
        self.start_date_label.pack()
        self.start_date_calendar = tkcalendar.DateEntry(self.start_date_frame, width=12)
        self.start_date_calendar.pack()
        self.end_date_frame = ttk.Frame(self.search_calendar_frame)
        self.end_date_frame.pack(side='right')
        self.end_date_label = ttk.Label(self.end_date_frame, text='End Date')
        self.end_date_label.pack()
        self.end_date_calendar = tkcalendar.DateEntry(self.end_date_frame, width=12)
        self.end_date_calendar.pack()

        # Create button to initiate search.
        self.search_button = ttk.Button(self.frame, text='Search', command=self.search)
        self.search_button.grid(row=3, column=0, pady=(10, 20))

        # Create textbox to display search results.
        self.result_text = scrolledtext.ScrolledText(self.frame, width=80, height=15, font=('Microsoft Sans Serif', 10), wrap=tk.WORD, state='disabled')
        self.result_text.grid(row=4, column=0)

        # Make screen expand to fill empty space horizontally.
        self.frame.columnconfigure(0, weight=1)

        # Update search type combobox to default value.
        self.update_search_type_options(None)   


    def update_search_type_options(self, e):
        """
        Updates search type combobox options based on search item combobox selection.
        """

        search_item = self.search_item_combo.get()
        if search_item == 'Projects':
            self.search_type_combo['values'] = ('Project Name', 'Last Modified Date')
            self.search_type_combo.current(0)
            # Reorganize widgets if needed.
            self.update_input_widgets(None)
        elif search_item == 'Files':
            self.search_type_combo['values'] = ('File Name', 'File Content')
            self.search_type_combo.current(0)
            # Reorganize widgets if needed.
            self.update_input_widgets(None)


    def update_input_widgets(self, e):
        """
        Handles reorganization of widgets based on search type combobox selection.
        """

        search_type = self.search_type_combo.get()
        if search_type == 'Last Modified Date':
            # Hide search entry.
            self.search_entry_frame.grid_remove()
            # Show calendar widgets.
            self.search_calendar_frame.grid(row=2, column=0)
        else:
            # Hide calendar widgets.
            self.search_calendar_frame.grid_remove()
            # Show search entry.
            self.search_entry_frame.grid()


    def search(self):
        """
        Searches for files based on the selected search item and type.
        """

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
        """
        Search for projects with names that match the given search string.
        """

        # Clear previous results
        self.result_text.delete(1.0, tk.END)

        # Get the search string.
        target_name = self.search_entry.get()
        
        # Search through all projects and display those which were last modified in the given interval.
        for name in self.data:
            if target_name in name:
                self.display_project_in_textbox(name)


    def search_projects_by_date(self):
        """
        Search for projects which were modified in the given date interval.
        """

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
        """
        Displays a project's details in the textbox.
        """

        # Get the project's details.
        project_details = self.data[name]

        # Create output string.
        formatted_path = os.path.normpath(f'output/{project_details["path"]}{name}/')
        output = ''
        output += f'Project: {name}\n'
        output += f'Path: {formatted_path}\n'
        output += f'Last Modified: {project_details["last_modified"]}\n'
        output += f'Size: {project_details["size"]}\n'
        output += '\n'

        # Insert output into textbox.
        self.result_text.configure(state='normal')
        self.result_text.insert(tk.END, output)
        self.result_text.configure(state='disabled')

    
    def search_files_by_name(self):
        """
        Search for files with naems that match the given search string.
        """

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
        """
        Search for files which contain lines that match the given search string.
        """

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
        """
        Displays the details of a single file result in the textbox.
        """

        absolute_file_path = os.path.normpath(os.path.join(root, file_name))
        relative_file_path = os.path.relpath(absolute_file_path, search_dir)
        formatted_path = os.path.normpath(f'output/{relative_file_path}')
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

        # Insert output into textbox.
        self.result_text.configure(state='normal')
        self.result_text.insert(tk.END, result)
        self.result_text.configure(state='disabled')


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
    