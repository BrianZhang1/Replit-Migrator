import os
import re
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk

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
        self.search_entry.pack(pady=10)

        # Combobox widget to select the search type.
        self.search_type_combo = ttk.Combobox(self.frame, width=27)
        self.search_type_combo['values'] = ('File Name', 'File Content', 'Last Modified Date')
        self.search_type_combo.current(1)
        self.search_type_combo.pack(pady=10)

        # Button to start the search.
        self.search_button = tk.Button(self.frame, text="Search", command=self.search_files)
        self.search_button.pack(pady=10)

        # ScrolledText widget to display the results
        self.result_text = scrolledtext.ScrolledText(self.frame, width=80, height=20)
        self.result_text.pack(pady=10)


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
        # TODO: Implement with tkcalendar

    