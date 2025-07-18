import random
import tkinter


def tweaks():
    def legacy_login():
        def login():
            global username, password
            username = _username.get()
            password = _password.get()
            win.destroy()

        _username = Entry(win)
        _password = Entry(win)
        _username.pack()
        _password.pack()
        Button(win, text='Login', command=login).pack()

    def temp():
        global username, password
        username = str(random.randint(100000000, 9999999999))
        password = str(random.randint(100000000, 9999999999))
        win.destroy()

    win = tkinter.Tk()
    win.title('Login Tweaks')
    Button(win, text='Login without password encrypt (Legacy Login)', command=legacy_login).pack()
    Button(win, text='Login with Temporary Account', command=temp).pack()



Button(text='Login Tweaks', command=tweaks).place(x=500, y=400, anchor='se')