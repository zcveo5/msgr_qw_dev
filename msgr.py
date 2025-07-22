import hashlib, os.path, shutil, socket, subprocess, threading, json
from json import JSONDecodeError
from pathlib import Path

import data.lib.connect.auth, data.lib.connect.chat

from data.lib.utils import *
from data.lib.utils2 import *

import data.lib.ui as ui
from data.lib.ui import Button, Label, Entry, Popup, Win, Text, ProgressBar, Listbox
from data.lib.encrypting import *

from tkinter import TclError, Frame
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Combobox
from tkinter.messagebox import askyesno, showerror

auth = data.lib.connect.auth
chat_lib = data.lib.connect.chat
work = True
stop_event = threading.Event()


def pprint(v, *args, **kwargs):
    print(f'[{os.path.basename(__file__)}]{v}', *args, **kwargs)


# init classes and functions


class Settings(ui.SidePanelRevision):
    def __init__(self):
        super().__init__(main, [default_bg, default_fg, font_theme], title=locale['settings_mm_butt'])
        self.window_other = None
        self.window_debug = None
        self.d_b = None
        self.window_locale = None
        self.window_theme = None
        self.br = Button
        self.test1 = Button
        self.test2 = Button
        self.l_th_b = Button
        self.theme_button = Button
        self.th_file = Entry
        self.advanced = None
        self.theme = user_local_settings['USER_SETTINGS']['THEME']
        self._base_widgets = [Button(self._o, text=locale['setting_sub_f_INTERFASE'],
                           command=self.sub_f_ui, fg=default_fg,
                           bg=default_bg, font=font_theme),
                              Button(self._o, text=locale['setting_sub_f_DEBUG'],
                           command=self.sub_f_debug, fg=default_fg,
                           bg=default_bg, font=font_theme),
                              Button(self._o, text=locale['setting_sub_f_PROFILE'],
                           command=self.sub_f_profile, bg=default_bg,
                           fg=default_fg, font=font_theme),
                              Button(self._o, text=locale['setting_sub_f_MODS_REPO'],
                           command=self.sub_f_mod_rep, bg=default_bg,
                           fg=default_fg, font=font_theme),
                              Button(self._o, text=locale['setting_sub_f_MEMORY'],
                           command=self.memory_manage, bg=default_bg)]

    def _create_base(self):
        for wid in self._base_widgets:
            wid.pack(anchor='nw')


    def create_copy(self, wid: tk.Button):
        wid_class = wid.__class__
        new_widget = wid_class(self._o)
        for _cfg_elem in wid.keys():
            new_widget.config({_cfg_elem: wid[_cfg_elem]})
        return new_widget



    def build(self):
        if self.build_state:
            self._create_base()
            super().build()
        else:
            self.destroy()
            self._create_base()
            super().build()
        

        
    def toggle_theme(self):
        global default_fg, default_bg
        if self.theme == 'light':
            self.theme = 'black'
            user_local_settings['USER_SETTINGS']['THEME'] = self.theme
            default_bg = 'black'
            default_fg = 'white'
            refresh()
        elif self.theme == 'black':
            self.theme = 'light'
            user_local_settings['USER_SETTINGS']['THEME'] = self.theme
            default_fg = 'black'
            default_bg = 'white'
            refresh()

    def sub_f_ui(self):
        def sel_t(event):
            pprint('sl_t')
            pprint(event)
            theme(d_b_t.get())
            user_local_settings['USER_SETTINGS']['THEME'] = d_b_t.get()
            dump_data_nc()
            reload_data_nc()
        def set_l(event):
            global lng
            pprint('sl_l')
            pprint(event)
            lng = d_b.get()
            user_local_settings['USER_SETTINGS']['SEL_LOCALE'] = d_b.get()
            dump_data_nc()
            reload_data_nc()
            refresh_locale()
        self.window_locale = Popup(main, 450, 250, [300, 300], [default_bg, default_fg, font_theme], title=locale['setting_sub_f_INTERFASE'])
        self.window_locale.pack_propagate(True)
        self.window_locale.configure(bg=default_bg)
        longs = os.listdir('./data/locale')
        Label(self.window_locale, text=locale['set_locale_txt'], fg=default_fg, bg=default_bg, font=font_theme).pack(anchor='nw', padx=3)
        d_b = ttk.Combobox(self.window_locale ,values=longs, state="readonly")
        d_b.bind("<<ComboboxSelected>>", set_l)
        d_b.pack(anchor='nw', padx=3)
        themes = os.listdir('./data/theme')
        Label(self.window_locale, text=locale['set_theme_txt'], fg=default_fg, bg=default_bg, font=font_theme).pack(
            anchor='nw', padx=3)

        d_b_t = ttk.Combobox(self.window_locale, values=themes, state="readonly")
        d_b_t.bind("<<ComboboxSelected>>", sel_t)
        d_b_t.pack(anchor='nw', padx=3)
        Button(self.window_locale, text=locale['cct_title'], command=create_custom_theme, bg=default_bg, fg=default_fg,
               font=font_theme).pack(anchor='nw', padx=3)


    @staticmethod
    def sub_f_profile():
        global bt_server_data
        def p_ip_check():
            global bt_server_data
            nonlocal ip_show_btn
            try:
                pprint(bt_server_data)
                if bt_server_data[1]['answer']['_show_ip'] == 'True':
                    ip_show_btn['text'] = locale['public_ip_hide']
                    auth.update_personal_conf(username, ['_show_ip', 'False'])
                else:
                    ip_show_btn['text'] = locale['public_ip_show']
                    auth.update_personal_conf(username, ['_show_ip', 'True'])
                bt_server_data = user.get_data()
            except ConnectionResetError:
                show('Error',
                      'An existing connection was forcibly closed by the remote host\nBebraTech Server currently unavailable.')
            except Exception as pip_ex:
                show('Error', f'{pip_ex}\n{traceback.format_exc()}')
        window_prof = Popup(main, 450, 250, [300, 300], [default_bg, default_fg, font_theme], title=locale['setting_sub_f_PROFILE'])
        window_prof.pack_propagate(True)
        Label(window_prof, text=f"{locale['curr_acc']}: {username}", bg=default_bg, fg=default_fg,
               font=font_theme).pack(anchor='nw', padx=3)
        Button(window_prof, text=locale['un_login'], command=other_cl.exit_acc, bg=default_bg, fg=default_fg,
               font=font_theme).pack(anchor='nw', padx=3)
        if 'answer' not in bt_server_data[1]:
            show('Error', 'Not Login')
            return
        if bt_server_data[1]['answer']['_show_ip'] == 'True':
            ip_show_btn = Button(window_prof, text=locale['public_ip_show'], command=p_ip_check, bg=default_bg, fg=default_fg, font=font_theme)
            ip_show_btn.pack(anchor='nw', padx=3)
        else:
            ip_show_btn = Button(window_prof, text=locale['public_ip_hide'], command=p_ip_check, bg=default_bg, fg=default_fg, font=font_theme)
            ip_show_btn.pack(anchor='nw', padx=3)



    def sub_f_debug(self):
        def exc():
            raise MemoryError
        def upd_ll_ff():
            base_conf['RUNT_ACTION'] = 'LL_F_Update'
        def upd_ll():
            base_conf['RUNT_ACTION'] = 'LL_Update'
        self.window_other = Popup(main, 450, 250, [300, 300], [default_bg, default_fg, font_theme], title=locale['setting_sub_f_DEBUG'])
        self.window_other.pack_propagate(True)
        Button(self.window_other, text='cut bt mod loader', command=other_cl.cut_mod).pack(anchor='nw', padx=3)
        Button(self.window_other, text='LowLevel Update From GitHub repository', command=upd_ll).pack(anchor='nw', padx=3)
        Button(self.window_other, text='LowLvl Update from file', command=upd_ll_ff).pack(anchor='nw', padx=3)
        Button(self.window_other, text='Get Exception', command=lambda: exc()).pack(anchor='nw', padx=3)
        Button(self.window_other, text='Get Exception', command=lambda: exc()).pack(anchor='nw', padx=3)
        Button(self.window_other, text='DebugMenu', command=lambda: Debug().debugtools()).pack(anchor='nw', padx=3)
        Button(self.window_other, text='statistics', command=lambda: threading.Thread(target=Debug().stats, daemon=True).start()).pack(anchor='nw', padx=3)

    @staticmethod
    def memory_manage():
        def clear_chat_history():
            if askyesno('Warn', 'Are you sure to clean ALL messages stored locally?'):
                os.remove('./data/chatHistory.json')
                show('OK', 'Completed!')
        def clear_pycache():
            current_dir = Path('.')
            for pycache_dir in current_dir.glob('**/__pycache__'):
                print(f"Removing: {pycache_dir}")
                shutil.rmtree(pycache_dir, ignore_errors=True)
            print("All __pycache__ directories removed successfully!")
            show('OK', 'Completed!')
        win = Popup(main, 450, 250, [300, 300], [default_bg, default_fg, font_theme],
                                  title=locale['setting_sub_f_MEMORY'])
        win.pack_propagate(True)

        Button(win, text='Delete Messages', command=clear_chat_history, bg=default_bg, fg=default_fg, font=font_theme).pack(anchor='nw')
        Button(win, text='Delete All Temporary Files', command=clear_pycache, bg=default_bg, fg=default_fg, font=font_theme).pack(anchor='nw')

    @staticmethod
    def sub_f_mod_rep():
        def get_mod_info(event):
            pprint(event)
            try:
                name_mod['text'] = mods_select.get(mods_select.curselection())
            except TclError:
                return
            try:
                name_mod['text'] += f'\n{_plugin_objects[mods_select.get(mods_select.curselection())]["metadata"]["description"]}'
                if mods_select.get(mods_select.curselection()) not in _plugin_objects:
                    name_mod['text'] += f'\n{locale["plg_fail"]}'
                    state_pl['text'] = f'{locale["plg_not_l"]}, {locale["plg_inst"]}'
                else:
                    state_pl['text'] = f'{locale["plg_l"]}, {locale["plg_inst"]}'
            except KeyError:
                if mods_select.get(mods_select.curselection()) in _plugin_objects:
                    state_pl['text'] = f'{locale["plg_l"]}, {locale["plg_inst"]}'
                    name_mod['text'] += '\n' + locale['plg_fail_desc']
                else:
                    name_mod['text'] += '\n' + locale['plg_unk_error']
                    if mods_select.get(mods_select.curselection()) not in _plugin_objects:
                        state_pl['text'] = f'{locale["plg_not_l"]}, '
                    else:
                        state_pl['text'] = f'{locale["plg_l"]}, '
                    if mods_select.get(mods_select.curselection()) not in installed_var.get():
                        state_pl['text'] += f'{locale["plg_not_in"]}'
                    else:
                        state_pl['text'] += f'{locale["plg_inst"]}'
            if mods_select.get(mods_select.curselection()) in ['Not connected to BebraTech server']:
                action_butt['state'] = tk.DISABLED
            else:
                action_butt['state'] = tk.NORMAL
            plug_metas = {}
            for _plug in os.listdir('./plugins'):
                try:
                    plug_metas.update({_plug: json.load(open(f'./plugins/{_plug}/metadata.json'))})
                except FileNotFoundError:
                    pass
            try:
                if plug_metas[mods_select.get(mods_select.curselection())]['state'] == 'True':
                    disable_butt['text'] = locale['repo_disable_text']
                else:
                    disable_butt['text'] = locale['repo_enable_text']
                disable_butt['state'] = tk.NORMAL
                disable_butt.place(x=580, y=30)
            except KeyError:
                disable_butt['state'] = tk.DISABLED
                disable_butt.place_forget()
        def install_mod():
            try:
                mods_select.get(mods_select.curselection())
            except TclError:
                return
            mod_data = {}
            try:
                mod_data = eval(auth.raw_request({'action': f'get_mod:{mods_select.get(mods_select.curselection())}'}))
            except AttributeError:
                showerror('DownloadError: AttributeError', 'You use old API version. Please download actual from github.')
            try:
                down_mod = str(mod_data['answer'])
            except KeyError:
                showerror('AuthSever_Error', 'KeyError: down_mod is {}')
                return
            except UnboundLocalError:
                showerror('UnboundLocalErrorX0001', 'X0001')
                return
            down_mod = down_mod.replace('&@', '\n')
            mod = SNConfig(down_mod).load()
            pprint(mod)
            compiled = {'meta': eval(mod['meta']), 'code': mod['code']}
            pprint(compiled)
            try:
                os.mkdir(f'./plugins/{compiled["meta"]["name"]}')
            except FileExistsError:
                pass
            with open(f'./plugins/{compiled["meta"]["name"]}/metadata.json', 'w'):
                pass
            with open(f'./plugins/{compiled["meta"]["name"]}/{compiled["meta"]["file"]}.py', 'w'):
                pass
            json.dump(compiled['meta'], JsonObject(open(f'./plugins/{compiled["meta"]["name"]}/metadata.json', 'w')))
            open(f'./plugins/{compiled["meta"]["name"]}/{compiled["meta"]["file"]}.py', 'w').write(compiled['code'].replace('%TAB', '	'))
        def remove_mod():
            nonlocal installed_var
            shutil.rmtree(f'./plugins/{mods_select.get(mods_select.curselection())}', ignore_errors=True)
            installed_var = tk.Variable(modl_win, os.listdir('./plugins'))
        def load_repo():
            mods_select.bind('<<ListboxSelect>>', get_mod_info)
            mods_select.configure(listvariable=mods_var)
            action_butt.configure(text=locale['plg_install_butt'], command=install_mod)
            disable_butt['state'] = tk.DISABLED
        def load_installed():
            nonlocal installed_var
            mods_select.bind('<<ListboxSelect>>', get_mod_info)
            installed_var = tk.Variable(modl_win, os.listdir('./plugins'))
            mods_select.configure(listvariable=installed_var)
            action_butt.configure(text=locale['plg_remove_butt'], command=remove_mod)
            disable_butt['state'] = tk.NORMAL
        def toggle_mod():
            selected_meta = json.load(open(f'./plugins/{mods_select.get(mods_select.curselection())}/metadata.json', 'r'))
            if selected_meta['state'] == 'True':
                selected_meta['state'] = 'False'
                json.dump(selected_meta, JsonObject(open(f'./plugins/{mods_select.get(mods_select.curselection())}/metadata.json', 'w')))
            else:
                selected_meta['state'] = 'True'
                json.dump(selected_meta, JsonObject(open(f'./plugins/{mods_select.get(mods_select.curselection())}/metadata.json', 'w')))

        modl_win = Popup(main, 450, 250, [800, 450], [default_bg, default_fg, font_theme], title='Plugins Repository')
        #modl_win.pack_propagate(True)
        try:
            raw = []
            try:
                raw = eval(user.get_modlist())
                modlist = eval(raw['answer'])
            except (KeyError, NameError):
                modlist = ['Not connected to BebraTech server']
            except TypeError as ex_modl:
                try:
                    adds = raw
                except Exception as adds_err:
                    adds = adds_err
                showerror('Error: TypeError', f'x00004 (MOD_REP_INIT_FAILED)\nfirst info: {adds}\nsecond info: {ex_modl}')
                modl_win.destroy()
                return
            except SyntaxError:
                showerror('Error', f'Maybe server error, i dont know\n\n{user.get_modlist()}')
                return
            Button(modl_win, text=locale['plg_repo_SUB'], command=load_repo, bg=default_bg, fg=default_fg, font=font_theme).place(x=0, y=30)
            #Button(modl_win, text=locale['plg_repo_github_SUB'], command=load_repo_git, bg=default_bg, fg=default_fg,font=font_theme).place(x=100, y=0)
            Button(modl_win, text=locale['plg_installed_SUB'], command=load_installed, bg=default_bg, fg=default_fg, font=font_theme).place(x=100, y=30)
            mods_var = tk.Variable(modl_win, modlist)
            installed_var = tk.Variable(modl_win, os.listdir('./plugins'))
            mods_select = tk.Listbox(modl_win, width=70, height=20, listvariable=installed_var, bg=default_bg, fg=default_fg, font=font_theme)
            mods_select.place(x=0, y=60)
            mods_select.bind('<<ListboxSelect>>', get_mod_info)
            action_butt = Button(modl_win, text='', command=install_mod, bg=default_bg, fg=default_fg, font=font_theme)
            action_butt.place(x=500, y=60)
            disable_butt = Button(modl_win, text='', command=toggle_mod, bg=default_bg, fg=default_fg, font=font_theme)
            state_pl = Label(modl_win, text='', bg=default_bg, fg=default_fg, font=font_theme)
            state_pl.place(x=500, y=90)
            load_installed()
            name_mod = Label(modl_win, text='', bg=default_bg, fg=default_fg, font=font_theme, justify=tk.LEFT)
            name_mod.place(x=500, y=120)
        except Exception as __mods_repo_ex:
            Label(modl_win, text=f'Error:\n{__mods_repo_ex.__class__}\n\n{traceback.format_exc()}', justify='left').pack(anchor='nw')


class TickSys:
    def __init__(self, tick_rate: int = 20):
        """Tick System for apps

        :param tick_rate - tick per second
        """
        self.tick_rate = tick_rate
        self.stop = False
        self.t = 0

    def start_tick(self):
        """Starts tick system. Need to run by threading.Thread"""
        while not self.stop:
            try:
                time.sleep(1 / self.tick_rate)
                self.t += 1
            except KeyboardInterrupt:
                break
            except Exception as _tick_thread_ex:
                print(f'[err][tick-sys] Error {_tick_thread_ex}')
        else:
            return


class Debug:
    def __init__(self):
        with open('./data/logs/stats_infile_log.log', 'w'):
            pass
        self.cmd = None
        self.debugger = None

    def debugtools(self):
        def unlock():
            var = tk.BooleanVar()
            var.set(True)
            use_exec_hook = Button(debugger, text='!exh', command=lambda: self.exc_hook_execute(use_exec_hook, var))
            use_exec_hook.grid(column=0, row=0)
            Button(debugger, text='data.nc editor', command=self.data_nc_editor).grid(column=1, row=1)
            Button(debugger, text='plugin create', command=self.plug_create).grid(column=1, row=2)
            Button(debugger, text='tk_settings', command=self.tk_settings).grid(column=1, row=3)
            Button(debugger, text='globals explorer', command=self.globals_explorer).grid(column=1, row=4)

            Button(debugger, text='EXECUTE', command=lambda: self.execute(self.cmd.get("0.0", "end"), var.get())).grid(column=1, row=99)
            Button(debugger, text='info', command=lambda: show('inf', f'ver: {version}\nroute to executable file: {__file__}\nfile name: {__name__}\napp enc: {encoding}')).grid(column=1, row=100)


        self.debugger = ui.Popup()
        debugger = self.debugger
        debugger.title('DEBUGTOOLS')
        debugger.resizable(False, False)
        self.cmd = Text(debugger)
        self.cmd.grid(column=0, row=1, columnspan=1, rowspan=100)

        unlock()

        debugger.protocol("WM_DELETE_WINDOW", lambda: self.close_debug(debugger, self.cmd))
    @staticmethod
    def stats():
        log_inf_bool = False
        def toggle_log_infile():
            nonlocal log_inf_bool
            if log_inf_bool:
                log_inf.configure(text='log_any_change_in_file:F')
            else:
                log_inf.configure(text='log_any_change_in_file:T')
            log_inf_bool = not log_inf_bool
        win = ui.Popup()
        win.title(f'Statistics t:{threading.enumerate().index(threading.current_thread())}')
        win.resizable(False, False)
        info = Label(win, text='', justify=tk.LEFT)
        log_inf = Button(win, text='log_any_change_in_file:F', command=toggle_log_infile)
        log_inf.pack(anchor='nw')
        info.pack(anchor='nw')
        last_inf = ''
        while not stop_event.is_set():
            try:
                info.configure(text=f'===EXEC_F_INF===\nlng:{lng}\ntheme:{user_local_settings["USER_SETTINGS"]["THEME"]}\nstats_thread_id:{threading.enumerate().index(threading.current_thread())}\nchat_lib.online_list:{chat_lib.online_list}'
                                    f'\ntype-onl-list:{type(chat_lib.online_list)}\ntype-msgs:{type(chat_lib.msgs())}\nmain_winfo:{main.winfo_exists()}\nonline_listbox_winfo:{online_listbox.winfo_exists()}\n'
                                    f'setts_class:{Settings}\nflog_exists:{os.path.exists("./data/logs/stats_infile_log.log")}\n'
                                    f'chat_lib_private:{chat_lib.private_msgs()}\nunread:{unread}\nread:{read}\nchat:{chat_selected}\norig_chat_List{orig_chat_list}\nscrolled:{scrolled}\n'
                                    f'===P_LOG_INF===\nmain_sys.stdout:{sys.stdout.__class__}\nmain_sys.stdout_output_file:{sys.stdout.name}\n'
                                    f'===MSGS_INF===\nread[gen]\nCANT BE:\nchat_lib._msgs\nchat_lib.loaded_msgs:\n\n{id(read["General"])}\n{id(chat_lib.loaded_msgs)}\n{123}\nif not 0, all ok:')
                if log_inf_bool and last_inf != info['text']:
                    with open('./data/logs/stats_infile_log.log', 'a') as f_l:
                        try:
                            f_l.write(f'\n\nchange at {tick_sys.t}tick\n' + info['text'])
                        except UnicodeError:
                            f_l.write(
                                data.lib.ru_to_en.replace_letters(f'\n\nchange at {tick_sys.t}tick\n' + info['text']))
                    last_inf = info['text']
            except (TclError, RuntimeError):
                show('Error', traceback.format_exc())
                break
            win.update()


    @staticmethod
    def plug_create():
        def compile_plug():
            metadata = {'name': name_plug.get(), 'file': 'mod', 'class': class_plug.get(), 'state': 'True'}
            raw_code = code.get("0.0", tk.END)

            code_v = f"#Start\n{raw_code.replace('    ', '%TAB').replace('	', '%TAB')}\n#End"
            dist = {'meta': str(metadata), 'code': code_v}

            conf = SNConfig('').dump(dist).replace('\n', '&@')
            code.insert(tk.END, f'\n\nResult:\n{conf}')

        def upload_plug():
            metadata = {'name': name_plug.get(), 'file': 'mod', 'class': class_plug.get(), 'state': 'True'}
            raw_code = code.get("0.0", tk.END)

            code_v = f"#Start\n{raw_code.replace('    ', '%TAB').replace('	', '%TAB')}\n#End"
            dist = {'meta': str(metadata), 'code': code_v}

            conf = SNConfig('').dump(dist).replace('\n', '&@')

            answer = eval(auth.raw_request({'action': 'upload_mod', 'MOD_NAME': metadata['name'], 'PLUG_CODE': conf}))
            try:
                if answer['answer'] == 'uploaded':
                    show('Info', 'Uploaded')
                else:
                    show('Error', 'Not Uploaded')
            except KeyError:
                show('e', 'bebra tech server not exists')

        def decompile():
            path = f'{name_plug.get()}'
            meta = f'./plugins/{path}/metadata.json'
            meta_decoded = json.load(open(meta, 'r'))
            code_path = f"./plugins/{path}/{meta_decoded['file']}.py"
            code.delete("0.0", tk.END)
            code.insert("0.0", open(code_path, 'r', encoding='windows-1251').read())
            name_plug.delete("0", tk.END)
            class_plug.delete("0", tk.END)
            name_plug.insert("0", meta_decoded['name'])
            class_plug.insert("0", meta_decoded['class'])

        def save_plug():
            conf = SNConfig('').dump(
                {'code': code.get("0.0", tk.END), 'class': class_plug.get(), 'name': name_plug.get()}).replace('\n',
                                                                                                            '&@').replace(
                '    ', '%TAB').replace('	', '%TAB')
            try:
                os.mkdir('./plugins/backup')
            except FileExistsError:
                pass
            with open(f'./plugins/backup/{name_plug.get()}.plug', 'w'):
                pass
            open(f'./plugins/backup/{name_plug.get()}.plug', 'w').write(conf)

        def open_plug():
            code.delete("0.0", tk.END)
            class_plug.delete("0", tk.END)
            plug = open(f'./plugins/backup/{name_plug.get()}.plug').read().replace('&@', '\n').replace('%TAB', '    ')
            name_plug.delete("0", tk.END)
            conf_plug = SNConfig(plug).load()
            pprint(conf_plug)
            code.insert("0.0", conf_plug['code'])
            name_plug.insert("0", conf_plug['name'])
            class_plug.insert("0", conf_plug['class'])

        win = ui.Popup()
        win.title('Plugin Create')
        win.resizable(False, False)
        name_plug = Entry(win)
        name_plug.insert("0", "Enter plugin name")
        name_plug.grid(column=0, row=0)
        class_plug = Entry(win)
        class_plug.insert("0", "Enter plugin main_class")
        class_plug.grid(column=0, row=1)
        code = Text(win)
        code.grid(column=1, row=0, rowspan=10, columnspan=2)
        Button(win, text='Compile', command=compile_plug).grid(column=1, row=11)
        Button(win, text='Compile & Upload', command=upload_plug).grid(column=1, row=12)
        Button(win, text='Open Compiled', command=decompile).grid(column=2, row=13)
        Button(win, text='Open .plug', command=open_plug).grid(column=2, row=11)
        Button(win, text='Save .plug', command=save_plug).grid(column=2, row=12)

    @staticmethod
    def data_nc_editor():
        def save():
            with open(f'./data/{base_conf["LOAD_NC"]}', 'w', encoding='windows-1251') as nc_file:
                nc_file.write(encrypt(txt.get("0.0", tk.END), eval(cc)))
            reload_data_nc()
            dump_data_nc()

        def load_data_nc():
            txt.delete("0.0", tk.END)
            txt.insert("0.0", decrypt(open(f'./data/{base_conf["LOAD_NC"]}', 'r').read(), eval(cc)))

        try:
            cc = base_conf['CC']
            editor_win = ui.Popup()
            txt = Text(editor_win)
            txt.grid(column=0, row=0, columnspan=2)
            Button(editor_win, text='Save', command=save).grid(column=0, row=1)
            Button(editor_win, text='Load', command=load_data_nc).grid(column=1, row=1)
        except Exception as editor_open_err:
            showerror('Error', f'Editor open error. {type(editor_open_err)}')

    @staticmethod
    def exc_hook_execute(b: Button, v):
        v.set(not v.get())
        if v.get():
            b.configure(text='!exh')
        else:
            b.configure(text='exh')

    @staticmethod
    def execute(code, use_exc_hook=False):
        handlers = code.split('\n')[0][1::]
        _handlers_dict = {}
        for _hand in handlers.split():
            tmp = _hand.split(':')
            try:
                _handlers_dict.update({tmp[0]: tmp[1]})
            except IndexError:
                showerror('Error', f'bad handler {tmp[0]}: must be splittable with ":" on 2 parts')
                return
        if use_exc_hook:
            code_ = (f""
                     f"def pp(v='Not provided'):\n"
                     f"   show('Print', v, ret_win=True).mainloop()\n"
                     f"print = pp\n"
                     f"{code.replace('	', '    ')}\n")
        else:
            code_ = code
        def exec__():
            try:
                exec(code_, globals(), locals())
            except Exception as ex:
                pprint(f'ex {ex}')
                showerror('e', traceback.format_exc())
        if _handlers_dict['EXECUTE_MODE'] == 'NOT_THREAD': # if it fails you don't write execute mode: first str must be "#EXECUTE_MODE:THREAD/NOT_THREAD ...other handlers"
            exec__()
        elif _handlers_dict['EXECUTE_MODE'] == 'THREAD':
            threading.Thread(target=exec__).start()
    @staticmethod
    def relog():
        global bt_server_data
        try:
            bt_server_data = user.get_data()
        except Exception as relog_ex:
            show('Error ' + str(type(relog_ex)), str(relog_ex), ret_win=True).mainloop()
        try:
            if bt_server_data[1]['status'] == 'error':
                show('Error', f'{bt_server_data}')
        except TypeError:
            pass

    @staticmethod
    def close_debug(win, txt):
        try:
            txt.pack_forget()
        except tkinter.TclError:
            pass
        win.destroy()

    @staticmethod
    def theme_reset():
        global default_fg, default_bg
        user_local_settings['USER_SETTINGS']['THEME'] = 'black'
        default_bg = 'black'
        default_fg = 'white'
        main.configure(bg=default_bg)

    def custom_req(self):
        auth.raw_request(eval(self.cmd.get("0.0", tk.END).replace('\n', '')))

    @staticmethod
    def tk_settings():

        def conf(sc, dpi):
            user_local_settings['USER_SETTINGS']['SCREEN_SETTINGS'] = [float(sc), int(dpi)]

        tk_setts = ui.Popup()
        tk_setts.resizable(False, False)
        Label(tk_setts, text='This settings may break msgr. Be accurate').grid(column=0, row=0, columnspan=2)
        tk_scale = Entry(tk_setts)
        tk_dpi_mode = Entry(tk_setts)
        Label(tk_setts, text='widgets scaling').grid(column=0, row=1)
        tk_scale.grid(column=1, row=1)
        Label(tk_setts, text='dpi mode. 0 - default, 1 - dpi from system, 2 - dpi per screen').grid(column=0, row=2)
        tk_dpi_mode.grid(column=1, row=2)
        Button(tk_setts, text='Confirm', command=lambda: conf(tk_scale.get(), tk_dpi_mode.get())).grid(column=0, row=3, columnspan=2)
        Button(tk_setts, text='Optimize for win11', command=lambda: conf(1.4, 1)).grid(column=0, row=4, columnspan=2)


    @staticmethod
    def globals_explorer():
        glb_exp = ui.Popup()
        glb = tk.Listbox(glb_exp, height=20, width=100)
        for _i in globals().items():
            if '__' not in _i[0]:
                if 'module' not in str(_i[1]):
                    glb.insert(tk.END, f'{_i[0]} = {_i[1]}')
        glb.pack()
        glb_exp.resizable(False, False)


class FirstSetup:
    def __init__(self, bg, fg, fnt):
        self.bg = bg
        self.fg = fg
        self.fnt = fnt
        self.locale = locale

    def get_win(self):
        def reload():
            nonlocal lb1, lb2, sel_lc, sel_th, cont
            for _i in win.winfo_children()[2::]:
                _i.pack_forget()
            win.winfo_children()[1].configure({'text': self.locale['fs_title'], 'bg': self.bg, 'fg': self.fg, 'font': self.fnt})
            win.winfo_children()[0].configure({'bg': self.bg, 'fg': self.fg, 'font': self.fnt})
            bg.configure(bg=self.bg)

            win.config()

            win.configure(bg=self.bg)
            lb1 = tkinter.Label(win, text=self.locale['fs_locale'], bg=self.bg, fg=self.fg, font=self.fnt)
            lb1.pack()
            sel_lc = Combobox(win, values=os.listdir('./data/locale'), state="readonly", font=self.fnt)
            sel_lc.pack()
            sel_lc.bind("<<ComboboxSelected>>", _locale_load_fs)
            lb2 = tkinter.Label(win, text=self.locale['fs_theme'], bg=self.bg, fg=self.fg, font=self.fnt)
            lb2.pack()
            sel_th = Combobox(win, values=os.listdir('./data/theme'), state="readonly", font=self.fnt)
            sel_th.pack()
            sel_th.bind("<<ComboboxSelected>>", _theme_load_fs)
            cont = tkinter.Button(win, text=self.locale['fs_continue'], bg=self.bg, fg=self.fg, font=self.fnt, command=ex)
            cont.pack()

        def ex():
            win.destroy()
            bg.destroy()
            reinit_window()

        def _locale_load_fs(event):
            self.locale = refresh_locale_easy(event.widget.get(), True)
            reload()

        def _theme_load_fs(event):
            _t = theme_easy(event.widget.get(), True)
            print(_t)
            self.bg = _t[0]
            self.fg = _t[1]
            self.fnt = _t[2]
            reload()
        bg = Popup(main, 450, 250, [900, 500], [self.bg, self.fg, self.fnt], '')
        win = Popup(main, 450, 250, [300, 200], [self.bg, self.fg, self.fnt], self.locale['fs_title'])
        for _w in bg.winfo_children():
            _w.place_forget()
            _w.pack_forget()
        lb1 = tkinter.Label(win, text=self.locale['fs_locale'], bg=self.bg, fg=self.fg, font=self.fnt)
        lb1.pack()
        sel_lc = Combobox(win, values=os.listdir('./data/locale'), state="readonly", font=self.fnt)
        sel_lc.pack()
        sel_lc.bind("<<ComboboxSelected>>", _locale_load_fs)
        lb2 = tkinter.Label(win, text=self.locale['fs_theme'], bg=self.bg, fg=self.fg, font=self.fnt)
        lb2.pack()
        sel_th = Combobox(win, values=os.listdir('./data/theme'), state="readonly", font=self.fnt)
        sel_th.pack()
        sel_th.bind("<<ComboboxSelected>>", _theme_load_fs)
        cont = tkinter.Button(win, text=self.locale['fs_continue'], bg=self.bg, fg=self.fg, font=self.fnt, command=ex)
        cont.pack()


def get_win_pos():
    spl = main.geometry().split('+')
    return f'{spl[1]}+{spl[2]}'


class Other:
    @staticmethod
    def exit_acc():
        user_local_settings['USER_SETTINGS']['USERNAME'] = ''
        user_local_settings['USER_SETTINGS']['PASSWORD'] = ''
        dump_data_nc()
        reload_data_nc()
        show('Info', 'Restart is required to exit your account')


    @staticmethod
    def cut_mod():
        if askyesno('confirmation', 'do you really want to disable BTAEML?'):
            user_local_settings['USER_SETTINGS']['BTAEML'] = 'False'
            show('ok', 'ok')


def account_loop():
    global bt_server_data
    while True:
        try:
            bt_server_data = user.get_data()
            if bt_server_data['status'] == 'error':
                raise Exception(f'AuthClient return a Error: {bt_server_data}')
        except Exception as _exL:
            show('Error AccountLoop ' + str(type(_exL)), str(_exL) + '\n\n' + traceback.format_exc(), ret_win=True).mainloop()
            break


def shutdown():
    global work
    work = False
    main.quit()
    main.destroy()


def plugin_info():
    show('BTAEML (BebraTech Application Engine Mod Loader)', "BTAEML (BebraTech Application Engine Mod Loader) coded by BebraTech Inc. (BTAE authors).\n"
                                         "ALL plugins/mods made by other people (not BebraTech Inc.)\n"
                                         "We aren't take responsibility if your PC damaged by plugins/mods.\n\n"
                                         "BTAEML is included in all BTAE version 2.8.9 and above.\n"
                                         "In other versions BTAEML work unstable.\n\n"
                                         "BTAEML Team (BebraTech subdivision) 2025")


def show(title, text, ret_win=False, custom_close=None, legacy=False):
    if legacy:
        class _TkM(ui.Popup):
            def __init__(self):
                self.looped_btae = False
                super().__init__()

            def mainloop(self, n = 0):
                self.looped_btae = True
                super().mainloop(n)
        info = _TkM()
        def exit_mb():
            nonlocal info
            if info.looped_btae:
                info.quit()
            info.destroy()
            info = None
            if custom_close is not None:
                custom_close()
        info.title(title)
        try:
            fnt = font_theme
            bg = default_bg
            fg = default_fg
            info.configure(bg=bg)
        except NameError:
            fnt = ('Consolas', 9)
            bg = 'white'
            fg = 'black'
            info.configure(bg=bg)
        info.resizable(False, False)
        info.attributes('-topmost', True)
        Label(info, text=text, bg=bg, fg=fg, font=fnt, justify=tk.LEFT).pack(anchor='center', pady=30, ipadx=10)
        Button(info, text='OK', bg=bg, fg=fg, font=fnt, command=exit_mb).pack(anchor='se', side='bottom', expand=True, ipadx=10, ipady=5)
        if ret_win:
            return info
    else:
        try:
            fnt = font_theme
            bg = default_bg
            fg = default_fg
        except NameError:
            fnt = ('Consolas', 9)
            bg = 'white'
            fg = 'black'
        def exit_mb():
            if custom_close is not None:
                custom_close()
            info.destroy()
        try:
            info = Popup(main, 450, 250, [200, 200], [bg, fg, fnt], title)
        except Exception as _show_frame_ex:
            return show(title, text + f'\nFailed to create ShowFrame: {_show_frame_ex} - {_show_frame_ex.__class__}', ret_win, custom_close, legacy=True)
        info.pack_propagate(True)
        Label(info, text=text, bg=bg, fg=fg, font=fnt, justify=tk.LEFT).pack(anchor='center', pady=30, ipadx=10)
        Button(info, text='OK', bg=bg, fg=fg, font=fnt, command=exit_mb).pack(anchor='se', side='bottom', expand=True, ipadx=10, ipady=5)
        if ret_win:
            return info

    return None


def theme(file2, ret=False):
    global default_fg, default_bg, font_theme, settings_cl
    pprint(f'[info] loading theme {file2}')
    file1 = f"./data/theme/{file2.replace('.theme', '')}.theme"
    try:
        theme_ = load_theme(open(file1, 'r', encoding=encoding))
    except FileNotFoundError:
        showerror(locale['error_title'], locale['theme_error'] + ' FileNotFound')
        return None
    except IndexError:
        showerror(locale['error_title'], locale['theme_error'] + ' Index')
        return None
    except LookupError:
        showerror(locale['error_title'], locale['theme_error'] + ' LookUp')
        return None
    font_theme = theme_[2]
    default_fg = theme_[1]
    default_bg = theme_[0]
    user_local_settings['USER_SETTINGS']['THEME'] = file2.replace('.theme', '')
    main.option_add('*Font', font_theme)
    main.option_add('*Background', default_bg)
    main.option_add('*Foreground', default_fg)
    settings_cl = Settings()
    if not loading:
        commit_theme()
    if ret:
        return font_theme, default_fg, default_bg
    return None


def reinit_window(no_reinit_theme=False):
        global main, chat_window, font_theme, online_listbox, settings_cl
        main.destroy_all_in()
        main.title(locale['WINDOW_TITLE_TEXT'])
        chat_window = Text(main, fg=default_fg, bg=default_bg, font=font_theme, width=110)
        chat_window.place(x=0, y=0)
        main = main
        online_listbox = online_listbox
        ui.update_win_scaling()
        settings_cl = Settings()
        refresh(no_reinit_theme)


def commit_theme():
    for _w in main.winfo_children():
        try:
            if isinstance(_w, Button | Label | Entry | Text | Listbox | Frame):
                try:
                    _w.configure(bg=default_bg)
                    _w.configure(fg=default_fg)
                    _w.configure(font=font_theme)
                except TclError:
                    pass
                if hasattr(_w, 'winfo_children'):
                    for _w_ch in _w.winfo_children():
                        if isinstance(_w_ch, Button | Label | Entry | Text | Listbox):
                            try:
                                _w_ch.configure(bg=default_bg)
                                _w_ch.configure(fg=default_fg)
                                _w_ch.configure(font=font_theme)
                            except TclError:
                                pass
        except TclError:
            print(f'[!] Failed to commit theme to {_w}')
    for _w in main.his.values():
        if isinstance(_w, Button | Label | Entry | Text | Listbox | Frame):
            try:
                _w.configure(bg=default_bg)
                _w.configure(fg=default_fg)
                _w.configure(font=font_theme)
            except TclError:
                pass


def change_lng(a):
        global lng
        lng = a
        user_local_settings['USER_SETTINGS']['SEL_LOCALE'] = a


def refresh_locale_easy(a, ret=False):
    global lng
    lng = a
    user_local_settings['USER_SETTINGS']['SEL_LOCALE'] = a
    try:
        encoding_l = 'utf-8'
        open(f'./data/locale/{lng}/locale.cfg', 'r', encoding=encoding_l)
    except UnicodeError:
        encoding_l = 'windows-1251'
    try:
        locale_fl1 = json.load(open(f'./data/locale/{lng}/locale.cfg', 'r', encoding=encoding_l))
    except JSONDecodeError:
        locale_fl1 = Config(f'./data/locale/{lng}/locale.cfg', coding=encoding_l)
    locale1 = Locale(locale_fl1)
    if ret:
        return locale1
    return None


def theme_easy(a, ret=False):
    user_local_settings['USER_SETTINGS']['THEME'] = a
    if ret:
        theme_ = load_theme(open(f'./data/theme/{a}', 'r', encoding=encoding))
        return theme_[0], theme_[1], theme_[2]
    return None


def change_enc(a):
    global encoding
    encoding = a


def refresh_locale():
    global locale, locale_fl, encoding
    pprint(f'ref locale {lng}')

    #try:
    #    locale_fl = json.load(open(f'./data/locale/{lng}/locale.cfg', encoding=encoding))
    #except UnicodeError:
    #    encoding = 'windows-1251'
    #    locale_fl = json.load(open(f'./data/locale/{lng}/locale.cfg', encoding=encoding))
    #except JSONDecodeError:
    #    try:
    #        locale_fl = Config(f'./data/locale/{lng}/locale.cfg', coding=encoding)
    #        reinit_window()
    #    except UnicodeDecodeError:
    #        if encoding == 'utf-8':
    #            encoding = 'windows-1251'
    #        else:
    #            encoding = 'utf-8'
    #        try:
    #            locale_fl = Config(f'./data/locale/{lng}/locale.cfg', coding=encoding)
    #            reinit_window()
    #        except (UnicodeDecodeError, LookupError, OSError):
    #            showerror(locale['error_title'], locale['uns_locale'])
    #    except LookupError:
    #        showerror(locale['error_title'], locale['encoding_error'])
    #    except OSError:
    #        showerror(locale['error_title'], locale['unk_error'])

    try:
        open(f'./data/locale/{lng}/locale.cfg', 'r', encoding=encoding)
    except UnicodeError:
        if encoding == 'utf-8':
            encoding = 'windows-1251'
        else:
            encoding = 'utf-8'

    try:
        locale_fl = json.load(open(f'./data/locale/{lng}/locale.cfg', 'r', encoding=encoding))
        print('Loaded as JSON')
    except JSONDecodeError:
        locale_fl = Config(f'./data/locale/{lng}/locale.cfg', coding=encoding)
        print('Loaded as Legacy')

    locale = Locale(locale_fl)
    reinit_window()

def send_message(event=None, is_private=False, **kw):
    pprint(event)
    try:
        to_send = {'text': send_entry.get("0.0", 'end'), '_show_ip': bt_server_data[1]['answer']['_show_ip'], 'name': username}
    except KeyError:
        show('Error', 'Not connected to Auth server')
        return
    if is_private:
        to_send.update({'to': 'private', 'to_cl': kw['private_addr']})
    else:
        to_send.update({'to': 'public'})
    message = to_send
    my_message.set("")
    try:
        chat.send(message)
    except OSError:
        showerror('Error', 'SOCK_DISCONNECTED')
        to_send['text'] += ' (!) SOCK_DISCONNECTED'
    if is_private:
        read[kw['private_addr']] = chat_lib.private_msgs()[kw['private_addr']]
    else:
        read['General'] = chat_lib.msgs()
    send_entry.delete("0.0", tk.END)


def load_chat(event):
    global chat_select_menu, chat_selected
    if event.widget.curselection() == ():
        print('chat load ============================================================================ error ::: empty event.widget...')
        return
    if event.widget.get(event.widget.curselection()[0]) in ['Online:', f'{username} | You', '']:
        print('chat load ============================================================================ error ::: event.widget... is Online: or user or empty')
        return
    chat_select_menu = False
    print(event.widget.get("0", tk.END))
    if event.widget.get(event.widget.curselection()[0]) not in orig_chat_list:
        print(f'new chat {event.widget.get(event.widget.curselection()[0])}')
        unread[event.widget.get(event.widget.curselection()[0])] = 0
        read[event.widget.get(event.widget.curselection()[0])] = []
        orig_chat_list.append(event.widget.get(event.widget.curselection()[0]))
        chat_lib.new_chat(chat_selected)
        print(chat_lib.private_msgs().keys())
    try:
        chat_selected = orig_chat_list[event.widget.curselection()[0]]
    except IndexError:
        print('chat load ============================================================================ error ::: index error, threads conflict')
        main.after(10, load_chat, event)
    if chat_selected == 'General':
        read['General'] = chat_lib.msgs()
    else:
        read[chat_selected] = chat_lib.private_msgs()[chat_selected].copy()
    unread[chat_selected] = 0
    reinit_ui(True)



def back_to_chat_select():
    global chat_select_menu, chat_selected
    chat_select_menu = True
    chat_selected = ''
    main.his['back_to_chat_select'].destroy()
    main.his.pop('back_to_chat_select')
    main.his['chat_label'].destroy()
    main.his.pop('chat_label')
    chat_window.place_forget()
    send_entry.place_forget()
    send_button.place_forget()
    send_private_button.place_forget()
    reinit_ui()


def reinit_ui(no_reinit_theme=False):
    global default_fg, default_bg, send_entry, chat_window, online_listbox, send_button, send_private_button, reinit_count
    try:
        if bt_server_data[1] == 'blocked':
            chat_window.place_forget()
            Label(text='You are blocked in BebraTech network').pack()
            Button(text='Exit from account', command=other_cl.exit_acc).pack()
            return
    except (KeyError, NameError):
        pass
    try:
        Button(text=locale['settings_mm_butt'], command=settings_cl.build, bg=default_bg, fg=default_fg, font=font_theme).place(relx=0.85, rely=0, relheight=0.05, relwidth=0.15)
    except NameError:
        pass

    if not loading:
        chat.send({'action_for_chat_server': 'OnlineList'})
    raw_online_list = chat_lib.online_list
    for _i in raw_online_list:
        if _i == username:
            raw_online_list[raw_online_list.index(_i)] = f'{username} | You'
    var = tk.Variable(main, value=raw_online_list)
    online_listbox = tk.Listbox(bg=default_bg, fg=default_fg, font=font_theme,
                          listvariable=var)
    online_listbox.bind("<<ListboxSelect>>", load_chat)
    online_listbox.place(relx=0.85, rely=0.05, relwidth=0.15, relheight=1)

    main.configure(bg=default_bg)
    if 'chat_select' in main.his:
        main.his['chat_select'].destroy()
        main.his.pop('chat_select')
    chat_select_listbox = main.create('chat_select', tk.Listbox, width=110, height=30, bg=default_bg, fg=default_fg, font=font_theme).tk
    if chat_select_menu:
        pprint('[info] ===================== LOADING CHAT SELECT')
        if 'General' in unread:
            if unread['General'] > 0:
                chat_select_listbox.insert(tk.END, f'General ({unread["General"]})')
            else:
                chat_select_listbox.insert(tk.END, f'General')
        else:
            chat_select_listbox.insert(tk.END, f'General')
        for chat_name in chat_lib.private_msgs().keys():
            if chat_name != '':
                res = chat_name
                if chat_name not in orig_chat_list:
                    orig_chat_list.append(chat_name)
                if chat_name in unread:
                    if unread[chat_name] > 0:
                        res += f' ({unread[chat_name]})'
                chat_select_listbox.insert(tk.END, res)
        chat_select_listbox.place(x=0, y=0, relwidth=0.85, relheight=1)
        chat_select_listbox.bind('<<ListboxSelect>>', load_chat)
    elif chat_selected == 'General':
        pprint('[info] ===================== LOADING GENERAL')
        chat_select_listbox.place_forget()
        main.create('back_to_chat_select', Button, True, bg=default_bg, fg=default_fg, font=font_theme, text=locale['back'], command=back_to_chat_select).build('pack', anchor='nw', side='left')
        main.create('chat_label', Label, True, bg=default_bg, fg=default_fg, font=font_theme, text=locale['chat_txt'] + ': ' + chat_selected).build('pack', anchor='nw', side='left', padx=5, pady=3)
        send_entry = main.create('send_entry', Text, True, width=110, bg=default_bg, fg=default_fg, font=font_theme).tk
        send_entry.bind("<Control-Return>", send_message)
        send_entry.place(x=0, rely=0.8, relwidth=0.75, relheight=0.1)
        send_button = Button(text=locale['send_button'], bg=default_bg, fg=default_fg, font=font_theme, command=send_message)
        send_button.place(relx=0.75, rely=0.8, relwidth=0.10, relheight=0.05)
        send_private_button = main.create('send_private_button', Button, True, text='Send Private', bg=default_bg, fg=default_fg, font=font_theme, command=send_private).tk
        send_private_button.place(relx=0.75, rely=0.85, relwidth=0.10, relheight=0.05)
        chat_window.bind('<MouseWheel>', scroll)
        chat_window.place(relwidth=0.85, relheight=0.8, relx=0, rely=0.05)
    elif chat_selected != 'General':
        pprint(f'[info] ===================== LOADING PRIVATE {chat_selected}')
        chat_window.place_forget()
        online_listbox.place_forget()
        def send_reply(event=None):
            send_message(event, True, private_addr=chat_selected)

        main.create('back_to_chat_select', Button, bg=default_bg, fg=default_fg, font=font_theme, text=locale['back'],
                    command=back_to_chat_select).build('place', x=0, y=0)
        main.create('chat_label', Label, bg=default_bg, fg=default_fg, font=font_theme,
                    text=locale['chat_txt'] + ': ' + chat_selected).build('place', x=80, y=0)
        send_entry = main.create('send_entry', Entry, True, width=110, bg=default_bg, fg=default_fg, font=font_theme, textvariable=my_message).tk
        send_entry.bind('<Return>', send_reply)
        send_entry.place(x=0, y=400)
        send_button = main.create('send_reply_button', Button, True, text=locale['send_reply_button'], bg=default_bg, fg=default_fg, font=font_theme,
                             command=send_reply).tk
        send_button.place(x=800, y=400)
        chat_window_private = main.create('chat_window_private', Text, True, fg=default_fg, bg=default_bg, font=font_theme, width=110).tk
        chat_window_private.bind('<MouseWheel>', scroll)
        chat_window_private.place(x=0, y=30)

    if not no_reinit_theme:
        if user_local_settings['USER_SETTINGS']['THEME'] == 'light':
            default_fg = 'black'
            main.configure(bg='white')
            main.update()
            default_bg = 'white'
        elif user_local_settings['USER_SETTINGS']['THEME'] == 'black':
            default_bg = 'black'
            main.configure(bg='black')
            main.update()
            default_fg = 'white'
        else:
            theme(user_local_settings['USER_SETTINGS']['THEME'])

    ui.lift_popups()

    reinit_count += 1


def read_loaded():
    unread['General'] = 0
    read['General'] = chat_lib.loaded_msgs.copy()

    for chat_name in chat_lib.loaded_private_msgs.copy():
        unread[chat_name] = 0
        read[chat_name] = chat_lib.loaded_private_msgs.copy()[chat_name]


def create_custom_theme():
    theme_create = ui.Popup()
    theme_create.configure(bg=default_bg)
    theme_create.resizable(False, False)
    theme_create.title(locale['cct_title'])
    Label(theme_create, text=locale['ct_bg'], bg=default_bg, fg=default_fg, font=font_theme).grid(column=0, row=0)
    Label(theme_create, text=locale['ct_fg'], bg=default_bg, fg=default_fg, font=font_theme).grid(column=0, row=1)
    Label(theme_create, text=locale['ct_fnt'], bg=default_bg, fg=default_fg, font=font_theme).grid(column=0, row=2)
    Label(theme_create, text=locale['name'], bg=default_bg, fg=default_fg, font=font_theme).grid(column=0, row=3)
    bg_ent = Entry(theme_create, width=30, bg=default_bg, fg=default_fg, font=font_theme)
    bg_ent.grid(column=1, row=0)
    fg_ent = Entry(theme_create, width=30, bg=default_bg, fg=default_fg, font=font_theme)
    fg_ent.grid(column=1, row=1)
    fnt_ent = Entry(theme_create, width=30, bg=default_bg, fg=default_fg, font=font_theme)
    fnt_ent.grid(column=1, row=2)
    fl_ent = Entry(theme_create, width=30, bg=default_bg, fg=default_fg, font=font_theme)
    fl_ent.grid(column=1, row=3)
    Button(theme_create, text=locale['cct_save'], command=lambda: save_theme(bg_ent.get(), fg_ent.get(), fnt_ent.get(), fl_ent.get()), bg=default_bg, fg=default_fg, font=font_theme).grid(column=0, row=4)
    Button()



def save_theme(bg, fg, fnt, name):
    with open(f'./data/theme/{name}.theme', 'w') as th:
        if fnt == '':
            fnt = None
        if fg == '':
            fg = None
        if bg == '':
            bg = None
        if name == '':
            showerror(locale['error_title'], locale['cct_syntax_error'])
            return
        th.write(f'main_color={bg}\nsecondary_color={fg}\nfont={fnt}')
    reinit_window()


def complete_recv():
    try:
        chat_lib.cl.send({'action_for_chat_server': 'OnlineList'})
        chat_win_ref(chat_lib.msgs())
        update_online_list(chat_lib.online_list)
        if chat_selected not in ['General', '']:
            chat_win_private_ref(chat_lib.private_msgs()[chat_selected])
    except Exception as _cr_ex:
        showerror('complete_recv error', f'{_cr_ex.__class__}:\n{traceback.format_exc()}')



def update_online_list(online_list):
    try:
        online_listbox.delete(0, tk.END)
        for _user in online_list:
            if _user == username:
                _user += ' | You'
            online_listbox.insert(tk.END, _user)
    except Exception as __ex:
        pprint(__ex)
        pprint(traceback.format_exc())


def chat_win_ref(to):
    if chat_selected == 'General':
        chat_window.delete("0.0", tk.END)
        scr = len(to) - 24 - scrolled
        scr_to = len(to) - scrolled
        if scr < 0:
            scr = 0
        if scr_to < 25:
            scr_to = 24
        _to = to[scr:scr_to]
        for msg in '\n'.join(_to):
            if 'PRIVATE: ' not in msg:
                chat_window.insert(tk.END, msg)


def chat_win_private_ref(to):
        try:
            main.his['chat_window_private'].tk.delete("0.0", tk.END)
            scr = len(to) - 24 - scrolled
            scr_to = len(to) - scrolled
            if scr < 0:
                scr = 0
            if scr_to < 25:
                scr_to = 24
            _to = to[scr:scr_to]
            main.his['chat_window_private'].tk.insert(tk.END, '\n'.join(_to))
        except (KeyError, tk.TclError):
            pass


def select_server(a):
    global server
    server = a
    user_local_settings['USER_SETTINGS']['SERVER'] = a


def select_bt_server(a):
    global bt_server
    bt_server = a
    user_local_settings['USER_SETTINGS']['BT_SERV'] = a


def dump_data_nc():
    dat_d['[SETTINGS]'] = str(user_local_settings)
    with open(f'./data/{base_conf["LOAD_NC"]}', 'w', encoding='windows-1251') as _fl:
        _fl.write(encrypt(dat.dump(dat_d), eval(base_conf['CC'])))


def reload_data_nc():
    global dat, dat_d, user_local_settings, setting_raw
    global username, password, server, bt_server, lng
    try:
        dat = SNConfig(decrypt(open(f'./data/{base_conf["LOAD_NC"]}', 'r', encoding='windows-1251').read(), eval(base_conf['CC'])))
        dat_d = dat.load()
        setting_raw = dat_d['[SETTINGS]']
        user_local_settings = eval(setting_raw)
        username = user_local_settings['USER_SETTINGS']['USERNAME']
        password = user_local_settings['USER_SETTINGS']['PASSWORD']
        server = user_local_settings['USER_SETTINGS']['SERVER']
        bt_server = user_local_settings['USER_SETTINGS']['BT_SERV']
        lng = user_local_settings['USER_SETTINGS']['SEL_LOCALE']
    except Exception as nc_ex_rel:
        show('Error', f'Error reloading {base_conf["LOAD_NC"]}. {type(nc_ex_rel)}')


def send_private():
    def _send():
        send_entry.delete("0", tk.END)
        send_entry.insert(tk.END, msg.get())
        send_message(None, True, private_addr=to_cl.get())
    win = ui.Popup()
    win.title('Private MSG Sender')
    Label(win, text='Private MSG Sender\n--------------------', font=('Consolas', 12), justify=tk.LEFT).pack(anchor='w')
    to_cl = Entry(win)
    to_cl.pack(anchor='w')
    msg = Entry(win)
    msg.pack(anchor='w')
    to_cl.insert(tk.END, 'receiver username')
    msg.insert(tk.END, 'message')
    Button(win, text='Send', command=_send).pack(anchor='w')
    win.resizable(False, False)
    win.geometry('300x300')


def change_username(a):
    user_local_settings['USER_SETTINGS']['USERNAME'] = a


def update_chat_list(this):
    main.his['chat_select'].tk.delete("0", tk.END)
    main.his['chat_select'].tk.insert(tk.END, f'General ({this})')
    for chat_name in chat_lib.private_msgs().keys():
        main.his['chat_select'].tk.insert(tk.END, chat_name + f' ({unread[chat_name]})')


def count_unread():
    for _i in chat_lib.private_msgs().keys():
        if _i not in orig_chat_list:
            orig_chat_list.append(_i)
    for _i in orig_chat_list:
        if _i != chat_selected:
            if _i == 'General':
                unread['General'] = len(chat_lib.msgs()) - len(read['General'])
            else:
                if _i not in read:
                    read[_i] = []
                unread[_i] = len(chat_lib.private_msgs()[_i]) - len(read[_i])
    try:
        if main.his['chat_select'].tk.winfo_exists():
            for _key, _value in unread.items():
                if _value != 0:
                    item = (orig_chat_list
                            .index(_key))
                    main.his['chat_select'].tk.delete(item, item)
                    main.his['chat_select'].tk.insert(item, _key + ' (' + str(_value) + ')')
    except KeyError:
        pass


def scroll(event):
    global scrolled
    if scrolled >= 0:
        pre_scr = scrolled + event.delta // 120
        if pre_scr >= 0:
            scrolled = pre_scr
    else:
        scrolled = 0
    if chat_selected not in ['General', '']:
        chat_win_private_ref(chat_lib.private_msgs()[chat_selected])
    else:
        chat_win_ref(chat_lib.msgs())


def detect_fatal_traceback():
    for line in sys.stdout.read().split('[ STDOUT ]'):
        if '[loader][traceback]' in line and line not in seed_traces:
            try:
                seed_traces.append(line)
                bg = Popup(main, 450, 250, [900, 500], [default_bg, default_fg, font_theme], '')
                win = Popup(main, 450, 250, [800, 400], [default_bg, default_fg, font_theme], 'Fatal Traceback')
                for _w in bg.winfo_children():
                    _w.place_forget()
                    _w.pack_forget()
                Label(win, text=line, justify='left').pack(anchor='nw')
                Button(win, text='Continue', command=main.quit).pack(anchor='se', side='bottom')
                main.mainloop()
                bg.destroy()
                win.destroy()
            except TclError:
                print('Failed to create traceback popup')






if os.path.basename(sys.argv[0]) in ['loader.py', 'launcher.pyw']:
    pprint('MSGR QW BY BEBRA TECH (C) 2023 - 2025')
    tick_sys = TickSys()
    #threading.Thread(target=tick_sys.start_tick, daemon=True).start()
    default_bg = 'black'
    default_fg = 'white'
    font_theme = ('Consolas', 9)
    debug_mode = False
    chat_select_menu = True
    backup_data_nc = True
    chat_selected = ''
    scrolled = 0
    unread = {}
    read = {}
    orig_chat_list = ['General']
    reinit_count = 0
    complete_recv_thread = threading.Thread(target=complete_recv, daemon=True)
    seed_traces = []

    for __argv_elem in sys.argv:
        if 'RunBeforeWin' in __argv_elem:
            try:
                exec(__argv_elem.split('$=%')[1])
            except Exception as _ex:
                showerror(f'E: {_ex.__class__}', f'${__argv_elem.split('$=%')[1]}$')

    def reinit_wrapper(event):
        print(f'reinit pinged {event.keysym}')
        if event.keysym == 'k':
            reinit_ui()

    def crv2():
        main.quit()
        main.mainloop()

    def cvr3():
        main.destroy_all_in()
        reinit_ui()

    def cvr4():
        reinit_window()
        main.recovery()

    def cvr_load_recovery():
        main.destroy_all_in()
        main.recovery()

    def complete_install():
        def mod_mainloop():
            if 'READY' not in sys.stdout.read():
                return
            else:
                main.mainloop = orig_ml
                main.recovery()
                main.mainloop()
        main.destroy_all_in()
        main.quit()
        orig_ml = main.mainloop
        main.mainloop = mod_mainloop

    def cvr5():
        cvr_scrolled = 0
        def exec_wrapper(event):
            exec(event.widget.get(), globals(), locals())

        def scroll_wrapper(event):
            nonlocal cvr_scrolled
            pseudo_result = cvr_scrolled + event.delta // 120
            if pseudo_result > 0:
                if pseudo_result + 24 < len(sys.stdout.read().split('\n')):
                    cvr_scrolled = pseudo_result
                    main['cmdline'].tk.delete("0.0", tk.END)
                    main['cmdline'].tk.insert(tk.END,
                                              '\n'.join(
                                                  sys.stdout.read().split('\n')[cvr_scrolled:cvr_scrolled + 24]
                                                ))
                    spl = main['dbg'].tk['text'].split('\n')
                    spl[1] = f'scrolled {cvr_scrolled}:{cvr_scrolled + 24}'
                    main['dbg'].tk['text'] = '\n'.join(spl)


        def cvr_cmdline_loop(_t=None):
            cont = True
            try:
                main['cmdline'].tk.delete("0.0", tk.END)
                main['cmdline'].tk.insert(tk.END,
                                          '\n'.join(
                                          sys.stdout.read().split('\n')[cvr_scrolled:cvr_scrolled + 24]
                                          ))
            except KeyError:
                cont = False
            except Exception as __ex:
                showerror('erq', f'cvr_cmdline_loop wh exec {__ex.__class__} : {__ex}')
                cont = False
            if cont:
                main.after(100, cvr_cmdline_loop, _t)

        def create_var():
            def commit():
                globals().update({name.get(): eval(type_v.get())(val.get())})
                locals().update({name.get(): eval(type_v.get())(val.get())})
            win = ui.Popup()
            Label(win, text='')
            name = Entry(win)
            name.pack()
            val = Entry(win)
            val.pack()
            type_v = Entry(win)
            type_v.pack()
            Button(win, text='create', command=commit).pack()

        main.destroy_all_in()
        main.create('back_from_cvr5', Button, recreate_if_exists=True, text='Back to recovery', command=cvr_load_recovery).build('place', x=0, y=0)
        main.create('cmdline', Text, recreate_if_exists=True).build('pack')
        main.create('dbg', Label, recreate_if_exists=True).build('pack')
        main.create('exec_line', Entry, recreate_if_exists=True, width=60).build('pack')
        main.create('create_var', Button, recreate_if_exists=True, text='create variable',
                    command=create_var).build('place', x=0, y=30)
        main['exec_line'].tk.bind('<Return>', exec_wrapper)
        nl = '\n'
        main['dbg'].tk['text'] = f'scroll limit: top: 0, bottom: {len(sys.stdout.read().split(nl))}\n'
        main['cmdline'].tk.bind('<MouseWheel>', scroll_wrapper)
        cvr_cmdline_loop()

    main = Win()
    main.tk_thread(detect_fatal_traceback, 100)
    main.report_callback_exception = sys.excepthook
    main.option_add('*Font', font_theme)
    main.option_add('*Background', default_bg)
    main.option_add('*Foreground', default_fg)
    main.recovery_widgets.append({'name': 'recovery_lbl', 'obj': Label,
                                  'kwargs': {'text': f'recovery menu', 'justify': 'left'},
                                  'place_mode': 'pack', 'place_kw': {'anchor': 'nw'}})
    main.recovery_widgets.append({'name': 'recovery_butt1', 'obj': Button, 'kwargs': {'text': 'Press here to open debugtools', 'command': Debug().debugtools}, 'place_mode': 'pack', 'place_kw': {'anchor': 'nw'}})
    main.recovery_widgets.append({'name': 'recovery_butt2', 'obj': Button,
                                  'kwargs': {'text': 'reinit_ui', 'command': cvr3},
                                  'place_mode': 'pack', 'place_kw': {'anchor': 'nw'}})
    main.recovery_widgets.append({'name': 'recovery_butt3', 'obj': Button,
                                  'kwargs': {'text': 'reinit window loop', 'command': crv2},
                                  'place_mode': 'pack', 'place_kw': {'anchor': 'nw'}})
    main.recovery_widgets.append({'name': 'recovery_butt4', 'obj': Button,
                                  'kwargs': {'text': 'reinit window', 'command': cvr4},
                                  'place_mode': 'pack', 'place_kw': {'anchor': 'nw'}})
    main.recovery_widgets.append({'name': 'recovery_butt5', 'obj': Button,
                                 'kwargs': {'text': 'open exec line', 'command': cvr5},
                                 'place_mode': 'pack', 'place_kw': {'anchor': 'nw'}})

    main.recovery_widgets.append(lambda: main.configure(bg=Button()['bg']))
    main.recovery_widgets.append(lambda: main.title('Recovery'))


    main.geometry([900, 500])
    #main.resizable(False, False)
    main.title('MSGR QW - Loading')
    pprint('[info] init window and vars')

    main.configure(bg='black')

    if '--no-install-script' in sys.argv:
        main.title('msgr-qw-no-install-script')
        main.mainloop()

    load_lbl = main.create('load_lbl', Label, text='Loading...', bg='black', fg='white',
                     font=('Consolas', 9), justify=tk.LEFT)
    load_lbl.build('place', x=0, y=0)

    pb = main.create('loading_pb', ProgressBar, len_to_count=11, bg='black', fg='white', font=('Consolas', 9))
    pb.build('place', x=450, y=490, anchor='center')

    pprint('[info] created loading screen')

    def printin_load_lbl(v, level='i'):
        if level == 'i':
            load_lbl['text'] += '\n' + v
        elif level == 'e':
            load_lbl['text'] += '\n' + v + '\n\nClick "Exit" to exit program.'
        main.update()

    exit_button = main.create('exit_button', Button, text='Exit', bg='black', fg='white', font=('Consolas', 9), command=sys.exit)
    exit_button.build('place', x=850, y=450)
    action_load = main.create('action_load', Button, text='No action', bg='black', fg='white', font=('Consolas', 9))
    action_load.build('place', x=10, y=450)

    pprint('[info] created loading_screen buttons')

    main.update()

    if 'BTAE!debugMode_ENABLE' in sys.argv:
        pprint('[info] Debug Mode is enabled')
        debug_mode = True

    run_f_setup = False
    refresh = reinit_ui
    work = True
    last_obj_id = ''
    loading = True
    chat_sel_menu = False
    send_button = Button()
    send_private_button = Button()
    version = 'QW_1.1.8-DEV'
    encoding = 'UTF-8'
    base_conf = json.load(open('./data/base_data.json', 'r'))
    other_cl = Other()
    online_listbox = tk.Listbox()

    pprint('[info] inited vars and ui-elements')

    pprint('[info] loading data.nc')
    try:
        dat = SNConfig(decrypt(open(f'./data/{base_conf["LOAD_NC"]}', 'r', encoding='windows-1251').read(), eval(base_conf['CC'])))
        dat_d = dat.load()
    except Exception as _nc_ex:
        pprint(f'[error] data.nc not loaded, {_nc_ex}, {type(_nc_ex)}')
        showerror('Error1', f'{base_conf["LOAD_NC"]} damaged')
        raise Exception('Error1', f'{base_conf["LOAD_NC"]} damaged')
    try:
        setting_raw = dat_d['[SETTINGS]']
        user_local_settings = eval(setting_raw)
    except Exception as data_nc_load_ex:
        showerror('Error2', f'{base_conf["LOAD_NC"]} damaged, {data_nc_load_ex}')
        raise Exception('Error2', f'{base_conf["LOAD_NC"]} damaged')

    pb.tk.plus()
    pprint('[info] loaded')
    lng = user_local_settings['USER_SETTINGS']['SEL_LOCALE']
    pprint('[info] setting SCREEN_SETTINGS')
    try:
        main.tk.call('tk', 'scaling', user_local_settings['USER_SETTINGS']['SCREEN_SETTINGS'][0])
    except KeyError:
        user_local_settings['USER_SETTINGS'].update({'SCREEN_SETTINGS': [1.0, 0]})
        main.tk.call('tk', 'scaling', user_local_settings['USER_SETTINGS']['SCREEN_SETTINGS'][0])
    ui.root_scaling = user_local_settings['USER_SETTINGS']['SCREEN_SETTINGS'][0]
    ui.update_win_scaling()

    pprint('[info] loading locale')
    try:
        try:
            locale_fl = json.load(open(f'./data/locale/{lng}/locale.cfg', 'r', encoding=encoding))
        except json.JSONDecodeError:
            locale_fl = Config(f'./data/locale/{lng}/locale.cfg', coding=encoding)
    except UnicodeDecodeError:
        encoding = 'windows-1251'
        try:
            locale_fl = json.load(open(f'./data/locale/{lng}/locale.cfg', 'r', encoding=encoding))
        except json.JSONDecodeError:
            locale_fl = Config(f'./data/locale/{lng}/locale.cfg', coding=encoding)
    locale = Locale(locale_fl)

    pprint(f'[info] locale_fl locale/{lng}/locale.cfg')
    pprint(f'[info] language {lng}')

    pb.tk.plus()

    for i in sys.argv:
        if 'BootUpAction' in i:
            exec(i.split('$=%')[1], globals(), locals())

    pprint('[info] init theme')
    if user_local_settings['USER_SETTINGS']['THEME'] == 'light':
        default_fg = 'black'
        main.configure(bg='white')
        main.update()
        default_bg = 'white'
    elif user_local_settings['USER_SETTINGS']['THEME'] == 'black':
        default_bg = 'black'
        main.configure(bg='black')
        main.update()
        default_fg = 'white'
    else:
        try:
            theme(user_local_settings['USER_SETTINGS']['THEME'])
        except NameError as theme_load_err:
            showerror('Error', f'main window is destroyed {theme_load_err}')
            raise Exception('Error', f'main window is destroyed {theme_load_err}')
    main.option_add('*Font', font_theme)
    main.option_add('*Background', default_bg)
    main.option_add('*Foreground', default_fg)

    pb.tk.plus()

    main.configure(bg=default_bg)
    load_lbl.configure(bg=default_bg, fg=default_fg, font=font_theme)
    exit_button.configure(bg=default_bg, fg=default_fg, font=font_theme)
    action_load.configure(bg=default_bg, fg=default_fg, font=font_theme)
    pb.tk.configure(bg=default_bg, fg=default_fg, font=font_theme)
    main.update()
    pprint('[info] setup theme for loading screen')

    username = user_local_settings['USER_SETTINGS']['USERNAME']
    password = user_local_settings['USER_SETTINGS']['PASSWORD']
    server = user_local_settings['USER_SETTINGS']['SERVER']
    bt_server = user_local_settings['USER_SETTINGS']['SERVER']
    hash_method = user_local_settings['USER_SETTINGS']['HASHING_METHOD']
    pprint('[info] init data.nc variables')

    pb.tk.plus()

    if eval(dat_d['[SETTINGS]'])['USER_SETTINGS']['FIRST_BOOT'] == 'True':
        pprint('[info] first boot, upa')
        policy_win = ui.Popup()
        policy_win.title('User Policy Agreement')
        Label(policy_win, text='Please agree with user policy', font=('Consolas', 10)).pack()
        Button(policy_win, text='BTAEML Agreement', command=lambda: exec('import plugins.core.mod\nplugins.core.mod.plugin_info()'), font=('Consolas', 10)).pack()
        Button(policy_win, text='Continue', command=lambda: exec('policy_win.quit()\npolicy_win.destroy()'), font=('Consolas', 10)).pack()
        policy_win.mainloop()

    pprint('[info] upa completed')
    pb.tk.plus()

    if bt_server == '' or server == '':
        pprint('[info] selecting servers')
        printin_load_lbl('Please, select servers')

        def select_servers(a, b):
            if b:
                select_bt_server(b)
            if a:
                select_server(a)
            dump_data_nc()
            reload_data_nc()
            server_select_win.quit()
            server_select_win.destroy()

        def p2p_connect():
            for w in server_select_win.winfo_children():
                w.pack_forget()
            Label(server_select_win, text='Running P2P Client...').pack()
            server_select_win.destroy()
            shutdown()
            subprocess.run([sys.executable, 'p2p.py'])


        server_select_win = ui.Popup()
        server_select_win.title(locale['server_select_win'])
        server_select_win.resizable(False, False)
        Label(server_select_win, text=locale['servers_setup_title']).pack()
        server_entry = Entry(server_select_win, width=50)
        if server == '':
            server_entry.pack()
        else:
            Label(server_select_win, text=locale['serv_selected_alr']).pack()
        #bt_server_entry = Entry(server_select_win, width=50)
        #if bt_server == '':
        #    bt_server_entry.pack()
        #else:
        #    Label(server_select_win, text=locale['bt_serv_selected_alr']).pack()
        Button(server_select_win, text=locale['conf_server'], command=lambda: select_servers(server_entry.get(), False)).pack()
        Button(server_select_win, text='P2P', command=lambda: p2p_connect()).pack()
        server_select_win.mainloop()

    pprint('[info] servers selected')
    pb.tk.plus()

    if username == '' or password == '':
        pprint('[info] login to account')
        printin_load_lbl('Please, login/register in your account')
        def conf_login(a, b, win):
            user_local_settings['USER_SETTINGS']['USERNAME'] = a
            if b != '':
                hs = hashlib.new(hash_method)
                hs.update(b.encode())
                user_local_settings['USER_SETTINGS']['PASSWORD'] = hs.hexdigest()
            else:
                user_local_settings['USER_SETTINGS']['PASSWORD'] = ' '
            win.destroy()
            dump_data_nc()
            reload_data_nc()
            win.quit()

        login_win = ui.Popup()
        login_win.title(locale['login_txt'])
        login_win.resizable(False, False)
        Label(login_win, text=locale['login_hint']).pack()
        usr_entry = Entry(login_win, width=30)
        usr_entry.pack()
        passw_entry = Entry(login_win, width=30)
        passw_entry.pack()
        Button(login_win, text=locale['conf_login_tex'], command=lambda: conf_login(usr_entry.get(), passw_entry.get(), login_win)).pack()
        login_win.mainloop()

    pprint('[info] login completed')
    pb.tk.plus()
    pprint('[info] connecting to servers')

    bt_server_data = (False, {})
    printin_load_lbl('Connecting to account...')
    try:
        pprint('[info] connecting to account server')
        user = auth.User(username, password, bt_server.split(':')[0], int(bt_server.split(':')[1]))
        try:
            bt_server_data = user.get_data()
        except AttributeError:
            bt_server_data = (False, {})
        pprint('bt data')
        if not bt_server_data[0] and 'another client' in bt_server_data[1]['answer']:
            printin_load_lbl(bt_server_data[1]['answer'], 'e')
            action_load.configure(text='Exit from account', command=other_cl.exit_acc)
            main.mainloop()
        if not bt_server_data[0] and bt_server_data[1]['answer'] != 'Incorrect password':
            def serv_sel_tmp():
                select_bt_server('')
                dump_data_nc()
            printin_load_lbl('Not connected to BebraTech Authentication Server', 'e')
            if debug_mode:
                load_lbl['text'] += f'\nDebug Info:\ntd[0] -> false\n{bt_server_data}'
            action_load.configure(text='Reset BebraTech server address', command=serv_sel_tmp)
            main.mainloop()
        elif bt_server_data[1]['answer'] == 'Incorrect password':
            user_local_settings['USER_SETTINGS']['PASSWORD'] = ''
            user_local_settings['USER_SETTINGS']['USERNAME'] = ''
            dump_data_nc()
            printin_load_lbl('Incorrect Password', 'e')
            if debug_mode:
                load_lbl['text'] += f'\nDebug Info:\njust incorrect password for acc {username}\n{bt_server_data}, {password}'
            main.mainloop()
    except Exception as _ex:
        def serv_sel_tmp():
            select_server('')
            dump_data_nc()
        bt_server_data = (False, {})
        printin_load_lbl(f'Not connected to BebraTech Authentication Server: Server on {bt_server} not found.', 'e')
        if debug_mode:
            load_lbl[
                'text'] += f'\nDebug Info:\nIncorrect IP in <bt_server> variable.'
        action_load.configure(text='Reset BebraTech server address', command=serv_sel_tmp)
        pprint(f'[error] Not connected to BebraTech Authentication Server: Server on {bt_server} not found {_ex}')
        main.mainloop()
    pb.tk.plus()

    chat = chat_lib.Chat(server.split(':')[0], int(server.split(':')[1]), username)
    try:
        pprint('[info] connecting to chat server')
        printin_load_lbl('Connecting to Chat...')
        chat.connect()
    except Exception as chat_err:
        def serv_1_sel_tmp():
            select_server('')
            dump_data_nc()
        pprint(type(chat_err))
        printin_load_lbl(f'Not connected to Chatting Server: Server on {server} not found.', 'e')
        if debug_mode:
            load_lbl[
                'text'] += f'\nDebug Info:\nIncorrect IP in <server> variable.'
        action_load.configure(text='Reset Chatting server address', command=serv_1_sel_tmp)
        main.mainloop()

    pb.tk.plus()

    print('[info] Servers connection Completed')

    my_message = tk.StringVar()
    send_entry = Text()

    if user_local_settings['USER_SETTINGS']['BTAEML'] == 'True':
        from data.lib.plugin_api import exec_plugs, get_plugs
        pprint('[info] BTAEML LOADED')

    try:
        _plugin_objects = get_plugs(sys.argv[1])
    except (NameError, FileNotFoundError):
        _plugin_objects = {}

    pb.tk.plus()

    exc_chf = SConfig(dat_d['[LOADER_CONFIG]'])

    os.chdir(os.path.dirname(os.path.realpath(__file__)))


    if eval(dat_d['[SETTINGS]'])['USER_SETTINGS']['FIRST_BOOT'] == 'True':
        user_local_settings['USER_SETTINGS']['FIRST_BOOT'] = 'False'
        run_f_setup = True


    try:
        pprint('[info] loading plugins')
        exec_plugs(_plugin_objects)
        pprint('[info] completed')
    except NameError:
        pprint('[warning] not detected plugin_api module')
        pass

    pb.tk.plus()

    # init theme
    pprint('[info] init theme')

    if user_local_settings['USER_SETTINGS']['THEME'] == 'light':
        default_fg = 'black'
        main.configure(bg='white')
        main.update()
        default_bg = 'white'
    elif user_local_settings['USER_SETTINGS']['THEME'] == 'black':
        default_bg = 'black'
        main.configure(bg='black')
        main.update()
        default_fg = 'white'
    else:
        theme(user_local_settings['USER_SETTINGS']['THEME'])

    pprint('[info] finishing')

    main.protocol("WM_DELETE_WINDOW", shutdown)


    reinit_window()

    if os.path.exists('./msgr_upd.py'):
        if open('./msgr.py', 'r').read() != open('./msgr_upd.py', 'r').read():
            upd = askyesno('Info', locale['update_detected'])
            if upd:
                base_conf['RUNT_ACTION'] = 'ON_FINISH_RESTART+LL_F_UPDATE'
                work = False

    for i in sys.argv:
        if 'StartUpAction' in i:
            exec(i.split('$=%')[1], globals(), locals())


    if bt_server_data[1] != 'blocked':
        chat_window = Text(fg=default_fg, bg=default_bg, font=font_theme, width=110)
        chat_window.bind('<MouseWheel>', scroll)
        chat_window.place(x=0, y=0)
    if not run_f_setup and work and bt_server_data[1] != 'blocked':
        try:
            if '_show_ip' not in bt_server_data[1]['answer']:
                auth.update_personal_conf(username, ['_show_ip', 'False'])
                auth.update_personal_conf(username, ['_admin', 'False'])
                Debug().relog()
        except KeyError:
            pprint('[error] Not Connected to servers, unable to use any network functions')
        #threading.Thread(target=account_loop).start()
    main.configure(bg=default_bg)
    main.title(locale['WINDOW_TITLE_TEXT'])

    settings_cl = Settings()
    refresh()
    reinit_window()
    reinit_ui()
    read_loaded()
    main.bind('<Key>', reinit_wrapper)
    pprint('[info] main thread started')
    if work:
        pprint('[info] work - true')
        threading.Thread(target=chat.async_recv, daemon=True).start()
        try:
            pprint('[info] starting crt')
            main.tk_thread(complete_recv, 100)
            pprint('[info] started')
        except RuntimeError:
            pprint('[error] crt_start ex Runt')
            pass
        loading = False
        reinit_ui()
        if run_f_setup:
            FirstSetup(default_bg, default_fg, font_theme).get_win()
        chat.send({'action_for_chat_server': 'MyUSER', 'username': username})
        main.tk_thread(count_unread, 500)
        print('[info] READY')
        print('[info] READY')
        print('[info] READY')
        print('[info] READY')

        pprint(f'[info] successful start with reinit_ui_counter = {reinit_count}')
        chat.send({'action_for_chat_server': 'ReadyToQ', 'username': username})
        c = 1
        while work:
            main.mainloop()
            print(f'unauthorized quit n {c}, lopping')
            c += 1
    pprint(f'[info] exited with reinit_ui_counter = {reinit_count}')
    pprint('[info] stopping program')
    work = False
    tick_sys.stop = True
    shutil.rmtree('./__pycache__', ignore_errors=True)

    pprint('[info] shutdown all threads')
    stop_event.set()
    c = 0
    for t in threading.enumerate():
        pprint(f'[info] num: {c}')
        c += 1
        if t != threading.current_thread():
            t.join(0)
    pprint('[info] disconnecting from servers')

    auth.disconnect()
    chat.shutdown(socket.SHUT_RDWR)
    chat.close()
    pprint('[info] backup data.nc and base_data')
    json.dump(base_conf, JsonObject(open('./data/base_data.json', 'w')))
    if backup_data_nc:
        dat_d['[SETTINGS]'] = str(user_local_settings)
        with open(f'./data/{base_conf["LOAD_NC"]}', 'w', encoding='windows-1251') as fl:
            fl.write(encrypt(dat.dump(dat_d), eval(base_conf['CC'])))
    pprint('[info] finish')
else:
    showerror('Error', 'License Error, Please run with launcher')