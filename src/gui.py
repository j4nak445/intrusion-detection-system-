import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.font import Font
import tkinter.ttk as ttk
import threading
import uuid
import pandas as pd
import joblib
import time

from src.model import train, evaluate
from src.data_loader import get_train_test
from src.detect import predict_sample, append_log
from src.utils import plot_attack_pie, plot_attack_bar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ROOT = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(ROOT, 'models')


class RetroIDSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Retro IDS SOC Dashboard')
        self.configure(bg='black')
        self.geometry('1000x680')

        default_font = Font(family='Courier', size=10, weight='bold')
        self.option_add('*Font', default_font)

        # -------- LIVE COUNTERS --------
        self.total_count = 0
        self.attack_count = 0
        self.normal_count = 0

        counter_frame = tk.Frame(self, bg='black')
        counter_frame.pack(fill='x')

        self.lbl_total = tk.Label(counter_frame, text="Total: 0", fg='cyan', bg='black')
        self.lbl_total.pack(side='left', padx=10)
        self.lbl_attack = tk.Label(counter_frame, text="Attacks: 0", fg='red', bg='black')
        self.lbl_attack.pack(side='left', padx=10)
        self.lbl_normal = tk.Label(counter_frame, text="Normal: 0", fg='lime', bg='black')
        self.lbl_normal.pack(side='left', padx=10)

        # -------- BUTTON PANEL --------
        left = tk.Frame(self, bg='black')
        left.pack(side='left', fill='y', padx=10, pady=10)

        tk.Button(left, text='Train Model', width=24, bg='gray20', fg='lime', command=self.train_model).pack(pady=6)
        tk.Button(left, text='Detect Attack', width=24, bg='gray20', fg='lime', command=self.detect_from_file).pack(pady=6)
        tk.Button(left, text='Upload Custom CSV', width=24, bg='gray20', fg='lime', command=self.detect_custom_csv).pack(pady=6)
        tk.Button(left, text='Show Statistics', width=24, bg='gray20', fg='lime', command=self.show_stats).pack(pady=6)
        tk.Button(left, text='View Logs', width=24, bg='gray20', fg='lime', command=self.view_logs).pack(pady=6)

        # -------- MAIN CONSOLE --------
        self.console = scrolledtext.ScrolledText(self, bg='black', fg='lime')
        self.console.pack(fill='both', expand=True, padx=10, pady=10)

        # -------- STATUS BAR --------
        self.status = tk.Label(self, text="Idle", bg='gray15', fg='white')
        self.status.pack(fill='x')

    # ================= LOGGING =================
    def log(self, text, color='lime'):
        self.console.insert('end', text + '\n')
        self.console.tag_add(color, "end-1l", "end")
        self.console.tag_config(color, foreground=color)
        self.console.see('end')

    def update_counters(self, is_attack):
        self.total_count += 1
        if is_attack:
            self.attack_count += 1
        else:
            self.normal_count += 1

        self.lbl_total.config(text=f"Total: {self.total_count}")
        self.lbl_attack.config(text=f"Attacks: {self.attack_count}")
        self.lbl_normal.config(text=f"Normal: {self.normal_count}")

    # ================= ALERT + ANIMATION =================
    def flash_alert(self):
        for _ in range(3):
            self.configure(bg='darkred')
            self.update()
            time.sleep(0.15)
            self.configure(bg='black')
            self.update()
            time.sleep(0.15)

    def animate_status(self):
        for i in range(6):
            self.status.config(text="Analyzing" + "." * (i % 4))
            time.sleep(0.3)
        self.status.config(text="Idle")

    # ================= TRAIN =================
    def train_model(self):
        def job():
            csv_path = filedialog.askopenfilename(title='Select training CSV', filetypes=[('CSV files','*.csv')])
            if not csv_path:
                return
            self.log(f'Loading {csv_path}')
            X_train, X_test, y_train, y_test = get_train_test(csv_path)
            self.log('Training model...')
            model, history = train(X_train, y_train, X_test, y_test, epochs=30)
            acc, report = evaluate(model, X_test, y_test)
            self.log(f'Test accuracy: {acc:.4f}')
            self.log(report)
            messagebox.showinfo('Training', f'Training finished. Test acc: {acc:.4f}')

        threading.Thread(target=job).start()

    # ================= SIMULATION DETECTION =================
    def detect_from_file(self):
        csv_path = os.path.join(ROOT, 'data', 'sample_for_detection.csv')
        if not os.path.exists(csv_path):
            messagebox.showerror("Error", "Train the model first.")
            return

        def job():
            self.animate_status()
            df = pd.read_csv(csv_path)
            for i in range(len(df)):
                r = predict_sample(df.iloc[[i]])
                cid = str(uuid.uuid4())
                result = 'attack' if r['is_attack'] else 'normal'
                append_log(cid, r['label'], result)

                if r['is_attack']:
                    self.log(f'⚠ {cid} -> {r["label"]} (ATTACK)', 'red')
                    self.flash_alert()
                else:
                    self.log(f'✔ {cid} -> {r["label"]} (NORMAL)', 'lime')

                self.update_counters(r['is_attack'])

        threading.Thread(target=job).start()

    # ================= CUSTOM CSV =================
    def detect_custom_csv(self):
        csv_path = filedialog.askopenfilename(title='Select CSV', filetypes=[('CSV files','*.csv')])
        if not csv_path:
            return

        def job():
            self.animate_status()
            df = pd.read_csv(csv_path)
            encoders = joblib.load(os.path.join(MODELS_DIR, 'encoders.pkl'))
            expected_cols = list(encoders.keys())
            missing = [c for c in expected_cols if c not in df.columns]

            if missing:
                messagebox.showerror("Invalid CSV", f"Missing features: {missing}")
                return

            for i in range(len(df)):
                r = predict_sample(df.iloc[[i]])
                cid = str(uuid.uuid4())
                result = 'attack' if r['is_attack'] else 'normal'
                append_log(cid, r['label'], result)

                if r['is_attack']:
                    self.log(f'⚠ {cid} -> {r["label"]} (ATTACK)', 'red')
                    self.flash_alert()
                else:
                    self.log(f'✔ {cid} -> {r["label"]} (NORMAL)', 'lime')

                self.update_counters(r['is_attack'])

        threading.Thread(target=job).start()

    # ================= STATS =================
    def show_stats(self):
        pie = plot_attack_pie()
        bar = plot_attack_bar()
        if pie is None or bar is None:
            messagebox.showinfo('Stats', 'No logs yet.')
            return

        win = tk.Toplevel(self)
        win.title('Statistics')
        canvas1 = FigureCanvasTkAgg(pie, master=win)
        canvas1.get_tk_widget().pack(side='left', fill='both', expand=True)
        canvas2 = FigureCanvasTkAgg(bar, master=win)
        canvas2.get_tk_widget().pack(side='right', fill='both', expand=True)
        canvas1.draw()
        canvas2.draw()

    # ================= LOG TABLE =================
    def view_logs(self):
        path = os.path.join(ROOT, 'logs', 'ids_logs.csv')
        if not os.path.exists(path):
            messagebox.showinfo('Logs', 'No logs yet.')
            return

        df = pd.read_csv(path)

        win = tk.Toplevel(self)
        win.title('IDS Logs')
        win.geometry('900x400')
        win.configure(bg='#111111')

        frame = tk.Frame(win, bg='#111111')
        frame.pack(fill='both', expand=True)

        columns = list(df.columns)
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        tree.pack(side='left', fill='both', expand=True)

        vsb = tk.Scrollbar(frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#111111", foreground="lime", fieldbackground="#111111")
        style.configure("Treeview.Heading", background="gray20", foreground="lime")

        tree.tag_configure('attack', foreground='red')

        for col in columns:
            tree.heading(col, text=col.upper())
            tree.column(col, anchor='center', width=170)

        for _, row in df.iterrows():
            tag = 'attack' if str(row['result']).lower() == 'attack' else ''
            tree.insert('', 'end', values=list(row), tags=(tag,))


if __name__ == '__main__':
    app = RetroIDSApp()
    app.mainloop()
