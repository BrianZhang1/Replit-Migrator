import tkinter as tk
from tkinter import scrolledtext
from openai import OpenAI

class ChatScreen:
    def __init__(self, root):
        self.root = root

        self.client = OpenAI()
        self.create_gui()

    def create_gui(self):
        self.frame = tk.Frame(self.root)

        self.chatbox = scrolledtext.ScrolledText(self.frame, width=40, height=10, wrap=tk.WORD)
        self.chatbox.pack(padx=10, pady=10)

        self.input_entry = tk.Entry(self.frame, width=40)
        self.input_entry.pack(padx=10, pady=5)

        self.send_button = tk.Button(self.frame, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)

    def send_message(self):
        user_message = self.input_entry.get()
        if user_message:
            self.display_message('You: ' + user_message)
            
            response = self.get_openai_response(user_message)
            
            self.display_message('Chatbot: ' + response)
            self.input_entry.delete(0, tk.END)

    def display_message(self, message):
        self.chatbox.insert(tk.END, message + "\n")
        self.chatbox.see(tk.END)

    def get_openai_response(self, user_message):
        response = self.client.chat.completions.create(
            model='gpt-3.5-turbo', 
            messages=[
                {"role": "user", "content": user_message}
            ],
            max_tokens=100
        )

        return response.choices[0].message.content
