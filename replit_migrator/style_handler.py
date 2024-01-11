from tkinter import ttk


class StyleHandler:
    """
    Handles the creation of consistent styles for all widgets.
    """

    def create_styles(self):
        '''
        Creates consistent project-wide styles to be used by all widgets.

        Tkinter styles are analogous to CSS classes in web development. They are a
        set of styling options that can be applied to any widget, reducing repetitive
        code.
        '''

        # Create style object.
        self.style = ttk.Style()

        # Create consistent font family.
        font_family = 'Microsoft Sans Serif'

        # Frame styles.
        self.style.configure('TFrame', background='white')

        # Label styles.
        self.style.configure('TLabel', background='white', font=(font_family, 12))
        self.style.configure('Title.TLabel', font=(font_family, 40, 'bold'), padding=30)
        self.style.configure('Header1.TLabel', font=(font_family, 20, 'bold'), padding=20)
        self.style.configure('Small.TLabel', background='white', font=(font_family, 10))

        # Button styles.
        self.style.configure('TButton', font=(font_family, 12), padding=5)
        self.style.configure('Large.TButton', font=(font_family, 16, 'bold'), background='green', padding=20)
        self.style.configure('Small.TButton', font=(font_family, 10), padding=5)

        # Entry styles.
        self.style.configure('TEntry', font=(font_family, 12))

        # Checkbutton styles.
        self.style.configure('TCheckbutton', font=(font_family, 10), background='white')

        # Combobox styles.
        self.style.configure('TCombobox', font=(font_family, 12))
