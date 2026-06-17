from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector
from tkcalendar import DateEntry

# ================= DATABASE =================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="grocery"
)
cursor = db.cursor()

# ================= PRODUCT FORM =================
def product_form(window):

    prodFrame = Frame(window, width=1400, height=608, bg="#e9e6d5")
    prodFrame.place(x=200, y=150)

    Label(prodFrame, text="Product Management",
          font=('Garamond', 16, 'bold'), bg="#e9e6d5", fg="#0a3e34").place(x=0, y=0, relwidth=1, height=40)

    Button(prodFrame, text="Back",
           font=('Garamond', 10, 'bold'),
           cursor='hand2',
           bg="#e9e6d5", fg="#0a3e34",
           command=lambda: prodFrame.place_forget()).place(x=10, y=50)

    # ================= VARIABLES =================
    selected_id = StringVar()
    prname_var = StringVar()
    brand_var = StringVar()
    category_var = StringVar()
    price_var = StringVar()
    quantity_var = StringVar()
    availability_var = StringVar()
    shelf_var = StringVar()
    supplier_var = StringVar()

    search_by_var = StringVar()
    search_var = StringVar()

    # ================= MANAGE FRAME =================
    manageFrame = LabelFrame(prodFrame, text="Manage Product Details",
                             font=('Garamond', 14, 'bold'),
                             bg="white", padx=30, pady=10)
    manageFrame.place(x=20, y=90, width=600, height=500)

    fields = [("Product Name:", prname_var), ("Brand:", brand_var)]
    for i, (lbl, var) in enumerate(fields):
        Label(manageFrame, text=lbl, font=('Garamond', 12),
              bg='white').grid(row=i, column=0, sticky=W, pady=5)
        Entry(manageFrame, textvariable=var,
              background='#e9e6d5').grid(row=i, column=1, pady=5)

    row = 2
    Label(manageFrame, text="Category:", font=('Garamond', 12),
          bg='white').grid(row=row, column=0, sticky=W, pady=5)

    ttk.Combobox(manageFrame, textvariable=category_var,
                 values=[
                     "Rice and Grains", "Canned and Packaged Goods",
                     "Beverages", "Snacks and Sweets", "Dairy Products",
                     "Meat and Poultry", "Seafood", "Fruits", "Vegetables",
                     "Frozen Foods", "Bread and Bakery", "Condiments and Sauces",
                     "Cooking Oil and Spices", "Instant Noodles and Ready Meals",
                     "Household Cleaning Supplies", "Personal Care and Hygiene",
                     "Baby Products"
                 ],
                 width=13, font=('Garamond', 12),
                 background='#e9e6d5').grid(row=row, column=1, pady=5)

    row += 1
    Label(manageFrame, text="Price:", font=('Garamond', 12),
          bg='white').grid(row=row, column=0, sticky=W, pady=5)
    Entry(manageFrame, textvariable=price_var,
          background='#e9e6d5').grid(row=row, column=1, pady=5)

    row += 1
    Label(manageFrame, text="Quantity:", font=('Garamond', 12),
          bg='white').grid(row=row, column=0, sticky=W, pady=5)
    Entry(manageFrame, textvariable=quantity_var,
          background='#e9e6d5').grid(row=row, column=1, pady=5)

    row += 1
    Label(manageFrame, text="Availability:", font=('Garamond', 12),
          bg='white').grid(row=row, column=0, sticky=W, pady=5)
    ttk.Combobox(manageFrame, textvariable=availability_var,
                 values=["Available", "Out of Stock"],
                 width=13, font=('Garamond', 12),
                 background='#e9e6d5').grid(row=row, column=1, pady=5)

    row += 1
    Label(manageFrame, text="Shelf Life:", font=('Garamond', 12),
          bg='white').grid(row=row, column=0, sticky=W, pady=5)
    DateEntry(manageFrame, textvariable=shelf_var,
              date_pattern="yyyy-mm-dd",
              width=13, font=('Garamond', 12),
              background='#e9e6d5').grid(row=row, column=1, pady=5)

    row += 1
    Label(manageFrame, text="Supplier:", font=('Garamond', 12),
          bg='white').grid(row=row, column=0, sticky=W, pady=5)
    supplier_combo = ttk.Combobox(
        manageFrame,
        textvariable=supplier_var,
        width=20,
        font=('Garamond', 12),
        state="readonly"
    )
    supplier_combo.grid(row=row, column=1, pady=5)

    # ================= FUNCTIONS =================
    def clear_fields():
        selected_id.set("")
        prname_var.set("")
        brand_var.set("")
        category_var.set("")
        price_var.set("")
        quantity_var.set("")
        availability_var.set("")
        shelf_var.set("")
        supplier_var.set("")

    def has_supplier_fk():
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA=%s AND TABLE_NAME='Product' AND COLUMN_NAME='SupplierID'
            """, ("grocery",))
            return (cursor.fetchone()[0] or 0) > 0
        except:
            return False

    def load_suppliers():
        try:
            cursor.execute("SELECT SupID, Name FROM Supplier WHERE IsArchived=0")
            rows = cursor.fetchall()
            options = [f"{r[0]} - {r[1]}" for r in rows]
            supplier_combo["values"] = options
            if options:
                supplier_combo.set(options[0])
        except:
            supplier_combo["values"] = []

    def save_product():
        try:
            name = prname_var.get().strip()
            brand = brand_var.get().strip()
            category = category_var.get().strip()
            price = float(price_var.get())
            qty = int(quantity_var.get())
            availability = availability_var.get().strip()
            shelf = shelf_var.get().strip()

            if not name or not brand or not category or not availability or not shelf:
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            supplier_id = None
            if supplier_var.get():
                try:
                    supplier_id = int(supplier_var.get().split(" - ")[0])
                except:
                    supplier_id = None

            if has_supplier_fk():
                query = """
                    INSERT INTO Product
                    (PrName, PrBrand, Category, Price, Quantity, Availability, ShelfLife, SupplierID, IsArchived)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0)
                """
                cursor.execute(query, (
                    name, brand, category, price, qty, availability, shelf, supplier_id
                ))
            else:
                query = """
                    INSERT INTO Product
                    (PrName, PrBrand, Category, Price, Quantity, Availability, ShelfLife, IsArchived)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,0)
                """
                cursor.execute(query, (
                    name, brand, category, price, qty, availability, shelf
                ))

            db.commit()
            show_all()
            clear_fields()
            messagebox.showinfo("Success", "Product added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Price must be a number and Quantity an integer")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def update_selected():
        if not selected_id.get():
            messagebox.showwarning("Select", "Select a product to update.")
            return

        try:
            name = prname_var.get().strip()
            brand = brand_var.get().strip()
            category = category_var.get().strip()
            price = float(price_var.get())
            qty = int(quantity_var.get())
            availability = availability_var.get().strip()
            shelf = shelf_var.get().strip()

            supplier_id = None
            if supplier_var.get():
                try:
                    supplier_id = int(supplier_var.get().split(" - ")[0])
                except:
                    supplier_id = None

            if has_supplier_fk():
                query = """
                    UPDATE Product SET
                    PrName=%s, PrBrand=%s, Category=%s,
                    Price=%s, Quantity=%s, Availability=%s, ShelfLife=%s, SupplierID=%s
                    WHERE PrID=%s
                """
                cursor.execute(query, (
                    name, brand, category, price, qty, availability, shelf, supplier_id,
                    selected_id.get()
                ))
            else:
                query = """
                    UPDATE Product SET
                    PrName=%s, PrBrand=%s, Category=%s,
                    Price=%s, Quantity=%s, Availability=%s, ShelfLife=%s
                    WHERE PrID=%s
                """
                cursor.execute(query, (
                    name, brand, category, price, qty, availability, shelf,
                    selected_id.get()
                ))

            db.commit()
            show_all()
            clear_fields()
            messagebox.showinfo("Updated", "Product updated.")
        except ValueError:
            messagebox.showerror("Error", "Price must be a number and Quantity an integer")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def archive_selected():
        if not selected_id.get():
            messagebox.showwarning("Select", "Select a product to archive.")
            return

        cursor.execute(
            "UPDATE Product SET IsArchived=1 WHERE PrID=%s",
            (selected_id.get(),)
        )
        db.commit()
        show_all()
        clear_fields()
        messagebox.showinfo("Archived", "Product archived successfully.")

    # ================= BUTTONS =================
    btn_row = Frame(manageFrame, bg="white")
    btn_row.grid(row=8, column=0, columnspan=3, pady=20, sticky="ew")
    btn_row.columnconfigure(0, weight=0)
    btn_row.columnconfigure(1, weight=0)
    btn_row.columnconfigure(2, weight=0)
    btn_row.columnconfigure(3, weight=0)
    btn_row.columnconfigure(4, weight=0)
 
    Button(btn_row, text="Save", width=10, fg='#0a3e34', bg='#e9e6d5',
           font=('Garamond', 12, 'bold'),
           command=save_product).grid(row=0, column=0, padx=5)
 
    Button(btn_row, text="Update", width=10, fg='#0a3e34', bg='#e9e6d5',
           font=('Garamond', 12, 'bold'),
           command=update_selected).grid(row=0, column=1, padx=5)
 
    Button(btn_row, text="Delete", width=10, fg='#0a3e34', bg='#e9e6d5',
           font=('Garamond', 12, 'bold'),
           command=archive_selected).grid(row=0, column=2, padx=5)
 
    Button(btn_row, text="Clear", width=10, fg='#0a3e34', bg='#e9e6d5',
           font=('Garamond', 12, 'bold'),
           command=clear_fields).grid(row=0, column=3, padx=5)



    # ================= SEARCH FRAME =================
    searchFrame = LabelFrame(prodFrame, text="Search Products",
                             font=('Garamond', 14, 'bold'),
                             padx=10, pady=10)
    searchFrame.place(x=650, y=90, width=700, height=500)

    Label(searchFrame, text="Search By:",
          font=('Garamond', 12)).grid(row=0, column=0)

    ttk.Combobox(searchFrame, textvariable=search_by_var,
                 values=["PrName", "PrBrand", "Category"],
                 state="readonly").grid(row=0, column=1)

    Entry(searchFrame, textvariable=search_var).grid(row=0, column=2)

    # ================= TREEVIEW =================
    tree_container = Frame(searchFrame)
    tree_container.place(x=0, y=50, width=650, height=400)
    tree_container.grid_propagate(False)
    scroll_y = ttk.Scrollbar(tree_container, orient="vertical")
    scroll_x = ttk.Scrollbar(tree_container, orient="horizontal")
    product_tree = ttk.Treeview(
        tree_container,
        columns=("PrID","PrName","PrBrand","Category",
                 "Price","Quantity","Availability","ShelfLife"),
        show="headings",
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set
    )
    product_tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")
    tree_container.rowconfigure(0, weight=1)
    tree_container.columnconfigure(0, weight=1)
    scroll_y.config(command=product_tree.yview)
    scroll_x.config(command=product_tree.xview)

    for col in product_tree["columns"]:
        product_tree.heading(col, text=col)
        product_tree.column(col, width=120)

    def search_product():
        keyword = search_var.get()
        field = search_by_var.get()

        if field == "":
            messagebox.showwarning("Warning", "Select a field to search.")
            return

        if has_supplier_fk():
            query = f"""
                SELECT p.PrID, p.PrName, p.PrBrand, p.Category,
                       p.Price, p.Quantity, p.Availability, p.ShelfLife,
                       COALESCE(s.Name, '') AS Supplier
                FROM Product p
                LEFT JOIN Supplier s ON p.SupplierID = s.SupID
                WHERE p.{field} LIKE %s AND p.IsArchived = 0
            """
        else:
            query = f"""
                SELECT p.PrID, p.PrName, p.PrBrand, p.Category,
                       p.Price, p.Quantity, p.Availability, p.ShelfLife,
                       '' AS Supplier
                FROM Product p
                WHERE p.{field} LIKE %s AND p.IsArchived = 0
            """
        cursor.execute(query, (f"%{keyword}%",))

        rows = cursor.fetchall()
        product_tree.delete(*product_tree.get_children())

        for row in rows:
            product_tree.insert("", END, values=row)

    def revive_selected():
        if not selected_id.get():
            messagebox.showwarning("Select", "Select a product to revive.")
            return

        cursor.execute(
            "UPDATE Product SET IsArchived=0 WHERE PrID=%s",
            (selected_id.get(),)
        )
        db.commit()
        show_archived()
        clear_fields()
        messagebox.showinfo("Restored", "Product restored successfully.")

    def show_all():
        if has_supplier_fk():
            cursor.execute("""
                SELECT p.PrID, p.PrName, p.PrBrand, p.Category,
                       p.Price, p.Quantity, p.Availability, p.ShelfLife,
                       COALESCE(s.Name, '') AS Supplier
                FROM Product p
                LEFT JOIN Supplier s ON p.SupplierID = s.SupID
                WHERE p.IsArchived=0
            """)
        else:
            cursor.execute("""
                SELECT p.PrID, p.PrName, p.PrBrand, p.Category,
                       p.Price, p.Quantity, p.Availability, p.ShelfLife,
                       '' AS Supplier
                FROM Product p
                WHERE p.IsArchived=0
            """)
        rows = cursor.fetchall()
        product_tree.delete(*product_tree.get_children())
        for r in rows:
            product_tree.insert("", END, values=r)

    def show_archived():
        if has_supplier_fk():
            cursor.execute("""
                SELECT p.PrID, p.PrName, p.PrBrand, p.Category,
                       p.Price, p.Quantity, p.Availability, p.ShelfLife,
                       COALESCE(s.Name, '') AS Supplier
                FROM Product p
                LEFT JOIN Supplier s ON p.SupplierID = s.SupID
                WHERE p.IsArchived=1
            """)
        else:
            cursor.execute("""
                SELECT p.PrID, p.PrName, p.PrBrand, p.Category,
                       p.Price, p.Quantity, p.Availability, p.ShelfLife,
                       '' AS Supplier
                FROM Product p
                WHERE p.IsArchived=1
            """)
        rows = cursor.fetchall()
        product_tree.delete(*product_tree.get_children())
        for r in rows:
            product_tree.insert("", END, values=r)

    Button(
        searchFrame,
        text="Search",
        width=10,
        font=('Garamond', 12, 'bold'),
        fg='#e9e6d5',
        bg='#0a3e34',
        command=search_product
    ).grid(row=0, column=3, padx=5)

    Button(searchFrame, text="Show All", width=10,
           font=('Garamond', 12, 'bold'),
           fg='#e9e6d5', bg='#0a3e34',
           command=show_all).grid(row=0, column=4, padx=5)

    Button(searchFrame, text="Archive", width=6,
           font=('Garamond', 12, 'bold'),
           fg='#e9e6d5', bg='#0a3e34',
           command=show_archived).grid(row=0, column=5, padx=5)

    Button(btn_row, text="Revive", width=10,
           font=('Garamond', 12, 'bold'),
           fg='#0a3e34', bg='#e9e6d5',
           command=revive_selected).grid(row=0, column=4, padx=5)

    def fill_form(event):
        values = product_tree.item(product_tree.focus(), "values")
        if values:
            selected_id.set(values[0])
            prname_var.set(values[1])
            brand_var.set(values[2])
            category_var.set(values[3])
            price_var.set(values[4])
            quantity_var.set(values[5])
            availability_var.set(values[6])
            shelf_var.set(values[7])
            try:
                if has_supplier_fk():
                    cursor.execute("""
                        SELECT s.SupID, s.Name
                        FROM Supplier s
                        JOIN Product p ON p.SupplierID = s.SupID
                        WHERE p.PrID=%s
                    """, (values[0],))
                    res = cursor.fetchone()
                    if res:
                        supplier_var.set(f"{res[0]} - {res[1]}")
                    else:
                        supplier_var.set("")
            except:
                supplier_var.set("")

    product_tree.bind("<<TreeviewSelect>>", fill_form)

    load_suppliers()
    show_all()
