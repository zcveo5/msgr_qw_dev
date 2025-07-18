import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import json
import re


class JsonEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Editor")
        self.root.geometry("800x600")

        # Создаем интерфейс
        self.create_widgets()

        # Цвета для подсветки синтаксиса
        self.tag_configure()

        # Привязка событий
        self.text.bind('<KeyRelease>', self.highlight_syntax)

    def create_widgets(self):
        # Панель инструментов
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(toolbar, text="Открыть", command=self.open_file).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Сохранить", command=self.save_file).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Форматировать", command=self.format_json).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Проверить", command=self.validate_json).pack(side=tk.LEFT, padx=2)

        # Текстовое поле с прокруткой
        self.text = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.NONE,
            font=("Consolas", 12),
            undo=True
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Статус бар
        self.status = tk.Label(self.root, text="Готово", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def tag_configure(self):
        # Настройка тегов для подсветки синтаксиса
        self.text.tag_configure("key", foreground="blue")
        self.text.tag_configure("string", foreground="green")
        self.text.tag_configure("number", foreground="purple")
        self.text.tag_configure("boolean", foreground="red")
        self.text.tag_configure("null", foreground="orange")

    def highlight_syntax(self, event=None):
        # Очищаем все теги
        for tag in ["key", "string", "number", "boolean", "null"]:
            self.text.tag_remove(tag, "1.0", tk.END)

        # Получаем весь текст
        content = self.text.get("1.0", tk.END)

        # Подсветка ключей
        for match in re.finditer(r'"(.*?)"\s*:', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end() - 1}c"
            self.text.tag_add("key", start, end)

        # Подсветка строк
        for match in re.finditer(r'"(.*?)"', content):
            # Пропускаем ключи
            if content[match.end()] == ':':
                continue
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add("string", start, end)

        # Подсветка чисел
        for match in re.finditer(r'\b\d+(\.\d+)?\b', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add("number", start, end)

        # Подсветка булевых значений
        for word in ["true", "false"]:
            start = "1.0"
            while True:
                pos = self.text.search(word, start, stopindex=tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(word)}c"
                self.text.tag_add("boolean", pos, end)
                start = end

        # Подсветка null
        start = "1.0"
        while True:
            pos = self.text.search("null", start, stopindex=tk.END)
            if not pos:
                break
            end = f"{pos}+4c"
            self.text.tag_add("null", pos, end)
            start = end

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, content)
                self.format_json()
                self.status.config(text=f"Открыт: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")

    def save_file(self):
        content = self.text.get(1.0, tk.END).strip()
        if not content:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            # Проверяем валидность перед сохранением
            json.loads(content)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            self.status.config(text=f"Сохранено: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный JSON:\n{str(e)}")

    def format_json(self):
        try:
            content = self.text.get(1.0, tk.END).strip()
            if not content:
                return

            # Форматируем с отступами
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=4, ensure_ascii=False)

            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, formatted)
            self.status.config(text="JSON отформатирован")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный JSON:\n{str(e)}")

    def validate_json(self):
        try:
            content = self.text.get(1.0, tk.END).strip()
            if not content:
                return

            json.loads(content)
            messagebox.showinfo("Проверка", "JSON валиден!")
            self.status.config(text="JSON валиден")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный JSON:\n{str(e)}")
            self.status.config(text="Ошибка в JSON")


if __name__ == "__main__":
    root = tk.Tk()
    app = JsonEditor(root)
    root.mainloop()