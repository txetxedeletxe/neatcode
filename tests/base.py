import unittest
import time

class TimedUnitTest(unittest.TestCase): 
                                        
    def setUp(self):
        self.t_start = time.time()

    def tearDown(self):
        self.t_end = time.time()
        t = self.t_end - self.t_start

        test_name = self.id().split(".")[-1]
        print('%s: %.3f' % (test_name, t))