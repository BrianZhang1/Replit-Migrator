import tkinter as tk

from replit_migrator.database_handler import DatabaseHandler
from replit_migrator.screens.scraper_screen import ScraperScreen
from replit_migrator.screens.home_screen import HomeScreen
from replit_migrator.screens.search_screen import SearchScreen
from replit_migrator.screens.report_screen import ReportScreen
from replit_migrator.screens.chat_screen import ChatScreen
from replit_migrator.screens.download_existing_screen import DownloadExistingScreen


class AppHandler:
    """Manages the application on the highest level."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Replit Repl.it Downloader')

        # Initialize screen to home page.
        self.screen = None
        self.change_screen('home')

        # Initialize data handler.
        self.data_handler = DatabaseHandler('replit_migrator/db.sqlite3')

        self.selected_project_id = None

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
            self.screen = HomeScreen(self.root, self.change_screen)
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
