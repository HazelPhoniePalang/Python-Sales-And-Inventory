import subprocess
import sys
from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector
import os
from datetime import datetime, date
import random


# ================= DATABASE CONNECTION HELPER =================
def connect_db():
    """
    Centralized database connection.
    Change the parameters here to match your MySQL setup.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="grocery"
    )


class CashierClass:
    def __init__(self, root, emp_id):
        self.root = root
        self.root.geometry("1500x768+10+5")
        self.root.title("Grocery Cashier System")
        self.root.config(bg='white')
        self.root.resizable(False, False)

        # ================= VARIABLES =================
        self.emp_id = emp_id
        self.cashier_name = self.get_cashier_name(self.emp_id)

        # Product Entry Variables
        self.var_pid = StringVar()
        self.var_pname = StringVar()
        self.var_price = DoubleVar()
        self.var_qty = IntVar()
        self.var_stock = StringVar()
        self.var_search = StringVar()

        # Customer Variables
        self.var_cname = StringVar()
        self.var_ccontact = StringVar()

        # Cart Calculation Variables
        self.cart_list = []  # Stores (pid, name, price, qty, total)
        self.var_total_bill = DoubleVar()
        self.var_total_bill.set(0.0)
        self.bill_no = ""

        # ================= TITLE SECTION =================
        titleLabel = Label(self.root, text="Grocery Sales & Inventory Management System",
                           font=('Garamond', 25, 'bold'), fg="white", bg="#0a3e34",
                           anchor='center', padx=10, pady=10)
        titleLabel.place(x=0, y=0, height=100, relwidth=1)

        # Date/Time/User Sub-label
        self.subLabel = Label(self.root, text="", font=('Garamond', 12, 'bold'), bg="#e9e6d5", fg="#0a3e34")
        self.subLabel.place(x=0, y=100, height=30, relwidth=1)
        self.update_time()

        # Logout Button
        logout_btn = Button(
            self.root,
            text="Logout",
            font=('Garamond', 15, 'bold'),
            fg='#0a3e34',
            bg='#e9e6d5',
            cursor="hand2",
            command=self.logout
        )
        logout_btn.place(x=1350, y=30)

        # ================= LEFT FRAME (Search Area) =================
        self.leftFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.leftFrame.place(x=10, y=140, width=450, height=120)

        lbl_search = Label(self.leftFrame, text="Search Product By Name:", font=("Garamond", 12, "bold"),
                           bg="white", fg="#0a3e34")
        lbl_search.place(x=10, y=10)

        txt_search = Entry(self.leftFrame, textvariable=self.var_search, font=("Garamond", 15), bg="#e9e6d5")
        txt_search.place(x=10, y=40, width=280, height=30)

        btn_search = Button(self.leftFrame, text="Search", command=self.search_product,
                            font=("Garamond", 12, "bold"), bg="#0a3e34", fg="white", cursor="hand2")
        btn_search.place(x=300, y=40, width=130, height=30)

        btn_show_all = Button(self.leftFrame, text="Show All Available", command=self.fetch_products,
                              font=("Garamond", 12, "bold"), bg="#555", fg="white", cursor="hand2")
        btn_show_all.place(x=10, y=80, width=420, height=30)

        # ================= BOTTOM LEFT FRAME (Product Table) =================
        self.botFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.botFrame.place(x=10, y=270, width=450, height=480)

        scrolly = Scrollbar(self.botFrame, orient=VERTICAL)
        self.product_table = ttk.Treeview(self.botFrame, columns=("pid", "name", "price", "qty", "status"),
                                          yscrollcommand=scrolly.set)

        scrolly.pack(side=RIGHT, fill=Y)
        scrolly.config(command=self.product_table.yview)

        self.product_table.heading("pid", text="ID")
        self.product_table.heading("name", text="Name")
        self.product_table.heading("price", text="Price")
        self.product_table.heading("qty", text="Stock")
        self.product_table.heading("status", text="Status")

        self.product_table.column("pid", width=40)
        self.product_table.column("name", width=140)
        self.product_table.column("price", width=70)
        self.product_table.column("qty", width=60)
        self.product_table.column("status", width=80)

        self.product_table["show"] = "headings"
        self.product_table.pack(fill=BOTH, expand=1)
        self.product_table.bind("<ButtonRelease-1>", self.get_data)

        # ================= MIDDLE FRAME (Customer, Calculator, Cart) =================
        self.middleFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.middleFrame.place(x=470, y=140, width=520, height=610)

        # --- Customer Details ---
        lbl_m_title = Label(self.middleFrame, text="Customer Details", font=("Garamond", 15, "bold"),
                            bg="#0a3e34", fg="white")
        lbl_m_title.pack(side=TOP, fill=X)

        cust_frame = Frame(self.middleFrame, bg="white")
        cust_frame.pack(fill=X, pady=5)

        Label(cust_frame, text="Name:", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=0, padx=5, sticky=W)
        Entry(cust_frame, textvariable=self.var_cname, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=0, column=1,
                                                                                                        padx=5)

        Label(cust_frame, text="Contact:", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=2, padx=5,
                                                                                        sticky=W)
        Entry(cust_frame, textvariable=self.var_ccontact, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=0,
                                                                                                               column=3,
                                                                                                               padx=5)

        # --- Calculator & Cart Area ---
        calc_cart_frame = Frame(self.middleFrame, bg="white")
        calc_cart_frame.pack(fill=BOTH, expand=True, pady=5)

        # Calculator (Left Side of Middle)
        self.calc_frame = Frame(calc_cart_frame, bd=2, relief=RIDGE, bg="#e9e6d5")
        self.calc_frame.place(x=5, y=0, width=240, height=270)

        self.calc_input = Entry(self.calc_frame, font=('Garamond', 15, 'bold'), width=18, justify=RIGHT)
        self.calc_input.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        btn_list = [
            '7', '8', '9', '+',
            '4', '5', '6', '-',
            '1', '2', '3', '*',
            'C', '0', '=', '/'
        ]

        r = 1
        c = 0
        for b in btn_list:
            cmd = lambda x=b: self.btn_click(x)
            Button(self.calc_frame, text=b, command=cmd, font=('Garamond', 12, 'bold'), width=4, height=2).grid(row=r,
                                                                                                             column=c,
                                                                                                             padx=2,
                                                                                                             pady=2)
            c += 1
            if c > 3:
                c = 0
                r += 1

        # Cart Table (Right Side of Middle)
        cart_frame = Frame(calc_cart_frame, bd=2, relief=RIDGE, bg="white")
        cart_frame.place(x=250, y=0, width=260, height=270)

        lbl_cart = Label(cart_frame, text="Cart / Purchase List", font=("Garamond", 12, "bold"), bg="#0a3e34",
                         fg="white")
        lbl_cart.pack(side=TOP, fill=X)

        scrolly_cart = Scrollbar(cart_frame, orient=VERTICAL)
        self.CartTable = ttk.Treeview(cart_frame, columns=("pname", "price", "qty"), yscrollcommand=scrolly_cart.set)
        scrolly_cart.pack(side=RIGHT, fill=Y)
        scrolly_cart.config(command=self.CartTable.yview)

        self.CartTable.heading("pname", text="Name")
        self.CartTable.heading("price", text="Price")
        self.CartTable.heading("qty", text="Qty")
        self.CartTable.column("pname", width=120)
        self.CartTable.column("price", width=60)
        self.CartTable.column("qty", width=40)
        self.CartTable["show"] = "headings"
        self.CartTable.pack(fill=BOTH, expand=1)
        self.CartTable.bind("<ButtonRelease-1>", self.get_cart_data)

        # --- Product Selection & Add to Cart (Bottom of Middle) ---
        prod_select_frame = Frame(self.middleFrame, bd=2, relief=RIDGE, bg="white")
        prod_select_frame.pack(side=BOTTOM, fill=X, pady=5)

        Label(prod_select_frame, text="Product Name", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=0,
                                                                                                   padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_pname, font=("Garamond", 10), bg="#e9e6d5", state='readonly',
              width=20).grid(row=0, column=1, padx=5, pady=2)

        Label(prod_select_frame, text="Price (PHP)", font=("Garamond", 10, "bold"), bg="white").grid(row=1, column=0,
                                                                                                  padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_price, font=("Garamond", 10), bg="#e9e6d5", state='readonly',
              width=20).grid(row=1, column=1, padx=5, pady=2)

        Label(prod_select_frame, text="Quantity", font=("Garamond", 10, "bold"), bg="white").grid(row=2, column=0, padx=5,
                                                                                               pady=2)
        Entry(prod_select_frame, textvariable=self.var_qty, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=2,
                                                                                                             column=1,
                                                                                                             padx=5,
                                                                                                             pady=2)

        Label(prod_select_frame, text="Stock Avail.", font=("Garamond", 10, "bold"), bg="white").grid(row=3, column=0,
                                                                                                  padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_stock, font=("Garamond", 10), bg="#e9e6d5", state='readonly',
              width=20).grid(row=3, column=1, padx=5, pady=2)

        # Buttons
        btn_prod_frame = Frame(prod_select_frame, bg="white")
        btn_prod_frame.grid(row=0, column=2, rowspan=4, padx=10)

        Button(btn_prod_frame, text="Add to Cart", command=self.add_cart, font=("Garamond", 12, "bold"), bg="#0a3e34",
               fg="white", width=12, height=2).pack(pady=2)
        Button(btn_prod_frame, text="Clear", command=self.clear_product_input, font=("Garamond", 12, "bold"), bg="#555",
               fg="white", width=12).pack(pady=2)

        lbl_inst = Label(self.middleFrame, text="Note: Select product from Left Table", font=("Garamond", 9), fg="red",
                         bg="white")
        lbl_inst.pack(side=BOTTOM)

        # ================= RIGHT FRAME (Billing Area) =================
        self.rightFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.rightFrame.place(x=1000, y=140, width=480, height=610)

        lbl_r_title = Label(self.rightFrame, text="Customer Receipt", font=("Garamond", 15, "bold"),
                            bg="#0a3e34", fg="white")
        lbl_r_title.pack(side=TOP, fill=X)

        self.txt_bill_area = Text(self.rightFrame, font=("courier new", 10))
        self.txt_bill_area.pack(fill=BOTH, expand=1)

        # Bill Buttons
        btn_bill_frame = Frame(self.rightFrame, bg="white")
        btn_bill_frame.pack(side=BOTTOM, fill=X)

        self.lbl_amnt = Label(btn_bill_frame, text="Total: 0.00 PHP", font=("Garamond", 14, "bold"), bg="white",
                              fg="#0a3e34")
        self.lbl_amnt.pack(fill=X, pady=5)

        Button(btn_bill_frame, text="Generate Bill", command=self.generate_bill, bg="#0a3e34", fg="white",
               font=("Garamond", 12, "bold"), width=15).pack(side=LEFT, padx=5, pady=10)
        Button(btn_bill_frame, text="Print & Save", command=self.print_bill, bg="#2196F3", fg="white",
               font=("Garamond", 12, "bold"), width=15).pack(side=LEFT, padx=5, pady=10)
        Button(btn_bill_frame, text="Clear All", command=self.clear_all, bg="#f44336", fg="white",
               font=("Garamond", 12, "bold"), width=10).pack(side=LEFT, padx=5, pady=10)

        # Initialize data
        self.fetch_products()

    # ================= LOGIC FUNCTIONS =================

    def update_time(self):
        current_date = date.today().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        self.subLabel.config(text=f"Welcome: {self.cashier_name}   |   Date: {current_date}   |   Time: {current_time}")
        self.subLabel.after(1000, self.update_time)

    def fetch_products(self):
        self.product_table.delete(*self.product_table.get_children())
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "SELECT PrID, PrName, Price, Quantity, Availability FROM Product WHERE IsArchived=0 AND Availability='Available' AND Quantity > 0")
            rows = cur.fetchall()
            for row in rows:
                self.product_table.insert("", END, values=row)
        except Exception as ex:
            messagebox.showerror("Error", f"Database Error: {str(ex)}")
        finally:
            if conn: conn.close()

    def search_product(self):
        if self.var_search.get() == "":
            messagebox.showerror("Error", "Please enter product name to search")
            return

        self.product_table.delete(*self.product_table.get_children())
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "SELECT PrID, PrName, Price, Quantity, Availability FROM Product WHERE PrName LIKE %s AND IsArchived=0 AND Quantity > 0",
                ('%' + self.var_search.get() + '%',)
            )
            rows = cur.fetchall()
            if len(rows) != 0:
                for row in rows:
                    self.product_table.insert("", END, values=row)
            else:
                messagebox.showinfo("Not Found", "No available product found with that name")
        except Exception as ex:
            messagebox.showerror("Error", f"Database Error: {str(ex)}")
        finally:
            if conn: conn.close()

    def get_data(self, ev):
        try:
            f = self.product_table.focus()
            content = (self.product_table.item(f))
            row = content['values']
            if row:
                self.var_pid.set(row[0])
                self.var_pname.set(row[1])
                self.var_price.set(row[2])
                self.var_qty.set(1)
                self.var_stock.set(row[3])
        except IndexError:
            pass

    def add_cart(self):
        # Validation checks
        if self.var_pid.get() == "":
            messagebox.showerror("Error", "Please select a product from the list")
            return

        try:
            qty = self.var_qty.get()
            stock = int(self.var_stock.get())
            price = float(self.var_price.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid Format for Quantity or Stock")
            return

        if qty == 0:
            messagebox.showerror("Error", "Quantity cannot be zero")
            return

        if qty > stock:
            messagebox.showerror("Error", "Requested quantity exceeds available stock")
            return

        # Check if already in cart
        for item in self.cart_list:
            if item[0] == self.var_pid.get():
                messagebox.showerror("Error", "Product already in cart. Remove it to update quantity.")
                return

        total_price = price * qty
        # Format: [pid, name, price, qty, total]
        self.cart_list.append([self.var_pid.get(), self.var_pname.get(), price, qty, total_price])

        # Add to Cart Treeview
        self.CartTable.insert("", END, values=(self.var_pname.get(), price, qty))
        self.update_total_bill()
        self.clear_product_input()
        messagebox.showinfo("Success", "Item Added to Cart")

    def get_cart_data(self, ev):
        # Optional: Logic if you want to select items in the cart
        pass

    def update_total_bill(self):
        total = 0.0
        for item in self.cart_list:
            total += item[4]
        self.var_total_bill.set(total)
        self.lbl_amnt.config(text=f"Total: {str(total)} PHP")

    def clear_product_input(self):
        self.var_pid.set("")
        self.var_pname.set("")
        self.var_price.set("")
        self.var_qty.set(0)
        self.var_stock.set("")

    def generate_bill(self):
        if len(self.cart_list) == 0:
            messagebox.showerror("Error", "Cart is empty")
            return
        if self.var_cname.get() == "" or self.var_ccontact.get() == "":
            messagebox.showerror("Error", "Customer Details Required")
            return

        # Receipt Header
        self.bill_no = str(random.randint(1000, 9999))
        date_now = datetime.now().strftime("%d/%m/%Y")
        time_now = datetime.now().strftime("%H:%M:%S")

        self.txt_bill_area.delete('1.0', END)
        self.txt_bill_area.insert(END, "\t    GROCERY STORE RECEIPT\n")
        self.txt_bill_area.insert(END, "\t    Tel: +63 900 000 0000\n")
        self.txt_bill_area.insert(END, "------------------------------------------------\n")
        self.txt_bill_area.insert(END, f" Bill No : {self.bill_no}\n")
        self.txt_bill_area.insert(END, f" Date    : {date_now}  Time: {time_now}\n")
        self.txt_bill_area.insert(END, f" Cashier : {self.cashier_name}\n")
        self.txt_bill_area.insert(END, f" Customer: {self.var_cname.get()}\n")
        self.txt_bill_area.insert(END, f" Contact : {self.var_ccontact.get()}\n")
        self.txt_bill_area.insert(END, "------------------------------------------------\n")
        self.txt_bill_area.insert(END, " Product\t\tQty\tPrice\tTotal\n")
        self.txt_bill_area.insert(END, "------------------------------------------------\n")

        # Receipt Body
        for item in self.cart_list:
            name = item[1]
            qty = item[3]
            price = item[2]
            total = item[4]
            self.txt_bill_area.insert(END, f" {name}\t\t{qty}\t{price}\t{total}\n")

        self.txt_bill_area.insert(END, "------------------------------------------------\n")
        self.txt_bill_area.insert(END, f" Total Amount:\t\t\t\tPHP {self.var_total_bill.get()}\n")
        self.txt_bill_area.insert(END, "------------------------------------------------\n")
        self.txt_bill_area.insert(END, "\t  THANK YOU FOR SHOPPING!\n")

    def print_bill(self):
        if len(self.cart_list) == 0:
            messagebox.showerror("Error", "Cart is empty")
            return
        if not self.bill_no:
            messagebox.showerror("Error", "Please Generate Bill First")
            return

        # Create bills folder if not exists
        if not os.path.exists("bills"):
            os.mkdir("bills")

        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()

            # Update Database Stock
            for item in self.cart_list:
                pid = item[0]
                qty_sold = item[3]

                # Get current stock to ensure accuracy
                cur.execute("SELECT Quantity FROM Product WHERE PrID=%s", (pid,))
                res = cur.fetchone()
                if res:
                    current_stock = res[0]
                    new_stock = current_stock - qty_sold

                    # Determine Status
                    status = "Available"
                    if new_stock <= 0:
                        new_stock = 0
                        status = "Out of Stock"

                    cur.execute("UPDATE Product SET Quantity=%s, Availability=%s WHERE PrID=%s",
                                (new_stock, status, pid))

            conn.commit()

            # Save to file only if DB update succeeds
            bill_content = self.txt_bill_area.get('1.0', END)
            with open(f"bills/{self.bill_no}.txt", "w") as f:
                f.write(bill_content)

            messagebox.showinfo("Success", f"Bill Saved as {self.bill_no}.txt and Stock Updated")
            self.clear_all()
            self.fetch_products()

        except Exception as ex:
            if conn: conn.rollback()
            messagebox.showerror("Error", f"Error Saving Bill: {str(ex)}")
        finally:
            if conn: conn.close()

    def clear_all(self):
        self.cart_list = []
        self.var_cname.set("")
        self.var_ccontact.set("")
        self.var_total_bill.set(0.0)
        self.bill_no = ""
        self.lbl_amnt.config(text="Total: 0.00 PHP")
        self.clear_product_input()
        self.CartTable.delete(*self.CartTable.get_children())
        self.txt_bill_area.delete('1.0', END)
        self.calc_input.delete(0, END)

    # --- Calculator Logic ---
    def btn_click(self, char):
        if char == 'C':
            self.calc_input.delete(0, END)
        elif char == '=':
            try:
                result = str(eval(self.calc_input.get()))
                self.calc_input.delete(0, END)
                self.calc_input.insert(0, result)
            except:
                self.calc_input.delete(0, END)
                self.calc_input.insert(0, "Error")
        else:
            self.calc_input.insert(END, char)

    def logout(self):
        self.root.destroy()
        # Ensure login.py exists in the same directory
        if os.path.exists("login.py"):
            subprocess.Popen([sys.executable, "login.py"])
        else:
            print("Logout successful (login.py not found)")

    def get_cashier_name(self, emp_id):
        if not emp_id:
            return "Unknown Cashier"
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
            # FIX: Added comma to make (emp_id,) a tuple
            cur.execute("SELECT FirstName, LastName FROM employees WHERE EmpID=%s AND Role='Cashier'", (emp_id,))
            result = cur.fetchone()
            if result:
                return f"{result[0]} {result[1]}"
            else:
                return "Unknown Cashier"
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
            return "Error"
        finally:
            if conn: conn.close()


if __name__ == "__main__":
    root = Tk()
    emp_id = None
    if len(sys.argv) > 1:
        try:
            emp_id = int(sys.argv[1])
        except:
            emp_id = None
    obj = CashierClass(root, emp_id)
    root.mainloop()
