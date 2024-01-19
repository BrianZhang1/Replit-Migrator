import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
import requests
import json

from .screen_superclass import Screen

class ChatScreen(Screen):
    """
    The screen which allows users to chat with an AI chatbot.
    """


    def __init__(self, root, change_screen, data_handler, API_ROOT_URL):
        # Call superclass constructor to initalize core functionality.
        super().__init__(root, change_screen, data_handler)

        self.API_ROOT_URL = API_ROOT_URL
        self.chat_history = self.data_handler.read_chat_history()

        self.create_gui()


    def create_gui(self):
        """
        Create the Tkinter GUI to be displayed by the app handler.
        """

        # Create essential widgets by calling superclass method.
        super().create_gui()

        # Create title label.
        self.title_label = ttk.Label(self.frame, text='Chat', style='Header1.TLabel')
        self.title_label.pack()

        # Create chatbox which displays message history.
        self.chatbox = scrolledtext.ScrolledText(self.frame, width=60, height=15, font=('Microsoft Sans Serif', 10), wrap=tk.WORD, state='disabled')
        for message in self.chat_history:
            self.display_message(message['role'], message['content'])
        self.chatbox.pack(padx=10, pady=10)

        # Create input widgets to send messages.
        self.input_frame = ttk.Frame(self.frame)
        self.input_frame.pack(pady=10)
        self.input_entry = ttk.Entry(self.input_frame, width=40)
        self.input_entry.pack(side='left', padx=(0, 10))
        self.send_button = ttk.Button(self.input_frame, text='Send', command=self.send_message)
        self.send_button.pack(side='right')

        # Create clear button to clear chat history.
        self.clear_button = ttk.Button(self.frame, text='Clear Chat History', command=self.clear_chat, style='Small.TButton')
        self.clear_button.pack(padx=10, pady=10)


    def send_message(self):
        """
        Manages the message submission process.
        """

        # Get user message from input entry.
        user_message = self.input_entry.get()
        if user_message:
            # Display message in chatbox.
            self.display_message('user', user_message)
            self.chat_history.append({'role': 'user', 'content': user_message})
            
            # Get response from OpenAI API.
            response = self.get_openai_response()
            self.chat_history.append({'role': 'assistant', 'content': response})
            
            # Display response in chatbox.
            self.display_message('assistant', response)
            self.data_handler.write_chat_history(self.chat_history)

            # Clear input entry.
            self.input_entry.delete(0, tk.END)


    def display_message(self, role, message):
        """
        Display a message in the chatbox.
        """

        self.chatbox.configure(state='normal')
        if role == 'user':
            self.chatbox.insert(tk.END, 'You: ' + message + '\n\n')
        elif role == 'assistant':
            self.chatbox.insert(tk.END, 'ChatGPT: ' + message + '\n\n')
        self.chatbox.see(tk.END)
        self.chatbox.configure(state='disabled')


    def get_openai_response(self):
        """
        Send a message to server to get a response from OpenAI API.
        """

        chat_history_json = json.dumps(self.chat_history)
        response = requests.post(f'{self.API_ROOT_URL}chat/', data={'chat_history': chat_history_json})
        response_json = json.loads(response.text)
        return response_json['chat_response']


    def clear_chat(self):
        """
        Clears the chat history from both screen and database.
        """

        # Show messagebox asking if user is sure they want to clear chat history.
        if not messagebox.askyesno('Clear Chat History', 'Are you sure you want to clear chat history?'):
            return

        # Clear chatbox.
        self.chatbox.configure(state='normal')
        self.chatbox.delete(1.0, tk.END)
        self.chatbox.configure(state='disabled')

        # Clear database history.
        self.chat_history = []
        self.data_handler.write_chat_history(self.chat_history)
