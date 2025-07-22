# downloaded from msgr-patches!

import math
import os.path
import sys
from tkinter import TclError
import tkinter
from typing import Literal, Union
import data.lib.ru_to_en

_ADVLOG = False # DO ADVLOG
_MODULE_LOG = True # DO ANY THIS MODULE LOGS

_windows = []
_widgets = {}
app_root_window = None
root_scaling = 1.0

def lift_popups():
    for _w in _widgets:
        if isinstance(_w, Popup):
            try:
                _w.lift()
                _w.focus_set()
            except TclError:
                print(f'Failed to lift {_w}')


def update_win_scaling():
    print(f'`````````````````````````````{_windows}, {root_scaling}')
    for _win in _windows:
        try:
            _win.tk.call('tk', 'scaling', root_scaling)
        except TclError:
            pass

#class LogMeta(type):
#    def __new__(cls, name, bases, dct):
#        new_class = super().__new__(cls, name, bases, dct)
#        return new_class
#
#class AdvLog(metaclass=LogMeta):
#    def __getattribute__(self, name):
#        attr = super().__getattribute__(name)
#        if callable(attr):
#            def wrapper(*args, **kwargs):
#                if isinstance(self, Widget) and _ADVLOG:
#                    args_str = ''
#                    kwa_str = ''
#                    for _arg in args:
#                        args_str += _arg + ', '
#                    for _kwarg_n, _kwarg_v in kwargs.items():
#                        kwa_str += _kwarg_n + '=' + str(_kwarg_v) + ', '
#                    if kwa_str == '':
#                        args_str = args_str[:-2:]
#                    print_adv(f'[advlog][{self._name}] call {self._name}.{name}({args_str}{kwa_str[:-2:]})')
#                elif isinstance(self, Win) and _ADVLOG:
#                    if name not in ['_root', '_nametowidget', '_register', 'deletecommand', 'after', '_substitute']:
#                        args_str = ''
#                        kwa_str = ''
#                        for _arg in args:
#                            args_str += str(_arg) + ', '
#                        for _kwarg_n, _kwarg_v in kwargs.items():
#                            kwa_str += str(_kwarg_n) + '=' + str(_kwarg_v) + ', '
#                        if kwa_str == '':
#                            args_str = args_str[:-2:]
#                        print_adv(f"[advlog][{self}] called {name}({args_str}{kwa_str[:-2:]})")
#                else:
#                    if _ADVLOG:
#                        print_adv(f"[advlog][{self}] called {name}")
#                return attr(*args, **kwargs)
#            return wrapper
#        return attr
class AdvLog:
    pass

BLACK_LIST_LOGGING = ['empty name']
if __name__ != '__main__':
    with open('./data/logs/btae_ui.log', 'w'):
        pass
    with open('./data/logs/advlog_btae_ui.log', 'w'):
        pass
    def print_adv(v):
        _out = True
        for i in BLACK_LIST_LOGGING:
            if i in v:
                _out = False
                break
        if _out and _MODULE_LOG:
            print(f'[{os.path.basename(__file__)}]{v}')
            if 'advlog' not in v:
                with open(f'./data/logs/btae_ui.log', 'a') as fl:
                    try:
                        fl.write(f'[{os.path.basename(__file__)}]{v}\n')
                    except UnicodeError:
                        fl.write(f'[{os.path.basename(__file__)}]{data.lib.ru_to_en.replace_letters(v)}\n')
            else:
                with open('./data/logs/advlog_btae_ui.log', 'a') as fl:
                    try:
                        fl.write(f'[{os.path.basename(__file__)}]{v}\n')
                    except UnicodeError:
                        fl.write(f'[{os.path.basename(__file__)}]{data.lib.ru_to_en.replace_letters(v)}\n')
else:
    def print_adv(v):
        print(v)


def _pass():
    pass

class Widget(AdvLog):
    def __init__(self, mast, obj, name: str, **kw):
        self._root_win = mast
        self.tk = obj
        self._kwargs = kw
        self._name = name
        self._place_mode = 'NotPlaced'
        self.destroyed = False
        if 'widgets' not in _widgets:
            _widgets['widgets'] = {}
            _widgets['widgets'][self._name] = self
        else:
            _widgets['widgets'][self._name] = self

    def build(self, mode: Literal['place', 'grid', 'pack'], **kwargs):
        print_adv(f'[{self._name}] build {mode}')
        if mode == 'place':
            self.tk.place(**kwargs)
        elif mode == 'grid':
            self.tk.grid(**kwargs)
        elif mode == 'pack':
            self.tk.pack(**kwargs)
        self._place_mode = mode

    def forget(self):
        if self._place_mode == 'place':
            self.tk.place_forget()
        elif self._place_mode == 'grid':
            self.tk.grid_forget()
        elif self._place_mode == 'pack':
            self.tk.pack_forget()

    def destroy(self):
        try:
            if self.tk.winfo_exists():
                self.forget()
                self.tk.destroy()
                print_adv(f'[{self._name}] {self._name} destroyed')
                self.destroyed = True
        except TclError as e:
            print_adv(f'[{self._name}] Error destroying: {e}')

    def configure(self, **kwargs):
        self.tk.configure(**kwargs)

    def __getitem__(self, item):
        return self.tk[item]

    def __setitem__(self, key, value):
        self.tk[key] = value


class CallBack:
    def __init__(self, target = _pass):
        self.Target = target


class ProgressBar(tkinter.Label):
    def __init__(self, len_to_count=100, **kwargs):
        super().__init__(**kwargs)
        self.percentage = 0
        self._ltc = len_to_count
        self._progress = "." * 100

        self['text'] = f'[{self._progress}] {self.percentage}/100'

    def plus(self, v=1):
        if self.percentage < 100:
            self.percentage += math.ceil(v * self._gen_percent())
            self._progress = '|' * self.percentage + '.' * (100 - self.percentage)
            try:
                if self.winfo_exists():
                    self['text'] = f'[{self._progress}] {self.percentage}/100'
            except TclError:
                pass
        else:
            self['text'] = f'[{self._progress}] Completed'
        self.update()

    def _gen_percent(self):
        return 100 / self._ltc



class Button(tkinter.Button):
    def __init__(self, master=None, command="", **kwargs):
        if command != "":
            command = self._wrap_command(command)
        super().__init__(
            master=master,
            command=command,
            **kwargs
        )

    @staticmethod
    def _wrap_command(cmd):
        def safe_command():
            try:
                cmd()
            except Exception as e:
                sys.excepthook(type(e), e, e.__traceback__)
        return safe_command


class Label(tkinter.Label):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master=master,
            **kwargs)


class Text(tkinter.Text):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master=master,
            **kwargs)


class Entry(tkinter.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(
           master=master,
           **kwargs)


class Listbox(tkinter.Listbox):
    def __init__(self, master=None, **kwargs):
        super().__init__(
           master=master,
           **kwargs)
        self._scrolled = 0
        self._data = []
        self.bind('<<MouseWheel>>', self._scroll_hook)

    def _scroll_hook(self, event):
        if 0 < self._scrolled < len(self.get('0', 'end').split('\n')):
            self._scrolled + event.delta // 120

    def update(self):
        super().delete('0', 'end')
        for _elem in self._data:
            super().insert("end", _elem)
        super().update()

    def insert(self, index: int | Literal['end'], *elements):
        if index == 'end':
            for _elem in elements:
                self._data.append(_elem)
        elif isinstance(index, int):
            for _elem in elements:
                self._data.insert(index, _elem)
        self.update()

    def delete(self, first: int, last: int | Literal['end'] | None = None):
        if last is int or last == 'end':
            if last == 'end':
                last = len(self._data)
            for _ in range(first, last):
                self._data.pop(first)
        else:
            self._data.pop(first)
        self.update()




POSSIBLE_WIDGETS = [Label, Button, Text, Entry, ProgressBar]
POSSIBLE_WIDGETS_TK = [tkinter.Label, tkinter.Button, tkinter.Text, tkinter.Entry]


class Win(tkinter.Tk, AdvLog):
    """Advanced Tk Widget"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.his = {}
        self._registered_widgets = []
        self.his_being = {}
        self.widgets_name = []
        self.recovery_widgets = []
        self._work_threads = False
        self.bind('<Control-s>', self.recovery)
        _windows.append(self)
        if app_root_window is None:
            self.force_main()

    def recovery(self, event=None):
        """Recovery menu"""
        self.destroy_all_in(True)
        for i in self.recovery_widgets:
            if callable(i):
                i()
            else:
                self.create(i['name'], i['obj'], recreate_if_exists=True, **i['kwargs']).build(i['place_mode'], **i['place_kw'])


    def geometry(self, size=None, pos=None):
        """Sets / gets window's geometry & pos"""
        if size is None:
            size = []
        if pos is None:
            pos = []
        if size:
            super().geometry(f'{size[0]}x{size[1]}')
        if pos:
            super().geometry(f'{super().geometry().split("+")[0]}+{pos[0]}+{pos[1]}')
        if not size and not pos:
            return super().geometry()
        return None

    def create(self, name: str, obj, recreate_if_exists=False, **kwargs) -> Widget:
        """Creates widgets, then returns created"""
        print_adv(f'[win {self.title()}] creating widget {name}')
        if name in self.his:
            if not recreate_if_exists:
                print(f'{name} is already created')
            else:
                self.his[name].destroy()
                self.his.pop(name)
        if not callable(obj):
            raise TypeError(f"Widget {obj} can't be not callable")
        create_kw = kwargs
        self.his[name] = Widget(self, obj(**create_kw), name=name)
        self._registered_widgets.append(self.his[name].tk)
        self.his_being.update({name: self.his[name]})
        self.widgets_name.append(name)
        return self.his[name]

    def being_ping(self):
        ans = {}
        for name in self.his_being:
            ans.update({name: self.his_being[name].tk.winfo_exists()})
        return ans

    def create_abstract(self, name: str, obj: CallBack):
        self.his.update({name: obj})

    def destroy_all_in(self, dont_create_help=False):
        print_adv(f'[win {self.title()}] destroying all widgets')
        for name in list(self.his.keys()):
            print_adv(f"[win {self.title()}] Destroying: {name}")
            self.his[name].destroy()
        for n in self.winfo_children():
            n.place_forget()
            n.pack_forget()
            n.grid_forget()
        self.config(bg=Button()['bg'])
        self.his = {}
        self.update()

    def update(self):
        super().update()

    def __getitem__(self, item):
        return self.his[item]

    def tk_thread(self, target, sleep_time, /, *args):
        """'thread' created by main.after
        :param target: target function
        :param sleep_time: time before calling target again
        :param args: *args for target

        to stop call Win().stop_threads()"""
        def wrapper(*_args):
            _ret = target(*_args)
            if _ret != -1:
                self.after(sleep_time, wrapper, *args)
        wrapper(*args)

    def force_main(self):
        """Forces window to be root (ui.app_root_window)"""
        global app_root_window
        app_root_window = self


class SidePanelWidget:
    def __init__(self, win: Union[Win, tkinter.Tk], style=None, _side: Literal['R', 'L'] = 'R', title: str = 'Side Panel'):
        self.his = {}
        self._title = title
        if isinstance(win, Win):
            self._win = win
        else:
            self._win = win
        self._side = _side
        self._o = None
        self._widgets = []
        if style is None:
            self._style = ['SystemButtonFace', 'SystemButtonText', 'TkDefaultFont']
        else:
            self._style = style
        self._font = tuple(self._style[2].split(':'))
        if len(self._font) == 1:
            self._font = (self._style[2])

    def build(self):
        print_adv(f'[side {self._title}] BUILDING')
        size = self._win.geometry().split('+')[0].split('x')
        size_x = int(size[0])
        size_y = int(size[1])
        pos_x = 0
        if self._side == 'L':
            pos_x = size_x - size_x // 3

        print_adv(f'[side {self._title}] CANVAS PROCESS')
        if not isinstance(self._win, Win):
            self._o = tkinter.Canvas(self._win, bg=self._style[0], height=size_y, width=size_x // 3)
        else:
            self._o = self._win.create(f'side-panel-_o-root${self._title}$', tkinter.Canvas, bg=self._style[0], height=size_y, width=size_x // 3).tk
        self._o.place(x=pos_x, y=0)

        print_adv(f'[side {self._title}] BASE BUTTONS')
        close_btn = tkinter.Button(self._o, text='X', command=self.destroy, bg=self._style[0], fg=self._style[1], font=self._font)
        self._o.create_window(10, 15, window=close_btn)

        title_label = tkinter.Label(self._o, text=self._title, bg=self._style[0], fg=self._style[1], font=self._font)
        self._o.create_window(25, 15, window=title_label, anchor='w')

        print_adv(f'[side {self._title}] CUSTOM WIDGETS')
        self._custom_create()
        self.his.update({'_O': self._o})
        print_adv(f'[side {self._title}] BUILD')

    def create(self, widget, x, y, name: str = '',  **kw):
        if self._o is None and {'widget': widget, 'x': x, 'y': y, 'name': name, 'kw': kw} not in self._widgets:
            if name != '':
                print_adv(f'[side {self._title}] p recreating {name}')
            else:
                try:
                    print_adv(f'[side {self._title}] p recreating empty name text={widget["text"]}')
                except TclError:
                    print_adv(f'[side {self._title}] p recreating empty name')
            self._widgets.append({'widget': widget, 'x': x, 'y': y, 'name': name, 'kw': kw})
            return None
        else:
            print_adv(f'[side {self._title}] creating {name}')
            if name != '':
                print_adv(f'[side {self._title}] NAME EXISTS')
                self.his.update({name: {'widget': widget, 'x': x, 'y': y, 'kw': kw}})
            if not isinstance(widget, int):
                print(f'[side {self._title}] Creating {widget}, {x}, {y}, {name}, {kw}')
                if widget.winfo_exists() and widget.winfo_parent():
                    new_widget = self._create_widget_copy(widget)
                    item = self._o.create_window(x, y, window=new_widget, **kw) # If it fails, you forget to call build
                else:
                    widget.configure(bg=self._style[0], fg=self._style[1], font=self._font)
                    item = self._o.create_window(x, y, window=widget, **kw)
                self._o.tag_raise(item)
            else:
                item = widget
            return item

    def _custom_create(self):
        for widget_info in self._widgets:
            if list(widget_info.keys()) != ['widget']:
                self.create(widget_info['widget'], widget_info['x'], widget_info['y'], widget_info['name'],
                        **widget_info['kw'])

    def destroy(self):
        for item in self._widgets:
            try:
                if isinstance(item['widget'], tkinter.Widget):
                    item['widget'].destroy()
            except TclError:
                pass
        self._widgets.clear()
        try:
            if isinstance(self._win, Win):
                try:
                    self._win.his.pop(f'side-panel-_o-root${self._title}$')
                except KeyError:
                    pass
            if self._o:
                self._o.destroy()
        except AttributeError:
            pass
        self._o = None

    def _create_widget_copy(self, original):
        widget_class = original.__class__
        config = original.configure()

        new_widget = widget_class(self._o)

        for key in config:
            if key not in ['class', 'master']:
                new_widget[key] = original[key]

        if 'command' in original.keys():
            new_widget.config(command=original['command'])
        try:
            new_widget.config(bg=self._style[0], fg=self._style[1], font=self._font)
        except TclError:
            pass

        return new_widget


class SidePanel(SidePanelWidget):
    def __init__(self, win: Union[Win, tkinter.Tk], style=None, _side: Literal['R', 'L'] = 'R', title: str = 'Side Panel'):
        super().__init__(win, style, _side, title)
        self.custom_widgets = []

    def create_custom_widget(self, widget, x: int, y: int, name: str = '', **kw):
        self.custom_widgets.append({'widget': widget, 'x': x, 'y': y, 'name': name, 'kw': kw})

    def build(self):
        for i in self.custom_widgets:
            self.create(i['widget'], i['x'], i['y'], i['name'], **i['kw'])
        super().build()


class Popup(tkinter.Frame):
    def __init__(self, master: Win | tkinter.Tk = app_root_window, x: int = -1, y: int = -1, size=None,
                 style=None, title: str = 'Popup'):
        if size is None:
            size = [300, 300]
        if master is None:
            master = app_root_window
        if x == -1:
            x = master.winfo_width() // 2
        if y == -1:
            y = master.winfo_height() // 2
        self.style = style
        self.size = size
        super().__init__(master, width=size[0], height=size[1], highlightthickness=2)
        if style is not None:
            self.configure(bg=style[0], highlightcolor=style[1])

        self.pack_propagate(False)
        self.close_btn = Button(self, text='X', command=self.place_forget)
        self.close_btn.pack(anchor='ne')
        self.title_lbl = Label(self, text=title)
        self.title_lbl.place(x=3, y=0)
        if style is not None:
            self.close_btn.configure(bg=style[0], fg=style[1], font=style[2])
            self.title_lbl.configure(bg=style[0], fg=style[1], font=style[2])

        self.bind('<Button-1>', self._start_move)
        self.bind('<B1-Motion>', self._move)

        self._start_x = 0
        self._start_y = 0
        if 'popups' in _widgets:
            _widgets['popups'][self.title_lbl['text']] = self
        else:
            _widgets['popups'] = {}
            _widgets['popups'][self.title_lbl['text']] = self

        self.place(x=x, y=y, anchor='center')

    def _start_move(self, event):
        self.lift()
        self._start_x = event.x
        self._start_y = event.y

    def _move(self, event):
        x = (event.widget.winfo_x() + (event.x - self._start_x)) + (self.winfo_width() // 2)
        y = (event.widget.winfo_y() + (event.y - self._start_y)) + (self.winfo_height() // 2)
        if not self.master.winfo_width() - (self.winfo_width()) > x - (self.winfo_width() // 2) > 0:
            x = self.winfo_x() + (self.winfo_width() // 2)
        if not self.master.winfo_height() - (self.winfo_height()) > y - (self.winfo_height() // 2) > 0:
            y = self.winfo_y() + (self.winfo_height() // 2)
        #self.title['text'] = f'{self.master.winfo_width()} > {x} > 0, {self.master.winfo_height()} > {y} > 0'
        self.place(x=x, y=y)

    def update_info(self):
        self._start_x = 0
        self._start_y = 0
        self.update_idletasks()

    def resizable(self, x, y):
        if x or y:
            self.pack_propagate(True)
        else:
            self.pack_propagate(False)

    def title(self, t):
        self.title_lbl['text'] = t


class SidePanelRevision(Popup):
    """Revision of SidePanel, using Popup class"""
    def __init__(self, master: Win = app_root_window, style=None, title: str = 'SidePanelRevision'):
        if style is None:
            style = ['black', 'white', 'Consolas 9']
        super().__init__(master, x=0, y=0, size=[master.winfo_width() // 3, master.winfo_height()], style=style, title=title)
        self.lift()
        self.unbind_all('<Button-1>')
        self.unbind_all('<B1-Motion>')
        self.place_forget()
        # Compatibility
        self._o = self
        self.build_state = False

    def build(self):
        self.lift()

        self.close_btn.config(bg=self.style[0], fg=self.style[1], font=self.style[2])
        self.title_lbl.config(bg=self.style[0], fg=self.style[1], font=self.style[2])
        self.config(height=self.master.winfo_height(), width=self.master.winfo_width() // 3)

        self.build_state = True
        self.place(x=0, y=0)

    def destroy(self):
        self.build_state = False
        self.place_forget()

    def _move(self, event):
        ...

    def _start_move(self, event):
        ...



class Beta:
    """Contains unfinished & broken things"""
    pass

if __name__ == '__main__':
    app = Win()
    side = SidePanel(app)
    app.create('_T_Button1', Button, text='123').build('pack')
    app.create('_T_Label1', Label, text='123').build('pack')
    app.create('_T_Entry1', Entry).build('pack')
    app.create('_T_Button2-side', Button, text='side', command=CallBack(side.build)).build('pack')
    side.create_custom_widget(Button(text='123'), 50, 50)
    app.create('_T_Button3', Button, text='destroy all w', command=CallBack(app.destroy_all_in)).build('pack')
    app.mainloop()

