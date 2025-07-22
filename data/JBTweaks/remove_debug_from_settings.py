import json
import os.path

from data.lib.ui import Popup


if not os.path.exists('./data/settings_conf.json'):
    with open('./data/settings_conf.json', 'w') as fl:
        fl.write('{}')
conf = json.load(open('./data/settings_conf.json'))
_conf = conf.copy()

class RemoveDebugFromSettingMod(Settings):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def sub_f_ui(self):
        super().sub_f_ui()
        Button(self.window_locale, text='Manage What widgets shown on side panel', command=self.ui_custom, bg=default_bg, fg=default_fg, font=font_theme).pack(anchor='nw', padx=3)

    def _create_base(self):
        for wid in self._base_widgets:
            if locale.get_key(wid['text']) not in conf:
                conf.update({locale.get_key(wid['text']): True})
            if conf[locale.get_key(wid['text'])]:
                wid.pack(anchor='nw')


    def ui_custom(self):
        def switch(event):
            _txt = event.widget['text'].split(' | ')[0]
            conf[_txt] = not conf[_txt]
            if conf != _conf:
                json.dump(conf, open('./data/settings_conf.json', 'w'))

        win = Popup(main, 450, 250, [300, 500], [default_bg, default_fg, font_theme], title='Settings UI Customization')
        for i in self._base_widgets:
            txt = locale.get_key(i['text'])
            if txt not in conf:
                conf.update({txt: True})
            b = Button(win, text=txt + ' | ' + str(' ' * (30 - len(txt))) +  ' | ' + str(conf[txt]), bg=default_bg, fg=default_fg, font=font_theme)
            b.pack(anchor='nw')
            b.bind('<ButtonPress-1>', switch)

        if conf != _conf:
            json.dump(conf, open('./data/settings_conf.json', 'w'))




Settings = RemoveDebugFromSettingMod
