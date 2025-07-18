from tkinter.messagebox import showerror

orig_Settings = Settings
globals()['__HasCompatibilityTweak__'] = True

class SideSettings(orig_Settings):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, '_o'):
            self._o = self.window
            self.window.geometry('200x400')
        self._create_base()
        if hasattr(self, '_base_widgets'):
            self._base_widgets += [Button(self._o, text='exit',
                           command=reinit_window, bg=default_bg,
                           fg=default_fg, font=font_theme)]
        if hasattr(self, 'adv'):
            self.adv += ' # Compatibility Tweak #'

    @staticmethod
    def create(obj=None, *args, **kwargs):
        if obj is not None:
            if hasattr(obj, 'pack'):
                obj.pack(anchor='nw')
        if args or kwargs:
            print(f'What is\n{args}\n{kwargs}')

    def _create_base(self):
        self.create(Label(), x=-100, y=-100, name='loaded')
        y = 30
        for wid in self._base_widgets:
            self.create(self.create_copy(wid), 5, y, f'Settings_Element:{y // 30}', anchor='nw')
            y += 30

    def build(self):
        self._create_base()


def reinit_window_mod(*args):
    global chat_window
    for i in main.winfo_children():
        i.place_forget()
        i.grid_forget()
        i.pack_forget()

    chat_window = Text(main, fg=default_fg, bg=default_bg, font=font_theme, width=110)
    chat_window.place(x=0, y=0)
    refresh(*args)


reinit_window = reinit_window_mod
globals()['settings'] = SideSettings
side_settings = globals()['settings']
Settings = SideSettings

orig_reinit = reinit_ui
def _reinit_ui(*args):
    orig_reinit(*args)
    print('# Compatibility Tweak UI Refresh #')
    Button(text='SideSettings Emulator', command=side_settings).place(x=800, y=100)

reinit_ui = _reinit_ui