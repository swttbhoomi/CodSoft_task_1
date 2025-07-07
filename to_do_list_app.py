import customtkinter as ctk
from datetime import datetime
import json
import os
from tkinter import messagebox
from tkcalendar import DateEntry

class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Todo List")
        self.geometry("1000x700")
        self.resizable(True, True)
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#181c2f")  # Modern dark blue background

        self.tasks = []
        self.theme_mode = "dark"
        self.load_tasks()
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Header
        self.header = ctk.CTkLabel(
            self,
            text="My Todo List",
            font=("Segoe UI", 32, "bold"),
            text_color="#a3bffa",
            fg_color="transparent"
        )
        self.header.grid(row=0, column=0, sticky="n", pady=(30, 10))

        self.create_main_content()
        self.create_floating_button()

    def create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.theme_button = ctk.CTkButton(
            self.main_frame,
            text="☀️",
            width=50,
            height=30,
            font=("Segoe UI", 16),
            command=self.toggle_theme,
            fg_color="#a3bffa",
            text_color="#181c2f",
            hover_color="#7f9cf5"
        )
        self.theme_button.place(relx=0.95, rely=0.05, anchor="ne")

        self.tasks_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.tasks_frame.grid(row=0, column=0, padx=40, pady=20, sticky="nsew")

        for i in range(3):  # 3 columns for more space
            self.tasks_frame.grid_columnconfigure(i, weight=1)

        self.refresh_tasks()

    def create_floating_button(self):
        self.floating_button = ctk.CTkButton(
            self,
            text="+",
            width=80,
            height=80,
            font=("Segoe UI", 36, "bold"),
            command=self.show_add_task_window,
            fg_color="#7f9cf5",
            hover_color="#a3bffa",
            text_color="#181c2f",
            corner_radius=40,
            border_width=3,
            border_color="#a3bffa"
        )
        self.floating_button.place(relx=0.95, rely=0.95, anchor="se")

    def get_priority_color(self, priority, completed=False):
        if completed:
            return "#3e4a5e"  # Muted blue-gray for completed tasks
        elif priority == "High":
            return "#7c3aed"  # Soft purple
        elif priority == "Medium":
            return "#7f9cf5"  # Soft blue
        else:
            return "#a3bffa"  # Lighter blue

    def get_priority_text_color(self, completed=False):
        if completed:
            return "#b0b0b0"
        else:
            return "#181c2f"

    def create_task_card(self, task, index):
        row = index // 3
        col = index % 3

        card_frame = ctk.CTkFrame(
            self.tasks_frame,
            fg_color=self.get_priority_color(task["priority"], task["completed"]),
            width=280,
            height=180,
            corner_radius=18,
            border_width=2,
            border_color="#e0e7ff"
        )
        card_frame.grid(row=row, column=col, padx=18, pady=18, sticky="nsew")
        card_frame.grid_propagate(False)
        card_frame.grid_columnconfigure(0, weight=1)

        overlay_frame = ctk.CTkFrame(
            card_frame,
            fg_color="transparent",
            corner_radius=18
        )
        overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        priority_badge = ctk.CTkLabel(
            overlay_frame,
            text=task["priority"],
            font=("Segoe UI", 11, "bold"),
            text_color="#ffffff",
            fg_color="transparent"
        )
        priority_badge.grid(row=0, column=0, padx=8, pady=8, sticky="ne")

        completed_var = ctk.BooleanVar(value=task["completed"])
        checkbox = ctk.CTkCheckBox(
            overlay_frame,
            text="",
            variable=completed_var,
            command=lambda: self.toggle_task_completion(index),
            fg_color=self.get_priority_text_color(task["completed"]),
            hover_color=self.get_priority_text_color(task["completed"])
        )
        checkbox.grid(row=0, column=0, padx=8, pady=8, sticky="nw")

        details_frame = ctk.CTkFrame(overlay_frame, fg_color="transparent")
        details_frame.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        details_frame.grid_columnconfigure(0, weight=1)

        desc_text = task["description"][:40] + "..." if len(task["description"]) > 40 else task["description"]
        desc_label = ctk.CTkLabel(
            details_frame,
            text=desc_text,
            font=("Segoe UI", 14, "bold" if not task["completed"] else "normal"),
            text_color=self.get_priority_text_color(task["completed"])
        )
        desc_label.grid(row=0, column=0, sticky="w")

        due_label = ctk.CTkLabel(
            details_frame,
            text=f"Priority: {task['priority']} | Due: {task['due_date']}",
            font=("Segoe UI", 11),
            text_color=self.get_priority_text_color(task["completed"])
        )
        due_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        buttons_frame = ctk.CTkFrame(overlay_frame, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, padx=8, pady=8, sticky="ew")

        edit_button = ctk.CTkButton(
            buttons_frame,
            text="Edit",
            width=60,
            height=30,
            command=lambda: self.edit_task(index),
            font=("Segoe UI", 11),
            fg_color="#e0e7ff",
            text_color="#181c2f",
            hover_color="#a3bffa"
        )
        edit_button.grid(row=0, column=0, padx=4)

        delete_button = ctk.CTkButton(
            buttons_frame,
            text="Del",
            width=60,
            height=30,
            command=lambda: self.delete_task(index),
            font=("Segoe UI", 11),
            fg_color="#e0e7ff",
            text_color="#181c2f",
            hover_color="#a3bffa"
        )
        delete_button.grid(row=0, column=1, padx=4)

    def show_add_task_window(self):
        add_window = ctk.CTkToplevel(self)
        add_window.title("Add New Task")
        add_window.geometry("400x500")
        add_window.resizable(False, False)
        add_window.configure(fg_color="#23294a")
        add_window.grab_set()
        add_window.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            add_window,
            text="Add New Task",
            font=("Segoe UI", 20, "bold"),
            text_color="#a3bffa"
        )
        title_label.grid(row=0, column=0, pady=20)

        task_entry = ctk.CTkEntry(
            add_window,
            placeholder_text="Enter task description...",
            font=("Segoe UI", 14),
            width=300
        )
        task_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        priority_var = ctk.StringVar(value="Medium")
        priority_dropdown = ctk.CTkOptionMenu(
            add_window,
            values=["Low", "Medium", "High"],
            variable=priority_var,
            font=("Segoe UI", 14),
            width=300
        )
        priority_dropdown.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        date_label = ctk.CTkLabel(
            add_window,
            text="Due Date:",
            font=("Segoe UI", 14, "bold"),
            text_color="#a3bffa"
        )
        date_label.grid(row=3, column=0, pady=(20, 5), sticky="w", padx=20)

        due_date_entry = DatePickerFrame(add_window)
        due_date_entry.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        def add_task_from_window():
            description = task_entry.get().strip()
            priority = priority_var.get()
            due_date = due_date_entry.get_date()

            if not description:
                messagebox.showwarning("Warning", "Please enter a task description!")
                return

            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                    return

            task = {
                "description": description,
                "priority": priority,
                "due_date": due_date,
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "completed": False
            }

            self.tasks.append(task)
            self.save_tasks()
            self.refresh_tasks()
            add_window.destroy()

        add_button = ctk.CTkButton(
            add_window,
            text="Add Task",
            command=add_task_from_window,
            font=("Segoe UI", 16, "bold"),
            width=300,
            height=40,
            fg_color="#7f9cf5",
            text_color="#181c2f",
            hover_color="#a3bffa"
        )
        add_button.grid(row=5, column=0, padx=20, pady=20)

        cancel_button = ctk.CTkButton(
            add_window,
            text="Cancel",
            command=add_window.destroy,
            font=("Segoe UI", 14),
            width=300,
            height=35,
            fg_color="#e0e7ff",
            text_color="#181c2f",
            hover_color="#a3bffa"
        )
        cancel_button.grid(row=6, column=0, padx=20, pady=10)

    def edit_task(self, index):
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            edit_window = ctk.CTkToplevel(self)
            edit_window.title("Edit Task")
            edit_window.geometry("400x300")
            edit_window.resizable(False, False)
            edit_window.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(edit_window, text="Task Description:", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
            desc_entry = ctk.CTkEntry(edit_window, font=("Segoe UI", 14))
            desc_entry.insert(0, task["description"])
            desc_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

            ctk.CTkLabel(edit_window, text="Priority:", font=("Segoe UI", 14, "bold")).grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")
            priority_var = ctk.StringVar(value=task["priority"])
            priority_dropdown = ctk.CTkOptionMenu(
                edit_window,
                values=["Low", "Medium", "High"],
                variable=priority_var,
                font=("Segoe UI", 14)
            )
            priority_dropdown.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

            ctk.CTkLabel(edit_window, text="Due Date (YYYY-MM-DD):", font=("Segoe UI", 14, "bold")).grid(row=4, column=0, padx=10, pady=(10, 5), sticky="w")
            due_entry = ctk.CTkEntry(edit_window, font=("Segoe UI", 14))
            due_entry.insert(0, task["due_date"])
            due_entry.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

            def save_changes():
                new_desc = desc_entry.get().strip()
                new_priority = priority_var.get()
                new_due = due_entry.get().strip()

                if not new_desc:
                    messagebox.showwarning("Warning", "Please enter a task description!")
                    return

                if new_due:
                    try:
                        datetime.strptime(new_due, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                        return

                self.tasks[index]["description"] = new_desc
                self.tasks[index]["priority"] = new_priority
                self.tasks[index]["due_date"] = new_due

                self.save_tasks()
                self.refresh_tasks()
                edit_window.destroy()

            save_button = ctk.CTkButton(
                edit_window,
                text="Save Changes",
                command=save_changes,
                font=("Segoe UI", 14),
                fg_color="#7f9cf5",
                text_color="#181c2f",
                hover_color="#a3bffa"
            )
            save_button.grid(row=6, column=0, padx=10, pady=20)

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            result = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?")
            if result:
                del self.tasks[index]
                self.save_tasks()
                self.refresh_tasks()

    def toggle_task_completion(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["completed"] = not self.tasks[index]["completed"]
            self.save_tasks()
            self.refresh_tasks()

    def refresh_tasks(self):
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        sorted_tasks = sorted(self.tasks, key=lambda x: (
            x["completed"],
            {"High": 0, "Medium": 1, "Low": 2}[x["priority"]],
            x["due_date"] if x["due_date"] != "No due date" else "9999-12-31"
        ))

        for i, task in enumerate(sorted_tasks):
            self.create_task_card(task, i)

    def toggle_theme(self):
        if self.theme_mode == "light":
            self.theme_mode = "dark"
            self.theme_button.configure(text="☀️")
            ctk.set_appearance_mode("dark")
            self.header.configure(text_color="#a3bffa")
        else:
            self.theme_mode = "light"
            self.theme_button.configure(text="🌙")
            ctk.set_appearance_mode("light")
            self.header.configure(text_color="#181c2f")
        self.refresh_tasks()

    def save_tasks(self):
        with open("tasks.json", "w") as f:
            json.dump(self.tasks, f, indent=2)

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            try:
                with open("tasks.json", "r") as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []
        else:
            self.tasks = []

class DatePickerFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.date_var = ctk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        self.date_entry = ctk.CTkEntry(
            self,
            placeholder_text="Due date (YYYY-MM-DD)",
            font=("Segoe UI", 14),
            textvariable=self.date_var
        )
        self.date_entry.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")

        self.calendar_button = ctk.CTkButton(
            self,
            text="📅",
            width=40,
            command=self.show_calendar
        )
        self.calendar_button.grid(row=0, column=1, padx=(0, 5), pady=5)

        self.clear_button = ctk.CTkButton(
            self,
            text="✕",
            width=40,
            command=self.clear_date
        )
        self.clear_button.grid(row=0, column=2, padx=0, pady=5)

        self.grid_columnconfigure(0, weight=1)

    def show_calendar(self):
        calendar_window = ctk.CTkToplevel(self)
        calendar_window.title("Select Date")
        calendar_window.geometry("300x250")
        calendar_window.resizable(False, False)
        calendar_window.grab_set()

        cal = DateEntry(
            calendar_window,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        cal.pack(padx=20, pady=20)

        buttons_frame = ctk.CTkFrame(calendar_window)
        buttons_frame.pack(pady=20)

        def select_date():
            selected_date = cal.get_date()
            self.date_var.set(selected_date.strftime("%Y-%m-%d"))
            calendar_window.destroy()

        def cancel():
            calendar_window.destroy()

        select_button = ctk.CTkButton(
            buttons_frame,
            text="Select",
            command=select_date
        )
        select_button.pack(side="left", padx=5)

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=cancel
        )
        cancel_button.pack(side="left", padx=5)

    def clear_date(self):
        self.date_var.set("")

    def get_date(self):
        return self.date_var.get()

    def set_date(self, date):
        self.date_var.set(date)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = TodoApp()
    app.protocol("WM_DELETE_WINDOW", app.quit)
    app.mainloop()
