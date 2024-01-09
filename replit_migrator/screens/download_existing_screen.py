import tkinter as tk
from tkinter import ttk

class DownloadExistingScreen:
    def __init__(self, root, change_screen, data_handler, select_project):
        self.root = root
        self.change_screen = change_screen
        self.data_handler = data_handler
        self.select_project = select_project

        self.create_gui()


    def create_gui(self):
        """Creates Tkinter GUI."""

        # Create frame that wraps this screen.
        self.frame = tk.Frame(self.root)

        self.instructions_label = tk.Label(self.frame, text='Select the scan you would like to download from, then press Continue.')
        self.instructions_label.pack()

        self.selection_combo = ttk.Combobox(self.frame, width=24)
        self.selection_combo['values'] = [f'{row['id']} - {row['date_time']}' for row in self.data_handler.get_migration_tables()]
        self.selection_combo.pack()

        self.continue_button = tk.Button(self.frame, text='Continue', command=self.continue_to_download)
        self.continue_button.pack()


    def continue_to_download(self):
        """
        Retrieves the selected project ID and passes it to select_project,
        which will change the screen to the scraper screen.
        """

        # Get selected project ID.
        selected_project_id = self.selection_combo.get().split(' - ')[0]

        # Change screen to scraper screen.
        self.select_project(selected_project_id)
    
