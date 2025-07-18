"""Encrypt Lib"""

import random


def generate_salt():
    codec = r"""qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890~!@#$%^&*()_+-=?><,./|"'[]{}:; йцукенгшщзхъфывапролджэячсмитьбю"""
    symbols = ['\n']
    for i in codec:
        symbols.append(i)
    randomized_symbols = {}
    symbols_c = symbols.copy()
    for i in range(len(symbols_c)):
        print(i)
        cur_ind = random.randint(0, len(symbols) - 1)
        randomized_symbols.update({symbols_c[i]: symbols[cur_ind]})
        symbols.remove(symbols[cur_ind])
    return randomized_symbols


def encrypt(data, salt):
    out = []
    for sym in data:
        try:
            out.append(salt[sym])
        except KeyError:
            salt.update({sym: "?"})
            out.append(salt[sym])
    return ''.join(out)


def decrypt(data, salt):
    out = []
    k_list = list(salt.keys())
    v_list = list(salt.values())
    for sym in data:
        try:
            out.append(k_list[v_list.index(sym)])
        except ValueError:
            out.append('?')
    return ''.join(out)