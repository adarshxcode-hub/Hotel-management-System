from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog
import mysql.connector
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import time
from datetime import datetime


class DashboardWindow:
    def __init__(self, root):
        self.root = Toplevel(root)
        self.root.title("Luxury Hotel Dashboard")
        self.root.geometry("1319x580+200+230")
        self.dark_mode = False

        header = tk.Frame(self.root, bg="#f5deb3", height=50)
        header.pack(fill=tk.X)

        self.datetime_label = tk.Label(header, font=("Segoe UI", 12), bg="#f5deb3", fg="#4b3832")
        self.datetime_label.pack(side=tk.RIGHT, padx=10, pady=10)
        self.update_time()



        self.sidebar_color = "tan"
        self.content_color = "#FFB6C1"

        self.setup_ui()
        self.load_data()


    def update_time(self):
        now = datetime.now()
        time_str = now.strftime("%A, %d %B %Y | %I:%M:%S %p")
        self.datetime_label.config(text=time_str)
        self.root.after(1000, self.update_time)





    def setup_ui(self):
        # Sidebar of the main dashboard ui 
        self.sidebar = Frame(self.root, bg=self.sidebar_color, width=180)
        self.sidebar.pack(side=LEFT, fill=Y)

        sidebar_label = Label(self.sidebar, text="Dashboard", bg=self.sidebar_color, fg="black",
                              font=("Helvetica", 18, "bold"))
        sidebar_label.pack(pady=20)

        self.btn_dashboard = Button(self.sidebar, text="📊 Charts", font=("Arial", 12,),
                                    fg="black", bg=self.sidebar_color, bd=0, cursor="hand2",
                                    activebackground="#34495E", command=self.load_data)
        self.btn_dashboard.pack(fill=X, pady=5)

        self.btn_theme = Button(self.sidebar, text="🌓 theme", font=("Arial", 12, ),
                                fg="black", bg=self.sidebar_color, bd=0, cursor="hand2",
                                activebackground="#34495E", command=self.toggle_theme)
        self.btn_theme.pack(fill=X, pady=5)

        self.btn_exit = Button(self.sidebar, text="❌ Exit", font=("Arial", 12, ),
                               fg="black", bg=self.sidebar_color, bd=0, cursor="hand2",
                               activebackground="#C0392B", command=self.root.destroy)
        self.btn_exit.pack(fill=X, pady=30)

        # Main content
        self.content = Frame(self.root, bg=self.content_color)
        self.content.pack(side=LEFT, fill=BOTH, expand=True)

        self.cards_frame = Frame(self.content, bg=self.content_color)
        self.cards_frame.pack(pady=10)

        self.charts_frame = Frame(self.content, bg=self.content_color)
        self.charts_frame.pack(pady=10, fill=BOTH, expand=True)

    # dark theme for the main ui of the interface
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.content_color = "#1F1F1F" if self.dark_mode else "white"
        fg_color = "white" if self.dark_mode else "black"

        self.content.config(bg=self.content_color)
        self.cards_frame.config(bg=self.content_color)
        self.charts_frame.config(bg=self.content_color)

        for widget in self.cards_frame.winfo_children():
            widget.config(bg="#333" if self.dark_mode else "#ECF0F1", fg=fg_color)
        for widget in self.charts_frame.winfo_children():
            if isinstance(widget, Label):
                widget.config(bg=self.content_color, fg=fg_color)

        self.load_data()

    def load_data(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        try:
            conn = mysql.connector.connect(
                host="localhost", username="root", password="Mysql@3115", database="sys")
            cursor = conn.cursor()

            # Summary Data
            cursor.execute("SELECT COUNT(*) FROM customer")
            total_customers = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM room_window")
            total_bookings = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM customer WHERE Gender='Male'")
            male = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM customer WHERE Gender='Female'")
            female = cursor.fetchone()[0]

            self.create_summary_card("👥 Customers", total_customers, "#D3B983")
            self.create_summary_card("🛏 Bookings", total_bookings, "#88C2A0")
            self.create_summary_card("♂ Male", male, "#D94444")
            self.create_summary_card("♀ Female", female, "#D65EA8")

            # Chart Data
            cursor.execute("SELECT Gender, COUNT(*) FROM customer GROUP BY Gender")
            gender_data = cursor.fetchall()

            cursor.execute("SELECT Nationality, COUNT(*) FROM customer GROUP BY Nationality")
            nationality_data = cursor.fetchall()

            cursor.execute("SELECT Roomtype, COUNT(*) FROM room_window GROUP BY Roomtype")
            roomtype_data = cursor.fetchall()

            cursor.execute("SELECT Meal, COUNT(*) FROM room_window GROUP BY Meal")
            meal_data = cursor.fetchall()

            conn.close()

            self.draw_chart_pie(gender_data, "Gender Distribution")
            self.draw_chart_bar(nationality_data, "Nationality Count")
            self.draw_chart_pie(meal_data, "Meal Preferences")
            self.draw_chart_bar(roomtype_data, "Room Type Distribution")

        except Exception as e:
            Label(self.content, text=f"Error: {e}", fg="red", bg=self.content_color).pack()

    def create_summary_card(self, title, value, color):
        card = Frame(self.cards_frame, bg=color, bd=2, relief=RIDGE)
        card.pack(side=LEFT, padx=10, pady=10)
        Label(card, text=title, font=("Arial", 14, "bold"), bg=color).pack(padx=15, pady=5)
        Label(card, text=str(value), font=("Arial", 20), bg=color).pack(pady=5)

    def draw_chart_bar(self, data, title):
        labels = [row[0] for row in data]
        values = [row[1] for row in data]
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(labels, values, color=['#5DADE2', '#58D68D', '#F4D03F', '#EC7063', '#AF7AC5'])
        ax.set_title(title)

        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=LEFT, padx=10)

    def draw_chart_pie(self, data, title):
        labels = [row[0] for row in data]
        sizes = [row[1] for row in data]
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']

        fig, ax = plt.subplots(figsize=(4, 2))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
        ax.set_title(title)

        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=LEFT, padx=10)



if __name__=="__main__":
    root = Tk()
    app = DashboardWindow()
    root.mainloop()