## META
class CombinedCM(object):
    def __init__(self,cms):
        self.cms = cms

    def __enter__(self):
        return [cm.__enter__() for cm in self.cms]

    def __exit__(self,*args,**kwargs):
        exit_val = [cm.__exit__(*args,**kwargs) for cm in self.cms]
        return all(exit_val)
            
## Object lifecycle
class ObjectLifecycleCM(object):
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
    def __init__(self, 
                    args=tuple(),
                    kwargs=dict()):
        super().__init__(self.construct,args=args,kwargs=kwargs)
        
    def construct(self, *args, **kwargs):
        return None

## Garbage Collection
import gc as _gc

class GarbageCollectorCM(object):
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

