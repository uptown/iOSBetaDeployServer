# -*- coding: utf-8 -*-

from functools import wraps
from django.utils.decorators import available_attrs
from django.db import transaction
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist


def transaction_with_error_handler(error_handler, using='default'):

    def decorator(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            with transaction.commit_manually(using=using):
                try:
                    ret = func(self, *args, **kwargs)
                    transaction.commit(using=using)
                    return ret
                except Exception, e:
                    transaction.rollback(using=using)
                    return error_handler(e)

        return wrapped
    return decorator

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
