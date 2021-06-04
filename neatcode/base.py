# TODO document code

import itertools as _itertools

class ConsistentObjectRepresentingBase(object):
    _REPR_STR="{className}({args})"
    def __init__(self, 
                    args=tuple(), 
                    kwargs=dict()):
        self._repr_args = args
        self._repr_kwargs = kwargs

    def __repr__(self):
        return self._get_repr()

    # Get methods
    def _get_repr(self):
        args, kwargs = self._get_argsrepr()
        args_str = self._combine_argsrepr(args,kwargs)

        return self._get_formated_repr(args_str)


    def _get_argsrepr(self):
        return self._compute_argsrepr(self._repr_args,self._repr_kwargs)


    def _get_formated_repr(self,args_str):
        return self._REPR_STR.format(className=type(self).__name__,
                                        args=args_str)

    # Attribute-free compute methods
    def _combine_argsrepr(self,args,kwargs):
        kwargs_strs = _itertools.starmap("{}={}".format,kwargs.items())
        args_str = ",".join((*args,*kwargs_strs))

        return args_str

    def _compute_argsrepr(self,args,kwargs):
        arg_repr = tuple(map(repr,args))
        kwarg_repr = tuple(map(repr,kwargs.values()))
        kwarg_repr = dict(zip(kwargs.keys(),kwarg_repr))

        return arg_repr, kwarg_repr



class AutoDocumentingBase(object):
    def __init__(self):
        self._generate_doc()

    def _get_doc(self):
        return self.__doc__

    def _generate_doc(self):
        self.__doc__ = self._get_doc()