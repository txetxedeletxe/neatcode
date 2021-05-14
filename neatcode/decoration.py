# TODO document code

import neatcode.policy as _policy
import neatcode.object_manipulation as _object_manipulation

class Decorator(object): # Base class for decorators    
    DOC_PREFIX = "\n@ Decorated by:\t{decoratorRepr}\n"
    REPR_STR = "{className}({args})"
    def __init__(self, callable_):
        self.callable = callable_
        self.__doc__ = self._generate_doc()

    def __call__(self,*args,**kwargs):
        return self.callable(*args,**kwargs)

    def __repr__(self):
        args, kwargs = self.__args__()
        
        return self.REPR_STR.format(className=type(self).__name__,)

    def __args__(self): # TODO implement object manipulator to get this method
        return tuple(), dict(callable_="callable_")

    def _generate_doc(self):
        c_doc = self.callable.__doc__ or ""
        return self.DOC_PREFIX.format(decoratorRepr=repr(self)) + c_doc


## Arguments
### Defaults
class PreargumentDecorator(Decorator):
    def __init__(self, 
                    callable_, 
                    preargs=tuple(), 
                    prekwargs=dict(),
                    substitution_policy=_policy.argument_substitution.default_preargs):
        super().__init__(callable_)

        self.preargs = preargs
        self.prekwargs = prekwargs

        self.substitution_policy = substitution_policy

    def __call__(self,*postargs,**postkwargs):
        args, kwargs = self.substitution_policy(self.preargs,
                                                postargs,
                                                self.prekwargs,
                                                postkwargs)
        return super().__call__(*args,**kwargs)

### Packing and Unpacking
class ArgPackDecorator(Decorator):
    def __init__(self, 
                    callable_,
                    args_kw=None,
                    kwarg_kw=None,
                    invert_positions=False,
                    discard_empty=True, # Could be more general... Does it need to be?
                    ):
        super().__init__(callable_)

        self.args_kw = args_kw
        self.kwarg_kw = kwarg_kw
        self.invert_positions = invert_positions
        self.discard_empty = discard_empty

    def __call__(self,*args,**kwargs):
        f_args = []
        f_kwargs = {}

        if (not self.discard_empty
            or len(args) > 0):
            if self.args_kw is None: f_args.append(args)
            else: f_kwargs[self.args_kw] = args

        if (not self.discard_empty
            or len(kwargs) > 0):
            if self.kwarg_kw is None: f_args.append(kwargs)
            else: f_kwargs[self.kwarg_kw] = kwargs

        if self.invert_positions: f_args = reversed(f_args)

        return super().__call__(*f_args,**f_kwargs)

class ArgUnpackDecorator(Decorator):
    def __init__(self, callable_):
        super().__init__(callable_)

    def __call__(self,arg_list,kwarg_dict):
        return super().__call__(*arg_list,**kwarg_dict)

class PosargsUnpackDecorator(Decorator):
    def __init__(self, callable_):
        super().__init__(callable_)

    def __call__(self,arg_list):
        return super().__call__(*arg_list)

class KwargsUnpackDecorator(Decorator):
    def __init__(self, callable_):
        super().__init__(callable_)

    def __call__(self,kwarg_dict):
        return super().__call__(**kwarg_dict)


## Return value
class ReturnValueSelectorDecorator(Decorator):
    @staticmethod
    def _default_error_handler(obj,key,error):
        if (isinstance(error,TypeError)
            and key == 0):
            return [obj]
        else:
            return [None]

    def __init__(self, 
                    callable_, 
                    rvalue_keys,
                    subscription_error_handler=_default_error_handler):
        super().__init__(callable_)

        self.rvalue_keys = rvalue_keys

        self.subscription_error_handler = subscription_error_handler

    def __call__(self,*args,**kwargs):
        r_value = super().__call__(*args,**kwargs)

        vals = []
        for r_val_idx in self.rvalue_keys:
            try:
                val = [r_value[r_val_idx]]
            except (KeyError, TypeError) as e:
                val =  self.subscription_error_handler(r_value,r_val_idx,e)
            vals += val

        return tuple(vals) if len(vals) != 1 else vals[0] # TODO: Policy?



class MultiCallableDecorator(object): # Does not inherit off of Decorator cuz it decorates various callables
    def __init__(self, callables):
        self.callables = callables
        self.__doc__ = self._generate_doc()

    def _generate_doc(self):
        return ""

## Composition
class CompositionDecorator(MultiCallableDecorator): 
    def __init__(self,callables):
        super().__init__(callables)
        
    def __call__(self,*args,**kwargs):
        r = self.callables[0](*args,**kwargs)
        for callable_ in self.callables[1:]:
            r = callable_(r)

        return r

    

class CombinationDecorator(MultiCallableDecorator): 
    def __init__(self,callables):
        super().__init__(callables)

    def __call__(self,*args,**kwargs):
        oc = _object_manipulation.ObjectCaller(args=args,kwargs=kwargs)
        return tuple(map(oc,self.callables))
        