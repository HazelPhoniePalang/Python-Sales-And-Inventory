import random
# from tkinter import
from datetime import date, datetime
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from employee import employee_form
from Product import product_form
from supplier import supplier_form
from Sales import sale_form
import mysql.connector
import os
from datetime import timedelta


#Functionality
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="grocery"
    )

def get_admin_name(emp_id):
    if not emp_id:
        return "Unknown Admin"
    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT FirstName, LastName FROM Employees WHERE EmpID=%s AND Role='Admin'", (emp_id,))
        res = cur.fetchone()
        if res:
            return f"{res[0]} {res[1]}"
        return "Unknown Admin"
    except mysql.connector.Error:
        return "Error"
    finally:
        if conn: conn.close()

emp_id = None
admin_name = "Unknown Admin"

login_root = None
emailEntry = None
PassEntry = None

class CashierClass:
    def __init__(self, root, emp_id):
        self.root = root
        self.root.geometry("1500x768+10+5")
        self.root.title("Grocery Cashier System")
        self.root.config(bg='white')
        self.root.resizable(False, False)

        self.emp_id = emp_id
        self.cashier_name = self.get_cashier_name(self.emp_id)

        self.var_pid = StringVar()
        self.var_pname = StringVar()
        self.var_price = DoubleVar()
        self.var_qty = IntVar()
        self.var_stock = StringVar()
        self.var_search = StringVar()
        self.var_cname = StringVar()
        self.var_ccontact = StringVar()
        self.cart_list = []
        self.var_total_bill = DoubleVar()
        self.var_total_bill.set(0.0)
        self.bill_no = ""

        titleLabel = Label(self.root, text="Grocery Sales & Inventory Management System",
                           font=('Garamond', 25, 'bold'), fg="white", bg="#0a3e34",
                           anchor='center', padx=10, pady=10)
        titleLabel.place(x=0, y=0, height=100, relwidth=1)
        self.subLabel = Label(self.root, text="", font=('Garamond', 12, 'bold'), bg="#e9e6d5", fg="#0a3e34")
        self.subLabel.place(x=0, y=100, height=30, relwidth=1)
        self.update_time()

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

        self.middleFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.middleFrame.place(x=470, y=140, width=520, height=610)

        lbl_m_title = Label(self.middleFrame, text="Customer Details", font=("Garamond", 15, "bold"),
                            bg="#0a3e34", fg="white")
        lbl_m_title.pack(side=TOP, fill=X)

        cust_frame = Frame(self.middleFrame, bg="white")
        cust_frame.pack(fill=X, pady=5)

        Label(cust_frame, text="Name:", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=0, padx=5, sticky=W)
        Entry(cust_frame, textvariable=self.var_cname, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=0, column=1, padx=5)

        Label(cust_frame, text="Contact:", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=2, padx=5, sticky=W)
        Entry(cust_frame, textvariable=self.var_ccontact, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=0, column=3, padx=5)

        calc_cart_frame = Frame(self.middleFrame, bg="white")
        calc_cart_frame.pack(fill=BOTH, expand=True, pady=5)
        self.calc_frame = Frame(calc_cart_frame, bd=2, relief=RIDGE, bg="#e9e6d5")
        self.calc_frame.place(x=5, y=0, width=240, height=270)
        self.calc_input = Entry(self.calc_frame, font=('Garamond', 15, 'bold'), width=18, justify=RIGHT)
        self.calc_input.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        btn_list = ['7', '8', '9', '+', '4', '5', '6', '-', '1', '2', '3', '*', 'C', '0', '=', '/']
        r = 1
        c = 0
        for b in btn_list:
            cmd = lambda x=b: self.btn_click(x)
            Button(self.calc_frame, text=b, command=cmd, font=('Garamond', 12, 'bold'), width=4, height=2).grid(row=r, column=c, padx=2, pady=2)
            c += 1
            if c > 3:
                c = 0
                r += 1
        cart_frame = Frame(calc_cart_frame, bd=2, relief=RIDGE, bg="white")
        cart_frame.place(x=250, y=0, width=260, height=270)
        lbl_cart = Label(cart_frame, text="Cart / Purchase List", font=("Garamond", 12, "bold"), bg="#0a3e34", fg="white")
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
        prod_select_frame = Frame(self.middleFrame, bd=2, relief=RIDGE, bg="white")
        prod_select_frame.pack(side=BOTTOM, fill=X, pady=5)
        Label(prod_select_frame, text="Product Name", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=0, padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_pname, font=("Garamond", 10), bg="#e9e6d5", state='readonly', width=20).grid(row=0, column=1, padx=5, pady=2)
        Label(prod_select_frame, text="Price (PHP)", font=("Garamond", 10, "bold"), bg="white").grid(row=1, column=0, padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_price, font=("Garamond", 10), bg="#e9e6d5", state='readonly', width=20).grid(row=1, column=1, padx=5, pady=2)
        Label(prod_select_frame, text="Quantity", font=("Garamond", 10, "bold"), bg="white").grid(row=2, column=0, padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_qty, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=2, column=1, padx=5, pady=2)
        Label(prod_select_frame, text="Stock Avail.", font=("Garamond", 10, "bold"), bg="white").grid(row=3, column=0, padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_stock, font=("Garamond", 10), bg="#e9e6d5", state='readonly', width=20).grid(row=3, column=1, padx=5, pady=2)
        btn_prod_frame = Frame(prod_select_frame, bg="white")
        btn_prod_frame.grid(row=0, column=2, rowspan=4, padx=10)
        Button(btn_prod_frame, text="Add to Cart", command=self.add_cart, font=("Garamond", 12, "bold"), bg="#0a3e34", fg="white", width=12, height=2).pack(pady=2)
        Button(btn_prod_frame, text="Clear", command=self.clear_product_input, font=("Garamond", 12, "bold"), bg="#555", fg="white", width=12).pack(pady=2)
        lbl_inst = Label(self.middleFrame, text="Note: Select product from Left Table", font=("Garamond", 9), fg="red", bg="white")
        lbl_inst.pack(side=BOTTOM)
        self.rightFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.rightFrame.place(x=1000, y=140, width=480, height=610)
        lbl_r_title = Label(self.rightFrame, text="Customer Receipt", font=("Garamond", 15, "bold"),
                            bg="#0a3e34", fg="white")
        lbl_r_title.pack(side=TOP, fill=X)
        self.txt_bill_area = Text(self.rightFrame, font=("courier new", 10))
        self.txt_bill_area.pack(fill=BOTH, expand=1)
        btn_bill_frame = Frame(self.rightFrame, bg="white")
        btn_bill_frame.pack(side=BOTTOM, fill=X)
        self.lbl_amnt = Label(btn_bill_frame, text="Total: 0.00 PHP", font=("Garamond", 14, "bold"), bg="white", fg="#0a3e34")
        self.lbl_amnt.pack(fill=X, pady=5)
        Button(btn_bill_frame, text="Generate Bill", command=self.generate_bill, bg="#0a3e34", fg="white", font=("Garamond", 12, "bold"), width=15).pack(side=LEFT, padx=5, pady=10)
        Button(btn_bill_frame, text="Print & Save", command=self.print_bill, bg="#2196F3", fg="white", font=("Garamond", 12, "bold"), width=15).pack(side=LEFT, padx=5, pady=10)
        Button(btn_bill_frame, text="Clear All", command=self.clear_all, bg="#f44336", fg="white", font=("Garamond", 12, "bold"), width=10).pack(side=LEFT, padx=5, pady=10)
        self.fetch_products()
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
            cur.execute("SELECT PrID, PrName, Price, Quantity, Availability FROM Product WHERE IsArchived=0 AND Availability='Available' AND Quantity > 0")
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
            cur.execute("SELECT PrID, PrName, Price, Quantity, Availability FROM Product WHERE PrName LIKE %s AND IsArchived=0 AND Quantity > 0", ('%' + self.var_search.get() + '%',))
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
        for item in self.cart_list:
            if item[0] == self.var_pid.get():
                messagebox.showerror("Error", "Product already in cart. Remove it to update quantity.")
                return
        total_price = price * qty
        self.cart_list.append([self.var_pid.get(), self.var_pname.get(), price, qty, total_price])
        self.CartTable.insert("", END, values=(self.var_pname.get(), price, qty))
        self.update_total_bill()
        self.clear_product_input()
        messagebox.showinfo("Success", "Item Added to Cart")
    def get_cart_data(self, ev):
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
        if not os.path.exists("bills"):
            os.mkdir("bills")
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
            for item in self.cart_list:
                pid = item[0]
                qty_sold = item[3]
                cur.execute("SELECT Quantity FROM Product WHERE PrID=%s", (pid,))
                res = cur.fetchone()
                if res:
                    current_stock = res[0]
                    new_stock = current_stock - qty_sold
                    status = "Available"
                    if new_stock <= 0:
                        new_stock = 0
                        status = "Out of Stock"
                    cur.execute("UPDATE Product SET Quantity=%s, Availability=%s WHERE PrID=%s", (new_stock, status, pid))
            conn.commit()
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
        show_login()
    def get_cashier_name(self, emp_id):
        if not emp_id:
            return "Unknown Cashier"
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
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
emp_id = None
admin_name = "Unknown Admin"

login_root = None
emailEntry = None
PassEntry = None

class CashierClass:
    def __init__(self, root, emp_id):
        self.root = root
        self.root.geometry("1500x768+10+5")
        self.root.title("Grocery Cashier System")
        self.root.config(bg='white')
        self.root.resizable(False, False)

        self.emp_id = emp_id
        self.cashier_name = self.get_cashier_name(self.emp_id)

        self.var_pid = StringVar()
        self.var_pname = StringVar()
        self.var_price = DoubleVar()
        self.var_qty = IntVar()
        self.var_stock = StringVar()
        self.var_search = StringVar()
        self.var_cname = StringVar()
        self.var_ccontact = StringVar()
        self.cart_list = []
        self.var_total_bill = DoubleVar()
        self.var_total_bill.set(0.0)
        self.bill_no = ""

        titleLabel = Label(self.root, text="Grocery Sales & Inventory Management System",
                           font=('Garamond', 25, 'bold'), fg="white", bg="#0a3e34",
                           anchor='center', padx=10, pady=10)
        titleLabel.place(x=0, y=0, height=100, relwidth=1)
        self.subLabel = Label(self.root, text="", font=('Garamond', 12, 'bold'), bg="#e9e6d5", fg="#0a3e34")
        self.subLabel.place(x=0, y=100, height=30, relwidth=1)
        self.update_time()

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

        self.middleFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.middleFrame.place(x=470, y=140, width=520, height=610)

        lbl_m_title = Label(self.middleFrame, text="Customer Details", font=("Garamond", 15, "bold"),
                            bg="#0a3e34", fg="white")
        lbl_m_title.pack(side=TOP, fill=X)

        cust_frame = Frame(self.middleFrame, bg="white")
        cust_frame.pack(fill=X, pady=5)

        Label(cust_frame, text="Name:", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=0, padx=5, sticky=W)
        Entry(cust_frame, textvariable=self.var_cname, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=0, column=1, padx=5)

        Label(cust_frame, text="Contact:", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=2, padx=5, sticky=W)
        Entry(cust_frame, textvariable=self.var_ccontact, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=0, column=3, padx=5)

        calc_cart_frame = Frame(self.middleFrame, bg="white")
        calc_cart_frame.pack(fill=BOTH, expand=True, pady=5)
        self.calc_frame = Frame(calc_cart_frame, bd=2, relief=RIDGE, bg="#e9e6d5")
        self.calc_frame.place(x=5, y=0, width=240, height=270)
        self.calc_input = Entry(self.calc_frame, font=('Garamond', 15, 'bold'), width=18, justify=RIGHT)
        self.calc_input.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        btn_list = ['7', '8', '9', '+', '4', '5', '6', '-', '1', '2', '3', '*', 'C', '0', '=', '/']
        r = 1
        c = 0
        for b in btn_list:
            cmd = lambda x=b: self.btn_click(x)
            Button(self.calc_frame, text=b, command=cmd, font=('Garamond', 12, 'bold'), width=4, height=2).grid(row=r, column=c, padx=2, pady=2)
            c += 1
            if c > 3:
                c = 0
                r += 1
        cart_frame = Frame(calc_cart_frame, bd=2, relief=RIDGE, bg="white")
        cart_frame.place(x=250, y=0, width=260, height=270)
        lbl_cart = Label(cart_frame, text="Cart / Purchase List", font=("Garamond", 12, "bold"), bg="#0a3e34", fg="white")
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
        prod_select_frame = Frame(self.middleFrame, bd=2, relief=RIDGE, bg="white")
        prod_select_frame.pack(side=BOTTOM, fill=X, pady=5)
        Label(prod_select_frame, text="Product Name", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=0, padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_pname, font=("Garamond", 10), bg="#e9e6d5", state='readonly', width=20).grid(row=0, column=1, padx=5, pady=2)
        Label(prod_select_frame, text="Price (PHP)", font=("Garamond", 10, "bold"), bg="white").grid(row=1, column=0, padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_price, font=("Garamond", 10), bg="#e9e6d5", state='readonly', width=20).grid(row=1, column=1, padx=5, pady=2)
        Label(prod_select_frame, text="Quantity", font=("Garamond", 10, "bold"), bg="white").grid(row=2, column=0, padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_qty, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=2, column=1, padx=5, pady=2)
        Label(prod_select_frame, text="Stock Avail.", font=("Garamond", 10, "bold"), bg="white").grid(row=3, column=0, padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_stock, font=("Garamond", 10), bg="#e9e6d5", state='readonly', width=20).grid(row=3, column=1, padx=5, pady=2)
        btn_prod_frame = Frame(prod_select_frame, bg="white")
        btn_prod_frame.grid(row=0, column=2, rowspan=4, padx=10)
        Button(btn_prod_frame, text="Add to Cart", command=self.add_cart, font=("Garamond", 12, "bold"), bg="#0a3e34", fg="white", width=12, height=2).pack(pady=2)
        Button(btn_prod_frame, text="Clear", command=self.clear_product_input, font=("Garamond", 12, "bold"), bg="#555", fg="white", width=12).pack(pady=2)
        lbl_inst = Label(self.middleFrame, text="Note: Select product from Left Table", font=("Garamond", 9), fg="red", bg="white")
        lbl_inst.pack(side=BOTTOM)
        self.rightFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.rightFrame.place(x=1000, y=140, width=480, height=610)
        lbl_r_title = Label(self.rightFrame, text="Customer Receipt", font=("Garamond", 15, "bold"),
                            bg="#0a3e34", fg="white")
        lbl_r_title.pack(side=TOP, fill=X)
        self.txt_bill_area = Text(self.rightFrame, font=("courier new", 10))
        self.txt_bill_area.pack(fill=BOTH, expand=1)
        btn_bill_frame = Frame(self.rightFrame, bg="white")
        btn_bill_frame.pack(side=BOTTOM, fill=X)
        self.lbl_amnt = Label(btn_bill_frame, text="Total: 0.00 PHP", font=("Garamond", 14, "bold"), bg="white", fg="#0a3e34")
        self.lbl_amnt.pack(fill=X, pady=5)
        Button(btn_bill_frame, text="Generate Bill", command=self.generate_bill, bg="#0a3e34", fg="white", font=("Garamond", 12, "bold"), width=15).pack(side=LEFT, padx=5, pady=10)
        Button(btn_bill_frame, text="Print & Save", command=self.print_bill, bg="#2196F3", fg="white", font=("Garamond", 12, "bold"), width=15).pack(side=LEFT, padx=5, pady=10)
        Button(btn_bill_frame, text="Clear All", command=self.clear_all, bg="#f44336", fg="white", font=("Garamond", 12, "bold"), width=10).pack(side=LEFT, padx=5, pady=10)
        self.fetch_products()
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
            cur.execute("SELECT PrID, PrName, Price, Quantity, Availability FROM Product WHERE IsArchived=0 AND Availability='Available' AND Quantity > 0")
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
            cur.execute("SELECT PrID, PrName, Price, Quantity, Availability FROM Product WHERE PrName LIKE %s AND IsArchived=0 AND Quantity > 0", ('%' + self.var_search.get() + '%',))
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
        for item in self.cart_list:
            if item[0] == self.var_pid.get():
                messagebox.showerror("Error", "Product already in cart. Remove it to update quantity.")
                return
        total_price = price * qty
        self.cart_list.append([self.var_pid.get(), self.var_pname.get(), price, qty, total_price])
        self.CartTable.insert("", END, values=(self.var_pname.get(), price, qty))
        self.update_total_bill()
        self.clear_product_input()
        messagebox.showinfo("Success", "Item Added to Cart")
    def get_cart_data(self, ev):
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
        if not os.path.exists("bills"):
            os.mkdir("bills")
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
            for item in self.cart_list:
                pid = item[0]
                qty_sold = item[3]
                cur.execute("SELECT Quantity FROM Product WHERE PrID=%s", (pid,))
                res = cur.fetchone()
                if res:
                    current_stock = res[0]
                    new_stock = current_stock - qty_sold
                    status = "Available"
                    if new_stock <= 0:
                        new_stock = 0
                        status = "Out of Stock"
                    cur.execute("UPDATE Product SET Quantity=%s, Availability=%s WHERE PrID=%s", (new_stock, status, pid))
            conn.commit()
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
        show_login()
    def get_cashier_name(self, emp_id):
        if not emp_id:
            return "Unknown Cashier"
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
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
            emp = result[0]
            role = result[1].lower()
            messagebox.showinfo("Success", f"Login Successful as {role.capitalize()}")
            try:
                login_root.destroy()
            except:
                pass
            if role == "admin":
                global emp_id, admin_name
                emp_id = emp
                admin_name = get_admin_name(emp_id)
                try:
                    window.deiconify()
                except:
                    pass
            elif role == "cashier":
                top = Toplevel(window)
                CashierClass(top, emp)
            else:
                messagebox.showerror("Error", "User role not recognized")
        else:
            messagebox.showerror("Error", "Invalid email or password")
        cursor.close()
        db.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))

def show_login():
    global login_root, emailEntry, PassEntry
    login_root = Toplevel(window)
    login_root.title("Login")
    login_root.geometry("450x350+550+100")
    login_root.resizable(0, 0)
    login_root.config(bg="#f3f1e8")
    loginLabel = Label(login_root, text="Welcome back", font=('Garamond', 20, 'bold'),
                       fg="#0a3e34", bg="#f3f1e8")
    loginLabel.place(x=140, y=40)
    Emaillabel = Label(login_root, text="Email:", font=('Garamond', 13, 'bold'),
                       bg="#f3f1e8", fg="#0a3e34")
    Emaillabel.place(x=72, y=115)
    emailEntry = Entry(login_root, width=40)
    emailEntry.place(x=128, y=118)
    Passlabel = Label(login_root, text="Password:", font=('Garamond', 13, 'bold'),
                      bg="#f3f1e8", fg="#0a3e34")
    Passlabel.place(x=72, y=185)
    PassEntry = Entry(login_root, show='*', width=36)
    PassEntry.place(x=155, y=188)
    loginBTN = Button(
        login_root,
        text="Login",
        font=('Garamond', 10, 'bold'),
        fg='#0a3e34',
        bg='#e9e6d5',
        width=10,
        height=1,
        command=login_user)
    loginBTN.place(x=190, y=260)
def update_dashboard_stats():
    emp_total = 0
    pr_total = 0
    sup_total = 0
    sales_total = 0.0

    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM employees WHERE Archived=0")
        emp_total = cur.fetchone()[0] or 0

        cur.execute("SELECT COUNT(*) FROM Product WHERE IsArchived=0")
        pr_total = cur.fetchone()[0] or 0

        cur.execute("SELECT COUNT(*) FROM Supplier WHERE IsArchived=0")
        sup_total = cur.fetchone()[0] or 0
    except mysql.connector.Error:
        pass
    finally:
        if conn: conn.close()

    try:
        if os.path.isdir("bills"):
            for fname in os.listdir("bills"):
                if not fname.endswith(".txt"):
                    continue
                try:
                    with open(os.path.join("bills", fname), "r") as f:
                        content = f.read()
                    marker = " Total Amount:"
                    if marker in content:
                        tail = content.split(marker, 1)[1]
                        # Expect format like "\t\t\t\tPHP 123.45"
                        amount_str = ""
                        for ch in tail:
                            if ch.isdigit() or ch in ".":
                                amount_str += ch
                            elif amount_str:
                                break
                        if amount_str:
                            sales_total += float(amount_str)
                except:
                    continue
    except:
        pass

    try:
        emp_value.config(text=str(emp_total))
        pr_value.config(text=str(pr_total))
        sup_value.config(text=str(sup_total))
        sl_value.config(text=f"₱{sales_total:,.2f}")
    except:
        pass

def collect_sales_by_date():
    result = {}
    try:
        if os.path.isdir("bills"):
            for fname in os.listdir("bills"):
                if not fname.endswith(".txt"):
                    continue
                try:
                    with open(os.path.join("bills", fname), "r") as f:
                        content = f.read()
                    # Parse date and total
                    # Date    : dd/mm/YYYY  Time: HH:MM:SS
                    date_str = None
                    total_val = None
                    # Extract date
                    try:
                        parts = content.split("Date")
                        if len(parts) > 1:
                            line = parts[1]
                            # line like "    : 12/12/2025  Time: 10:20:30"
                            segs = line.split(":")
                            if len(segs) >= 2:
                                ds = segs[1].strip().split("  ")[0].strip()
                                date_str = ds
                    except:
                        date_str = None
                    # Extract total
                    try:
                        marker = " Total Amount:"
                        if marker in content:
                            tail = content.split(marker, 1)[1]
                            amt = ""
                            for ch in tail:
                                if ch.isdigit() or ch in ".":
                                    amt += ch
                                elif amt:
                                    break
                            if amt:
                                total_val = float(amt)
                    except:
                        total_val = None
                    if date_str and total_val is not None:
                        # normalize to yyyy-mm-dd
                        try:
                            d = datetime.strptime(date_str, "%d/%m/%Y").date()
                            key = d.isoformat()
                            result[key] = result.get(key, 0.0) + total_val
                        except:
                            pass
                except:
                    continue
    except:
        pass
    return result

def collect_sales_by_cashier(since_date=None):
    totals = {}
    try:
        if os.path.isdir("bills"):
            for fname in os.listdir("bills"):
                if not fname.endswith(".txt"):
                    continue
                try:
                    with open(os.path.join("bills", fname), "r") as f:
                        content = f.read()
                    # Extract cashier
                    cashier = None
                    bill_date = None
                    try:
                        for line in content.splitlines():
                            if "Cashier" in line:
                                parts = line.split(":")
                                if len(parts) >= 2:
                                    name = parts[1].strip()
                                    if name:
                                        cashier = name
                                        break
                    except:
                        cashier = None
                    # Extract date (dd/mm/YYYY)
                    try:
                        for line in content.splitlines():
                            if "Date" in line and "Time" in line:
                                segs = line.split(":")
                                if len(segs) >= 2:
                                    ds = segs[1].strip().split("  ")[0].strip()
                                    bill_date = datetime.strptime(ds, "%d/%m/%Y").date()
                                    break
                    except:
                        bill_date = None
                    # Extract total
                    total_val = None
                    try:
                        marker = " Total Amount:"
                        if marker in content:
                            tail = content.split(marker, 1)[1]
                            amt = ""
                            for ch in tail:
                                if ch.isdigit() or ch in ".":
                                    amt += ch
                                elif amt:
                                    break
                            if amt:
                                total_val = float(amt)
                    except:
                        total_val = None
                    if cashier and total_val is not None:
                        if since_date and bill_date:
                            if bill_date < since_date:
                                continue
                        totals[cashier] = totals.get(cashier, 0.0) + total_val
                except:
                    continue
    except:
        pass
    return totals

def draw_sales_graph(canvas, period_days=30):
    canvas.delete("all")
    data_map = collect_sales_by_date()
    today = date.today()
    days = [today - timedelta(days=i) for i in range(period_days-1, -1, -1)]
    labels = [d.isoformat() for d in days]
    values = [data_map.get(l, 0.0) for l in labels]
    w = int(canvas["width"])
    h = int(canvas["height"])
    pad_left = 50
    pad_bottom = 30
    pad_top = 20
    pad_right = 10
    gx0 = pad_left
    gy0 = pad_top
    gx1 = w - pad_right
    gy1 = h - pad_bottom
    canvas.create_rectangle(gx0, gy0, gx1, gy1, outline="#cccccc")
    max_val = max(values) if values else 0.0
    
    if max_val <= 0:
        canvas.create_text((w//2), (h//2), text="No sales data", fill="#0a3e34", font=("Garamond", 12, "bold"))
        return
    bar_count = len(values)
    bar_space = (gx1 - gx0) / bar_count
    bar_w = max(2, bar_space * 0.6)
    for i, v in enumerate(values):
        x_center = gx0 + i * bar_space + bar_space / 2
        bar_h = 0
        try:
            bar_h = (v / max_val) * (gy1 - gy0)
        except:
            bar_h = 0
        x0 = x_center - bar_w / 2
        y0 = gy1 - bar_h
        x1 = x_center + bar_w / 2
        y1 = gy1
        canvas.create_rectangle(x0, y0, x1, y1, fill="#0a3e34", outline="")
        if i % 5 == 0:
            canvas.create_text(x_center, gy1 + 12, text=days[i].strftime("%m-%d"), fill="#555555", font=("Garamond", 8))
    # y-axis labels
    canvas.create_text(pad_left - 10, gy1, text="0", fill="#555555", font=("Garamond", 8), anchor="e")
    canvas.create_text(pad_left - 10, (gy0 + gy1)//2, text=f"{max_val/2:,.0f}", fill="#555555", font=("Garamond", 8), anchor="e")
    canvas.create_text(pad_left - 10, gy0, text=f"{max_val:,.0f}", fill="#555555", font=("Garamond", 8), anchor="e")

def draw_cashier_graph(canvas, since_date=None):
    canvas.delete("all")
    data_map = collect_sales_by_cashier(since_date=since_date)
    # Sort cashiers by total sales descending
    items = sorted(data_map.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in items]
    values = [v for _, v in items]
    w = int(canvas["width"])
    h = int(canvas["height"])
    pad_left = 60
    pad_bottom = 50
    pad_top = 20
    pad_right = 10
    gx0 = pad_left
    gy0 = pad_top
    gx1 = w - pad_right
    gy1 = h - pad_bottom
    canvas.create_rectangle(gx0, gy0, gx1, gy1, outline="#cccccc")
    max_val = max(values) if values else 0.0
    if not items or max_val <= 0:
        canvas.create_text((w//2), (h//2), text="No cashier sales data", fill="#0a3e34", font=("Garamond", 12, "bold"))
        return
    bar_count = len(values)
    bar_space = (gx1 - gx0) / bar_count
    bar_w = max(8, bar_space * 0.6)
    # store bar hit regions for hover tooltips
    canvas._bar_hits = []
    for i, v in enumerate(values):
        x_center = gx0 + i * bar_space + bar_space / 2
        bar_h = 0
        try:
            bar_h = (v / max_val) * (gy1 - gy0)
        except:
            bar_h = 0
        x0 = x_center - bar_w / 2
        y0 = gy1 - bar_h
        x1 = x_center + bar_w / 2
        y1 = gy1
        canvas.create_rectangle(x0, y0, x1, y1, fill="#0a3e34", outline="")
        # amount label above bar
        canvas.create_text(x_center, y0 - 12, text=f"₱{v:,.0f}", fill="#333333", font=("Garamond", 9, "bold"))
        # cashier label on x-axis, allow short multiline if long
        name = labels[i]
        if len(name) > 14:
            name = name[:14] + "…"
        canvas.create_text(x_center, gy1 + 20, text=name, fill="#555555", font=("Garamond", 9), anchor="n")
        canvas._bar_hits.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "label": labels[i], "value": v})

def _canvas_hover_tooltip(event):
    canvas = event.widget
    hits = getattr(canvas, "_bar_hits", [])
    # Clear previous tooltip
    if getattr(canvas, "_tooltip_id", None):
        try:
            canvas.delete(canvas._tooltip_id)
        except:
            pass
        canvas._tooltip_id = None
    x, y = event.x, event.y
    for item in hits:
        if item["x0"] <= x <= item["x1"] and item["y0"] <= y <= item["y1"]:
            text = f'{item["label"]}: ₱{item["value"]:,.2f}'
            canvas._tooltip_id = canvas.create_text(x + 10, y - 10, text=text, fill="#0a3e34", font=("Garamond", 9, "bold"), anchor="nw")
            break

def _canvas_hover_leave(event):
    canvas = event.widget
    if getattr(canvas, "_tooltip_id", None):
        try:
            canvas.delete(canvas._tooltip_id)
        except:
            pass
        canvas._tooltip_id = None

#GUI
window =Tk()

window.title("Dashboard")
window.geometry("1500x768+10+5")
window.resizable(0,0)
window.config(bg='#e9e6d5')

titleLabel = Label(window,
                   compound="left",
                   text="Grocery Sales & Inventory Management System",
                   font=('Garamond', 25, 'bold'),
                   fg="white",
                   bg="#27693f",
                   anchor='center',
                   padx=10, pady=10)

titleLabel.place(x=0, y=0, height=150,relwidth= 1)

def logout():
    try:
        window.destroy()
    except:
        pass
    show_login()

logout = Button(
    window,
    text="Logout",
    font=('Garamond', 20, 'bold'),
    fg='#0a3e34',
    bg='#e9e6d5',
    command=logout
)

logout.place(x=1230, y=40)

def _apply_button_hover(btn):
    def on_enter(_e):
        try:
            btn.config(bg='#dcd8c6', cursor='hand2')
        except:
            pass
    def on_leave(_e):
        try:
            btn.config(bg='#e9e6d5', cursor='')
        except:
            pass
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
_apply_button_hover(logout)

def update_time():
    current_date = date.today().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    subLabel.config(text=f"Welcome: {admin_name}      Date: {current_date}      Time: {current_time}", bg="#e9e6d5", fg="#0a3e34")
    subLabel.after(1000, update_time)

subLabel = Label(
    window,
    text="Loading...",
    font=('Garamond', 12, 'bold')
)
subLabel.place(x=0, y=125, relwidth= 1)

leftFrame = Frame(window, background='#27693f')
leftFrame.place(x=0, y=150, width=200 ,height=620)

menuLabel = Label(leftFrame,text = 'Menu',
                 font= ('Garamond', 20, 'bold'),bg ='#27693f', fg = '#e9e6d5')
menuLabel.pack(fill=X, padx=0, pady=10)


#Employee board
employee_btn = Button(leftFrame, text = 'Employee',
                    font = ('Garamond', 15, 'bold'),
                      fg='#0a3e34',
                      bg='#e9e6d5',
                      width= 15,
                      height= 1,
                      command=lambda:employee_form(window))
employee_btn.pack(padx=0,
                  pady=5)
_apply_button_hover(employee_btn)


sup_btn = Button(leftFrame, text = 'Supplier',
                 font = ('Garamond', 15, 'bold'),
                    fg='#0a3e34',
                    bg='#e9e6d5',
                    width= 15,
                    height= 1,
                    command=lambda:supplier_form(window))
sup_btn.pack(padx=0,
             pady=5)
_apply_button_hover(sup_btn)


pr_btn = Button(leftFrame, text = 'Product',
                 font = ('Garamond', 15, 'bold'),
                    fg='#0a3e34',
                    bg='#e9e6d5',
                    width=15,
                    height=1,
                    command=lambda:product_form(window))
pr_btn.pack(padx=0,
            pady=5)
_apply_button_hover(pr_btn)


sale_btn = Button(leftFrame, text = 'Sales',
                 font = ('Garamond', 15, 'bold'),
                    fg='#0a3e34',
                    bg='#e9e6d5',
                    width=15,
                    height=1,
                    command=lambda:sale_form(window))
sale_btn.pack(padx=0,
             pady=5)
_apply_button_hover(sale_btn)

emp_Frame = Frame(window, background='#27693f',  bd=3, relief=RIDGE)
emp_Frame.place(x=220, y=185, width=300 ,height=110)

emp_title = Label(emp_Frame, text="Total Employees",
                  font=("Garamond", 18, "bold"),
                  bg="#27693f", fg="#e9e6d5")
emp_title.place(x=30, y=15)



emp_value = Label(emp_Frame, text="0",
                  font=("Garamond", 30, "bold"),
                  bg="#27693f", fg="#e9e6d5")
emp_value.place(x=120, y=55)


sup_Frame = Frame(window, background='#27693f',  bd=3, relief=RIDGE)
sup_Frame.place(x=220, y=310, width=300 ,height=110)

sup_title = Label(sup_Frame, text="Total Suppliers",
                  font=("Garamond", 18, "bold"),
                  bg="#27693f", fg="#e9e6d5")
sup_title.place(x=30, y=15)

sup_value = Label(sup_Frame, text="0",
                  font=("Garamond", 30, "bold"),
                  bg="#27693f", fg="#e9e6d5")
sup_value.place(x=120, y=55)

pr_Frame = Frame(window, background='#27693f',  bd=3, relief=RIDGE)
pr_Frame.place(x=220, y=435, width=300 ,height=110)

pr_title = Label(pr_Frame, text="Total Products",
                 font=("Garamond", 18, "bold"),
                 bg="#27693f", fg="#e9e6d5")
pr_title.place(x=30, y=15)

pr_value = Label(pr_Frame, text="0",
                 font=("Garamond", 30, "bold"),
                 bg="#27693f", fg="#e9e6d5")
pr_value.place(x=120, y=55)

sl_Frame = Frame(window, background='#27693f',  bd=3, relief=RIDGE)
sl_Frame.place(x=220, y=560, width=300 ,height=110)

sl_title = Label(sl_Frame, text="Total Sales",
                 font=("Garamond", 18, "bold"),
                 bg="#27693f", fg="#e9e6d5")
sl_title.place(x=30, y=15)

sl_value = Label(sl_Frame, text="₱0",
                 font=("Garamond", 30, "bold"),
                 bg="#27693f", fg="#e9e6d5")
sl_value.place(x=80, y=55)

# ------Sales graph area-------
graph_Frame = Frame(window, background='white', bd=3, relief=RIDGE)
graph_Frame.place(x=540, y=185, width=930 ,height=485)
graph_title = Label(graph_Frame, text="Cashier Total Sales", font=("Garamond", 14, "bold"), bg="white", fg="#0a3e34")
graph_title.place(x=10, y=10)
graph_canvas = Canvas(graph_Frame, width=910, height=420, bg="white", highlightthickness=0)
graph_canvas.place(x=10, y=40)

graph_mode_var = StringVar(value="Cashiers")
graph_period_var = StringVar(value="30 days")

def refresh_graph():
    mode = graph_mode_var.get()
    period = graph_period_var.get()
    days_map = {"7 days": 7, "30 days": 30, "90 days": 90}
    period_days = days_map.get(period, 30)
    if mode == "Cashiers":
        graph_title.config(text="Cashier Total Sales")
        since = date.today() - timedelta(days=period_days)
        draw_cashier_graph(graph_canvas, since_date=since)
    else:
        graph_title.config(text=f"Daily Sales (last {period_days} days)")
        draw_sales_graph(graph_canvas, period_days=period_days)


controls_frame = Frame(graph_Frame, bg="white")
controls_frame.place(x=540, y=8, width=500, height=28)

Label(
    controls_frame,
    text="Type:",
    font=("Garamond", 10, "bold"),
    bg="white",
    fg="#0a3e34"
).pack(side=LEFT, padx=(0,4))

mode_menu = OptionMenu(controls_frame, graph_mode_var, "Cashiers", "Daily")
mode_menu.config(
    bg="#e9e6d5",
    fg="#0a3e34",
    activebackground="#dcd8c6"
)
mode_menu.config(font=("Garamond", 10, "bold"))
mode_menu["menu"].config(font=("Garamond", 10))
mode_menu.pack(side=LEFT, padx=(0,10))

Label(
    controls_frame,
    text="Range:",
    font=("Garamond", 10, "bold"),
    bg="white",
    fg="#0a3e34"
).pack(side=LEFT, padx=(0,4))

period_menu = OptionMenu(controls_frame, graph_period_var, "7 days", "30 days", "90 days")
period_menu.config(
    bg="#e9e6d5",
    fg="#0a3e34",
    activebackground="#dcd8c6"
)
period_menu.config(font=("Garamond", 10, "bold"))
period_menu["menu"].config(font=("Garamond", 10))
period_menu.pack(side=LEFT, padx=(0,10))

refresh_btn = Button(
    controls_frame,
    text="Refresh",
    font=("Garamond", 10, "bold"),
    fg="#0a3e34",
    bg="#e9e6d5",
    command=refresh_graph
)
refresh_btn.pack(side=LEFT, padx=(5,0))


graph_canvas.bind("<Motion>", _canvas_hover_tooltip)
graph_canvas.bind("<Leave>", _canvas_hover_leave)

window.withdraw()

update_time()
update_dashboard_stats()
refresh_graph()

if __name__ == "__main__":
    show_login()
    window.mainloop()
