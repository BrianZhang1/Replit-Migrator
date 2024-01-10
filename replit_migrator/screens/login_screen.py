import tkinter as tk
from tkinter import messagebox
import requests
import json


class LoginScreen:
    """
    Login screen for the user to login to their Replit Migrator account.
    """


    def __init__(self, root, data_handler, change_screen, API_ROOT_URL):
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
        self.frame = tk.Frame(self.root)

        # Create screen title.
        self.title_label = tk.Label(self.frame, text='Login or Register')
        self.title_label.pack()

        # Create username label and entry.
        self.username_label = tk.Label(self.frame, text='Username:')
        self.username_label.pack()
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.pack()

        # Create password label and entry.
        self.password_label = tk.Label(self.frame, text='Password:')
        self.password_label.pack()
        self.password_entry = tk.Entry(self.frame, show='*')
        self.password_entry.pack()

        # Create login button.
        self.login_button = tk.Button(self.frame, text='Login', command=self.login)
        self.login_button.pack()

        # Create register button.
        self.register_button = tk.Button(self.frame, text='Register', command=self.register)
        self.register_button.pack()

    
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



