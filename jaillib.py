import json
import os
import traceback

#print(f'$ JAIL LIB \n $ # $ # $ # $ # $ # $ # $ # $ #\nGlobals (for optimizing, only keys):\n{', '.join(globals().keys())}\nLocals (for optimizing, only keys):\n{', '.join(locals().keys())}\n$ # $ # $ # $ # $ # $ # $ # $ # ')

if not os.path.exists('./data/JBTweaks'):
    os.mkdir('./data/JBTweaks')

print('$JB Loading Tweaks...')
print(f'$JB Running as {__name__}')
tweaks_files = []
globals()['__JailBreakTweaks__'] = []
for file in os.listdir('./data/JBTweaks'):
    if file not in ['tweaks.json', 'configure.py', '__pycache__']:
        print(f'$JB Detected {file}')
        tweaks_files.append(file)
if not os.path.exists('./data/JBTweaks/tweaks.json'):
    with open('./data/JBTweaks/tweaks.json', 'w') as fl:
        fl.write('{}')
_setts = json.load(open('./data/JBTweaks/tweaks.json', 'r'))
print('====== EXECUTING ======')
for file in tweaks_files:
    adv = ''
    if file not in _setts:
        adv = '(!)'
        _setts.update({file: {'state': 'True'}})
    if _setts[file]['state'] == 'True':
        print(f'$JB Executing {file} {adv}')
        globals()['__JailBreakTweaks__'].append(f'{file}')
        try:
            exec(open(f'./data/JBTweaks/{file}', 'r', errors='replace').read(), globals(), locals())
        except Exception as _ex:
            print(f'============================== TWEAK ERROR {str(_ex.__class__).upper()} ==============================\n\nError in {file}:\n{open(f'./data/JBTweaks/{file}', 'r', errors='replace').read()}\n\n{traceback.format_exc()}')

print('$JB Tweaks Loaded!')
