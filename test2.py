import tkinter as tk


class DragManager:
    def __init__(self, widget):
        self.widget = widget
        self.drag_start_x = 0
        self.drag_start_y = 0

        widget.bind("<Button-1>", self.on_drag_start)
        widget.bind("<B1-Motion>", self.on_drag_move)

    def on_drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        # Визуальный фидбек
        #self.widget.config(relief=tk.SUNKEN)

    def on_drag_move(self, event):
        # Вычисляем новую позицию ОТНОСИТЕЛЬНО окна
        x = self.widget.winfo_x() + (event.x - self.drag_start_x)
        y = self.widget.winfo_y() + (event.y - self.drag_start_y)

        # Плавное перемещение БЕЗ пересоздания
        self.widget.place(x=x, y=y)


# Использование
root = tk.Tk()
frame = tk.Label(text='Hi')
frame.place(x=50, y=50)

# Применяем менеджер перемещения
DragManager(frame)

root.geometry("400x300")
root.mainloop()