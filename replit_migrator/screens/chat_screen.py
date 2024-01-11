import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
from openai import OpenAI

class ChatScreen:
    def __init__(self, root, change_screen, data_handler):
        self.root = root
        self.change_screen = change_screen
        self.data_handler = data_handler

        self.client = OpenAI()
        self.chat_history = self.data_handler.read_chat_history()

        self.create_gui()


    def create_gui(self):
        self.frame = ttk.Frame(self.root)

        # Create title label.
        self.title_label = ttk.Label(self.frame, text='Chat', style='Header1.TLabel')
        self.title_label.pack()

        self.chatbox = scrolledtext.ScrolledText(self.frame, width=60, height=15, wrap=tk.WORD)
        for message in self.chat_history:
            self.display_message(message['role'], message['content'])
        self.chatbox.pack(padx=10, pady=10)
        self.chatbox.configure(state='disabled')

        # Create input frame.
        self.input_frame = ttk.Frame(self.frame)
        self.input_frame.pack(pady=10)
        self.input_entry = ttk.Entry(self.input_frame, width=40)
        self.input_entry.pack(side='left', padx=(0, 10))
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side='right')

        self.clear_button = ttk.Button(self.frame, text="Clear Chat History", command=self.clear_chat, style='Small.TButton')
        self.clear_button.pack(padx=10, pady=10)

        # Create back button.
        self.back_button = ttk.Button(self.frame, text="Back", command=lambda: self.change_screen('home'))
        self.back_button.place(x=30, y=510)


    def send_message(self):
        user_message = self.input_entry.get()
        if user_message:
            self.display_message('user', user_message)
            self.chat_history.append({'role': 'user', 'content': user_message})
            
            response = self.get_openai_response()
            self.chat_history.append({'role': 'assistant', 'content': response})
            
            self.display_message('assistant', response)
            self.data_handler.write_chat_history(self.chat_history)
            self.input_entry.delete(0, tk.END)


    def display_message(self, role, message):
        self.chatbox.configure(state='normal')
        if role == 'user':
            self.chatbox.insert(tk.END, 'You: ' + message + '\n')
        elif role == 'assistant':
            self.chatbox.insert(tk.END, 'ChatGPT: ' + message + '\n')
        self.chatbox.see(tk.END)
        self.chatbox.configure(state='disabled')


    def get_openai_response(self):
        system_prompt = '''
            You are an assistant that answers user's questions related to the Replit Migrator app.
            The features include:
                - downloading all Replit files from the web through Selenium
                - direct express if user has already gone through the download process
                - generating reports based on project and file data
                - the option to interact with an AI chatbot (you)
                - searching for projects and files by name, date, or content
                - backup their migration data to the cloud
            To access report, search, and express download, the user must have already downloaded
            their Replit files.
            Politely refuse to answer questions that are not related to the app.
            '''
        response = self.client.chat.completions.create(
            model='gpt-3.5-turbo', 
            messages=[{'role': 'system', 'content': system_prompt}] + self.chat_history
        )

        return response.choices[0].message.content


    def clear_chat(self):
        # Show messagebox asking if user is sure they want to clear chat history.
        if not messagebox.askyesno('Clear Chat History', 'Are you sure you want to clear chat history?'):
            return

        # Clear chat history.
        self.chatbox.configure(state='normal')
        self.chatbox.delete(1.0, tk.END)
        self.chatbox.configure(state='disabled')
        self.chat_history = []
        self.data_handler.write_chat_history(self.chat_history)
