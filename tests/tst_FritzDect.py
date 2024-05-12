# coding: UTF-8
import time
import unittest
import json

import fritz_lib.fritz

################################
# get the code
with open('framework_helper.py', 'r') as f1, open('../src/11081_Fritz DECT200 (11081).py', 'r') as f2:
    framework_code = f1.read()
    debug_code = f2.read()

exec (framework_code + debug_code)


################################################################################

class TestSequenceFunctions(unittest.TestCase):
    cred = 0
    tst = 0

    def setUp(self):
        print("\n###setUp")
        with open("credentials.txt") as f:
            self.cred = json.load(f)

        self.tst = FritzDECT200_11081_11081(0)
        self.tst.debug = True
        self.tst.debug_input_value[self.tst.PIN_I_USER] = self.cred["PIN_I_USER"]
        self.tst.debug_input_value[self.tst.PIN_I_PW] = self.cred["PIN_I_PW"]
        self.tst.debug_input_value[self.tst.PIN_I_SIP] = self.cred["PIN_I_SIP"]
        self.tst.debug_input_value[self.tst.PIN_I_SAIN] = self.cred["PIN_I_SAIN"]
        self.tst.debug_input_value[self.tst.PIN_I_NINTERVALL] = 5
        self.tst.on_init()

    def tearDown(self):
        print("\n### tearDown")
        self.tst.debug_input_value[self.tst.PIN_I_NINTERVALL] = 0

    def test_set_switch(self):
        print("\n### test_set_switch")
        self.tst.on_input_value(self.tst.PIN_I_BONOFF, True)
        self.assertTrue(self.tst.debug_output_value[self.tst.PIN_O_BRMONOFF])
        time.sleep(3)
        self.tst.on_input_value(self.tst.PIN_I_BONOFF, False)
        self.assertFalse(self.tst.debug_output_value[self.tst.PIN_O_BRMONOFF])

    def test_on_init(self):
        print("\n### test_on_init")
        self.assertTrue(self.tst.PIN_O_NAME in self.tst.debug_output_value)
        self.assertTrue(self.tst.debug_output_value[self.tst.PIN_O_NAME])

    def test_singleton(self):
        print("\n### test_singleton")

        self.tst2 = FritzDECT200_11081_11081(1)
        self.tst2.debug = True
        self.tst2.debug_input_value[self.tst2.PIN_I_USER] = self.cred["PIN_I_USER"]
        self.tst2.debug_input_value[self.tst2.PIN_I_PW] = self.cred["PIN_I_PW"]
        self.tst2.debug_input_value[self.tst2.PIN_I_SIP] = self.cred["PIN_I_SIP"]
        self.tst2.debug_input_value[self.tst2.PIN_I_SAIN] = self.cred["PIN_I_SAIN"]
        self.tst2.debug_input_value[self.tst2.PIN_I_NINTERVALL] = 5
        self.tst2.on_init()
        self.tst2.debug_input_value[self.tst2.PIN_I_NINTERVALL] = 0

    def test_sbc(self):
        print("\n### test_sbc")
        tst1 = FritzDECT200_11081_11081(1)
        tst1._set_input_value(tst1.PIN_I_NINTERVALL, 0)
        tst1.on_init()
        print(tst1.g_out_sbc)
        tst1.on_init()
        print(tst1.g_out_sbc)
        tst1.set_output_value_sbc(1, 0)
        self.assertFalse(tst1.g_debug_sbc, "a1")
        tst1.set_output_value_sbc(1, 1)
        self.assertFalse(tst1.g_debug_sbc, "a2")
        tst1.set_output_value_sbc(1, 1)
        self.assertTrue(tst1.g_debug_sbc, "b")
        tst1.set_output_value_sbc(1, 0)
        self.assertFalse(tst1.g_debug_sbc, "c")
        tst1.set_output_value_sbc(1, 0)
        self.assertTrue(tst1.g_debug_sbc, "d")

        tst1.debug_input_value[tst1.PIN_I_NINTERVALL] = 0

    def test_interval(self):
        print("\n### test_interval")
        interval = 5
        self.tst.debug_input_value[self.tst.PIN_I_NINTERVALL] = interval
        self.tst.on_input_value(self.tst.PIN_I_NINTERVALL, interval)
        self.tst.debug_output_value = {}
        self.tst.g_out_sbc = {}

        print("** Sleeping 3s")
        time.sleep(3)
        self.assertFalse(self.tst.PIN_O_NAME in self.tst.debug_output_value)

        print("** Sleeping 5s")
        time.sleep(5)
        self.assertTrue(self.tst.debug_output_value[self.tst.PIN_O_NAME])

    def test_globals(self):
        self.tst.debug_input_value[self.tst.PIN_I_NINTERVALL] = 0
        global fritz_box
        fritz_box = fritz_lib.fritz.FritzBox()

        self.assertTrue("fritz_box" in globals())

        del fritz_box
        self.assertFalse("fritz_box" in globals())

        try:
            del fritz_box
        except Exception as e:
            pass

        self.assertFalse("fritz_box" in globals())


if __name__ == '__main__':
    unittest.main()
