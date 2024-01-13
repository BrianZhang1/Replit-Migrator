import tkinter as tk

# Import all screens.
from replit_migrator.database_handler import DatabaseHandler
from replit_migrator.style_handler import StyleHandler
from replit_migrator.screens.scraper_screen import ScraperScreen
from replit_migrator.screens.home_screen import HomeScreen
from replit_migrator.screens.search_screen import SearchScreen
from replit_migrator.screens.report_screen import ReportScreen
from replit_migrator.screens.chat_screen import ChatScreen
from replit_migrator.screens.download_existing_screen import DownloadExistingScreen
from replit_migrator.screens.login_screen import LoginScreen


class AppHandler:
    """
    Manages the application on the highest level.
    """

    def __init__(self):
        """
        Starts the application.
        """

        # Create and configure the root window.
        self.root = tk.Tk()
        self.root.title('Repl.it Migrator')
        self.root.geometry('1024x576')
        self.root.resizable(False, False)
        self.root.configure(bg='white')
        self.root.iconbitmap('replit_migrator/icon.ico')

        # Create constant variable for the Replit Migrator Database API endpoint.
        self.API_ROOT_URL = 'https://brianz1alt2.pythonanywhere.com/'

        # Initialize data handler.
        self.data_handler = DatabaseHandler('replit_migrator/db.sqlite3', self.API_ROOT_URL)

        # Create variable to persist selected project ID when changing screens.
        self.selected_project_id = None

        # Upon app startup, check if user is logged in.
        if self.data_handler.check_if_logged_in():
            # User is logged in. Get their login details.
            login_details = self.data_handler.read_login_details()
            # Update local database to latest version from server.
            self.data_handler.download_database_from_server(login_details['username'], login_details['password'])

        # Create consistent styles for all widgets.
        self.style_handler = StyleHandler()
        self.style_handler.create_styles()

        # Initialize screen to home page.
        self.screen = None
        self.change_screen('home')

        # Start the Tkinter main loop.
        self.root.mainloop()


    def change_screen(self, screen):
        """
        Handles changing between screens.
        """

        # Remove existing screen from display.
        if self.screen is not None:
            try:
                self.screen.frame.pack_forget()
            except tk.TclError:
                self.screen.frame.grid_forget()

        # Change self.screen to the new screen object.
        if screen == 'home':
            self.screen = HomeScreen(self.root, self.change_screen, self.data_handler)
        elif screen == 'scraper':
            self.screen = ScraperScreen(self.root, self.change_screen, self.data_handler, self.selected_project_id)
        elif screen == 'download_existing':
            self.screen = DownloadExistingScreen(self.root, self.change_screen, self.data_handler, self.select_project)
        elif screen == 'search':
            self.screen = SearchScreen(self.root, self.change_screen, self.data_handler)
        elif screen == 'report':
            self.screen = ReportScreen(self.root, self.change_screen, self.data_handler)
        elif screen == 'chat':
            self.screen = ChatScreen(self.root, self.change_screen, self.data_handler)
        elif screen == 'login':
            self.screen = LoginScreen(self.root, self.change_screen, self.data_handler, self.API_ROOT_URL)
        else:
            # Exit function with error message.
            print('Target screen not found.')
            return

        # Display the new screen.
        self.screen.frame.pack(fill=tk.BOTH, expand=True)


    def select_project(self, project_id):
        """
        Selects a project to scrape.
        """

        self.selected_project_id = project_id
        self.change_screen('scraper')

