import subprocess
import sys
from tkinter import *
from tkinter import messagebox
import mysql.connector


# Database connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="grocery"
    )


# Login function
def login_user():
    email = emailEntry.get()
    password = PassEntry.get()

    if not email or not password:
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        db = connect_db()
        cursor = db.cursor()

        query = """
            SELECT EmpID, Role
            FROM Employees
            WHERE Email=%s AND Password=%s
        """
        cursor.execute(query, (email, password))
        result = cursor.fetchone()

        if result:
            emp_id = result[0]
            role = result[1].lower()
            messagebox.showinfo("Success", f"Login Successful as {role.capitalize()}")

            window.destroy()

            if role == "admin":
                subprocess.Popen([sys.executable, "main.py", str(emp_id)])
            elif role == "cashier":
                subprocess.Popen([sys.executable, "Cashier.py", str(emp_id)])
            else:
                messagebox.showerror("Error", "User role not recognized")

        else:
            messagebox.showerror("Error", "Invalid email or password")

        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))


def show_login():
    global window, emailEntry, PassEntry
    window = Tk()
    window.title("Login")
    window.geometry("450x350+550+100")
    window.resizable(0, 0)
    window.config(bg="#f3f1e8")
    loginLabel = Label(window, text="Welcome back", font=('Garamond', 20, 'bold'),
                       fg="#0a3e34", bg="#f3f1e8")
    loginLabel.place(x=140, y=40)
    Emaillabel = Label(window, text="Email:", font=('Garamond', 13, 'bold'),
                       bg="#f3f1e8", fg="#0a3e34")
    Emaillabel.place(x=72, y=115)
    emailEntry = Entry(window, width=40)
    emailEntry.place(x=128, y=118)
    Passlabel = Label(window, text="Password:", font=('Garamond', 13, 'bold'),
                      bg="#f3f1e8", fg="#0a3e34")
    Passlabel.place(x=72, y=185)
    PassEntry = Entry(window, show='*', width=36)
    PassEntry.place(x=155, y=188)
    loginBTN = Button(
        window,
        text="Login",
        font=('Garamond', 10, 'bold'),
        fg='#0a3e34',
        bg='#e9e6d5',
        width=10,
        height=1,
        command=login_user)
    loginBTN.place(x=190, y=260)
    window.mainloop()

if __name__ == "__main__":
    show_login()
