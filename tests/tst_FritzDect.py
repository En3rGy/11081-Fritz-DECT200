# coding: UTF-8

import unittest
import json

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
        self.tst.on_init()

        self.tst.debug_input_value[self.tst.PIN_I_SUSERPW] = self.cred["PIN_I_SUSERPW"]
        self.tst.debug_input_value[self.tst.PIN_I_SIP] = self.cred["PIN_I_SIP"]
        self.tst.debug_input_value[self.tst.PIN_I_SAIN] = self.cred["PIN_I_SAIN"]


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

    def test_trigger(self):
        print("\n### test_trigger")
        self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF] = -1

        self.tst.trigger()
        self.assertTrue(self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF] != -1)

    def test_extern_xml(self):
        print("\n### test_extern_xml")
        xml = '<devicelist version="1" fwversion="7.21"><device identifier="08761 0131475" id="17" functionbitmask="35712" fwversion="04.16" manufacturer="AVM" productname="FRITZ!DECT 200"><present>1</present><txbusy>0</txbusy><name>Waschmaschine</name><switch><state>1</state><mode>manuell</mode><lock>0</lock><devicelock>0</devicelock></switch><simpleonoff><state>1</state></simpleonoff><powermeter><voltage>231186</voltage><power>131960</power><energy>940184</energy></powermeter><temperature><celsius>185</celsius><offset>0</offset></temperature></device><device identifier="08761 0170037" id="18" functionbitmask="35712" fwversion="04.16" manufacturer="AVM" productname="FRITZ!DECT 200"><present>1</present><txbusy>0</txbusy><name>Trockner</name><switch><state>0</state><mode>manuell</mode><lock>0</lock><devicelock>0</devicelock></switch><simpleonoff><state>0</state></simpleonoff><powermeter><voltage>231927</voltage><power>0</power><energy>2073514</energy></powermeter><temperature><celsius>195</celsius><offset>0</offset></temperature></device><device identifier="08761 0170039" id="19" functionbitmask="35712" fwversion="04.16" manufacturer="AVM" productname="FRITZ!DECT 200"><present>1</present><txbusy>0</txbusy><name>IT Secondary</name><switch><state>1</state><mode>manuell</mode><lock>0</lock><devicelock>0</devicelock></switch><simpleonoff><state>1</state></simpleonoff><powermeter><voltage>230910</voltage><power>30610</power><energy>600185</energy></powermeter><temperature><celsius>205</celsius><offset>0</offset></temperature></device><device identifier="08761 0216542" id="20" functionbitmask="35712" fwversion="04.16" manufacturer="AVM" productname="FRITZ!DECT 200"><present>1</present><txbusy>0</txbusy><name>Gefrierschrank</name><switch><state>1</state><mode>manuell</mode><lock>1</lock><devicelock>1</devicelock></switch><simpleonoff><state>1</state></simpleonoff><powermeter><voltage>230090</voltage><power>640</power><energy>935776</energy></powermeter><temperature><celsius>175</celsius><offset>0</offset></temperature></device><device identifier="08761 0198885" id="21" functionbitmask="35712" fwversion="04.16" manufacturer="AVM" productname="FRITZ!DECT 200"><present>1</present><txbusy>0</txbusy><name>IT-Schrank</name><switch><state>1</state><mode>manuell</mode><lock>1</lock><devicelock>1</devicelock></switch><simpleonoff><state>1</state></simpleonoff><powermeter><voltage>230687</voltage><power>7790</power><energy>792528</energy></powermeter><temperature><celsius>195</celsius><offset>0</offset></temperature></device><device identifier="11657 0020838" id="22" functionbitmask="35712" fwversion="04.17" manufacturer="AVM" productname="FRITZ!DECT 210"><present>1</present><txbusy>0</txbusy><name>Automower</name><switch><state>0</state><mode>manuell</mode><lock>0</lock><devicelock>0</devicelock></switch><simpleonoff><state>0</state></simpleonoff><powermeter><voltage>230737</voltage><power>0</power><energy>9956</energy></powermeter><temperature><celsius>35</celsius><offset>0</offset></temperature></device><device identifier="08761 0088135" id="23" functionbitmask="35712" fwversion="04.16" manufacturer="AVM" productname="FRITZ!DECT 200"><present>1</present><txbusy>0</txbusy><name>P1070-001 (TV)</name><switch><state>1</state><mode>manuell</mode><lock>0</lock><devicelock>0</devicelock></switch><simpleonoff><state>1</state></simpleonoff><powermeter><voltage>231234</voltage><power>1430</power><energy>175536</energy></powermeter><temperature><celsius>205</celsius><offset>0</offset></temperature></device><device identifier="11630 0066891" id="24" functionbitmask="35712" fwversion="04.16" manufacturer="AVM" productname="FRITZ!DECT 200"><present>1</present><txbusy>0</txbusy><name>P1070-007 (B&amp;E)</name><switch><state>1</state><mode>manuell</mode><lock>0</lock><devicelock>0</devicelock></switch><simpleonoff><state>1</state></simpleonoff><powermeter><voltage>231214</voltage><power>9080</power><energy>63133</energy></powermeter><temperature><celsius>190</celsius><offset>0</offset></temperature></device></devicelist>'

        self.tst.on_input_value(self.tst.PIN_I_SXML, xml)
        self.assertEqual(True, self.tst.debug_output_value[self.tst.PIN_O_BRMONOFF])
        self.assertEqual(1430, self.tst.debug_output_value[self.tst.PIN_O_NMW])
        self.assertEqual(175536, self.tst.debug_output_value[self.tst.PIN_O_NZAEHLERWH])
        self.assertEqual(20.5, self.tst.debug_output_value[self.tst.PIN_O_NTEMP])
        self.assertEqual(xml, self.tst.debug_output_value[self.tst.PIN_O_SXML])

    def test_timer(self):
        print("\n### test_timer")
        self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF] = -1
        # self.tst.trigger()
        self.assertEqual(-1, self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF], "a")
        self.tst._set_input_value(self.tst.PIN_I_NINTERVALL, 3)
        #self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF] = -1
        self.tst.g_out_sbc = {}

        time.sleep(5)

        self.assertNotEqual(-1, self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF], "b")

    def test_trigger_wrong_sid(self):
        print("\n### test_timer")

        self.tst.on_input_value(self.tst.PIN_I_SSID, "abc")
        self.tst._set_input_value(self.tst.PIN_I_NINTERVALL, 3)
        self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF] = -1
        self.tst.trigger()
        self.assertNotEqual(-1, self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF], "a")

    def test_no_route(self):
        print("\n### test_no_route")

        self.tst.debug_input_value[self.tst.PIN_I_SIP] = "192.168.100.100"
        self.tst.trigger()

    def test_interval(self):
        print("\n### test_interval")

        self.tst._set_input_value(self.tst.PIN_I_NINTERVALL, 0)
        self.tst.on_init()
        print("Step 1")
        self.tst.g_out_sbc[self.tst.PIN_O_SXML] = ""
        self.tst.debug_input_value[self.tst.PIN_I_NINTERVALL] = 3
        self.tst.on_input_value(self.tst.PIN_I_NINTERVALL, 3)
        self.assertNotEqual("", self.tst.g_out_sbc[self.tst.PIN_O_SXML], "a")

        print("Step 2")
        self.tst.g_out_sbc[self.tst.PIN_O_SXML] = ""
        time.sleep(4)
        self.assertNotEqual("", self.tst.g_out_sbc[self.tst.PIN_O_SXML], "b")
        self.tst.g_out_sbc[self.tst.PIN_O_SXML] = ""

        print("Step 3")
        self.tst.g_out_sbc[self.tst.PIN_O_SXML] = ""
        time.sleep(4)
        self.assertNotEqual("", self.tst.g_out_sbc[self.tst.PIN_O_SXML], "c")
        self.tst.g_out_sbc[self.tst.PIN_O_SXML] = ""


    def test_sid(self):
        print("\n### test_sid")
        self.tst.get_sid()
        self.assertTrue(self.tst.g_ssid)
        self.assertNotEqual("0000000000000000", self.tst.g_ssid)

    def test_switch(self):
        print("\n### test_switch")
        self.tst.on_input_value(self.tst.PIN_I_BONOFF, 1)
        self.assertEqual(True, self.tst.debug_output_value[self.tst.PIN_O_BRMONOFF])

    def test_switch_wrong_sid(self):
        print("\n### test_switch_wrong_sid")
        self.tst.on_input_value(self.tst.PIN_I_SSID, "abc")
        self.tst.on_input_value(self.tst.PIN_I_BONOFF, 1)
        self.assertEqual(True, self.tst.debug_output_value[self.tst.PIN_O_BRMONOFF])


if __name__ == '__main__':
    unittest.main()
