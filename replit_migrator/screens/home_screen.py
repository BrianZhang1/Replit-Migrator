import tkinter as tk

class HomeScreen:
    def __init__(self, root, change_screen):
        self.root = root
        self.change_screen = change_screen

        self.create_gui()


    def create_gui(self):
        """Creates Tkinter GUI."""

        # Create frame that wraps this screen.
        self.frame = tk.Frame(self.root)

        # Create title label.
        self.title_label = tk.Label(self.frame, text="Replit Migrator", font=("Helvetica", 20))
        self.title_label.pack(pady=20)

        # Create buttons that navigate to other screens.
        self.migration_button = tk.Button(self.frame, text="Begin Migration", command=lambda: self.change_screen('scraper'))
        self.migration_button.pack()
        self.search_button = tk.Button(self.frame, text="Search", command=lambda: self.change_screen('search'))
        self.search_button.pack()
        self.report_button = tk.Button(self.frame, text="Report", command=lambda: self.change_screen('report'))
        self.report_button.pack()
