import tkinter as tk

ui = tk.Tk()
ui.title('ADV for Jb')
try:
    tk.Label(ui, text='\n'.join(globals()['__JailBreakTweaks__'])).pack()
except KeyError:
    tk.Label(ui, text='\n'.join(globals().keys())).pack()
main.tk_thread(ui.update, 100)