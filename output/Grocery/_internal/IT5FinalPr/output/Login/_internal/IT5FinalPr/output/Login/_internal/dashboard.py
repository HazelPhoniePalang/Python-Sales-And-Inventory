import subprocess
import sys
from datetime import date, datetime
from tkinter import *
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

# Resolve admin identity from argv
emp_id = None
if len(sys.argv) > 1:
    try:
        emp_id = int(sys.argv[1])
    except:
        emp_id = None
admin_name = get_admin_name(emp_id)

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
    window.destroy()
    subprocess.Popen([sys.executable, "login.py"])

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


update_time()
update_dashboard_stats()
refresh_graph()

window.mainloop()
