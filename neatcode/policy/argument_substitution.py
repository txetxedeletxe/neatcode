# Base classes
class PrioritizeAndMergeSubstitutor(object):
    def __init__(self):
        pass

    def get_priority(self,*args):
        return tuple(range(len(args)))

    def merge(self,*p_args):
        return None

    def __call__(self,*args):
        priorities = self.get_priority(*args)
        
        argsorted = sorted(range(len(priorities)), key=priorities.__getitem__)
        p_args = list(map(args.__getitem__,argsorted))

        return self.merge(*p_args)

class ArgPrioritizer(object):
    def __init__(self,
                    prioritize_post=True,
                    prioritize_non_empty=False):
        self.prioritize_post = prioritize_post
        self.prioritize_non_empty = prioritize_non_empty

    def _prioritize(self, pre, post):
        a, b = pre, post
        if self.prioritize_post:
            a, b = b, a
    
        if self.prioritize_non_empty and len(a) == 0:
            return b, a 
        return a, b

# All arg
class ArgIgnorer(ArgPrioritizer):
    def __init__(self,
                    prioritize_post=False,
                    prioritize_non_empty=False):
        super().__init__(prioritize_post,prioritize_non_empty)

    def __call__(self,pre,post):
        a, _ = self._prioritize(pre,post)
        return a

# Posargs
class PosargsOverwriter(ArgPrioritizer):
    def __init__(self, prioritize_post=False):
        super().__init__(prioritize_post)

    def __call__(self, preargs, postargs):
        a, b = self._prioritize(preargs,postargs)
        a, b = list(a), list(b)

        r = a + b[len(a):]
        return tuple(r)

class PosargsAppender(ArgPrioritizer):
    def __init__(self, prioritize_post=False):
        super().__init__(prioritize_post)

    def __call__(self, preargs, postargs):
        a, b = self._prioritize(preargs,postargs)
        a, b = list(a), list(b)

        r = a + b
        return tuple(r)

# Kwargs
class KwargsOverwriter(ArgPrioritizer):
    def __init__(self, prioritize_post=False):
        super().__init__(prioritize_post)

    def __call__(self, prekwargs, postkwargs):
        a, b = self._prioritize(prekwargs,postkwargs)
        r = dict(b)

        for k,v in a.items():
            r[k] = v

        return r





class CombinedArgSubstitutor(object):
    def __init__(self,
                    arg_substitutor,
                    kwarg_substitutor,
                    arg_kwarg_combiner):

        self.arg_substitutor = arg_substitutor
        self.kwarg_substitutor = kwarg_substitutor
        self.arg_kwarg_combiner = arg_kwarg_combiner

def default_preargs(preargs=tuple(),
                    postargs=tuple(),
                    prekwargs=dict(),
                    postkwargs=dict()):

    args = list(postargs) + list(preargs)[len(postargs):]
    kwargs = dict(prekwargs)
    for k,v in postkwargs.items():
        kwargs[k] = v
        
    return args, kwargs

def ignore_postargs(preargs=tuple(),
                    postargs=tuple(),
                    prekwargs=dict(),
                    postkwargs=dict()):
    return preargs, prekwargs