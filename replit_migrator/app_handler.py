import tkinter as tk

from replit_migrator.screens.replit_scraper import ReplitScraper


class AppHandler:
    """Manages the application on the highest level."""

    def __init__(self):
        root = tk.Tk()
        root.title('Replit Repl.it Downloader')
        replit_scraper = ReplitScraper(root)
        root.mainloop()