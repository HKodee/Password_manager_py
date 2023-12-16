import json
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class PasswordManager:
    def __init__(self, key_file='key.key', data_file='passwords.json'):
        self.key_file = key_file
        self.data_file = data_file
        self.load_key()
        self.load_passwords()

    def load_key(self):
        try:
            with open(self.key_file, 'rb') as key_file:
                self.key = key_file.read()
        except FileNotFoundError:
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(self.key)

    def load_passwords(self):
        try:
            with open(self.data_file, 'rb') as data_file:
                encrypted_data = data_file.read()
                cipher = Fernet(self.key)
                decrypted_data = cipher.decrypt(encrypted_data).decode('utf-8')
                self.accounts = json.loads(decrypted_data)
        except FileNotFoundError:
            self.accounts = {}
        except json.JSONDecodeError:
            self.accounts = {}

    def save_passwords(self):
        cipher = Fernet(self.key)
        encrypted_data = cipher.encrypt(json.dumps(self.accounts).encode('utf-8'))
        with open(self.data_file, 'wb') as data_file:
            data_file.write(encrypted_data)

    def add_password(self, account_name, site, password):
        if account_name not in self.accounts:
            self.accounts[account_name] = {}
        if site not in self.accounts[account_name]:
            self.accounts[account_name][site] = password
            self.save_passwords()
            return "Password added successfully."
        else:
            return "Site already exists in the password manager."

    def get_passwords(self, account_name):
        return self.accounts.get(account_name, {})

    def edit_password(self, account_name, site, new_password):
        if account_name in self.accounts:
            if site in self.accounts[account_name]:
                self.accounts[account_name][site] = new_password
                self.save_passwords()
                return "Password updated successfully."
            else:
                return "Site not found in the password manager."
        else:
            return "Account not found in the password manager."

    def delete_password(self, account_name, site):
        if account_name in self.accounts:
            if site in self.accounts[account_name]:
                del self.accounts[account_name][site]
                self.save_passwords()
                return "Password deleted successfully."
            else:
                return "Site not found in the password manager."
        else:
            return "Account not found in the password manager."

class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.configure(bg='#ccc')  # Set light blue background color

        # Set the style for the Treeview widget
        style = ttk.Style()
        style.theme_use('clam')  # Use a clean and modern theme
        style.configure("Treeview", font=('Arial', 12), rowheight=25, background='#b3e0ff', fieldbackground='#b3e0ff', borderwidth=0)
        style.map("Treeview", relief=[('selected', 'sunken')])

        self.password_manager = PasswordManager()

        self.create_widgets()

        # Populate the grid with passwords when the application starts
        self.populate_password_grid()

    def create_widgets(self):
        # Button widgets
        add_button = ttk.Button(self.root, text="Add", command=self.add_new_entry)
        add_button.pack(pady=10)

        # Treeview widget for displaying passwords in a grid
        self.tree = ttk.Treeview(self.root, columns=('S.no', 'Account', 'Site', 'Password'), show='headings', style="Treeview", height=20)
        self.tree.heading('S.no', text='S.no', anchor='center')
        self.tree.heading('Account', text='Account', anchor='center')
        self.tree.heading('Site', text='Site', anchor='center')
        self.tree.heading('Password', text='Password', anchor='center')
        self.tree.pack(pady=20)

        # Bind event for right-click
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Context menu for right-click options
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Edit Password", command=self.edit_password)
        self.context_menu.add_command(label="Delete Password", command=self.delete_password)

        # Instance variable for serial number
        self.serial_number = 1

    def add_new_entry(self):
        account_name = simpledialog.askstring("Input", "Enter account:")
        site = simpledialog.askstring("Input", "Enter site:")
        password = simpledialog.askstring("Input", "Enter password:", show='*')

        if account_name and site and password:
            result = self.password_manager.add_password(account_name, site, password)
            messagebox.showinfo("Result", result)
            self.populate_password_grid()
        else:
            messagebox.showinfo("Error", "Account, site, and password cannot be empty.")

    def populate_password_grid(self):
        # Clear existing items in the grid
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Reset serial number to 1
        self.serial_number = 1

        # Populate the grid with passwords
        for account_name, account_data in self.password_manager.accounts.items():
            if isinstance(account_data, dict):  # Check if account_data is a dictionary
                for site, password in account_data.items():
                    self.tree.insert('', 'end', values=(self.serial_number, account_name, site, password))
                    self.serial_number += 1

    def show_context_menu(self, event):
        # Select the item that was right-clicked
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def edit_password(self):
        selected_item = self.tree.selection()
        if selected_item:
            account_name = self.tree.item(selected_item, "values")[1]
            site = self.tree.item(selected_item, "values")[2]
            new_password = simpledialog.askstring("Edit Password", f"Enter new password for {account_name}/{site}:", show='*')
            if new_password:
                result = self.password_manager.edit_password(account_name, site, new_password)
                messagebox.showinfo("Result", result)
                self.populate_password_grid()

    def delete_password(self):
        selected_item = self.tree.selection()
        if selected_item:
            account_name = self.tree.item(selected_item, "values")[1]
            site = self.tree.item(selected_item, "values")[2]
            result = self.password_manager.delete_password(account_name, site)
            messagebox.showinfo("Result", result)
            self.populate_password_grid()

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap('password.ico')
    app = PasswordManagerGUI(root)
    root.mainloop()
