from tkinter import *
from tkinter import ttk, messagebox
import os
import re
from datetime import datetime, date, timedelta


def sale_form(window):

    saleFrame = Frame(window, width=1400, height=608, bg="#e9e6d5")
    saleFrame.place(x=200, y=150)

    header = Label(saleFrame, text="Sales & Receipts Viewer", font=('Garamond', 16, 'bold'), bg="#e9e6d5", fg="#0a3e34")
    header.place(x=0, y=0, relwidth=1, height=40)

    back_btn = Button(saleFrame, text="Back", font=('Garamond', 10, 'bold'), cursor='hand2', command=lambda: saleFrame.place_forget(), bg="#e9e6d5", fg="#0a3e34")
    back_btn.place(x=10, y=50)

    filter_frame = Frame(saleFrame, bg="#e9e6d5")
    filter_frame.place(x=100, y=45, width=900, height=40)

    total_label = Label(saleFrame, text="Total: ₱0.00", font=('Garamond', 14, 'bold'), bg="#e9e6d5", fg="#0a3e34")
    total_label.place(x=1050, y=50)

    list_frame = Frame(saleFrame, bg="white", bd=2, relief=RIDGE)
    list_frame.place(x=10, y=100, width=900, height=480)

    detail_frame = Frame(saleFrame, bg="white", bd=2, relief=RIDGE)
    detail_frame.place(x=930, y=100, width=450, height=480)

    scrolly = ttk.Scrollbar(list_frame, orient="vertical")
    scrollx = ttk.Scrollbar(list_frame, orient="horizontal")

    tree = ttk.Treeview(list_frame, columns=("bill","date","time","cashier","customer","total"), show="headings", yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
    tree.pack(fill=BOTH, expand=True)

    scrolly.config(command=tree.yview)
    scrollx.config(command=tree.xview)

    tree.heading("bill", text="Bill No")
    tree.heading("date", text="Date")
    tree.heading("time", text="Time")
    tree.heading("cashier", text="Cashier")
    tree.heading("customer", text="Customer")
    tree.heading("total", text="Total")

    tree.column("bill", width=80)
    tree.column("date", width=100)
    tree.column("time", width=80)
    tree.column("cashier", width=140)
    tree.column("customer", width=140)
    tree.column("total", width=100)

    receipt_text = Text(detail_frame, font=("courier new", 10))
    receipt_text.pack(fill=BOTH, expand=True)
    period_var = StringVar(value="all")

    def parse_receipt(path):
        try:
            with open(path, "r") as f:
                content = f.read()
            bill = None
            m = re.search(r"Bill No\s*:\s*(\d+)", content)
            if m:
                bill = m.group(1)
            dt = None
            tm = None
            m = re.search(r"Date\s*:\s*([0-9]{2}/[0-9]{2}/[0-9]{4}).*?Time:\s*([0-9]{2}:[0-9]{2}:[0-9]{2})", content, re.S)
            if m:
                dt = m.group(1)
                tm = m.group(2)
            cashier = ""
            m = re.search(r"Cashier\s*:\s*(.+)", content)
            if m:
                cashier = m.group(1).strip()
            customer = ""
            m = re.search(r"Customer\s*:\s*(.+)", content)
            if m:
                customer = m.group(1).strip()
            total = 0.0
            m = re.search(r"Total Amount:[^\n]*PHP\s*([0-9]+(?:\.[0-9]+)?)", content)
            if m:
                try:
                    total = float(m.group(1))
                except:
                    total = 0.0
            parsed_date = None
            if dt:
                try:
                    parsed_date = datetime.strptime(dt, "%d/%m/%Y").date()
                except:
                    parsed_date = None
            return {"bill": bill or os.path.basename(path).replace(".txt",""), "date": dt or "", "time": tm or "", "cashier": cashier, "customer": customer, "total": total, "path": path, "parsed_date": parsed_date}
        except:
            return None

    def load_receipts(period):
        tree.delete(*tree.get_children())
        total_sum = 0.0
        today = date.today()
        start = None
        end = None
        if period == "daily":
            start = today
            end = today
        elif period == "weekly":
            start = today - timedelta(days=6)
            end = today
        elif period == "monthly":
            start = today.replace(day=1)
            end = today
        elif period == "yearly":
            start = date(today.year, 1, 1)
            end = today
        receipts = []
        if os.path.isdir("bills"):
            for fname in os.listdir("bills"):
                if fname.endswith(".txt"):
                    info = parse_receipt(os.path.join("bills", fname))
                    if info:
                        d = info["parsed_date"]
                        if start and end:
                            if not d or d < start or d > end:
                                continue
                        receipts.append(info)
        receipts.sort(key=lambda r: (r["parsed_date"] or date(1970,1,1), r["time"]))
        for r in receipts:
            total_sum += r["total"]
            tree.insert("", END, values=(r["bill"], r["date"], r["time"], r["cashier"], r["customer"], f"₱{r['total']:,.2f}"))
        total_label.config(text=f"Total: ₱{total_sum:,.2f}")

    def on_select(ev):
        f = tree.focus()
        vals = tree.item(f, "values")
        if not vals:
            return
        bill = vals[0]
        path = None
        bp = os.path.join("bills", f"{bill}.txt")
        if os.path.exists(bp):
            path = bp
        else:
            for fname in os.listdir("bills"):
                if fname.endswith(".txt") and fname.startswith(str(bill)):
                    path = os.path.join("bills", fname)
                    break
        receipt_text.delete("1.0", END)
        if path and os.path.exists(path):
            with open(path, "r") as f:
                receipt_text.insert(END, f.read())
    tree.bind("<<TreeviewSelect>>", on_select)

    def set_period(p):
        period_var.set(p)
        load_receipts(p)

    btn_all = Button(filter_frame, text="All", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white", command=lambda: set_period("all"), width=10)
    btn_daily = Button(filter_frame, text="Daily", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white", command=lambda: set_period("daily"), width=10)
    btn_weekly = Button(filter_frame, text="Weekly", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white", command=lambda: set_period("weekly"), width=10)
    btn_monthly = Button(filter_frame, text="Monthly", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white", command=lambda: set_period("monthly"), width=10)
    btn_yearly = Button(filter_frame, text="Yearly", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white", command=lambda: set_period("yearly"), width=10)

    btn_all.pack(side=LEFT, padx=5)
    btn_daily.pack(side=LEFT, padx=5)
    btn_weekly.pack(side=LEFT, padx=5)
    btn_monthly.pack(side=LEFT, padx=5)
    btn_yearly.pack(side=LEFT, padx=5)

    
    load_receipts("all")

