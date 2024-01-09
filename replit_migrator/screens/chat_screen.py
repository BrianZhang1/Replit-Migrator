import tkinter as tk
from tkinter import scrolledtext
from openai import OpenAI

class ChatScreen:
    def __init__(self, root, data_handler):
        self.root = root
        self.data_handler = data_handler

        self.client = OpenAI()
        self.chat_history = self.data_handler.read_chat_history()

        self.create_gui()


    def create_gui(self):
        self.frame = tk.Frame(self.root)

        self.chatbox = scrolledtext.ScrolledText(self.frame, width=40, height=10, wrap=tk.WORD)
        for message in self.chat_history:
            self.display_message(message['role'], message['content'])
        self.chatbox.pack(padx=10, pady=10)

        self.input_entry = tk.Entry(self.frame, width=40)
        self.input_entry.pack(padx=10, pady=5)

        self.send_button = tk.Button(self.frame, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)

        self.clear_button = tk.Button(self.frame, text="Clear", command=self.clear_chat)
        self.clear_button.pack(padx=10, pady=10)


    def send_message(self):
        user_message = self.input_entry.get()
        if user_message:
            self.display_message('user', user_message)
            self.chat_history.append({'role': 'user', 'content': user_message})
            
            response = self.get_openai_response(user_message)
            self.chat_history.append({'role': 'assistant', 'content': response})
            
            self.display_message('assistant', response)
            self.data_handler.write_chat_history(self.chat_history)
            self.input_entry.delete(0, tk.END)


    def display_message(self, role, message):
        if role == 'user':
            self.chatbox.insert(tk.END, 'You: ' + message + '\n')
        elif role == 'assistant':
            self.chatbox.insert(tk.END, 'ChatGPT: ' + message + '\n')
        self.chatbox.see(tk.END)


    def get_openai_response(self, user_message):
        system_prompt = '''
            You are an assistant that answers user's questions related to the Replit Migrator app.
            The features include:
                - downloading all Replit files from the web through Selenium
                - generating reports based on project and file data
                - the option to interact with an AI chatbot (you)
                - searching for projects and files by name, date, or content
            Politely refuse to answer questions that are not related to the app.
            '''
        response = self.client.chat.completions.create(
            model='gpt-3.5-turbo', 
            messages=[{'role': 'system', 'content': system_prompt}] + self.chat_history
        )

        return response.choices[0].message.content


    def clear_chat(self):
        self.chatbox.delete(1.0, tk.END)
        self.chat_history = []
        self.data_handler.write_chat_history(self.chat_history)
