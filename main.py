import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x600")

        # Данные тренировок
        self.trainings = []
        self.load_data()

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Фрейм для ввода данных
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10)

        # Поле даты
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, padx=5)

        # Поле типа тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, padx=5)
        self.type_combo = ttk.Combobox(
            input_frame,
            values=["Кардио", "Силовая", "Йога", "Растяжка", "Функциональная"]
        )
        self.type_combo.grid(row=0, column=3, padx=5)

        # Поле длительности
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, padx=5)
        self.duration_entry = ttk.Entry(input_frame)
        self.duration_entry.grid(row=0, column=5, padx=5)

        # Кнопка добавления тренировки
        add_button = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        add_button.grid(row=0, column=6, padx=5)

        # Таблица для отображения тренировок
        columns = ("ID", "Дата", "Тип тренировки", "Длительность (мин)")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Фрейм для фильтрации
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=10)

        # Фильтрация по типу тренировки
        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, padx=5)
        self.filter_type = ttk.Combobox(
            filter_frame,
            values=["Все"] + ["Кардио", "Силовая", "Йога", "Растяжка", "Функциональная"]
        )
        self.filter_type.set("Все")
        self.filter_type.grid(row=0, column=1, padx=5)

        # Фильтрация по дате
        ttk.Label(filter_frame, text="С даты (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5)
        self.start_date_entry = ttk.Entry(filter_frame)
        self.start_date_entry.grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="По дату (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5)
        self.end_date_entry = ttk.Entry(filter_frame)
        self.end_date_entry.grid(row=0, column=5, padx=5)

        # Кнопки фильтрации
        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=0, column=6, padx=5)

        clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        clear_filter_button.grid(row=0, column=7, padx=5)

    def validate_input(self, date_str, duration_str):
        """Проверка корректности ввода"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты (используйте ГГГГ-ММ-ДД)")
            return False

        try:
            duration = float(duration_str)
            if duration <= 0:
                messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат длительности")
            return False

        return True

    def add_training(self):
        """Добавление новой тренировки"""
        date_str = self.date_entry.get()
        training_type = self.type_combo.get()
        duration_str = self.duration_entry.get()

        if not all([date_str, training_type, duration_str]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        if not self.validate_input(date_str, duration_str):
            return

        training = {
            "id": len(self.trainings) + 1,
            "date": date_str,
            "type": training_type,
            "duration": float(duration_str)
        }

        self.trainings.append(training)
        self.save_data()
        self.refresh_table()
        self.clear_input()

    def clear_input(self):
        """Очистка полей ввода"""
        self.date_entry.delete(0, tk.END)
        self.type_combo.set("")
        self.duration_entry.delete(0, tk.END)

    def refresh_table(self, data=None):
        """Обновление таблицы с тренировками"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        display_data = data if data is not None else self.trainings

        for training in display_data:
            self.tree.insert("", "end", values=(
                training["id"],
                training["date"],
                training["type"],
                f"{training['duration']:.0f}"
            ))

    def apply_filter(self):
        """Применение фильтров"""
        filtered = self.trainings

        # Фильтр по типу тренировки
        type_filter = self.filter_type.get()
        if type_filter != "Все":
            filtered = [t for t in filtered if t["type"] == type_filter]

        # Фильтр по дате
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                filtered = [t for t in filtered
                           if datetime.strptime(t["date"], "%Y-%m-%d") >= start_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат начальной даты")
                return

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                filtered = [t for t in filtered
                           if datetime.strptime(t["date"], "%Y-%m-%d") <= end_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат конечной даты")
                return

        self.refresh_table(filtered)

    def clear_filter(self):
        """Сброс фильтров и обновление таблицы"""
        self.filter_type.set("Все")
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        self.refresh_table()

    def save_data(self):
        """Сохранение данных в JSON-файл"""
        try
def save_data(self):
        """Сохранение данных в JSON-файл"""
        try:
            with open("trainings.json", "w", encoding="utf-8") as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

    def load_data(self):
        """Загрузка данных из JSON-файла"""
        if os.path.exists("trainings.json"):
            try:
                with open("trainings.json", "r", encoding="utf-8") as f:
                    self.trainings = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
                self.trainings = []
        else:
            self.trainings = []

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
