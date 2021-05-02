import unittest

import neatcode.object_manipulation as object_manipulation
import neatcode.decoration as decoration


class DecorationTest(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()