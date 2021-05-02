
import copy


import functools
import itertools


    
## Higher order functions
def argstar_deco(f):
    """Function decorator that unfolds positional arguments 1 level before passing them to the wrapped function
    as variable length positional arguments."""
    @functools.wraps(f)
    def _f(*arg_l):
        return f(*itertools.chain(*arg_l))
    
    return _f

def preargs_deco(f, preargs=tuple(),prekwargs=dict()):
    """Function decorator that applies certain arguments to the parameters of a function as defaults"""
    @functools.wraps(f)
    def _f(*postargs,**postkwargs):
        args = list(postargs) + list(preargs)[len(postargs):]
        kwargs = dict(prekwargs)
        for k,v in postkwargs.items():
            kwargs[k] = v
            
        return f(*args,**kwargs)
            
    return _f

def function_composition(*funcs):
    """Compound multiple functions "funcs" by calling them sequentially in order, and feeding the ouput of a function to the input of the next.
    The functions in "func" must be callable with a single positional argument, except for the first function.
    Return a function that computes the function composition. The parameters of the returned function are the same as the first function in "funcs"."""
    def _f(*args,**kwargs):
        partial = None
        
        if funcs:
            partial = funcs[0](*args,**kwargs)
            for f in funcs[1:]:
                partial = f(partial)
                
        return partial
    
    return _f

## Null func
def null_func(*args,**kwargs):
    return None
    
## Map extensions
### Classes
class Mapper(object):
    def __init__(self,f):
        self.f = f
    def __call__(self,it):
        return map(self.f,it)
    
class StarMapper(Mapper):
    def __init__(self,f):
        super().__init__(argstar_deco(f))
    def __call__(self,*its):
        f_it = its[0] if len(its) == 1 else zip(*its)
        return super()(f_it)
    
class FuncMapper(Mapper):
    def __init__(self,fs):
        super().__init__(fs)
    def __call__(self,*args,**kwargs):
        return map(lambda x: x(*args,**kwargs),self.fs)
        
### Direct functions
def starmap(*its,f=null_func):
    f_it = its[0] if len(its) == 1 else zip(*its)
    return map(argstar_deco(f),f_it)

def funcmap(*args,fs=tuple()): # kwargs are not possible
    return map(lambda x: x(*args),fs)

# Equality OPs
def key_eq(a,b,key):
    return a[key] == b[key]

# Object transformations
def key_remap(l,map_table,inplace=False):
    lt = copy.copy(l)
    
    l, lt = (lt,l) if inplace else (l,lt)
    
    for si in map_table:
        del lt[si]
    
    for si, ti in map_table.items():
        lt[ti] = l[si]
        
    return lt
        
class KeyRemaper:
    def __init__(self,map_table,inplace=False):
        self.map_table = map_table
        self.inplace = inplace
        
    def __call__(self,l):
        return key_remap(l,self.map_table,self.inplace)
