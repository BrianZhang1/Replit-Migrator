import tkinter as tk

from replit_migrator.screens.scraper_screen import ScraperScreen
from replit_migrator.screens.home_screen import HomeScreen


class AppHandler:
    """Manages the application on the highest level."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Replit Repl.it Downloader')

        # Initialize screen to home page.
        self.screen = None
        self.change_screen('home')

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
            self.screen = ScraperScreen(self.root)
        else:
            # Exit function with error message.
            print('Target screen not found.')
            return

        # Add new screen to display.
        self.screen.frame.pack()
