import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Hardcoded email and password
HARDCODED_EMAIL = "siva"
HARDCODED_PASSWORD = "123456"

# Main Application Class
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Retail Application")
        self.geometry("800x600")
        self.resizable(True, True)

        # Container to hold all frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        # Dictionary to hold references to all frames
        self.frames = {}

        for F in (LoginPage, HomePage, AddInStockProductPage, AddSoldProductPage, SmartDashboardPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

# Login Page
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Center all widgets in the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Add a frame to hold the login widgets and center it
        login_frame = tk.Frame(self)
        login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        login_frame.grid_rowconfigure(2, weight=1)
        login_frame.grid_columnconfigure(1, weight=1)

        tk.Label(login_frame, text="Email:", font=("Arial", 16)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.email_entry = tk.Entry(login_frame, font=("Arial", 16), width=30)
        self.email_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(login_frame, text="Password:", font=("Arial", 16)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 16), width=30)
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Button(login_frame, text="Login", command=self.check_login, font=("Arial", 16)).grid(row=2, column=0, columnspan=2, pady=20)

    def check_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email == HARDCODED_EMAIL and password == HARDCODED_PASSWORD:
            self.controller.show_frame("HomePage")
        else:
            messagebox.showerror("Login Failed", "Incorrect email or password")

# Home Page
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Center all widgets in the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add a frame to hold the buttons and center it
        button_frame = tk.Frame(self)
        button_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        button_frame.grid_rowconfigure(2, weight=1)
        button_frame.grid_columnconfigure(0, weight=1)

        tk.Button(button_frame, text="Add In-Stock Product", command=lambda: self.controller.show_frame("AddInStockProductPage"), font=("Arial", 16), width=25).grid(row=0, column=0, pady=10)
        tk.Button(button_frame, text="Add Sold Product", command=lambda: self.controller.show_frame("AddSoldProductPage"), font=("Arial", 16), width=25).grid(row=1, column=0, pady=10)
        tk.Button(button_frame, text="Smart Dashboard", command=lambda: self.controller.show_frame("SmartDashboardPage"), font=("Arial", 16), width=25).grid(row=2, column=0, pady=10)

# Add In-Stock Product Page
class AddInStockProductPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Center all widgets in the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add a frame to hold the content and center it
        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        tk.Label(content_frame, text="Add In-Stock Product", font=("Arial", 18)).grid(row=0, column=0, pady=10)
        tk.Button(content_frame, text="Back to Home", command=lambda: self.controller.show_frame("HomePage"), font=("Arial", 16)).grid(row=1, column=0, pady=10)

# Add Sold Product Page
class AddSoldProductPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Center all widgets in the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add a frame to hold the content and center it
        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        tk.Label(content_frame, text="Add Sold Product", font=("Arial", 18)).grid(row=0, column=0, pady=10)
        tk.Button(content_frame, text="Back to Home", command=lambda: self.controller.show_frame("HomePage"), font=("Arial", 16)).grid(row=1, column=0, pady=10)

# Smart Dashboard Page
class SmartDashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
        self.original_geometry = self.controller.geometry()

    def create_widgets(self):
        # Center all widgets in the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add a frame to hold the content and center it
        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        content_frame.grid_rowconfigure(2, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        tk.Label(content_frame, text="Smart Dashboard", font=("Arial", 18)).grid(row=0, column=0, pady=10)
        tk.Button(content_frame, text="Open Dashboard", command=self.open_dashboard, font=("Arial", 16)).grid(row=1, column=0, pady=10)
        tk.Button(content_frame, text="Back to Home", command=self.go_back_home, font=("Arial", 16)).grid(row=2, column=0, pady=10)

    def open_dashboard(self):
        # Open the smart dashboard in a new pywebview window
        import webview
        webview.create_window("Smart Dashboard", "https://www.swiggy.com/")
        webview.start()

    def go_back_home(self):
        self.controller.show_frame("HomePage")
        self.controller.geometry(self.original_geometry)

if __name__ == "__main__":
    app = App()
    app.mainloop()
