import tkinter as tk
import traceback


def ask_for_input(prompt):
    popup = tk.Tk()
    tk.Label(popup, text=prompt).pack()
    v = tk.Entry(popup)
    v.pack()
    tk.Button(popup, text='Confirm', command=popup.quit).pack()
    popup.mainloop()
    val = v.get()
    popup.destroy()
    return val


def pp(*args, **kwargs):
    try:
        output.configure(state='normal')
        output.insert('end', f'{args[0]}')
        output.insert('end', '''
''')
        output.update()
        output.configure(state='disabled')
    except tk.TclError:
        pass


def execute(event):
    def _exec(source):
        code = """
print = pp
input = ask_for_input\n""" + source

        try:
            exec(code, globals(), locals())
        except Exception as _ex:
            pp(f'Traceback received while executing:\n{traceback.format_exc()}')

    cmd = event.widget.get().split()
    if cmd[0] == '$local':
        _exec(' '.join(cmd[1::]))
    elif cmd[0] == '$file':
        _exec(open(f'{cmd[1]}', 'r').read())
    else:
        pp(f'Unknown command {cmd[0]}.\nCommands:\n$local executes code locally (exec)\n$file executes file (exec(open))')


terminal = tk.Tk()
terminal.resizable(True, False)
output = tk.Text(terminal)
output.pack(fill='both')
output.configure(state='disabled')
entry = tk.Entry(terminal, width=50)
entry.pack(fill='both')
entry.bind('<Return>', execute)

if __name__ == '__main__':
    terminal.mainloop()
else:
    main.tk_thread(terminal.update, 100)

