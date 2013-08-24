# -*- coding: utf-8 -*-

from functools import wraps

def error_handling(error_handler):

    def decorator(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            try:
                ret = func(self, *args, **kwargs)
                return ret
            except Exception, e:
                import traceback
                traceback.print_exc()
                return error_handler(e)

        return wrapped
    return decorator
