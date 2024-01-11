from tkinter import ttk
from tkinter import messagebox
import webbrowser

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
        self.frame = ttk.Frame(self.root)

        # Create title label.
        self.title_label = ttk.Label(self.frame, text="Replit Migrator", style='Title.TLabel')
        self.title_label.pack(pady=(30, 0))

        # Create uniform button padding.
        button_pady = 3

        # Create buttons that navigate to other screens.
        self.migration_button = ttk.Button(self.frame, text="Start New Migration", command=lambda: self.change_screen('scraper'), style='Large.TButton')
        self.migration_button.pack(pady=(button_pady, 30))
        
        # Only display 'download existing', 'search', and 'report' button if migration data already exists.
        if len(self.data_handler.get_migration_tables()) > 0:
            self.download_existing_button = ttk.Button(self.frame, text="Download Existing Scan", command=lambda: self.change_screen('download_existing'), style='Small.TButton')
            self.download_existing_button.pack(pady=button_pady)
            self.search_button = ttk.Button(self.frame, text="Search", command=lambda: self.change_screen('search'), style='Small.TButton')
            self.search_button.pack(pady=button_pady)
            self.report_button = ttk.Button(self.frame, text="Generate Report", command=lambda: self.change_screen('report'), style='Small.TButton')
            self.report_button.pack(pady=button_pady)
        
        self.chat_button = ttk.Button(self.frame, text="Chat", command=lambda: self.change_screen('chat'), style='Small.TButton')
        self.chat_button.pack(pady=button_pady)

        # Check if user is logged in.
        if self.login_details is not None:
            # User is logged in. Create logout button.
            self.logout_button = ttk.Button(self.frame, text="Logout", command=self.logout, style='Small.TButton')
            self.logout_button.pack(pady=button_pady)
        else:
            # Create login/register button.
            self.login_button = ttk.Button(self.frame, text="Login/Register", command=lambda: self.change_screen('login'), style='Small.TButton')
            self.login_button.pack(pady=button_pady)
        
        # Create help/about button.
        help_about_url = 'https://docs.google.com/document/d/1RcFAa4-UuUQxfu1vcu62hD4HCSAUPN74eueKUCz6LJU/edit?usp=sharing'
        self.help_about_button = ttk.Button(self.frame, text="Help/About", command=lambda: webbrowser.open(help_about_url), style='Small.TButton')
        self.help_about_button.pack(pady=button_pady)


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
