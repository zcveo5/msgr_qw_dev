import json
import os
import shutil
import tkinter as tk_
from tkinter import ttk
from tkinter.messagebox import showerror
import data.lib.ui as btaeui

glb_msgr = None
settings_orig = None
SettingsModClass = None
side = None

root_path_plug = os.path.dirname(__file__).replace('\\'[0:1], '/')

class Plugin:
    @staticmethod
    def give_data(app):
        global glb_msgr, SettingsModClass, side
        glb_msgr = app

        class SettingsMod(glb_msgr.Settings):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._base_widgets.append(btaeui.Button(self._o, text='Multi NC Menu',
                                      command=nc_menu, bg=glb_msgr.default_bg,
                                      fg=glb_msgr.default_fg, font=glb_msgr.font_theme))

            #def _create_base(self):
            #    super()._create_base()
            #    self.create(btaeui.Button(self._o, text='Multi NC Menu',
            #                          command=nc_menu, bg=glb_msgr.default_bg,
            #                          fg=glb_msgr.default_fg, font=glb_msgr.font_theme),
            #                x=5, y=165, anchor='w')

        SettingsModClass = SettingsMod
        side = Side(glb_msgr.main, [glb_msgr.default_bg, glb_msgr.default_fg, ':'.join(glb_msgr.font_theme)], title='Multi NC Menu')

    @staticmethod
    def execute():
        main()

def create_instance(name):
    if os.path.exists(f'{root_path_plug}/ncs/{name}.nc'):
        showerror('Error', f'Instance with name {name} already exists')
        return
    with open(f'{root_path_plug}/ncs/{name}.nc', 'w'):
        pass

def create_instance_ui():
    win = tk_.Tk()
    name = btaeui.Entry(win)
    name.pack()
    btaeui.Button(win, text='Confirm', command=lambda: create_instance(name.get())).pack()

def find_nc():
    for file in os.listdir('./data'):
        if os.path.isfile(f'./data/{file}') and len(file.split('.')) > 1:
            if file.split('.')[1].lower() == 'nc':
                return file
    return None


def load_instance(event):
    print(f'loading instance {event.widget.get()}')
    glb_msgr.dump_data_nc()
    to_load = f'{root_path_plug}/ncs/{event.widget.get()}'
    nc_current = f'./data/{find_nc()}'
    nc_current_fn = find_nc()
    shutil.move(to_load, f'./data/{event.widget.get()}')
    shutil.move(nc_current, f'{root_path_plug}/ncs/{nc_current_fn}')
    glb_msgr.base_conf['LOAD_NC'] = event.widget.get()
    glb_msgr.reload_data_nc()
    glb_msgr.reinit_window()
    i = glb_msgr.show('Warning', 'To prevent conflicts, you need to restart app.', custom_close=glb_msgr.main.quit, ret_win=True)
    i.winfo_children()[0].destroy()
    glb_msgr.backup_data_nc = False

class Side(btaeui.SidePanel):
    def _create_base(self):
        self.create(btaeui.Label(), x=-100, y=-100, name='loaded')
        var = os.listdir(os.path.dirname(__file__).replace('\\'[0:1], '/') + '/ncs')
        cb = ttk.Combobox(self._o, values=var)
        print(cb)
        cb.bind('<<ComboboxSelected>>', load_instance)
        cb.place(x=5, y=45, anchor='w')
        self._widgets.append({'widget': cb})
        self.create(btaeui.Button(text='Create Instance', command=create_instance_ui), x=5, y=70, anchor='w')
        self.create(btaeui.Label(text=f'Current Instance: {glb_msgr.base_conf["LOAD_NC"]}'), x=5, y=100, anchor='w')

    def build(self):
        self.destroy()
        super().build()
        self._create_base()




def main():
    global settings_orig
    settings_orig = glb_msgr.Settings()
    glb_msgr.Settings = SettingsModClass


def nc_menu():
    side.build()