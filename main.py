import sqlite3
import csv
from datetime import datetime
import math
from io import BytesIO
from PIL import Image, ImageDraw

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.graphics.texture import Texture
from kivy.core.window import Window

# Default White Background
Window.clearcolor = (0.95, 0.95, 0.95, 1)

class LoginScreen(Screen):
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    status_label = ObjectProperty(None)

    def login(self):
        user = self.username_input.text.strip()
        pwd = self.password_input.text.strip()
        if not user or not pwd:
            self.status_label.text = "Enter username & password"
            return
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (user,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0] == pwd:
            self.manager.current_user = user
            self.manager.current = 'dashboard'
            self.manager.get_screen('dashboard').refresh_data()
            self.status_label.text = ""
        else:
            self.status_label.text = "Invalid Login"

    def register(self):
        user = self.username_input.text.strip()
        pwd = self.password_input.text.strip()
        if not user or not pwd:
            self.status_label.text = "Fields cannot be blank"
            return
        try:
            conn = sqlite3.connect("expenses.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users(username, password, budget) VALUES (?, ?, ?)", (user, pwd, 0))
            conn.commit()
            conn.close()
            self.status_label.text = "Account Created"
        except sqlite3.IntegrityError:
            self.status_label.text = "Username already exists"

class DashboardScreen(Screen):
    amount_input = ObjectProperty(None)
    category_spinner = ObjectProperty(None)
    notes_input = ObjectProperty(None)
    history_label = ObjectProperty(None)
    status_label = ObjectProperty(None)
    graph_box = ObjectProperty(None)
    summary_label = ObjectProperty(None)
    budget_input = ObjectProperty(None)
    month_spinner = ObjectProperty(None)
    year_spinner = ObjectProperty(None)
    theme_button = ObjectProperty(None)

    welcome_text = StringProperty("Welcome")
    current_graph_type = "pie"
    is_dark = False

    def refresh_data(self):
        self.welcome_text = f"Logged in as: {self.manager.current_user}"
        self.apply_filters()

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        if self.is_dark:
            Window.clearcolor = (0.1, 0.1, 0.1, 1)
            self.theme_button.text = "☀️ Light"
        else:
            Window.clearcolor = (0.95, 0.95, 0.95, 1)
            self.theme_button.text = "🌙 Dark"

    def apply_filters(self):
        user = self.manager.current_user
        month = self.month_spinner.text if self.month_spinner.text != "All Months" else None
        year = self.year_spinner.text if self.year_spinner.text != "All Years" else None

        self.refresh_history(user, month, year)
        self.update_graph(user, month, year)
        self.update_summary(user, month, year)
        self.check_monthly_budget(user, month, year)

    def add_expense(self):
        user = self.manager.current_user
        try:
            amount = float(self.amount_input.text)
        except:
            self.status_label.text = "Invalid amount"
            return
        category = self.category_spinner.text
        notes = self.notes_input.text.strip()
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses(username, amount, category, date_added, notes) VALUES (?, ?, ?, ?, ?)",
            (user, amount, category, date_now, notes)
        )
        conn.commit()
        conn.close()

        self.amount_input.text = ""
        self.notes_input.text = ""
        self.apply_filters()

    def update_summary(self, user, month=None, year=None):
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()

        query = "SELECT SUM(amount) FROM expenses WHERE username=?"
        params = [user]
        if month:
            query += " AND strftime('%m', date_added) = ?"
            params.append(month.zfill(2))
        if year:
            query += " AND strftime('%Y', date_added) = ?"
            params.append(year)

        cursor.execute(query, params)
        total = cursor.fetchone()[0]
        total = total if total else 0

        cursor.execute("SELECT budget FROM users WHERE username=?", (user,))
        budget = cursor.fetchone()[0]
        conn.close()

        remaining = budget - total
        self.summary_label.text = (
            f"Total: ${total:.2f} | Budget: ${budget:.2f} | Remaining: ${remaining:.2f}"
        )

    def set_budget(self):
        user = self.manager.current_user
        try:
            budget = float(self.budget_input.text)
        except:
            self.status_label.text = "Invalid budget"
            return
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET budget=? WHERE username=?", (budget, user))
        conn.commit()
        conn.close()
        self.status_label.text = "Budget Updated"
        self.apply_filters()

    def check_monthly_budget(self, user, month=None, year=None):
        if not month and not year:
            now = datetime.now()
            month = now.strftime("%m")
            year = now.strftime("%Y")

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT budget FROM users WHERE username=?", (user,))
        budget_row = cursor.fetchone()
        budget = budget_row[0] if budget_row else 0

        query = "SELECT SUM(amount) FROM expenses WHERE username=? AND strftime('%Y', date_added)=? AND strftime('%m', date_added)=?"
        cursor.execute(query, (user, year, month))
        total = cursor.fetchone()[0]
        total = total if total else 0
        conn.close()

        if budget > 0 and total > budget:
            popup = Popup(
                title='⚠️ Monthly Budget Exceeded!',
                content=Label(text=f'You have spent ${total:.2f} this month, which exceeds your ${budget:.2f} budget.', color=(0.8,0.2,0.2,1)),
                size_hint=(0.8,0.4)
            )
            popup.open()
        elif budget > 0 and total >= (budget * 0.8):
            popup = Popup(
                title='⚠️ Budget Warning',
                content=Label(text=f'You have spent ${total:.2f} ({(total/budget)*100:.1f}%) of your ${budget:.2f} budget.', color=(0.9,0.6,0.1,1)),
                size_hint=(0.8,0.4)
            )
            popup.open()

    def refresh_history(self, user, month=None, year=None):
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()

        query = "SELECT id, amount, category, date_added, notes FROM expenses WHERE username=?"
        params = [user]
        if month:
            query += " AND strftime('%m', date_added) = ?"
            params.append(month.zfill(2))
        if year:
            query += " AND strftime('%Y', date_added) = ?"
            params.append(year)
        query += " ORDER BY id DESC LIMIT 15"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.history_label.text = "No expenses yet"
            return

        text = ""
        for row in rows:
            note_display = f" ({row[4]})" if row[4] else ""
            text += f"🔹 ${row[1]:.2f} | {row[2]}{note_display} | {row[3]}\n"
        self.history_label.text = text

    def delete_expense(self):
        try:
            expense_id = int(self.amount_input.text)
        except:
            self.status_label.text = "Enter expense ID to delete"
            return
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        conn.close()
        self.status_label.text = "Expense Deleted"
        self.apply_filters()

    def export_csv(self):
        user = self.manager.current_user
        month = self.month_spinner.text if self.month_spinner.text != "All Months" else None
        year = self.year_spinner.text if self.year_spinner.text != "All Years" else None

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        query = "SELECT amount, category, date_added, notes FROM expenses WHERE username=?"
        params = [user]
        if month:
            query += " AND strftime('%m', date_added) = ?"
            params.append(month.zfill(2))
        if year:
            query += " AND strftime('%Y', date_added) = ?"
            params.append(year)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        filename = f"{user}_expenses.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Amount", "Category", "Date", "Notes"])
            writer.writerows(rows)
        self.status_label.text = f"Exported: {filename}"

    def change_graph_type(self, graph_type):
        self.current_graph_type = graph_type
        self.apply_filters()

    def update_graph(self, user, month=None, year=None):
        self.graph_box.clear_widgets()
        
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        query = """
            SELECT category, SUM(amount), COUNT(*)
            FROM expenses
            WHERE username=?
        """
        params = [user]
        if month:
            query += " AND strftime('%m', date_added) = ?"
            params.append(month.zfill(2))
        if year:
            query += " AND strftime('%Y', date_added) = ?"
            params.append(year)
        query += " GROUP BY category"
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()

        if not data:
            return

        labels = [row[0] for row in data]
        amounts = [float(row[1]) for row in data]
        counts = [row[2] for row in data]
        
        # Colors
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        
        img_size = 500  # Larger image for better visibility
        img = Image.new('RGB', (img_size, img_size), 'white')
        draw = ImageDraw.Draw(img)
        
        # --- PIE CHART ---
        if self.current_graph_type == "pie":
            total = sum(amounts)
            start_angle = -90  # Start from top
            
            for i, amount in enumerate(amounts):
                angle = (amount / total) * 360
                end_angle = start_angle + angle
                draw.pieslice(
                    [(50, 50), (450, 450)],  # Larger pie size
                    start=start_angle,
                    end=end_angle,
                    fill=colors[i % len(colors)]
                )
                # Draw label
                import math
                mid_angle = start_angle + (angle / 2)
                x = 250 + 170 * math.cos(math.radians(mid_angle))
                y = 250 + 170 * math.sin(math.radians(mid_angle))
                label_text = f"{labels[i]}\n({counts[i]} items)"
                draw.text((x, y), label_text, fill='black', anchor='mm')
                start_angle = end_angle
        
        # --- BAR CHART ---
        elif self.current_graph_type == "bar":
            bar_width = 40
            gap = 20
            start_x = 50
            max_amount = max(amounts) if amounts else 1
            chart_height = 350
            scale = chart_height / max_amount
            
            # Draw axes
            draw.line([(40, 50), (40, 450), (480, 450)], fill='black', width=2)
            
            for i, amount in enumerate(amounts):
                bar_height = amount * scale
                x0 = start_x + i * (bar_width + gap)
                x1 = x0 + bar_width
                y0 = 450 - bar_height
                y1 = 450
                draw.rectangle([x0, y0, x1, y1], fill=colors[i % len(colors)])
                # Labels
                draw.text((x0, 455), labels[i], fill='black')
                draw.text((x0 + 5, y0 - 20), f"${int(amount)}", fill='black')
        
        # --- LINE CHART ---
        elif self.current_graph_type == "line":
            max_amount = max(amounts) if amounts else 1
            chart_height = 350
            scale = chart_height / max_amount
            padding = 60
            points = []
            
            for i, amount in enumerate(amounts):
                x = padding + i * ((img_size - 2*padding) / max(1, len(amounts)-1))
                y = 450 - (amount * scale)
                points.append((x, y))
            
            # Draw axes
            draw.line([(padding, 50), (padding, 450), (img_size - padding, 450)], fill='black', width=2)
            
            # Draw line
            if len(points) > 1:
                draw.line(points, fill='#45B7D1', width=4)
            # Draw points
            for i, (x, y) in enumerate(points):
                draw.ellipse([(x-6, y-6), (x+6, y+6)], fill='#FF6B6B')
                draw.text((x, 455), labels[i], fill='black')
                draw.text((x, y-20), f"${int(amounts[i])}", fill='black')
        
        # --- TEXTURE RENDER (FIXED) ---
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        raw_data = img.tobytes()
        texture = Texture.create(size=(img.width, img.height))
        texture.blit_buffer(raw_data, colorfmt='rgba', bufferfmt='ubyte')
        self.graph_box.add_widget(KivyImage(texture=texture, size_hint=(1, 1)))
        # -----------------------------------------

    def logout(self):
        self.manager.current_user = ""
        self.manager.current = 'login'

class AppManager(ScreenManager):
    current_user = StringProperty("")

class ExpenseTrackerApp(App):
    def build(self):
        self.init_database()
        return AppManager()

    def init_database(self):
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                budget REAL DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                amount REAL,
                category TEXT,
                date_added TEXT,
                notes TEXT
            )
        """)
        conn.commit()
        conn.close()

if __name__ == '__main__':
    ExpenseTrackerApp().run()
