from tkinter import ttk


class Screen:
    """
    The superclass which all screens inherit from. Contains essential
    methods and attributes.
    """


    def __init__(self, root, change_screen, data_handler):
        """
        Initialize the screen.

        Every screen has a root (the main tkinter window), a function to change screens,
        and a data handler to read and write data to the database.
        """

        # Initialize essential parameters for all screens.
        self.root = root
        self.change_screen = change_screen
        self.data_handler = data_handler


    def create_gui(self):
        """
        Creates the Tkinter GUI for the screen.

        Every screen has a frame (in which all widgets for that screen are contained)
        as well as a back button to return to the home screen.
        """
        
        # Create frame (pack() in change_screen() method of app_handler to display this screen).
        self.frame = ttk.Frame(self.root)

        # Create back button.
        self.back_button = ttk.Button(self.frame, text='Back', command=lambda: self.change_screen('home'))
        self.back_button.place(x=30, y=510)
