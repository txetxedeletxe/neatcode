"""
==================
Context Management
==================

This module contains **Context Manager** (CM) pattern implementations.

Name Overlapping CMs
--------------------

CMs for temporarily overlapping (substituting and adding) "names" to different namespace constructs

    DictOverlapCM           Overlap the values of names (keys) in a dictionary
    NameOverlapCM           Overlap the values of names in a namespace (global namespace by default)
    BuiltinOverlapCM        Overlap builtin values (use with caution)


Object Lifecycle CMs
--------------------

CMs for managing the *lifecycle* (creation and destruction) of objects.

    ObjectLifecycleCM       Basic implementation of object lifecycle management
    SelfConstructingOLCM    User-extensible base class for lifecycle management


Garbage Collection CMs
----------------------

CMs for declaring explicit garbage collection checkpoints

    GarbageCollectorCM      Garbage collection at the end (and/or beginning) of the context

Timing CMs
----------

CMs for measuring the execution time of code blocks

    TimingCM                Record the timestamp at the beginning and the end of the context

Meta
----

Tools to augment the usability of CMs.

    CombinedCM              Execute multiple CMs in a single context.
    CMIterator              Iterate throught CMs activating each one for one iteration.

"""

## Name Overlap
class DictOverlapCM(object):
    def __init__(self, dictionary:dict, overwrite_dict:dict):
        self.dictionary = dictionary
        self.overwrite_dict = overwrite_dict

        self.overwritten_dict = None
        self.added_keys = None

    def __enter__(self):
        overwrite_keys = set(self.overwrite_dict.keys())

        overwritten_keys = overwrite_keys & (set(self.dictionary.keys()))
        overwritten_values = map(self.dictionary.__getitem__,overwritten_keys)
        self.overwritten_dict = dict(zip(overwritten_keys,overwritten_values))
        
        self.added_keys = overwrite_keys - overwritten_keys

        self.dictionary.update(self.overwrite_dict)

    def __exit__(self,*args,**kwargs):
        self.dictionary.update(self.overwritten_dict)
        for k in self.added_keys: del self.dictionary[k] # TODO add exception handling

import inspect as _inspect
class NameOverlapCM(DictOverlapCM):
    def __init__(self, overwrite_dict:dict, namespace=None):
        self.namespace = namespace
        if self.namespace is None:
            cf = _inspect.currentframe()
            if cf is None:
                pass # TODO add error for unexpected behaviour
            globals_ = cf.f_back.f_globals
            super().__init__(globals_,overwrite_dict)
        else:
            super().__init__(self.namespace.__dict__,overwrite_dict)

import builtins as _builtins
class BuiltinOverlapCM(NameOverlapCM):
    def __init__(self, overwrite_dict:dict):
        super().__init__(overwrite_dict,_builtins)

## Object lifecycle
class ObjectLifecycleCM(object):
    """
        Basic implementation of object lifecycle management.

        Creates the object on entering the context and destorys it on exit.

        Object creation is handled by a callback `constructor` with optional arguments.
    """
    def __init__(self,
                    constructor : "callable",
                    args : tuple = tuple(),
                    kwargs : dict = dict()):
        self.constructor = constructor

        self.args = args
        self.kwargs = kwargs

        self.o = None
        
    def __enter__(self):
        self.o = self.constructor(*self.args, **self.kwargs)
        return self.o
    
    def __exit__(self,*args,**kwargs):
        if self.o is not None: del self.o

class SelfConstructingOLCM(ObjectLifecycleCM):
    """
        User-extensible base class for lifecycle management.

        Same behaviour as ??ObjectLifecycleCM??.

        Object creation is handled by a internal method ??_construct??, which users may override 
        in subclasses.
    """
    def __init__(self, 
                    args : tuple = tuple(),
                    kwargs : dict = dict()):
        super().__init__(self._construct,args=args,kwargs=kwargs)
        
    def _construct(self, *args, **kwargs):
        return None

## Garbage Collection
import gc as _gc

class GarbageCollectorCM(object):
    """
        Garbage collection at the end (and/or beginning) of the context
        
        Calls the garbage collector for collection at the entry and/or exit point of the
        CM (configurable in construction).
    """
    def __init__(self,
                    pre_collect : bool = False,
                    post_collect : bool = True):
        self.pre_collect = pre_collect
        self.post_collect = post_collect

    def __enter__(self):
        if self.pre_collect: _gc.collect()

    def __exit__(self,*args,**kwargs):
        if self.post_collect: _gc.collect()

## Time
import time as _time

class TimingCM(object):
    """
        Record the timestamp at the beginning and the end of the context.
        
        Both timestamps are accessible as attributes ??t_start?? and ??t_end??. The difference between them
        (execution time of the context) is accessible as a method ??t_delta??.
    """
    def __init__(self):
        self.t_start = -1
        self.t_end = -1

    def __enter__(self):
        self.t_start = _time.time()
        return self

    def __exit__(self,*args,**kwargs):
        self.t_end = _time.time()

    def t_delta(self):
        return self.t_end - self.t_start

## META
class MultiCMWrapper(object): # TODO 
    """
        Base class for wrappers that wrap multiple CMs.

        Defines a `cms` attribute that contains a collection of context managers.
    """
    def __init__(self, cms : tuple):
        self.cms = cms

class CombinedCM(MultiCMWrapper):
    """
        Execute multiple CMs in a single context.

        CM that wraps multiple CMs and executes all of them on context entry and exit.

        On context entry    -   Returns a tuple with the return values of the wrapped CMs (in corresponding order)
        On context exit     -   Returns a boolean value aggregated from exit return values of the wrapped CMs.
                                The aggregation function is configurable using the attribute `exit_criterion`
    """
    def __init__(self,
                    cms : tuple,
                    exit_criterion : "callable" = all):
        super().__init__(cms=cms)

        self.exit_criterion = exit_criterion

    def __enter__(self):
        return tuple((cm.__enter__() for cm in self.cms))

    def __exit__(self,*args,**kwargs):
        exit_val = tuple((cm.__exit__(*args,**kwargs) for cm in self.cms))
        return self.exit_criterion(exit_val)
            

class CMIterator(MultiCMWrapper):
    """
        Iterate throught CMs activating each one for one iteration.

        Iterator that wraps multiple CM. When iterated through, it activates each CM for one iteration (in
        the corresponding order).
    """
    def __init__(self, cms : tuple):
        super().__init__(cms)

    def __iter__(self):
        for cm in self.cms:
            with cm as cm_r:
                yield cm_r


