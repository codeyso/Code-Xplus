# -*- coding: utf-8 -*-
"""
全局变量: GlobalVar
"""
def _init():
    global _global_dict
    _global_dict = {}

def set_value(name, value, bool=False):
    if bool:
        _global_dict[name] = value
    elif name in _global_dict:
        pass
    elif not bool:
        _global_dict[name] = value

def get_value(name, defValue=''):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue
def add_value(name, value):
    if isinstance(_global_dict[name], dict) and isinstance(value, dict):
        _global_dict[name].update(value)
    elif isinstance(_global_dict[name], list) and isinstance(value, list):
        _global_dict[name] = _global_dict[name] + value