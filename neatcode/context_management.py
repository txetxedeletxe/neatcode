"""
==================
Context Management
==================

This module contains **Context Manager** (CM) pattern implementations.

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

"""
            
## Object lifecycle
class ObjectLifecycleCM(object):
    """
        Basic implementation of object lifecycle management.

        Creates the object on entering the context and destorys it on exit.

        Object creation is handled by a callback with optional arguments.
    """
    def __init__(self,
                    constructor,
                    args=tuple(),
                    kwargs=dict()):
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

        Same behaviour as ´ObjectLifecycleCM´.

        Object creation is handled by the method ´construct´, which users may override 
        in subclasses.
    """
    def __init__(self, 
                    args=tuple(),
                    kwargs=dict()):
        super().__init__(self.construct,args=args,kwargs=kwargs)
        
    def construct(self, *args, **kwargs):
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
                    pre_collect=False,
                    post_collect=True):
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
        
        Both timestamps are accessible as attributes ´t_start´ and ´t_end´. The difference between them
        (execution time of the context) is accessible as a method ´t_delta´.
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
class CombinedCM(object):
    """
        Execute multiple CMs in a single context.

        Wraps multiple CMs and executes them on context entry and exit.

        On context entry    -   Returns a tuple with the return values of the wrapped CMs (in corresponding order)
        On context exit     -   Returns a boolean value aggregated from exit return values of the wrapped CMs.
                                The aggregation function is configurable using the attribute `exit_criterion`
    """
    def __init__(self,
                    cms,
                    exit_criterion=all):
        self.cms = cms

        self.exit_criterion = exit_criterion

    def __enter__(self):
        return [cm.__enter__() for cm in self.cms]

    def __exit__(self,*args,**kwargs):
        exit_val = [cm.__exit__(*args,**kwargs) for cm in self.cms]
        return self.exit_criterion(exit_val)
            



