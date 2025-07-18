import threading
from tkinter import Label, Button
from jailbreak import ModWin

def reinit_ui_mod(*args, **kwargs):
    main.wm_geometry('900x500')
    orig_reinit_ui(*args, **kwargs)


class _Obj:
    def __getattribute__(self, item):
        print(f'[*] $JBLS emulating {item}')
        return _Obj()

    def __call__(self, *args, **kwargs):
        ...

def work_loop():
    global work
    work = True

orig_reinit_ui = reinit_ui
reinit_ui = reinit_ui_mod

main.quit() ; main.destroy()
main = ModWin()
main.wm_geometry('900x500')
main.adv = 'Legacy'
#main.resizable(False, False)
load_lbl = Label(justify='left')
load_lbl.place(x=0, y=30)
exit_button = Button(text='exit', command=exit)
exit_button.pack(anchor='nw')
action_load = Button(text='action')
action_load.pack(anchor='nw')
pb = _Obj()
Button(text='work=True', command=work_loop).pack()
Button(text='quit', command=main.quit).pack()

bt_server_data = (True, {'password': '123123123'})
receive_thread = _Obj()
exec(open('./jaillib.py', 'r').read())