class AttributeExtractor(object):
    def __init__(self,attr_name):
        self.attr_name = attr_name
    
    def __call__(self,obj):
        return getattr(obj,self.attr_name)

class KeyExtractor(object):
    def __init__(self,key):
        self.key = key
    
    def __call__(self,obj):
        return obj[self.key]

class ObjectCaller(object):
    def __init__(self,
                    args=tuple(), 
                    kwargs=dict()):

        self.args = args
        self.kwargs = kwargs
    
    def __call__(self,obj):
        return obj(*self.args, **self.kwargs)

class MethodCaller(AttributeExtractor,ObjectCaller):
    def __init__(self,method_name, 
                        args=tuple(), 
                        kwargs=dict()):
        
        AttributeExtractor.__init__(self,attr_name=method_name)
        ObjectCaller.__init__(self,args=args, kwargs=kwargs)
        
        
    def __call__(self,obj):
        method = AttributeExtractor.__call__(self,obj) # call superclass to get the method
        return ObjectCaller.__call__(self,method)


        
