import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from tkinter import messagebox
from reportlab.pdfgen import canvas
import threading
import matplotlib.dates as mdates
import random
import customtkinter as ctk
import sqlite3
import threading
import ollama
import matplotlib.pyplot as plt
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("Dark")

class ModernBankApp(ctk.CTk):

    def draw_annual_report_layout(self, canvas, doc):
        # 1. الخلفية العلوية (الأزرق الداكن)
        canvas.setFillColorRGB(0.08, 0.18, 0.35)
        canvas.rect(0, 550, 650, 250, fill=1, stroke=0)
        
        # 2. العنوان الرئيسي
        canvas.setFillColorRGB(1, 1, 1)
        canvas.setFont("Helvetica-Bold", 30)
        canvas.drawString(50, 720, "2026 ANNUAL REPORT")
        canvas.setFont("Helvetica", 14)
        canvas.drawString(50, 690, "Strategic Overview | FY 2026")
        
        # 3. المربعات الملونة الثلاثة (تصميم حديث)
        box_y = 400
        box_w = 150
        box_h = 100
        
        # مربع Financial
        canvas.setFillColorRGB(0.85, 0.92, 0.98) # أزرق فاتح
        canvas.rect(50, box_y, box_w, box_h, fill=1, stroke=0)
        canvas.setFillColorRGB(0.1, 0.2, 0.4)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(60, box_y + 75, "FINANCIAL HIGHLIGHTS")
        canvas.setFont("Helvetica-Bold", 22)
        canvas.drawString(60, box_y + 40, "$2.4B")
        
        # مربع Sustainability
        canvas.setFillColorRGB(0.85, 0.98, 0.88) # أخضر فاتح
        canvas.rect(220, box_y, box_w, box_h, fill=1, stroke=0)
        canvas.setFillColorRGB(0.1, 0.3, 0.2)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(230, box_y + 75, "SUSTAINABILITY")
        canvas.setFont("Helvetica-Bold", 22)
        canvas.drawString(230, box_y + 40, "-48%")
        
        # مربع Innovation
        canvas.setFillColorRGB(0.92, 0.88, 0.98) # بنفسجي فاتح
        canvas.rect(390, box_y, box_w, box_h, fill=1, stroke=0)
        canvas.setFillColorRGB(0.3, 0.1, 0.4)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(400, box_y + 75, "INNOVATION")
        canvas.setFont("Helvetica-Bold", 22)
        canvas.drawString(400, box_y + 40, "127")
        
        # 4. تذييل الصفحة (Footer)
        canvas.setFillColorRGB(0.1, 0.15, 0.2)
        canvas.rect(0, 0, 650, 40, fill=1, stroke=0)
        canvas.setFillColorRGB(0.7, 0.7, 0.7)
        canvas.setFont("Helvetica-Oblique", 10)
        canvas.drawString(50, 15, "CONFIDENTIAL | AI BANK PRO | 2026 | All rights reserved.")
    
    def predict_future_balance(self, cid, name):
        conn = sqlite3.connect('bank_system.db')
        cur = conn.cursor()
        # جلب آخر 10 عمليات للعميل ليعرف الـ AI نمطه
        cur.execute("SELECT type, amount FROM transactions WHERE customer_id = ? ORDER BY id DESC LIMIT 10", (cid,))
        transactions = cur.fetchall()
        cur.execute("SELECT balance FROM customers WHERE id = ?", (cid,))
        current_balance = cur.fetchone()[0]
        conn.close()
        
        # تحويل البيانات لنص
        history = "; ".join([f"{t[0]} {t[1]}" for t in transactions])
        
        # البرومبت الذكي
        prompt = f"Client: {name}. Current Balance: {current_balance}. Transaction History: {history}. Based on this, predict the balance after 30 days and provide one short advice for the client."
        
        # استدعاء الـ AI
        res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
        messagebox.showinfo("AI Financial Forecast", res['message']['content'])
    def run_data_audit(self):
        conn = sqlite3.connect('bank_system.db')
        cur = conn.cursor()
        cur.execute("SELECT id, name, balance FROM customers")
        customers = cur.fetchall()
        
        self.audit_data = [] # قائمة لحفظ الأخطاء
        audit_report = "Audit Results:\n"
        inconsistency_found = False
        
        for cid, name, current_balance in customers:
            cur.execute("SELECT type, amount FROM transactions WHERE customer_id = ?", (cid,))
            transactions = cur.fetchall()
            
            calculated_balance = 0
            for t_type, amount in transactions:
                if t_type == "Deposit":
                    calculated_balance += amount
                else:
                    calculated_balance -= amount
            
            if calculated_balance != current_balance:
                audit_report += f"❌ Mismatch for {name}: DB={current_balance}, Correct={calculated_balance}\n"
                inconsistency_found = True
                # حفظ بيانات العميل والنتيجة الصحيحة للإصلاح لاحقاً
                self.audit_data.append((calculated_balance, cid))
        
        conn.close()
        
        if not inconsistency_found:
            messagebox.showinfo("Audit Success", "System is consistent!")
        else:
            # إضافة زر Fix Errors إذا وجدت أخطاء
            response = messagebox.askyesno("Audit Alert", audit_report + "\nDo you want to fix these errors?")
            if response:
                self.fix_balances()
    def fix_balances(self):
        conn = sqlite3.connect('bank_system.db')
        cur = conn.cursor()
        
        for new_balance, cid in self.audit_data:
            cur.execute("UPDATE customers SET balance = ? WHERE id = ?", (new_balance, cid))
            
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "All balances have been synchronized with transaction history.")
    def generate_ai_report_text(self, cid, name):
        conn = sqlite3.connect('bank_system.db')
        cur = conn.cursor()
        cur.execute("SELECT type, amount FROM transactions WHERE customer_id = ?", (cid,))
        rows = cur.fetchall()
        conn.close()
        
        # تحويل البيانات لنص يحلله الـ AI
        transactions_summary = "; ".join([f"{r[0]} of {r[1]} IQD" for r in rows])
        prompt = f"Write a professional, 3-paragraph financial report for client {name}. Based on these transactions: {transactions_summary}. Include an analysis of their spending habits and one financial recommendation."
        
        # استدعاء الـ AI
        res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
        return res['message']['content']
    def analyze_client_behavior(self, cid):
        conn = sqlite3.connect('bank_system.db')
        cur = conn.cursor()
        # جلب آخر 5 عمليات للعميل لتحليلها
        cur.execute("SELECT type, amount FROM transactions WHERE customer_id = ? ORDER BY id DESC LIMIT 5", (cid,))
        transactions = cur.fetchall()
        conn.close()
        
        # تحويل البيانات لنص يقرأه الـ AI
        history_text = ", ".join([f"{t[0]} {t[1]}" for t in transactions])
        prompt = f"Analyze this user behavior: {history_text}. Is this client a saver or a spender? Provide a short 2-line financial profile."
        
        res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
        messagebox.showinfo("AI Behavior Analysis", res['message']['content'])
    def process_chat(self):
        user_input = self.chat_entry.get()
        if not user_input.strip(): return 
        
        self.chat_display.insert("end", f"\nYou: {user_input}")
        
        # 1. فحص هل المستخدم يسأل عن رصيد (بحث محلي من قاعدة البيانات)
        if "balance of" in user_input.lower():
            name = user_input.lower().split("balance of")[-1].strip()
            conn = sqlite3.connect('bank_system.db')
            cur = conn.cursor()
            cur.execute("SELECT balance FROM customers WHERE name = ?", (name,))
            res = cur.fetchone()
            conn.close()
            
            if res:
                reply = f"The current balance for {name} is {res[0]} IQD."
            else:
                reply = f"I couldn't find a client named {name} in the database."
        
        # 2. إذا لم يكن سؤالاً عن رصيد، نرسله للـ AI مع التعليمات الجديدة
        else:
            try:
                response = ollama.chat(model='llama3', messages=[
                    {'role': 'system', 'content': 'You are a professional banking assistant. Only answer questions related to banking, finance, and client data. If the user asks about something unrelated, politely decline.'},
                    {'role': 'user', 'content': user_input}
                ])
                reply = response['message']['content']
            except Exception as e:
                reply = "Sorry, I am having trouble connecting to the AI engine."
        
        # عرض الرد في الواجهة
        self.chat_display.insert("end", f"\nAI: {reply}")
        self.chat_entry.delete(0, 'end')
    def open_ai_chatbot(self):
        chat_win = ctk.CTkToplevel(self)
        chat_win.title("AI Bank Assistant")
        chat_win.geometry("400x500")

        self.chat_display = ctk.CTkTextbox(chat_win, width=380, height=350)
        self.chat_display.pack(pady=10)
        self.chat_display.insert("0.0", "AI: Hello! How can I help you today? (e.g., 'Find client Ahmed')")

        self.chat_entry = ctk.CTkEntry(chat_win, placeholder_text="Ask me anything...")
        self.chat_entry.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(chat_win, text="Send", command=self.process_chat).pack()

    def process_chat(self):
        user_input = self.chat_entry.get()
        self.chat_display.insert("end", f"\nYou: {user_input}")
        
        # ربط المدخلات بـ AI
        response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': user_input}])
        ai_reply = response['message']['content']
        
        self.chat_display.insert("end", f"\nAI: {ai_reply}")
        self.chat_entry.delete(0, 'end')
    def update_rates(self):
        # محاكاة تحديث أسعار مباشر
        rates = {"USD/IQD": 1500 + random.randint(-5, 5), 
                 "EUR/IQD": 1620 + random.randint(-5, 5), 
                 "JPY/IQD": 210 + random.randint(-2, 2)}
        for cur, val in rates.items():
            self.rates_labels[cur].configure(text=str(val))
        self.after(3000, self.update_rates) # تحديث كل 3 ثوانٍ
    def toggle_lock(self, cid, win):
        conn = sqlite3.connect('bank_system.db')
        cur = conn.cursor()
        
        cur.execute("SELECT status FROM customers WHERE id = ?", (cid,))
        current_status = cur.fetchone()[0]
        new_status = 'Locked' if current_status == 'Active' else 'Active'
        
        
        cur.execute("UPDATE customers SET status = ? WHERE id = ?", (new_status, cid))
        conn.commit()
        conn.close()
        messagebox.showinfo("Status Updated", f"Account is now {new_status}")
        win.destroy()
        self.load_data()

    def on_export_click(self, cid, name):
        # استخدام Thread لمنع تجمد الواجهة
        threading.Thread(target=self.export_pdf, args=(cid, name)).start()

    # 1. عرف دالة الرسم داخل الكلاس (لكن ليس داخل دالة export_pdf)
    
    def draw_official_design(self, canvas, doc):
        # الخلفية الزرقاء في الأعلى
        canvas.setFillColorRGB(0.1, 0.2, 0.35)
        canvas.rect(0, 650, 600, 150, fill=1, stroke=0)
        
        # العنوان الرئيسي
        canvas.setFillColorRGB(1, 1, 1)
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawString(50, 740, "2026 ANNUAL REPORT")
        canvas.setFont("Helvetica", 12)
        canvas.drawString(50, 715, "AI BANK PRO | STRATEGIC FINANCIAL OVERVIEW")
        
        # تذييل الصفحة
        canvas.setFillColorRGB(0.1, 0.6, 0.6)
        canvas.rect(0, 0, 600, 30, fill=1, stroke=0)
        canvas.setFillColorRGB(1, 1, 1)
        canvas.setFont("Helvetica-Oblique", 10)
        canvas.drawString(50, 10, "CONFIDENTIAL | AI BANK PRO | 2026")

            
    def export_pdf(self, cid, name):
        try:
            filename = os.path.join(os.getcwd(), f"Annual_Report_{name}.pdf")
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            story.append(Spacer(1, 450))
            story.append(Paragraph(f"Customer: {name}", styles['Normal']))
            doc.build(story, onFirstPage=self.draw_annual_report_layout, onLaterPages=self.draw_annual_report_layout)
            messagebox.showinfo("Success", "تم إنشاء التقرير بنجاح!")
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"فشل إنشاء التقرير: {e}")
    
    def __init__(self):
        super().__init__()
        self.geometry("1000x650")
        self.title("AI Bank Pro | Enterprise Edition")
        
        # --- Sidebar (يجب أن يتم إنشاؤه أولاً) ---
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkButton(self.sidebar, text="Run Integrity Audit", fg_color="red", command=self.run_data_audit).pack(pady=20)
        # الآن يمكنك إضافة الأزرار داخلها
        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.load_dashboard).pack(pady=20)
        ctk.CTkButton(self.sidebar, text="Manage Clients", command=self.load_customers).pack(pady=10)
        
        # إضافة زر المساعد هنا
        ctk.CTkButton(self.sidebar, text="AI Assistant", fg_color="#1f538d", command=self.open_ai_chatbot).pack(pady=20, padx=10)

        # --- Live Currency Rates ---
        self.rates_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.rates_frame.pack(fill="x", pady=30, padx=10)
        ctk.CTkLabel(self.rates_frame, text="Live Market Rates (IQD)", font=("Arial", 12, "bold")).pack()
        
        self.rates_labels = {}
        for cur in ["USD/IQD", "EUR/IQD", "JPY/IQD"]:
            row = ctk.CTkFrame(self.rates_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=cur).pack(side="left")
            lbl = ctk.CTkLabel(row, text="---")
            lbl.pack(side="right")
            self.rates_labels[cur] = lbl
        
        self.update_rates() 
        
        # --- زر الشارت الجديد ---
        ctk.CTkButton(self.sidebar, text="Market Charts", command=self.show_market_chart).pack(pady=10)

        # --- Main Frame ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.load_dashboard()

    def load_dashboard(self):
        for w in self.main_frame.winfo_children(): w.destroy()
        
        # استخدام إطار رمادي دافئ بدلاً من الأسود
        self.stats_frame = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b", corner_radius=10)
        self.stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.stats_frame, text="Financial Performance Overview", font=("Arial", 16, "bold")).pack(pady=10)
        self.draw_chart()
        
    def show_market_chart(self):
        chart_win = ctk.CTkToplevel(self)
        chart_win.title("Market Analysis - Daily Price History")
        chart_win.geometry("700x500")
        
        # تحسين شكل الشارت: خلفية رمادية داكنة احترافية
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor('#2b2b2b') 
        ax.set_facecolor('#333333') 
        
        # بيانات تجريبية (تاريخ وسعر)
        days = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%d/%m") for i in range(7)][::-1]
        
        # أسعار العملات (مثال)
        data = {
            "USD": [1450, 1452, 1448, 1455, 1450, 1460, 1458],
            "EUR": [1590, 1595, 1588, 1600, 1592, 1605, 1602],
            "GBP": [1850, 1855, 1848, 1860, 1852, 1865, 1862]
        }
        
        # رسم خط لكل عملة
        colors = {"USD": "#00ffcc", "EUR": "#ffcc00", "GBP": "#ff5555"}
        for currency, prices in data.items():
            ax.plot(days, prices, marker='o', label=currency, color=colors[currency], linewidth=2)
        
        # تنسيق المحاور
        ax.set_title("Currency Price History (Last 7 Days)", color="white", fontsize=14)
        ax.tick_params(colors='white')
        ax.grid(color='#444444', linestyle='--')
        ax.legend(facecolor='#333333', labelcolor='white')
        
        # عرض الشارت داخل التطبيق
        canvas = FigureCanvasTkAgg(fig, master=chart_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def draw_chart(self):
        conn = sqlite3.connect('bank_system.db')
        cur = conn.cursor()
        cur.execute("SELECT type, COUNT(*) FROM transactions GROUP BY type")
        data = cur.fetchall(); conn.close()
        
        stats = {"Deposit": 0, "Withdraw": 0}
        for t, c in data:
            if t == "Deposit": stats["Deposit"] += c
            elif t == "Withdraw": stats["Withdraw"] += c

        # تحسين مظهر الشارت: خلفية رمادية داكنة احترافية
        fig, ax = plt.subplots(figsize=(5, 3), facecolor='#2b2b2b', dpi=100)
        ax.set_facecolor('#3b3b3b') # لون خلفية الشارت نفسه
        
        # استخدام ألوان أكثر تباين وجمال (أخضر هادئ وبرتقالي عصري)
        bars = ax.bar(stats.keys(), stats.values(), color=['#4CAF50', '#FF9800'], width=0.5)
        
        ax.tick_params(colors='white') # جعل النصوص بيضاء
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    def load_customers(self):
        for w in self.main_frame.winfo_children(): w.destroy()
        add_frame = ctk.CTkFrame(self.main_frame)
        add_frame.pack(fill="x", padx=10, pady=5)
        self.name_e = ctk.CTkEntry(add_frame, placeholder_text="Name"); self.name_e.pack(side="left", padx=5)
        self.phone_e = ctk.CTkEntry(add_frame, placeholder_text="Phone"); self.phone_e.pack(side="left", padx=5)
        ctk.CTkButton(add_frame, text="Add", command=self.add_client).pack(side="left", padx=5)
        
        self.search_e = ctk.CTkEntry(self.main_frame, placeholder_text="Search Name...")
        self.search_e.pack(fill="x", padx=10, pady=5)
        self.search_e.bind("<KeyRelease>", self.load_data)
        
        self.tree = ttk.Treeview(self.main_frame, columns=("ID", "Name", "Phone", "Balance"), show='headings')
        for col in ["ID", "Name", "Phone", "Balance"]: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.show_details)
        self.load_data()

    def add_client(self):
        name, phone = self.name_e.get(), self.phone_e.get()
        if name and phone:
            conn = sqlite3.connect('bank_system.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO customers (name, phone, balance) VALUES (?, ?, 0)", (name, phone))
            conn.commit(); conn.close(); self.load_data()

    def load_data(self, event=None):
        
        for i in self.tree.get_children(): self.tree.delete(i)
        
        
        self.tree.tag_configure('locked', foreground='red')
        
        query = self.search_e.get()
        conn = sqlite3.connect('bank_system.db')
        cur = conn.cursor()
        
        cur.execute("SELECT id, name, phone, balance, status FROM customers WHERE name LIKE ?", ('%'+query+'%',))
        
        for row in cur.fetchall():
            # row[4] هو عمود الـ status
            tag = 'locked' if row[4] == 'Locked' else ''
            # إدراج الصف في الجدول مع التاج
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3]), tags=(tag,))
        
        conn.close()

    def show_details(self, event):
        sel = self.tree.selection()
        if not sel: return
        data = self.tree.item(sel[0])['values']
        win = ctk.CTkToplevel(self); win.title(f"Account: {data[1]}"); win.geometry("500x400")
        tabs = ctk.CTkTabview(win); tabs.pack(fill="both", expand=True)
        tabs.add("Actions"); tabs.add("History"); tabs.add("AI Advisor")
        # ... (باقي الكود كما هو)
        
        ctk.CTkButton(tabs.tab("AI Advisor"), text="Get Tip", command=lambda: self.get_advice()).pack(pady=20)
        # إضافة الزر الجديد هنا
        ctk.CTkButton(tabs.tab("AI Advisor"), text="AI Forecast", fg_color="#2a8d1f", 
                      command=lambda: self.predict_future_balance(data[0], data[1])).pack(pady=20)
       
        ctk.CTkButton(win, text="Export PDF", command=lambda: self.export_pdf(data[0], data[1])).pack(pady=10)
        
        ctk.CTkButton(tabs.tab("Actions"), text="Toggle Lock Status", fg_color="orange", 
                      command=lambda: self.toggle_lock(data[0], win)).pack(pady=5)
        amt_e = ctk.CTkEntry(tabs.tab("Actions"), placeholder_text="Amount"); amt_e.pack(pady=20)
        ctk.CTkButton(tabs.tab("Actions"), text="Deposit", command=lambda: self.db_action(1, float(amt_e.get()), data[0], win)).pack(pady=5)
        ctk.CTkButton(tabs.tab("Actions"), text="Withdraw", command=lambda: threading.Thread(target=self.ai_logic, args=(float(amt_e.get()), data[0], win)).start()).pack(pady=5)

        # إعداد الجدول ليقبل 3 أعمدة
        h_tree = ttk.Treeview(tabs.tab("History"), columns=("Type", "Amount", "Date"), show="headings")
        h_tree.heading("Type", text="Type")
        h_tree.heading("Amount", text="Amount")
        h_tree.heading("Date", text="Date") # أضفنا عمود التاريخ
        h_tree.column("Type", width=100)
        h_tree.column("Amount", width=100)
        h_tree.column("Date", width=150)
        h_tree.pack(fill="both", expand=True)

        conn = sqlite3.connect('bank_system.db')
        cur = conn.cursor()
        # جلب البيانات الثلاثة (النوع، المبلغ، والتاريخ)
        cur.execute("SELECT type, amount, timestamp FROM transactions WHERE customer_id = ?", (data[0],))
        for row in cur.fetchall():
            # row هو tuple يحتوي على (type, amount, timestamp)
            h_tree.insert("", "end", values=row)
        conn.close()
        
        ctk.CTkButton(tabs.tab("AI Advisor"), text="Get Tip", command=lambda: self.get_advice()).pack(pady=50)

    def ai_logic(self, val, cid, win):
        try:
            res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': f"Withdraw {val}. Suspicious? Reply YES or NO"}])
            if 'YES' in res['message']['content'].upper():
                if messagebox.askyesno("AI Alert", "Suspicious! Continue?"): self.after(0, lambda: self.db_action(-1, val, cid, win))
            else: self.after(0, lambda: self.db_action(-1, val, cid, win))
        except: self.after(0, lambda: self.db_action(-1, val, cid, win))

    def get_advice(self):
        res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': "Give a financial tip"}])
        messagebox.showinfo("AI", res['message']['content'])

    def db_action(self, m, val, cid, win):
        conn = sqlite3.connect('bank_system.db')
        cur = conn.cursor()
        
        cur.execute("SELECT status FROM customers WHERE id = ?", (cid,))
        status = cur.fetchone()[0]
        if status == 'Locked':
            messagebox.showerror("Error", "This account is LOCKED!")
            conn.close()
            return
            
        cur.execute("UPDATE customers SET balance = balance + ? WHERE id = ?", (val * m, cid))
        
        # تم حذف السطر المكرر هنا ليبقى تسجيل واحد فقط للعملية
        cur.execute("INSERT INTO transactions (customer_id, type, amount) VALUES (?, ?, ?)", 
                    (cid, "Deposit" if m == 1 else "Withdraw", val))
        
        conn.commit()
        conn.close()
        
        if m == -1 and val > 10000:
            messagebox.showwarning("SECURITY ALERT", "Large Withdrawal Detected!")

        win.destroy()
        self.load_data()

        
        if m == -1 and val > 10000:
            messagebox.showwarning("SECURITY ALERT", "Large Withdrawal Detected!")

        win.destroy()
        self.load_data()

if __name__ == "__main__":
    app = ModernBankApp()
    app.mainloop()
zz
