import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

class ChatApplication:
    def __init__(self, client_socket, peer_socket):
        self.client_socket = client_socket
        self.peer_socket = peer_socket
        self.root = tk.Tk()
        self.root.title("Chat Application")
        self.create_widgets()

    def create_widgets(self):
        self.chat_box = scrolledtext.ScrolledText(self.root, width=50, height=20)
        self.chat_box.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        self.message_entry = tk.Entry(self.root, width=40)
        self.message_entry.grid(row=1, column=0, padx=10, pady=10)
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            # Send message logic here
            self.message_entry.delete(0, tk.END)
            self.display_message("You", message)

    def display_message(self, sender, message):
        self.chat_box.configure(state='normal')
        self.chat_box.insert(tk.END, f"{sender}: {message}\n")
        self.chat_box.configure(state='disabled')
        self.chat_box.yview(tk.END)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Close sockets or any cleanup logic here
            self.root.destroy()

    def show_signup_dialog(self):
        username = simpledialog.askstring("Sign Up", "Please enter a username:")
        if username:
            # Send sign-up request with the username
            # Handle response accordingly
            messagebox.showinfo("Sign Up", "Sign up successful!")
        else:
            messagebox.showwarning("Sign Up", "Username cannot be empty!")

    def show_login_dialog(self):
        username = simpledialog.askstring("Log In", "Please enter your username:")
        if username:
            # Send login request with the username
            # Handle response accordingly
            messagebox.showinfo("Log In", "Log in successful!")
        else:
            messagebox.showwarning("Log In", "Username cannot be empty!")

def main():
    # Initialize your sockets and other necessary components
    client_socket = None  # Replace None with your client socket
    peer_socket = None    # Replace None with your peer socket

    # Create the GUI
    app = ChatApplication(client_socket, peer_socket)

    # Additional buttons for sign-up and login
    signup_button = tk.Button(app.root, text="Sign Up", command=app.show_signup_dialog)
    signup_button.grid(row=2, column=0, padx=10, pady=10)

    login_button = tk.Button(app.root, text="Log In", command=app.show_login_dialog)
    login_button.grid(row=2, column=1, padx=10, pady=10)

    app.root.mainloop()

if __name__ == "__main__":
    main()
