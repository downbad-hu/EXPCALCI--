import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime
import shutil
from hashlib import sha256
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DB_FILE = "expenses.db"
BACKUP_DIR = "backups"
CURRENCIES = {"₹": 1, "$": 83}
DEFAULT_THEME = "cosmo"

# ---------------- Database ---------------- #
def init_db():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
                 id INTEGER PRIMARY KEY, amount REAL, category TEXT, type TEXT, date TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
                 key TEXT PRIMARY KEY, value TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS goals (
                 id INTEGER PRIMARY KEY, name TEXT, target REAL, progress REAL)""")
    conn.commit()
    conn.close()

def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    res = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return res

def get_setting(key):
    r = db_query("SELECT value FROM settings WHERE key=?", (key,), True)
    return r[0][0] if r else None

def set_setting(key, val):
    db_query("INSERT OR REPLACE INTO settings VALUES(?,?)", (key, val))

def hash_pin(pin): return sha256(pin.encode()).hexdigest()

# ---------------- Transactions ---------------- #
def add_transaction(amount, cat, typ):
    db_query("INSERT INTO transactions(amount,category,type,date) VALUES(?,?,?,?)",
             (amount, cat, typ, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def fetch_transactions():
    return db_query("SELECT * FROM transactions ORDER BY date DESC", fetch=True)

def summary():
    inc = db_query("SELECT SUM(amount) FROM transactions WHERE type='income'", fetch=True)[0][0] or 0
    exp = db_query("SELECT SUM(amount) FROM transactions WHERE type='expense'", fetch=True)[0][0] or 0
    return inc, exp, inc - exp

# ---------------- Goals ---------------- #
def add_goal(name, target):
    db_query("INSERT INTO goals(name,target,progress) VALUES(?,?,?)", (name, target, 0))

def update_goal_progress(goal_id, amount):
    db_query("UPDATE goals SET progress=progress+? WHERE id=?", (amount, goal_id))

def fetch_goals():
    return db_query("SELECT * FROM goals", fetch=True)

# ---------------- Backup & Restore ---------------- #
def backup():
    f = os.path.join(BACKUP_DIR, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    shutil.copy(DB_FILE, f)
    return f

def restore(path): shutil.copy(path, DB_FILE)

# ---------------- Login ---------------- #
class LoginScreen:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.pin_hash = get_setting("pin")

        self.frame = tb.Frame(root, padding=50)
        self.frame.pack(expand=True)

        tb.Label(self.frame, text="Enter PIN", font=("Helvetica", 16)).pack(pady=10)
        self.pin_var = tk.StringVar()
        tb.Entry(self.frame, textvariable=self.pin_var, show="*", width=20).pack(pady=10)

        self.login_btn = tb.Button(self.frame, text="Login", bootstyle="success", command=self.check_pin)
        self.login_btn.pack(pady=10)

        if not self.pin_hash:
            tb.Label(self.frame, text="No PIN set. Please create one.", bootstyle="danger").pack(pady=5)
            self.set_btn = tb.Button(self.frame, text="Set PIN", bootstyle="info", command=self.set_pin)
            self.set_btn.pack(pady=5)

    def check_pin(self):
        if not self.pin_hash:
            messagebox.showerror("Error", "Please set a PIN first.")
            return

        if hash_pin(self.pin_var.get()) == self.pin_hash:
            self.frame.destroy()
            self.on_success()
        else:
            messagebox.showerror("Error", "Incorrect PIN. Try again.")

    def set_pin(self):
        pin = self.pin_var.get()
        if len(pin) >= 4:
            set_setting("pin", hash_pin(pin))
            self.pin_hash = hash_pin(pin)
            messagebox.showinfo("Success", "PIN set successfully! Now click Login.")
        else:
            messagebox.showerror("Error", "PIN must be at least 4 digits.")

# ---------------- Main App ---------------- #
class App:
    def __init__(self, root):
        self.root = root
        self.cur = tk.StringVar(value=get_setting("currency") or "₹")
        self.theme = get_setting("theme") or DEFAULT_THEME
        tb.Style(theme=self.theme)
        root.title("Expense Tracker")
        root.geometry("1280x720")

        self.notebook = tb.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.frames = {}
        tabs = [("🔥 Dashboard", "Dashboard"), ("📜 History", "History"), ("📊 Analytics", "Analytics"), ("🎯 Goals", "Goals"), ("⚙ Settings", "Settings")]
        for e, t in tabs:
            f = tb.Frame(self.notebook)
            self.notebook.add(f, text=f"{e} {t}")
            self.frames[t] = f

        self.dashboard()
        self.history()
        self.analytics()
        self.goals()
        self.settings()
        self.update_summary()
        self.load_hist()
        self.load_goals()

    # ---------- Dashboard ---------- #
    def dashboard(self):
        f = self.frames["Dashboard"]
        card_frame = tb.Frame(f)
        card_frame.pack(fill="x", pady=10)

        self.inc_card = tb.Label(card_frame, text="", font=("Helvetica", 16), bootstyle="success-inverse")
        self.inc_card.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        self.exp_card = tb.Label(card_frame, text="", font=("Helvetica", 16), bootstyle="danger-inverse")
        self.exp_card.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        self.bal_card = tb.Label(card_frame, text="", font=("Helvetica", 16), bootstyle="info-inverse")
        self.bal_card.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        tb.Label(f, text="➕ Add Transaction", font=("Helvetica", 14)).pack(pady=10)
        self.amount_var = tk.DoubleVar()
        self.category_var = tk.StringVar()
        self.type_var = tk.StringVar(value="expense")

        tb.Entry(f, textvariable=self.amount_var, width=20).pack(pady=5)
        tb.Entry(f, textvariable=self.category_var, width=20).pack(pady=5)
        tb.OptionMenu(f, self.type_var, "expense", "income").pack(pady=5)
        tb.Button(f, text="Add", bootstyle="success", command=self.add_txn).pack(pady=10)

    def add_txn(self):
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        category = self.category_var.get().strip()
        txn_type = self.type_var.get()
        if amount <= 0 or not category:
            messagebox.showerror("Error", "Please enter valid data.")
            return

        amount_inr = amount if self.cur.get() == "₹" else amount * CURRENCIES["$"]
        add_transaction(amount_inr, category, txn_type)

        self.amount_var.set(0)
        self.category_var.set("")
        self.update_summary()
        self.load_hist()
        self.load_analytics()
        messagebox.showinfo("Success", f"{txn_type.capitalize()} added successfully!")

    def update_summary(self):
        inc, exp, bal = summary()
        def fmt(x): return f"{self.cur.get()} {round(x / CURRENCIES[self.cur.get()], 2)}"
        self.inc_card.config(text=f"💰 Income\n{fmt(inc)}")
        self.exp_card.config(text=f"💸 Expense\n{fmt(exp)}")
        self.bal_card.config(text=f"📊 Balance\n{fmt(bal)}")

    # ---------- History ---------- #
    def history(self):
        f = self.frames["History"]
        self.hist = tb.Treeview(f, columns=("ID", "Amount", "Category", "Type", "Date"), show="headings", height=20)
        for col in ("ID", "Amount", "Category", "Type", "Date"):
            self.hist.heading(col, text=col)
            self.hist.column(col, width=150)
        self.hist.pack(fill="both", expand=True)
        tb.Button(f, text="Refresh", bootstyle="info", command=self.load_hist).pack(pady=5)

    def load_hist(self):
        for i in self.hist.get_children():
            self.hist.delete(i)
        for r in fetch_transactions():
            amt = f"{self.cur.get()} {round(r[1] / CURRENCIES[self.cur.get()], 2)}"
            self.hist.insert("", END, values=(r[0], amt, r[2], r[3], r[4]))

    # ---------- Analytics ---------- #
    def analytics(self):
        f = self.frames["Analytics"]
        self.chart_frame = tb.Frame(f)
        self.chart_frame.pack(fill="both", expand=True)
        self.load_analytics()

    def load_analytics(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        data = fetch_transactions()
        if not data:
            tb.Label(self.chart_frame, text="No data to show charts", font=("Helvetica", 14)).pack()
            return

        # Pie Chart
        exp_data = {}
        for r in data:
            if r[3] == "expense":
                exp_data[r[2]] = exp_data.get(r[2], 0) + r[1]

        if exp_data:
            fig1, ax1 = plt.subplots(figsize=(4, 3))
            ax1.pie(exp_data.values(), labels=exp_data.keys(), autopct="%1.1f%%")
            ax1.set_title("Expenses by Category")
            chart1 = FigureCanvasTkAgg(fig1, master=self.chart_frame)
            chart1.get_tk_widget().pack(side="left", padx=10)

        # Bar Chart
        months = {}
        for r in data:
            month = r[4][:7]
            if month not in months:
                months[month] = {"income": 0, "expense": 0}
            months[month][r[3]] += r[1]

        if months:
            fig2, ax2 = plt.subplots(figsize=(4, 3))
            x = list(months.keys())
            income_vals = [v["income"] for v in months.values()]
            expense_vals = [v["expense"] for v in months.values()]
            ax2.bar(x, income_vals, label="Income", color="green")
            ax2.bar(x, expense_vals, label="Expense", color="red", alpha=0.7)
            ax2.set_title("Monthly Income vs Expense")
            ax2.legend()
            chart2 = FigureCanvasTkAgg(fig2, master=self.chart_frame)
            chart2.get_tk_widget().pack(side="left", padx=10)

    # ---------- Goals ---------- #
    def goals(self):
        f = self.frames["Goals"]
        self.goal_name = tk.StringVar()
        self.goal_target = tk.DoubleVar()
        tb.Entry(f, textvariable=self.goal_name, width=20).pack(pady=5)
        tb.Entry(f, textvariable=self.goal_target, width=20).pack(pady=5)
        tb.Button(f, text="Add Goal", bootstyle="success", command=self.add_goal).pack(pady=10)
        self.goal_frame = tb.Frame(f)
        self.goal_frame.pack(fill="both", expand=True)

    def add_goal(self):
        name = self.goal_name.get().strip()
        try:
            target = float(self.goal_target.get())
        except ValueError:
            messagebox.showerror("Error", "Enter valid target")
            return

        if not name or target <= 0:
            messagebox.showerror("Error", "Enter valid goal")
            return

        add_goal(name, target)
        self.goal_name.set("")
        self.goal_target.set(0)
        self.load_goals()

    def load_goals(self):
        for widget in self.goal_frame.winfo_children():
            widget.destroy()
        for g in fetch_goals():
            pb = tb.Progressbar(self.goal_frame, maximum=g[2], value=g[3])
            tb.Label(self.goal_frame, text=f"🎯 {g[1]} - {g[3]}/{g[2]}").pack(pady=5)
            pb.pack(fill="x", padx=10, pady=5)

    # ---------- Settings ---------- #
    def settings(self):
        f = self.frames["Settings"]
        tb.Label(f, text="Theme:").pack(pady=5)
        th = tk.StringVar(value=self.theme)
        tb.OptionMenu(f, th, *tb.Style().theme_names(), command=lambda v: [tb.Style().theme_use(v), set_setting("theme", v)]).pack()

        tb.Label(f, text="Currency:").pack(pady=5)
        tb.OptionMenu(f, self.cur, *CURRENCIES.keys(), command=lambda v: [set_setting("currency", v), self.update_summary(), self.load_hist()]).pack()

        tb.Button(f, text="Backup DB", command=lambda: [backup(), messagebox.showinfo("OK", "Backup done")]).pack(pady=5)
        tb.Button(f, text="Restore Backup", command=self.restore_backup).pack(pady=5)
        tb.Button(f, text="Reset Data", bootstyle="danger", command=self.reset_data).pack(pady=5)

    def restore_backup(self):
        path = filedialog.askopenfilename(filetypes=[("DB Files", "*.db")])
        if path:
            restore(path)
            messagebox.showinfo("Restored", "Backup restored! Restart app to apply changes.")

    def reset_data(self):
        if messagebox.askyesno("Confirm", "Are you sure? This will erase all data."):
            os.remove(DB_FILE)
            init_db()
            self.update_summary()
            self.load_hist()
            self.load_analytics()
            self.load_goals()
            messagebox.showinfo("Reset", "All data cleared!")

# ---------------- Run ---------------- #
if __name__ == "__main__":
    init_db()
    root = tb.Window(themename=DEFAULT_THEME)
    def start(): App(root)
    LoginScreen(root, start)
    root.mainloop()
