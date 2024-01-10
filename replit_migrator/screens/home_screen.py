import tkinter as tk
from tkinter import messagebox

class HomeScreen:
    def __init__(self, root, change_screen, data_handler):
        self.root = root
        self.change_screen = change_screen
        self.data_handler = data_handler

        # Check if user is logged in.
        self.is_logged_in = self.data_handler.check_if_logged_in()
        # If user is logged in, get their login details.
        if self.is_logged_in:
            self.login_details = self.data_handler.read_login_details()
        else:
            self.login_details = None

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
        self.download_existing_button = tk.Button(self.frame, text="Download Existing Scan", command=lambda: self.change_screen('download_existing'))
        self.download_existing_button.pack()
        self.search_button = tk.Button(self.frame, text="Search", command=lambda: self.change_screen('search'))
        self.search_button.pack()
        self.report_button = tk.Button(self.frame, text="Report", command=lambda: self.change_screen('report'))
        self.report_button.pack()
        self.chat_button = tk.Button(self.frame, text="Chat", command=lambda: self.change_screen('chat'))
        self.chat_button.pack()

        # Check if user is logged in.
        if self.login_details is not None:
            # User is logged in. Create logout button.
            self.logout_button = tk.Button(self.frame, text="Logout", command=self.logout)
            self.logout_button.pack()
        else:
            # Create login/register button.
            self.login_button = tk.Button(self.frame, text="Login/Register", command=lambda: self.change_screen('login'))
            self.login_button.pack()


    def logout(self):
        """
        Logs the user out of their Replit Migrator account.
        """

        # Delete login details from local database.
        self.data_handler.delete_login_details()

        # Notify user that they have been logged out.
        messagebox.showinfo('Logged Out', 'You have been logged out. Your data is no longer synced to cloud.')

        # Refresh screen to update widgets.
        self.change_screen('home')
