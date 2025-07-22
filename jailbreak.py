import io
import json
import os.path
import subprocess
import sys
import tkinter
from tkinter import Button
from tkinter.messagebox import showinfo
try:
    from data.lib import ui
except ModuleNotFoundError:
    print('$ Using legacy ui format;')
    from data import btaeui as ui
    if not hasattr(ui, 'Win'):
        print('$ Using VERY legacy ui format; Errors granted')
        ui.Win = tkinter.Tk

class ModWin(ui.Win):
    def __init__(self, **kwargs):
        self.__mainloop = False
        self.adv = ''
        super().__init__(**kwargs)
        self.title()
        if not hasattr(self, 'his'):
            self.his = {}
        if not hasattr(self, 'tk_thread'):

            def _tk_thread(target, sleep_time, /, *args):
                def wrapper(*_args):
                    _ret = target(*_args)
                    if _ret != -1:
                        self.after(sleep_time, wrapper, *args)
                wrapper(*args)

            self.tk_thread = _tk_thread
        self.his['load_lbl'] = tkinter.Label(justify='left')
        self.his['load_lbl'].place(x=0, y=0)
        def _wrapper():
            try:
                temp = sys.stdout.read().split('\n')
            except io.UnsupportedOperation:
                temp = ["Can't read logs :("]
            if len(temp) > 24:
                temp = temp[len(temp) - 24::]
            try:
                self.his['load_lbl']['text'] = '\n'.join(temp)
            except KeyError:
                print('Loaded!')
                return -1
        self.tk_thread(_wrapper, 50)
    def mainloop(self, n = 0):
        try:
            temp = sys.stdout.read()
        except io.UnsupportedOperation:
            temp = ['READY', '[msgr.py][info] BTAEML LOADED']
            Button(text='[ JAILBREAK ] quit this window cycle', command=self.quit).pack()
        if 'READY' in temp and eval(os.environ['__JailBreak_CODE_CONFIG__'])['bypass_script'] == 'default' or '[msgr.py][info] BTAEML LOADED' in temp and eval(os.environ['__JailBreak_CODE_CONFIG__'])['bypass_script'] == 'srv':
            print('$JB Final mainloop')
            if not os.path.exists('./data/JBTweaks'):
                print('$JB Running setup...')
                setup()
            super().mainloop(n)
        else:
            print('$JB Skipping non-final mainloop')
    def title(self, t):
        super().title(f'{t} | JailBreak {self.adv}')

    def orig_mainloop(self):
        super().mainloop()

def setup():
    showinfo('$JB', 'Welcome to Jailbreak!\n\nTweaks should be installed in data/JBTweaks\nTo configure Tweaks run data/JBTweaks/configure.py\n\nEnjoy!')
    os.makedirs('./data/JBTweaks', exist_ok=True)
    with open('./data/JBTweaks/configure.py', 'w') as fl:
        fl.write(...)


if __name__ == '__main__':
    print('$JB Launcher Mode')
    if '--debug' not in sys.argv:
        if not os.path.exists('./jailbreak_data.json') or '--update-config' in sys.argv:
            with open('./jailbreak_data.json', 'w'):
                pass
            print('$ Analyzing source code...')
            _result = {}
            _code = open('./msgr.py', 'r', errors='Replace').read()
            if 'RunBeforeWin' not in _code:
                print('$ RunBeforeWin is not supported')
                _result['legacy'] = True
            else:
                print('$ RunBeforeWin is supported')
                _result['legacy'] = False
            print('$ Finding launcher...')
            if os.path.exists('./loader.py') and os.path.exists('./launcher.pyw'):
                print('$ Detected loader/launcher system')
                _result['file_to_load'] = 'loader.py'
            elif os.path.exists('./launcher.pyw'):
                print('$ Detected launcher')
                _result['file_to_load'] = 'launcher.pyw'
            elif os.path.exists('./run.pyw'):
                print('$ Detected run.pyw legacy system')
                _result['file_to_load'] = 'run.pyw'
            print('\n[*] servers - bypasses only servers connection\n[*] non final - bypasses all non final mainloop')
            ans = input('[?] Mainloop bypass script:')
            if ans == 'servers':
                _result['bypass_script'] = 'srv'
            elif ans == 'non final':
                _result['bypass_script'] = 'default'
            json.dump(_result, open('./jailbreak_data.json', 'w'))
            print(f'Analyzing completed:\nLegacy: {_result["legacy"]}\nExecutable: {_result["file_to_load"]}')
        config = json.load(open('./jailbreak_data.json', 'r'))
        globals()['__JailBreak_CODE_CONFIG__'] = config
        os.environ['__JailBreak_CODE_CONFIG__'] = str(config)
        os.environ['__LOW_LAUNCHER'] = os.path.abspath('launcher.pyw')

        if config['legacy']:
            subprocess.run([sys.executable,
                            config['file_to_load'],
                            "BootUpAction$=%exec(open('./jailbreak_legacy_script.py', 'r').read())"] + sys.argv[1::])
        else:
            subprocess.run([sys.executable,
                            config['file_to_load'],
                            'RunBeforeWin$=%from jailbreak import * ; Win = ModWin', "BootUpAction$=%exec(open('./jaillib.py', 'r').read())"] + sys.argv[1::])

    else:
        print('Debug mode:')
        while True:
            exec(input('>>>'))