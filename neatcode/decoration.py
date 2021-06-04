# TODO document code

import neatcode.policy as _policy
import neatcode.object_manipulation as _object_manipulation
import neatcode.base as _base

import re as _re
import itertools as _itertools

class DecoratorBase(_base.ConsistentObjectRepresentingBase,
                    _base.AutoDocumentingBase): # base
    _SHALLOW_REGEX=_re.compile(r"^([^()]*)(\(.*\))?$")

    def __init__(self,
                    args=tuple(),
                    kwargs=dict()):

        _base.ConsistentObjectRepresentingBase.__init__(self,args=args,kwargs=kwargs)
        _base.AutoDocumentingBase.__init__(self)

    def _get_shallow_args(self,args,kwargs):
        args_match = map(self._SHALLOW_REGEX.match,args)
        kwargs_match = map(self._SHALLOW_REGEX.match,kwargs.values())

        args_values = tuple((m.group(1) for m in args_match))
        kwargs_values = tuple((m.group(1) for m in kwargs_match))

        args = args_values
        kwargs = dict(zip(kwargs.keys(),kwargs_values))

        return args, kwargs

class Decorator(DecoratorBase): # Base class for single callable decorators    
    _DOC_FORMAT = "\n@ Decorated by:\t{decoratorRepr}\n{callableDoc}"
    def __init__(self, callable_, args=tuple(),kwargs=dict()):
        self.callable = callable_
    
        super().__init__(args=(self.callable,*args),kwargs=kwargs)

    def __call__(self,*args,**kwargs):
        return self.callable(*args,**kwargs)

    # Doc generation
    def _get_doc(self): 
        c_doc = self.callable.__doc__ or ""

        # Get representation of args
        args, kwargs = self._get_argsrepr()
        args = args[1:] # The decorated callable is redundant

        # Clean represenation of args
        args, kwargs = self._get_shallow_args(args, kwargs)

        # Combine argrepr into string
        arg_str = self._combine_argsrepr(args,kwargs)
        self_repr = self._get_formated_repr(arg_str)

        # Format into doc
        return self._DOC_FORMAT.format(decoratorRepr=self_repr,callableDoc=c_doc)

    

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
    def _default_error_handler(obj,key,error): # This needs to be here?
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



class MultiCallableDecorator(DecoratorBase): # Does not inherit off of Decorator cuz it decorates various callables
    def __init__(self, callables, args=tuple(),kwargs=dict()):
        self.callables = callables
        
        super().__init__(args=(callables,*args),kwargs=kwargs)

    # Doc generation 
    def _get_doc(self):
        return "" # TODO finish up autodoc

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
        