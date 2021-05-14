import unittest
import time

import neatcode.object_manipulation as object_manipulation
import neatcode.decoration as decoration


class TimedUnitTest(unittest.TestCase): # This should be abstracted and put in another file when more files 
                                        # are added for unit testing
    def setUp(self):
        self.t_start = time.time()

    def tearDown(self):
        self.t_end = time.time()
        t = self.t_end - self.t_start

        test_name = self.id().split(".")[-1]
        print('%s: %.3f' % (test_name, t))

    

class UsabilityTestDecoration(TimedUnitTest):
    def __init__(self, method_name,
                    key="hi",
                    items=[dict(hi=0)]*5000000):
        super().__init__(method_name)

        self.key = "hi"
        self.items = items
        self.correct_result = list(map(lambda x: x[self.key], self.items))
    
    def test_key_extactor(self):
        ke_list = list(map(object_manipulation.KeyExtractor(self.key),self.items))
        self.assertListEqual(ke_list,self.correct_result)

    def test_preargument_decorator(self):
        ke2 = object_manipulation.MethodCaller
        ke2 = decoration.PreargumentDecorator(ke2, prekwargs=dict(method_name="__getitem__"))
        ke2 = decoration.ArgPackDecorator(ke2,args_kw="args",kwarg_kw="kwargs") # This is a class

        ke21_list = list(map(ke2(self.key),self.items))
        ke22_list = list(map(ke2(self.key),self.items))


        self.assertListEqual(ke21_list,self.correct_result)
        self.assertListEqual(ke22_list,self.correct_result)


    def test_composition_decorator(self):

        c0 = object_manipulation.MethodCaller

        c1 = decoration.PreargumentDecorator
        c1 = decoration.PreargumentDecorator(c1,preargs=(c0,))

        c2 = decoration.ArgPackDecorator
        c2 = decoration.PreargumentDecorator(c2,prekwargs=dict(args_kw="args",kwarg_kw="kwargs"))

        c = decoration.CompositionDecorator((c1,c2)) # This is a metaclass, istances of it are classes

        ke31 = c(prekwargs=dict(method_name="__getitem__"))
        ke32 = c(prekwargs=dict(method_name="__getitem__"))

        ke31_list = list(map(ke31(self.key),self.items))
        ke32_list = list(map(ke32(self.key),self.items))

        self.assertListEqual(ke31_list,self.correct_result)
        self.assertListEqual(ke32_list,self.correct_result)


class DocumentationTestDecoration(unittest.TestCase):
    def __init__(self, method_name,
                    key="hi"):
        super().__init__(method_name)

        self.key = "hi"
    
    def test_key_extactor(self):
        ke = object_manipulation.KeyExtractor
        ke_obj = ke(self.key)

        print("KeyExtractor doc:\n",ke.__doc__)
        print("KeyExtractor instance doc:\n",ke_obj.__doc__)


    def test_preargument_decorator(self):
        ke = object_manipulation.MethodCaller
        parg = decoration.PreargumentDecorator
        apd = decoration.ArgPackDecorator

        print("MethodCaller doc:\n",ke.__doc__)
        print("PreargumentDecorator doc:\n",parg.__doc__)
        print("ArgPackDecorator doc:\n",apd.__doc__)

        ke_parg = parg(ke, prekwargs=dict(method_name="__getitem__"))

        print("PreargumentDecorator instance doc:\n",ke_parg.__doc__)

        ke_apd = decoration.ArgPackDecorator(ke_parg,args_kw="args",kwarg_kw="kwargs") # This is a class

        print("ArgPackDecorator instance doc:\n",ke_apd.__doc__)

        ke_obj = ke_apd(self.key)

        print("Decorated MethodCaller instance doc:\n",ke_obj.__doc__)

    def test_composition_decorator(self):
        
        c0 = object_manipulation.MethodCaller

        c1 = decoration.PreargumentDecorator
        c1 = decoration.PreargumentDecorator(c1,preargs=(c0,))

        c2 = decoration.ArgPackDecorator
        c2 = decoration.PreargumentDecorator(c2,prekwargs=dict(args_kw="args",kwarg_kw="kwargs"))

        c = decoration.CompositionDecorator((c1,c2)) # This is a metaclass, istances of it are classes

        ke31 = c(prekwargs=dict(method_name="__getitem__"))
        ke32 = c(prekwargs=dict(method_name="__getitem__"))

        ke31_list = list(map(ke31(self.key),self.items))
        ke32_list = list(map(ke32(self.key),self.items))

        self.assertListEqual(ke31_list,self.correct_result)
        self.assertListEqual(ke32_list,self.correct_result)
        



if __name__ == "__main__":
    unittest.main()