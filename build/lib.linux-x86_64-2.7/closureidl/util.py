from decorator import decorator as _decorator

def join(sep):
    def _join(f, *args, **kwargs):
        return sep.join(f(*args, **kwargs))
    return _decorator(_join)