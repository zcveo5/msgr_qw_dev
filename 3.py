
def get_var_name(var_value, use_locals=False, **kwargs):
    """Gets var name from globals() / locals()
    :param var_value: value of variable
    :param use_locals: use locals to find var_name. need to give 'locals' argument to kwargs"""
    where = globals()
    if use_locals:
        where = kwargs['locals']
    vl = list(where.values())
    ks = list(where.keys())
    ind = vl.index(var_value)
    return ks[ind]