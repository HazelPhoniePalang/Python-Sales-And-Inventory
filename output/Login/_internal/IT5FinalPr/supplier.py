from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector

# ========== Database Setup ==========
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="grocery"
    )

# ========== Supplier Form ==========
def supplier_form(window):

    # ---------- GUI ----------
    supframe = Frame(window, width=1400, height=608, bg="#e9e6d5")
    supframe.place(x=200, y=150)

    Label(
        supframe,
        text="Supplier Management",
        font=('Garamond', 16, 'bold'),
         bg="#e9e6d5", fg="#0a3e34"
    ).place(x=0, y=0, relwidth=1, height=40)

    Button(
        supframe,
        text="Back",
        font=('Garamond', 10, 'bold'),
        cursor='hand2',
        bg="#e9e6d5", fg="#0a3e34",
        command=lambda: supframe.place_forget()
    ).place(x=10, y=50)

    # ---------- Entries ----------
    Label(supframe, text="Invoice No.", font=('Garamond', 12,'bold'), bg='#e9e6d5').place(x=20, y=90)
    invoice_entry = Entry(supframe, bg="white")
    invoice_entry.place(x=140, y=95, width=200)

    Label(supframe, text="Supplier Name", font=('Garamond', 12,'bold'), bg='#e9e6d5').place(x=20, y=130)
    name_entry = Entry(supframe, bg="white")
    name_entry.place(x=140, y=135, width=200)

    Label(supframe, text="Contact", font=('Garamond', 12,'bold'), bg='#e9e6d5').place(x=20, y=170)
    contact_entry = Entry(supframe, bg="white")
    contact_entry.place(x=140, y=175, width=200)

    Label(supframe, text="Description", font=('Garamond', 12,'bold'), bg='#e9e6d5').place(x=20, y=210)
    desc_entry = Text(supframe, bg="white")
    desc_entry.place(x=140, y=215, width=300, height=130)

    # ---------- Helpers ----------
    def clear_fields():
        invoice_entry.delete(0, END)
        name_entry.delete(0, END)
        contact_entry.delete(0, END)
        desc_entry.delete("1.0", END)
        tree.selection_remove(tree.selection())

    def load_suppliers():
        tree.delete(*tree.get_children())

        db = connect_db()
        cur = db.cursor()
        cur.execute("""
            SELECT SupID, InvoiceNo, Name, Contact, Description
            FROM Supplier
            WHERE IsArchived = 0
        """)
        for row in cur.fetchall():
            tree.insert("", END, values=row)
        db.close()

    # ---------- CRUD ----------
    def save_supplier():
        if not invoice_entry.get() or not name_entry.get():
            messagebox.showwarning("Input Error", "Invoice No and Name are required")
            return

        db = connect_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO Supplier (InvoiceNo, Name, Contact, Description, IsArchived)
            VALUES (%s, %s, %s, %s, 0)
        """, (
            invoice_entry.get(),
            name_entry.get(),
            contact_entry.get(),
            desc_entry.get("1.0", END).strip()
        ))
        db.commit()
        db.close()

        clear_fields()
        load_suppliers()
        messagebox.showinfo("Success", "Supplier saved")

    def update_supplier():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Select a supplier to update")
            return

        sup_id = tree.item(selected)['values'][0]

        db = connect_db()
        cur = db.cursor()
        cur.execute("""
            UPDATE Supplier
            SET InvoiceNo=%s, Name=%s, Contact=%s, Description=%s
            WHERE SupID=%s
        """, (
            invoice_entry.get(),
            name_entry.get(),
            contact_entry.get(),
            desc_entry.get("1.0", END).strip(),
            sup_id
        ))
        db.commit()
        db.close()

        clear_fields()
        load_suppliers()
        messagebox.showinfo("Updated", "Supplier updated")

    def delete_supplier():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Select a supplier to archive")
            return

        sup_id = tree.item(selected)['values'][0]

        db = connect_db()
        cur = db.cursor()
        cur.execute("UPDATE Supplier SET IsArchived=1 WHERE SupID=%s", (sup_id,))
        db.commit()
        db.close()

        clear_fields()
        load_suppliers()
        messagebox.showinfo("Archived", "Supplier archived")

    def revive_supplier():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Select a supplier to revive.")
            return

        sup_id = tree.item(selected)['values'][0]

        db = connect_db()
        cur = db.cursor()
        cur.execute("UPDATE Supplier SET IsArchived=0 WHERE SupID=%s", (sup_id,))
        db.commit()
        db.close()

        load_suppliers()
        clear_fields()
        messagebox.showinfo("Restored", "Supplier restored successfully.")

    def search_supplier():
        tree.delete(*tree.get_children())

        db = connect_db()
        cur = db.cursor()
        cur.execute("""
            SELECT SupID, InvoiceNo, Name, Contact, Description
            FROM Supplier
            WHERE InvoiceNo LIKE %s AND IsArchived = 0
        """, ('%' + search_entry.get() + '%',))

        for row in cur.fetchall():
            tree.insert("", END, values=row)
        db.close()

    def show_archived_suppliers():
        tree.delete(*tree.get_children())

        db = connect_db()
        cur = db.cursor()
        cur.execute("""
            SELECT SupID, InvoiceNo, Name, Contact, Description
            FROM Supplier
            WHERE IsArchived = 1
        """)

        for row in cur.fetchall():
            tree.insert("", END, values=row)

        db.close()

    def show_all_suppliers():
        load_suppliers()

    # ---------- Buttons ----------
    Button(supframe, text="Save", font=('Garamond', 12,'bold'),
           bg="#0a3e34", fg="white", command=save_supplier).place(x=20, y=370, width=90)

    Button(supframe, text="Update", font=('Garamond', 12,'bold'),
           bg="#0a3e34", fg="white", command=update_supplier).place(x=130, y=370, width=90)

    Button(supframe, text="Delete", font=('Garamond', 12,'bold'),
           bg="#a30000", fg="white", command=delete_supplier).place(x=240, y=370, width=90)

    Button(supframe, text="Clear", font=('Garamond', 12,'bold'),
           bg="#444444", fg="white", command=clear_fields).place(x=350, y=370, width=90)

    Button(supframe, text="Revive", font=('Garamond', 12, 'bold'),
           bg="#0a3e34", fg="white", command=revive_supplier).place(x=460, y=370, width=90)

    # ---------- Search ----------
    Label(supframe, text="Invoice No", font=('Garamond', 12,'bold'),
          bg="#e9e6d5").place(x=530, y=90)

    search_entry = Entry(supframe, bg="white")
    search_entry.place(x=630, y=90, width=200)

    Button(supframe, text="Search", font=('Garamond', 12,'bold'),
           bg="#0a3e34", fg="white", command=search_supplier).place(x=850, y=85, width=90)

    Button(supframe, text="Show All", font=('Garamond', 12,'bold'),
           bg="#0a3e34", fg="white", command=show_all_suppliers).place(x=960, y=85, width=90)

    Button(supframe, text="Archived",font=('Garamond', 12, 'bold'),
        bg="#0a3e34",fg="white",command=show_archived_suppliers).place(x=1070, y=85, width=90)

    # ---------- Treeview ----------
    tree_frame = Frame(supframe, bg="white", bd=2, relief=RIDGE)
    tree_frame.place(x=550, y=130, width=630, height=380)

    tree = ttk.Treeview(
        tree_frame,
        columns=("SupID", "InvoiceNo", "Name", "Contact", "Description"),
        show="headings"
    )

    for col, w in zip(tree["columns"], [60, 120, 150, 120, 200]):
        tree.heading(col, text=col)
        tree.column(col, width=w)

    tree.pack(fill=BOTH, expand=1)

    def populate_fields(event):
        selected = tree.focus()
        if not selected:
            return
        vals = tree.item(selected)['values']
        invoice_entry.delete(0, END)
        invoice_entry.insert(0, vals[1])
        name_entry.delete(0, END)
        name_entry.insert(0, vals[2])
        contact_entry.delete(0, END)
        contact_entry.insert(0, vals[3])
        desc_entry.delete("1.0", END)
        desc_entry.insert(END, vals[4])

    tree.bind("<ButtonRelease-1>", populate_fields)

    load_suppliers()
