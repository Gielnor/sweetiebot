import logging
import random
import unicodedata

def logerrors(func):
    from functools import wraps
    @wraps(func)
    def logged(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception:
            logging.exception('Error in '+func.__name__)
            return "My code is problematic :sweetieoops:"
    return logged

def randomstr():
    return ('%08x' % random.randrange(16**8))

def fuck(u):
    return unicodedata.normalize('NFKD', u).encode('ascii', 'ignore')

