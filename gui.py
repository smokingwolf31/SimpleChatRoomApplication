import tkinter as tk
from tkinter import messagebox, scrolledtext
from socket import *
import pickle
import threading
import account
import message as msg

class MessengerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Simple Messenger")
        
        self.account = None
        
        self.login_frame = tk.Frame(self.master)
        self.login_frame.pack(padx=20, pady=20)
        
        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=1, columnspan=2, padx=5, pady=5)
        
        self.chat_frame = tk.Frame(self.master)
        
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, height=20, width=50)
        self.chat_display.pack(padx=5, pady=5)
        
        self.message_label = tk.Label(self.chat_frame, text="Message:")
        self.message_label.pack(padx=5, pady=5)
        
        self.message_entry = tk.Entry(self.chat_frame)
        self.message_entry.pack(padx=5, pady=5)
        
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.pack(padx=5, pady=5)
        
        self.login_frame.tkraise()
        
        self.init_client()

    def init_client(self):
        self.server_address = '127.0.0.1'  # Server IP address
        self.server_port = 15040  # Server port
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((self.server_address, self.server_port))

    def login(self):
        username = self.username_entry.get()
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        message = msg.Message(request="LogIn********", text=username)
        self.client_socket.sendall(pickle.dumps(message))

        response = pickle.loads(self.client_socket.recv(4028))
        self.account = response.account
        if not self.account.accUsername:
            messagebox.showerror("Error", "Invalid username or user already logged in")
        else:
            self.chat_frame.pack(padx=20, pady=20)
            self.chat_frame.tkraise()

    def send_message(self):
        if not self.account:
            messagebox.showerror("Error", "You must login first")
            return
        
        message_text = self.message_entry.get()
        if not message_text:
            messagebox.showerror("Error", "Message cannot be empty")
            return
        
        # Display sender's message in the chat box
        self.display_message(f"You: {message_text}")
        
        # Send the message to the server
        message = msg.Message(request="MsgOfflineAcc", text=f"{self.account.accUsername} {message_text}")
        self.client_socket.sendall(pickle.dumps(message))
        self.message_entry.delete(0, tk.END)

    def display_message(self, message):
        # Display received message in the chat box
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.see(tk.END)

def main():
    root = tk.Tk()
    app = MessengerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
