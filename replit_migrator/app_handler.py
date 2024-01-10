import tkinter as tk

from replit_migrator.database_handler import DatabaseHandler
from replit_migrator.screens.scraper_screen import ScraperScreen
from replit_migrator.screens.home_screen import HomeScreen
from replit_migrator.screens.search_screen import SearchScreen
from replit_migrator.screens.report_screen import ReportScreen
from replit_migrator.screens.chat_screen import ChatScreen
from replit_migrator.screens.download_existing_screen import DownloadExistingScreen
from replit_migrator.screens.login_screen import LoginScreen


class AppHandler:
    """Manages the application on the highest level."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Replit Repl.it Downloader')

        # Create constant variable for the Replit Migrator Database API endpoint.
        self.API_ROOT_URL = 'https://brianz1alt2.pythonanywhere.com/'

        # Initialize data handler.
        self.data_handler = DatabaseHandler('replit_migrator/db.sqlite3', self.API_ROOT_URL)

        # Initalize core attributes.
        self.selected_project_id = None

        # Upon app startup, check if user is logged in.
        if self.data_handler.check_if_logged_in():
            # User is logged in. Get their login details.
            login_details = self.data_handler.read_login_details()
            # Update local database to latest version from server.
            self.data_handler.download_database_from_server(login_details['username'], login_details['password'])

        # Initialize screen to home page.
        self.screen = None
        self.change_screen('home')

        # Start the tkinter main loop.
        self.root.mainloop()


    def change_screen(self, screen):
        """Handles changing between screens."""

        # Remove existing screen from display.
        if self.screen is not None:
            try:
                self.screen.frame.pack_forget()
            except tk.TclError:
                self.screen.frame.grid_forget()

        # Change self.screen to the target screen.
        if screen == 'home':
            self.screen = HomeScreen(self.root, self.change_screen, self.data_handler)
        elif screen == 'scraper':
            if self.selected_project_id is None:
                self.screen = ScraperScreen(self.root, self.data_handler)
            else:
                self.screen = ScraperScreen(self.root, self.data_handler, self.selected_project_id)
        elif screen == 'download_existing':
            self.screen = DownloadExistingScreen(self.root, self.change_screen, self.data_handler, self.select_project)
        elif screen == 'search':
            self.screen = SearchScreen(self.root, self.data_handler)
        elif screen == 'report':
            self.screen = ReportScreen(self.root, self.data_handler)
        elif screen == 'chat':
            self.screen = ChatScreen(self.root, self.data_handler)
        elif screen == 'login':
            self.screen = LoginScreen(self.root, self.data_handler, self.change_screen, self.API_ROOT_URL)
        else:
            # Exit function with error message.
            print('Target screen not found.')
            return

        # Add new screen to display.
        self.screen.frame.pack()


    def select_project(self, project_id):
        """Selects a project to scrape."""

        self.selected_project_id = project_id
        self.change_screen('scraper')
