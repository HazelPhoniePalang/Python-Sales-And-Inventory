from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector

# ---------------- DB CONNECT -----------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="grocery"
    )


def employee_form(window):
    # ---------------- VARIABLES -----------------
    labels = [
        "Employee ID", "First Name", "Last Name", "Email", "Gender",
        "Date of Birth", "Contact No", "Employee Type", "Education",
        "Address", "Date of Joining", "Salary", "Role","Password"
    ]
    entries = {}

    # ---------------- GUI FRAMES -----------------
    empl_Frame = Frame(window, width=1400, height=608, bg="#e9e6d5")
    empl_Frame.place(x=200, y=150)

    Label(empl_Frame, text="Employee Management",
          font=('Garamond', 16, 'bold'), bg="#e9e6d5", fg="#0a3e34").place(x=0, y=0, relwidth=1, height=40)

    Button(empl_Frame, text="Back",
           font=('Garamond', 10, 'bold'),
           cursor='hand2',
           bg="#e9e6d5", fg="#0a3e34",
           command=lambda: empl_Frame.place_forget()).place(x=10, y=50)

    topFrame = Frame(empl_Frame, bg='white')
    topFrame.place(x=0, y=90, relwidth=1, height=235)

    searchFrame = Frame(topFrame)
    searchFrame.pack()

    search_comboB = ttk.Combobox(searchFrame,
                                 values=('ID', 'Name', 'Email'),
                                 font=('Garamond', 12, 'bold'),
                                 state='readonly')
    search_comboB.set('Search By')
    search_comboB.grid(column=0, row=0, padx=20)

    search_entry = Entry(searchFrame,
                         font=('Garamond', 12, 'bold'),
                         bg='#e9e6d5')
    search_entry.grid(column=1, row=0)

    # ---------------- TREEVIEW -----------------
    tree_frame = Frame(topFrame)
    tree_frame.pack(pady=10, fill="both", expand=True)

    scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    scroll_y.pack(side="right", fill="y")
    scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    scroll_x.pack(side="bottom", fill="x")

    emp_tree = ttk.Treeview(
        tree_frame,
        columns=labels,
        show='headings',
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set
    )
    emp_tree.pack(fill="both", expand=True)
    scroll_y.config(command=emp_tree.yview)
    scroll_x.config(command=emp_tree.xview)

    for col in labels:
        emp_tree.heading(col, text=col)
        emp_tree.column(col, width=150)

    # ---------------- EMPLOYEE INPUT FORM -----------------
    formFrame = Frame(empl_Frame, bg="white")
    formFrame.place(x=0, y=330, relwidth=1, height=278)

    row, col = 0, 0
    for index, label_text in enumerate(labels):
        Label(formFrame, text=label_text, font=('Garamond', 12, 'bold'), bg="white").grid(
            row=row, column=col, padx=50, pady=10, sticky="w")

        if label_text == "Gender":
            entry = ttk.Combobox(formFrame, font=('Garamond', 12),
                                 values=["Male", "Female"], state="readonly", width=18)
            entry.set('Gender')
        elif label_text == "Employee Type":
            entry = ttk.Combobox(formFrame, font=('Garamond', 12),
                                 values=["Regular", "Part-Time", "Contract"], state="readonly", width=18)
            entry.set('Employee Type')
        elif label_text == "Role":
            entry = ttk.Combobox(formFrame, font=('Garamond', 12),
                                 values=["Admin", "Cashier"], state="readonly", width=18)
            entry.set('Role')
        elif label_text in ["Date of Birth", "Date of Joining"]:
            entry = DateEntry(formFrame, width=18, font=('Garamond', 12),
                              background="#aada8e", foreground="#e9e6d5", date_pattern="yyyy-mm-dd")
        else:
            entry = Entry(formFrame, width=20, font=('Garamond', 12), bg='#e9e6d5')

        entry.grid(row=row, column=col + 1, padx=20, pady=10)
        entries[label_text] = entry

        col += 2
        if col > 4:
            col = 0
            row += 1

    # ---------------- BUTTONS -----------------
    btnFrame = Frame(formFrame, bg="white")
    btnFrame.grid(row=row + 1, column=0, columnspan=6, pady=20)

    # ---------- DATABASE FUNCTIONS ----------
    def clear_entries():
        for label in labels:
            if isinstance(entries[label], ttk.Combobox):
                entries[label].set("")
            else:
                entries[label].delete(0, END)

    def fill_form_from_treeview(event):
        selected = emp_tree.focus()
        if not selected:
            return
        values = emp_tree.item(selected, "values")
        for i, label in enumerate(labels):
            if isinstance(entries[label], ttk.Combobox):
                entries[label].set(values[i])
            else:
                entries[label].delete(0, END)
                entries[label].insert(0, values[i])

    def add_employee_db():
        try:
            conn = connect_db()
            cur = conn.cursor()
            values = [entries[label].get() for label in labels]
            sql = """INSERT INTO employees
            (EmpID, FirstName, LastName, Email, Gender, DOB, ContactNo,
             EmpType, Education, Address, DOJ, Salary, Role, Password)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(sql, values)
            conn.commit()
            messagebox.showinfo("Success", "Employee added successfully!")
            show_all_db()
            clear_entries()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def update_employee_db():
        selected = emp_tree.focus()
        if not selected:
            messagebox.showwarning("Select Row", "Select a record to update.")
            return
        try:
            conn = connect_db()
            cur = conn.cursor()
            values = [entries[label].get() for label in labels]
            sql = """UPDATE employees SET
                        FirstName=%s, LastName=%s, Email=%s, Gender=%s, DOB=%s,
                        ContactNo=%s, EmpType=%s, Education=%s, Address=%s,
                        DOJ=%s, Salary=%s, Role=%s, Password=%s
                     WHERE EmpID=%s"""
            update_values = values[1:] + [values[0]]
            cur.execute(sql, update_values)
            conn.commit()
            messagebox.showinfo("Updated", "Employee record updated!")
            show_all_db()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def delete_employee_db():
        selected = emp_tree.focus()
        if not selected:
            messagebox.showwarning("Select Row", "Select a record first.")
            return
        emp_id = emp_tree.item(selected, "values")[0]
        if not messagebox.askyesno("Confirm", "Archive this employee?"):
            return
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE employees SET Archived=1 WHERE EmpID=%s", (emp_id,))
            conn.commit()
            emp_tree.delete(selected)
            messagebox.showinfo("Archived", "Employee archived successfully.")
            clear_entries()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def show_all_db():
        for row in emp_tree.get_children():
            emp_tree.delete(row)
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM employees WHERE Archived=0")
            rows = cur.fetchall()
            for row in rows:
                emp_tree.insert("", END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def show_archived_db():
        for row in emp_tree.get_children():
            emp_tree.delete(row)
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM employees WHERE Archived=1")
            rows = cur.fetchall()
            for row in rows:
                emp_tree.insert("", END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def revive_employee_db():
        selected = emp_tree.focus()
        if not selected:
            messagebox.showwarning("Select Row", "Select a record first.")
            return
        emp_id = emp_tree.item(selected, "values")[0]
        if not messagebox.askyesno("Confirm", "Restore this employee?"):
            return
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE employees SET Archived=0 WHERE EmpID=%s", (emp_id,))
            conn.commit()
            emp_tree.delete(selected)  # Remove from archive view immediately
            messagebox.showinfo("Restored", "Employee restored successfully.")
            show_archived_db()  # Refresh archive table
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def search_employee_db():
        field = search_comboB.get()
        value = search_entry.get().strip()
        if field == "Search By" or value == "":
            messagebox.showwarning("Input Needed", "Choose a field and enter value")
            return
        db_field = {"ID": "EmpID", "Name": "FirstName", "Email": "Email"}[field]
        for row in emp_tree.get_children():
            emp_tree.delete(row)
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM employees WHERE {db_field} LIKE %s", (f"%{value}%",))
            rows = cur.fetchall()
            for row in rows:
                emp_tree.insert("", END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    # ---------------- BUTTONS -----------------
    Button(btnFrame, text="Add Employee", width=15, bg="#0a3e34", fg="white",
           font=('Garamond', 12, 'bold'), command=add_employee_db).grid(row=0, column=0, padx=10)

    Button(btnFrame, text="Update", width=15, bg="#0a3e34", fg="white",
           font=('Garamond', 12, 'bold'), command=update_employee_db).grid(row=0, column=1, padx=10)

    Button(btnFrame, text="Delete", width=15, bg="#a30000", fg="white",
           font=('Garamond', 12, 'bold'), command=delete_employee_db).grid(row=0, column=2, padx=10)

    Button(btnFrame, text="Clear", width=15, bg="#444444", fg="white",
           font=('Garamond', 12, 'bold'), command=clear_entries).grid(row=0, column=3, padx=10)

    Button(searchFrame, text="Search", width=10, fg='#e9e6d5', bg='#0a3e34',
           font=('Garamond', 12, 'bold'), command=search_employee_db).grid(column=2, row=0, padx=20)

    Button(searchFrame, text="Show All", width=10, fg='#e9e6d5', bg='#0a3e34',
           font=('Garamond', 12, 'bold'), command=show_all_db).grid(column=3, row=0, padx=20)

    Button(searchFrame, text="Archive", width=12, fg='#e9e6d5', bg='#0a3e34',
           font=('Garamond', 12, 'bold'), command=show_archived_db).grid(column=4, row=0, padx=10)

    Button(searchFrame, text="Revive", width=12, fg='#e9e6d5', bg='#0a3e34',
           font=('Garamond', 12, 'bold'), command=revive_employee_db).grid(column=5, row=0, padx=10)

    emp_tree.bind("<<TreeviewSelect>>", fill_form_from_treeview)

    # Show all on start
    show_all_db()
