# 💸 Expense Tracker — Modern Tkinter App

A simple yet powerful **Expense Tracker** built using **Python**, **Tkinter**, and **ttkbootstrap**, designed to help you manage income, expenses, and financial goals — all in one elegant desktop app.

---

## 🚀 Features

### 💰 Transactions
- Add **income** or **expense** entries with categories.
- View your complete transaction history in a sortable table.
- Automatically calculates **total income**, **expenses**, and **balance**.

### 📊 Analytics
- Visualize **expenses by category** using pie charts.
- Track **monthly income vs expense** with bar charts.
- Built with **Matplotlib** for clean and accurate visualization.

### 🎯 Goals
- Create savings or spending **goals** with custom target amounts.
- Monitor progress through smooth progress bars.

### 🔐 Secure Login
- PIN-protected login system (hashed using **SHA-256**).
- Set your PIN on first launch for added security.

### ⚙️ Settings
- Choose from multiple modern **themes** (via `ttkbootstrap`).
- Switch between **₹ (INR)** and **$ (USD)** currency options.
- Backup and restore your local database with one click.
- Reset all data easily when starting fresh.

### 💾 Backup System
- Automatically stores backups inside the `/backups` folder.
- Timestamped filenames for organized version control.

---

## 🧱 Tech Stack

| Component | Technology |
|------------|-------------|
| UI | Tkinter + ttkbootstrap |
| Database | SQLite3 |
| Charts | Matplotlib |
| Language | Python 3.x |
| Security | SHA-256 PIN hashing |

---

## 📁 Project Structure

ExpenseTracker.py
expenses.db
backups/
├── backup_20251022_153045.db

yaml
Copy code

---

## ⚡ Getting Started

### 1️⃣ Install Dependencies
Make sure you have **Python 3.8+** installed.

Run:
```bash
pip install ttkbootstrap matplotlib
2️⃣ Run the App
bash
Copy code
python ExpenseTracker.py
3️⃣ Set Your PIN
On first launch, you’ll be asked to create a PIN (minimum 4 digits).
Use this PIN to log in every time you open the app.

💡 Optional: Build a Windows Executable
To create a standalone .exe (no Python required):

bash
Copy code
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=icon.ico ExpenseTracker.py
Your executable will appear inside the dist/ folder.

🗃️ Database Info
SQLite Tables:

transactions: Stores all income and expense records.

settings: Saves preferences like theme, currency, and PIN.

goals: Keeps goal name, target, and progress data.

All information is saved locally in expenses.db.

🧠 Tips
Delete expenses.db if you ever want to start from scratch.

All backups are stored in the /backups folder.

Currency conversions are applied automatically when switching.

📸 Screenshots (Optional)
(Add screenshots here once available)
Example:

Dashboard

Analytics charts

Goals tab

📜 License
Built and licensed to d0wnbad hu, free to use.
You may use, modify, and distribute it for personal or educational purposes.

