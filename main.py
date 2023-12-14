import tkinter as tk

from replit_scraper import ReplitScraper


def main():
    """Program entrypoint."""
    root = tk.Tk()
    root.title('Replit Repl.it Downloader')
    replit_scraper = ReplitScraper(root)
    root.mainloop()


if __name__ == '__main__':
    main()