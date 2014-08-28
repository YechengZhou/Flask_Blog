__author__ = 'yechengzhou'

import functools
def checklogin(func):
    @functools.wraps(func)
    def wrapper():
        if True:
            func.username = 'hhe'
            #print func
        else:
            func.username = None
        return func()
    return wrapper


@checklogin
def a():
    print
    print 123

if __name__ == '__main__':
    a()
    #print a