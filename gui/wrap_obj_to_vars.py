import tkinter as tk
from datetime import datetime
from pathlib import Path
from src.helpers import parse_date
from undo_redo import Undo

# special case datetime
def closure_date_write(root, key, var):
    def callback(*args):
        Undo.ref().store_change(var, 
            root[key].strftime('%Y-%m-%d %H:%M:%S'), var.get())
        root[key] = parse_date(var.get(), '')
    return callback

# sepcial case paths
def closure_path_write(root, key, var):
    def callback(*args):
        Undo.ref().store_change(var, str(root[key]), var.get())
        root[key] = Path(var.get())
    return callback

# when updating an item
def closure_write(root, key, var):
    def callback(*args):
        Undo.ref().store_change(var, root[key], var.get())
        root[key] = var.get()
    return callback

# when deleting an item
def closure_unset(root, key, var):
    def callback(*args):
        del root[key]

def create_wrapper(root, key, wrapper):
    """Wrap a variable to tkinter variable"""
    if isinstance(root[key], bool):
        var = tk.BooleanVar(value=root[key])
    elif isinstance(root[key], str):
        var = tk.StringVar(value=root[key])
    elif isinstance(root[key], int):
        var = tk.IntVar(value=root[key])
    elif isinstance(root[key], float):
        var = tk.DoubleVar(value=root[key])
    elif isinstance(root[key], datetime):
        var = tk.StringVar(value=root[key].strftime('%Y-%m-%d %H:%M:%S'))
        var.trace_add('write', closure_date_write(root, key, var))
        return var
    elif isinstance(root[key], Path):
        path = str(root[key])
        var = tk.StringVar(value=path if path != '.' else '')
        var.trace_add('write', closure_path_write(root, key, var))
        return var
    elif isinstance(root[key], (list, tuple)):
        lst = []
        for i, _ in enumerate(root[key]):
            lst.append(create_wrapper(root[key], i, wrapper))
        return lst
    elif isinstance(root[key], dict):
        dct = {}
        for k,v in root[key].items():
            dct[k] = create_wrapper(root[key], k, wrapper)
        return dct
    elif not root[key] or isinstance(root[key], set):
        return # unhandled
    elif str(type(root[key]))[1:6] == 'class':
        return wrap_instance(root[key], wrapper)
    else:
        return # unhandled
            
    var.trace_add('write', closure_write(root, key, var))
    var.trace_add('unset', closure_unset(root, key, var))
    return var


def wrap_instance(inst, wrapped=None):
    """Wrapp a class instance"""
    if not wrapped:
        wrapped = {}
    assert str(type(inst))[1:6] == 'class'
    inst_id = f'_{id(inst)}'
    if inst_id in wrapped:
        return wrapped[inst_id] # prevent cyclic wrap
    
    wrapped[inst_id] = dct = {}
    for k,v in inst.__dict__.items():
        if k[0] != '_' and not hasattr(v, '__call__'):
            dct[k] = create_wrapper(inst.__dict__, k, wrapped)
        elif k == '_data':
            dct['_data'] = v

    return dct


def reload_item(to, key, vlu, wrapped):
    '''
    When reloading a wrapped item, reload values into already wrapped
    Reset all wraps messes up GUI, so do this instead
    '''
    if not to:
        return
    if isinstance(vlu, dict):
        # remove keys no longer in stored in vlu
        for k in [k for k in to[key].keys() if k not in vlu]:
            del to[k]
        # set vlues and add new keys
        for k,v in vlu.items():
            if k in to[key]:
                reload_item(to[key], k, v, wrapped)
            else:
                w = create_wrapper(vlu, k, wrapped)
                to[key][k] = w
    elif isinstance(vlu, (list, tuple)):
        from_len = len(vlu)
        to_len = len(to[key])
        while len(to[key]) > from_len:
            to[key].pop() # too many in to
        for i, v in enumerate(vlu):
            if i < to_len:
                reload_item(to[key], i, v, wrapped)
            else: # when we have more items than to
                w = create_wrapper(vlu, i, wrapped)
                to[key].append(w)
    elif isinstance(vlu, datetime):
        to[key].set(vlu.strftime('%Y-%m-%d %H:%M:%S'))
    elif isinstance(vlu, Path):
        to[key].set(str(vlu))
    elif isinstance(vlu, (str, int, float, bool)):
        to[key].set(vlu)
    elif str(type(vlu))[1:6] == 'class':
        reload_wrapped(to[key], vlu, wrapped)
    else:
        to[key].set(vlu)


def reload_wrapped(to, from_, wrapped=None):
    '''
    When reloading a wrapped item, reload values into already wrapped
    Reset all wraps messes up GUI, so do this instead
    '''
    if not wrapped:
        wrapped = {}
    assert str(type(from_))[1:6] == 'class'
    inst_id = f'_{id(from_)}'
    if inst_id in wrapped:
        return wrapped[inst_id] # prevent cyclic wrap
    
    wrapped[inst_id] = {}
    for k,v in from_.__dict__.items():
        if k == '_data':
            to['_data'] = v
        elif k[0] == '_':
            continue
        elif to[k] is None:
            to[k] = create_wrapper(
                from_.__dict__, k, wrapped)
        else:
            reload_item(to, k, v, wrapped)


