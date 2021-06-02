import unittest

from neatcode import context_management as cm

class CMTest(unittest.TestCase):

    def test_dict_overwrite(self):
        d = dict(a=0)
        with cm.DictOverlapCM(d,dict(a=1)):
            self.assertEqual(d["a"],1)
        self.assertEqual(d["a"],0)

    def test_dict_add(self):
        d = dict()
        with cm.DictOverlapCM(d,dict(a=1)):
            self.assertIn("a",d)
        self.assertNotIn("a",d)

    def test_name_overwrite(self):
        global a # this only works with globals
        a = 0
        with cm.NameOverlapCM(dict(a=1)):
            self.assertEqual(a,1)
        self.assertEqual(a,0)

    def test_namespace_overwrite(self):
        class NS:
            def __init__(self):
                self.a = 0

        ns = NS()
        with cm.NameOverlapCM(dict(a=1),ns):
            self.assertEqual(ns.a,1)
        self.assertEqual(ns.a,0)

    def test_builtin_overwrite(self):
        def prod(it):
            p = 1
            for i in it:
                p *= i
            return p

        test_array = tuple(range(1,10))
        rsum = sum(test_array)
        with cm.BuiltinOverlapCM(dict(sum=prod)):
            rprod = sum(test_array)
        
        self.assertEqual(rprod,prod(test_array))
        self.assertEqual(rsum,sum(test_array))
    
        


