from tkinter import ttk

from .screen_superclass import Screen


class DownloadExistingScreen(Screen):
    """
    The screen which allows users to directly download existing Repl.it scans.
    """


    def __init__(self, root, change_screen, data_handler, select_project):
        # Call superclass constructor to initalize core functionality.
        super().__init__(root, change_screen, data_handler)

        self.select_project = select_project

        self.create_gui()


    def create_gui(self):
        """
        Create the Tkinter GUI to be displayed by the app handler.
        """

        # Create essential widgets by calling superclass method.
        super().create_gui()

        # Create title label.
        self.title_label = ttk.Label(self.frame, text='Download Existing Scan', style='Header1.TLabel')
        self.title_label.pack()

        # Create instructions label.
        self.instructions_label = ttk.Label(self.frame, text='Select the scan you would like to download from, then press Continue.')
        self.instructions_label.pack(pady=(self.root.winfo_reqheight()/2-150, 10))

        # Create selection combo box widget to allow user to select previous migration.
        selection_combo_values = [f'{row['id']} - {row['date_time']}' for row in self.data_handler.get_migration_tables()]
        self.selection_combo = ttk.Combobox(self.frame, width=24, state='readonly', values=selection_combo_values)
        self.selection_combo.pack(pady=10)

        # Create continue button.
        self.continue_button = ttk.Button(self.frame, text='Continue', command=self.continue_to_download)
        self.continue_button.pack(pady=10)


    def continue_to_download(self):
        """
        Retrieves the selected project ID and passes it to select_project,
        which will change the screen to the scraper screen.
        """

        # Get selected project ID.
        selected_project_id = self.selection_combo.get().split(' - ')[0]

        # Change screen to scraper screen.
        self.select_project(selected_project_id)
    
