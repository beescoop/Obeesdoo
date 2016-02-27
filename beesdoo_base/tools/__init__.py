# -*- coding: utf-8 -*-

def concat_names(*args):
    """
        Concatenate only args that are not empty
        @param args: a list of string
    """
    return ' '.join(filter(bool, args))
