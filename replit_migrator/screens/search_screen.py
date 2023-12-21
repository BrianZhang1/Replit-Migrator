import os
import re
import tkinter as tk
from tkinter import scrolledtext

class SearchScreen:
    def __init__(self, root):
        self.root = root

        self.create_gui();


    def create_gui(self):
        """Creates Tkinter GUI."""

        # Create frame that wraps this screen.
        self.frame = tk.Frame(self.root)

        # Entry widget for the search string
        self.entry = tk.Entry(self.frame, width=30)
        self.entry.pack(pady=10)

        # Button to start the search
        self.search_button = tk.Button(self.frame, text="Search", command=self.search_files)
        self.search_button.pack(pady=10)

        # ScrolledText widget to display the results
        self.result_text = scrolledtext.ScrolledText(self.frame, width=80, height=20)
        self.result_text.pack(pady=10)


    def search_files(self):
        """Search for files that match the given search string."""

        # Clear previous results
        self.result_text.delete(1.0, tk.END)

        # Search through the files in the output directory for the search_string.
        search_string = self.entry.get()
        search_dir = os.path.join(os.getcwd(), 'output/')
        for root, dirs, files in os.walk(search_dir):
            for file_name in files:
                file_path = os.path.normpath(os.path.join(root, file_name))
                # Search through the specific file using regular expressions.
                with open(file_path, 'r') as file:
                    for line_number, line in enumerate(file):
                        if re.search(search_string, line):
                            result = f"File: {file_path}\nLine: {line_number}\n\n"
                            self.result_text.insert(tk.END, result)
