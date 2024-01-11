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
        self.frame = ttk.Frame(self.root)

        # Create title label.
        self.title_label = ttk.Label(self.frame, text='Download Existing Scan', style='Header1.TLabel')
        self.title_label.pack()

        self.instructions_label = ttk.Label(self.frame, text='Select the scan you would like to download from, then press Continue.')
        self.instructions_label.pack(pady=(self.root.winfo_reqheight()/2-150, 10))

        self.selection_combo = ttk.Combobox(self.frame, width=24)
        self.selection_combo['values'] = [f'{row['id']} - {row['date_time']}' for row in self.data_handler.get_migration_tables()]
        self.selection_combo.pack(pady=10)

        self.continue_button = ttk.Button(self.frame, text='Continue', command=self.continue_to_download)
        self.continue_button.pack(pady=10)

        # Create back button.
        self.back_button = ttk.Button(self.frame, text="Back", command=lambda: self.change_screen('home'))
        self.back_button.place(x=30, y=510)


    def continue_to_download(self):
        """
        Retrieves the selected project ID and passes it to select_project,
        which will change the screen to the scraper screen.
        """

        # Get selected project ID.
        selected_project_id = self.selection_combo.get().split(' - ')[0]

        # Change screen to scraper screen.
        self.select_project(selected_project_id)
    
