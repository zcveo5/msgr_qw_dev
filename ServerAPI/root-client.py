import random
import subprocess
import sys
import threading
import time
import traceback
from tkinter import Listbox
from tkinter.messagebox import showerror
import data.lib.connect.auth
import data.lib.connect.chat_alt
from data.lib.ui import Win, Label, Button, tkinter, Entry
from tkinter.scrolledtext import ScrolledText

server: subprocess.Popen | None

def custom_exc_handler(exc_type, exc_value=None, exc_traceback=None):
    tb_lines = list(traceback.format_exception(exc_type, exc_value, exc_traceback))
    tb_text = "".join(tb_lines)
    print('===== TRACEBACK =====\n' + tb_text + f'\n===== END =====')
    showerror(f'Error: {exc_type.__class__}', tb_text)

sys.excepthook = custom_exc_handler
tkinter.report_callback_exception = custom_exc_handler
#sys.stdout = StringIO(' - ~ * $ Root Client $ * ~ - ')
work = True
server = None
log = [' ~ $ Server Not Started $ ~ ']

def read_logs():
    while work:
        for line in server.stdout:
            if line not in log:
                log.append(line)
                print(f'[SERVER] {line}')
        for line in server.stderr:
            if line not in log:
                log.append(line)
                print(f'[SERVER_SETERR] {line}')
        time.sleep(0.5)


def read_logs_ui():
    scrolled = 0
    def update_logs():
        logs_text.delete("0.0", "end")
        for i in log[scrolled:scrolled+20]:
            logs_text.insert("end", i)
        win.after(100, update_logs)
    def scroll(event):
        nonlocal scrolled
        temp = scrolled + event.delta // 120
        if 0 < temp < len(log):
            scrolled = temp
    win = tkinter.Tk()
    logs_text = ScrolledText(win)
    logs_text.pack()
    logs_text.bind('<<MouseWheel>>', scroll)
    win.resizable(False, False)
    update_logs()


def start_server():
    global server, log
    log = [' ~ $ Starting Server $ ~ \n']
    try:
        server = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    except Exception as _ex:
        showerror('Error', f'Error starting server: {_ex.__class__}\n\n{traceback.format_exc()}')

    threading.Thread(target=read_logs, daemon=True).start()
    root.create('StartClient', Button, recreate_if_exists=True, text='Start Root Client!', command=start_root_client).build('pack', anchor='nw')


def start_root_client():
    def start(event):
        try:
            RootClient(username.get(), password.get(),':'.join(log[1].split(':')[1::])[1:-1:])
        except Exception as root_client_error:
            showerror(f'{root_client_error.__class__}', traceback.format_exc())
            print(traceback.format_exc())
    win = tkinter.Tk()
    win.title('auth')
    win.resizable(False, False)
    Label(win, text='account').pack()
    username = Entry(win)
    username.pack()
    username.bind('<Return>', start)
    password = Entry(win)
    password.pack()
    password.bind('<Return>', start)


class RootClient:
    def __init__(self, username, password, addr):
        global client
        client = self
        self._user = username
        self._addr = addr
        self._theme = './data/themes/hh.theme'
        self.win = Win()
        self.win.geometry([900, 500])
        self.win.title(f'ROOT:MSGR-QW AS {username} AT {addr}')
        self.win.resizable(False, False)
        Label(self.win, text='Authenticating...').pack(anchor='nw')
        print(addr)
        self.auth = data.lib.connect.auth.User(username, password, addr.split(':')[0], int(addr.split(':')[1]))
        self.chat = data.lib.connect.chat_alt.Chat(addr.split(':')[0], int(addr.split(':')[1]), username)
        self.chat.send({'action_for_chat_server': 'MyUSER', 'username': username})
        self.chat.connect()
        self.online_list = Listbox(self.win)
        self.online_list.pack(anchor='se')
        self.win.tk_thread(self.update_info, 100)
        threading.Thread(target=self.chat.async_recv, daemon=True).start()
        self.user_data = self.auth.get_data()
        Label(self.win, text=self.user_data).pack(anchor='nw')
        Button(self.win, text='Refresh', command=self.ui).pack(anchor='ne')


    def update_info(self):
        self.online_list.insert("end", 'users online')
        self.chat.send({'action_for_chat_server': 'OnlineList'})
        self.online_list.delete("0", 'end')
        for i in self.chat.online_list():
            self.online_list.insert("end", i)


    def ui(self):
        self.win.destroy_all_in()
        Button(self.win, text='Refresh', command=self.ui).pack(anchor='ne')
        self.online_list = Listbox(self.win)
        self.online_list.pack(anchor='se')



client: RootClient | None
client = None
root = Win()
root.geometry([900, 500])
root.resizable(False, False)
root.create('WelcomeLbl', Label, text='Welcome to Root Client!').build('pack', anchor='nw')
root.create('StartServer', Button, text='Start Server', command=start_server).build('pack', anchor='nw')
root.create('ReadLogs', Button, text='Read Server Logs', command=read_logs_ui).build('pack', anchor='nw')
#root.create('ReadRootLogs', Button, text='Read Program Logs', command=read_logs_root_ui).build('pack', anchor='nw')
root.mainloop()
