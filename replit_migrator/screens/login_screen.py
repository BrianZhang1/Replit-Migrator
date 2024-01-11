import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import json


class LoginScreen:
    """
    Login screen for the user to login to their Replit Migrator account.
    """


    def __init__(self, root, change_screen, data_handler, API_ROOT_URL):
        """Initialize the login screen."""

        # Initialize attributes from parameters.
        self.root = root
        self.data_handler = data_handler
        self.API_ROOT_URL = API_ROOT_URL

        # Initalize methods from parameters.
        self.change_screen = change_screen

        # Create GUI.
        self.create_gui()
    

    def create_gui(self):
        """Creates Tkinter GUI."""

        # Create frame that wraps this screen.
        self.frame = ttk.Frame(self.root)

        # Create title label.
        self.title_label = ttk.Label(self.frame, text='Login or Register', style='Header1.TLabel')
        self.title_label.pack()

        # Create username frame, label, and entry.
        self.username_frame = ttk.Frame(self.frame)
        self.username_frame.pack(pady=(self.root.winfo_reqheight()/2-150, 10))
        self.username_label = ttk.Label(self.username_frame, text='Username:')
        self.username_label.pack(side='left', padx=(0, 10))
        self.username_entry = ttk.Entry(self.username_frame)
        self.username_entry.pack(side='right')

        # Create password label and entry.
        self.password_frame = ttk.Frame(self.frame)
        self.password_frame.pack()
        self.password_label = ttk.Label(self.password_frame, text='Password:')
        self.password_label.pack(side='left', padx=(0, 10))
        self.password_entry = ttk.Entry(self.password_frame, show='*')
        self.password_entry.pack(side='right')

        # Create button frame with login and register buttons.
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(pady=30)
        self.login_button = ttk.Button(self.button_frame, text='Login', command=self.login)
        self.login_button.pack(side='left', padx=(0, 20))
        self.register_button = ttk.Button(self.button_frame, text='Register', command=self.register)
        self.register_button.pack(side='right')

        # Create back button.
        self.back_button = ttk.Button(self.frame, text="Back", command=lambda: self.change_screen('home'))
        self.back_button.place(x=30, y=510)

    
    def login(self):
        """
        Logs the user in using the username and password provided.

        Makes a request to the Replit Migrator Database API to authenticate the user.
        Upon successful authentication, user migration data will be retrieved, processed,
        and stored.
        """

        # Get username and password.
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Attempt to retrieve user migration data from the API.
        response = self.data_handler.download_database_from_server(username, password)

        # Parse and store JSON data from response.
        response_json = json.loads(response.text)

        # Check for error.
        if 'status' in response_json and response_json['status'] == 'error':
            # Server responded with an error. Notify user of error and exit.
            messagebox.showerror('Error', response_json['message'])
            return

        # Save login details for future requests.
        self.data_handler.write_login_details(username, password)

        # Notify user of successful operation.
        messagebox.showinfo('Success', 'Successfully logged in. Migration data has been downloaded from the cloud.')

        # Return to home screen.
        self.change_screen('home')


    def register(self):
        """
        Makes a request to register a new account to the Replit Migrator
        Database API.
        """

        # Get username and password.
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Attempt to register new account.
        response = requests.post(f'{self.API_ROOT_URL}register/', data={'username': username, 'password': password})

        # Parse and store JSON data from response.
        response_json = json.loads(response.text)

        # Check for error.
        if 'status' in response_json and response_json['status'] == 'error':
            # Server responded with an error. Notify user of error and exit.
            messagebox.showerror('Error', response_json['message'])
            return

        # Registration successful. Save login details for future requests.
        self.data_handler.write_login_details(username, password)

        # Upload existing migration data and chat history to Replit Migrator Database.
        response = self.data_handler.upload_database_to_server(username, password)

        # Parse and store JSON data from response.
        response_json = json.loads(response.text)

        # Check for error.
        if 'status' in response_json and response_json['status'] == 'error':
            # Server responded with an error. Notify user of error and exit.
            messagebox.showerror('Error', response_json['message'])
            return

        # Notify user of successful operation.
        messagebox.showinfo('Success', 'Successfully registered new account and logged in. Migration data will now be backed up to the cloud.')

        # Return to home screen.
        self.change_screen('home')



