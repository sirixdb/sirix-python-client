from functools import partial, update_wrapper


def partialized(func, *args, **kwargs):
    partialed: func = update_wrapper(partial(func, *args, **kwargs), func)
    return partialed
