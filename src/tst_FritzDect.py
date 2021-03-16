# coding: UTF-8

import time

import unittest

import re
import httplib
import urllib
import codecs
import md5
import threading


class hsl20_3:
    LOGGING_NONE = 0

    def __init__(self):
        pass

    class BaseModule:
        debug_output_value = {}  # type: float
        debug_set_remanent = {}  # type: float
        debug_input_value = {}

        def __init__(self, a, b):
            pass

        def _get_framework(self):
            f = hsl20_3.Framework()
            return f

        def _get_logger(self, a, b):
            return 0

        def _get_remanent(self, key):
            return 0

        def _set_remanent(self, key, val):
            self.debug_set_remanent = val

        def _set_output_value(self, pin, value):
            self.debug_output_value[int(pin)] = value
            print "# Out: " + str(value) + " @ pin " + str(pin)

        def _set_input_value(self, pin, value):
            self.debug_input_value[int(pin)] = value
            print "# In: " + str(value) + " @ pin " + str(pin)

        def _get_input_value(self, pin):
            if pin in self.debug_input_value:
                return self.debug_input_value[pin]
            else:
                return 0

    class Framework:
        def __init__(self):
            pass

        def _run_in_context_thread(self, a):
            pass

        def create_debug_section(self):
            d = hsl20_3.DebugHelper()
            return d

    class DebugHelper:
        def __init__(self):
            pass

        def set_value(self, cap, text):
            print("DEBUG value\t'" + str(cap) + "': " + str(text))

        def add_message(self, msg):
            print("Debug Msg\t" + str(msg))

    ############################################


class FritzDECT200_11081_11081(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "hsl20_3_FritzBox")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE, ())
        self.PIN_I_SXML = 1
        self.PIN_I_SSID = 2
        self.PIN_I_SIP = 3
        self.PIN_I_SUSERPW = 4
        self.PIN_I_SAIN = 5
        self.PIN_I_BONOFF = 6
        self.PIN_I_NSIDTIMEOUT = 7
        self.PIN_I_NINTERVALL = 8
        self.PIN_O_BRMONOFF = 1
        self.PIN_O_NMW = 2
        self.PIN_O_NZAEHLERWH = 3
        self.PIN_O_NTEMP = 4
        self.PIN_O_SSID = 5
        self.PIN_O_SXML = 6
        self.FRAMEWORK._run_in_context_thread(self.on_init)

    ############################################

    g_out_sbc = {}
    g_ssid = ""
    g_debug_sbc = False

    def set_output_value_sbc(self, pin, val):
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print ("# SBC: " + str(val) + " @ pin " + str(pin) + ", data not send!")
                self.g_debug_sbc = True
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val
        self.g_debug_sbc = False

    def get_sid(self, user_pw, ip):
        # split username from password
        pw = user_pw[user_pw.find('@') + 1:]
        user = user_pw.split('@')[0]
        challenge = ""

        try:
            response = urllib.urlopen('http://' + ip + '/login_sid.lua')
            challenge = response.read()
            challenge = re.findall('<Challenge>(.*?)</Challenge>', challenge)[0]
        except Exception as e:
            self.DEBUG.add_message("'" + str(e) + "' in get_sid()")
            pass

        if len(challenge) == 0:
            return ""

        challenge_resp = codecs.utf_16_le_encode(unicode('%s-%s' %
                                                         (challenge, pw)))[0]
        challenge_resp = (challenge + "-" +
                          md5.new(challenge_resp).hexdigest().lower())

        data = {"response": challenge_resp, "username": user}
        response = urllib.urlopen('http://' + ip + '/login_sid.lua',
                                  urllib.urlencode(data))
        sid = response.read()
        sid = re.findall('<SID>(.*?)</SID>', sid)

        if len(sid) == 0:
            return ""

        sid = sid[0]

        if sid == '0000000000000000':
            return ""
        else:
            self.g_ssid = sid
            return sid

    def set_dect_200(self, on_off, ip, ain, sid):
        # Dect200 #1 on/off
        cmd = 'setswitchoff'
        if bool(on_off) is True:
            cmd = "setswitchon"

        url = str('http://' + ip +
                   '/webservices/homeautoswitch.lua?ain=' + ain +
                   '&switchcmd=' + cmd +
                   '&sid=' + sid)
        self.DEBUG.set_value("11081 Switch cmd", url)
        resp = urllib.urlopen(url)
        self.DEBUG.set_value("11081 Set switch result", resp.getcode())
        return {"code": resp.getcode(), "data": resp.read()}

    def get_xml(self, sIp, sSid):
        try:
            resp = urllib.urlopen('http://' +
                                  sIp +
                                  '/webservices/homeautoswitch.lua?' +
                                  'switchcmd=getdevicelistinfos' +
                                  '&sid=' + sSid)
            self.DEBUG.add_message("11081 Get XML result: " + str(resp.getcode()))
            return {"code": resp.getcode(), "data": resp.read()}

        except Exception as e:
            return {"code": 999, "data": ""}

    def get_dect_200_status(self, xml, ain):
        data = {}
        state = re.findall('<device identifier="' + ain +
                           '" id=.*?>.*?<state>(.*?)</state>', xml)

        if len(state) == 0:
            return {}
        else:
            state = state[0]

        if state != "":
            data["state"] = int(state)
            self.set_output_value_sbc(self.PIN_O_BRMONOFF, bool(data["state"]))

        power = re.findall('<device identifier="' + ain +
                           '" id=.*?>.*?<power>(.*?)</power>', xml)
        if len(power) != 0:
            data["power"] = int(power[0])
            self.set_output_value_sbc(self.PIN_O_NMW, float(data["power"]))

        energy = re.findall('<device identifier="' + ain +
                            '" id=.*?>.*?<energy>(.*?)</energy>', xml)
        if len(energy) != 0:
            data["energy"] = int(energy[0])
            self.set_output_value_sbc(self.PIN_O_NZAEHLERWH, float(data["energy"]))

        temp = re.findall('<device identifier="' + ain +
                          '" id=.*?>.*?<celsius>(.*?)</celsius>', xml)

        if len(temp) != 0:
            temp = int(temp[0])
            offset = re.findall('<device identifier="' + ain +
                                '" id=.*?>.*?<offset>(.*?)</offset>', xml)

            if len(offset) != 0:
                temp = temp + int(offset[0])

            data["temp"] = temp / 10.0
            self.set_output_value_sbc(self.PIN_O_NTEMP, float(data["temp"]))

        return data

    def logout(self, ip, sid):
        http_client = httplib.HTTPConnection('http://' + ip, timeout=5)
        http_client.request("GET", '/login_sid.lua?logout=true&sid=' + sid)
        response = http_client.getresponse()
        return response.status

    def trigger(self):
        # Get SID if not available
        sid = self._get_input_value(self.PIN_I_SSID)

        if not sid:
            sid = self.get_sid(self._get_input_value(self.PIN_I_SUSERPW),
                               self._get_input_value(self.PIN_I_SIP))
            self.DEBUG.set_value("11081 SID", sid)

        if sid == "":
            self.DEBUG.add_message("11081 Could not receive valid SID")
        else:
            self.set_output_value_sbc(self.PIN_O_SSID, sid)

            # If new XML available or trigger arrived,
            # get and process new status data
            xml = self.get_xml(self._get_input_value(self.PIN_I_SIP), sid)

            # Evaluate XML data
            self.get_dect_200_status(xml["data"], self._get_input_value(self.PIN_I_SAIN))

            if xml["code"] == 200:
                self.set_output_value_sbc(self.PIN_O_SXML, xml["data"])
            else:
                self.DEBUG.add_message("11081 Error processing XML, code:" +
                                       str(xml["code"]))

        interval = self._get_input_value(self.PIN_I_NINTERVALL)
        if interval > 0:
            threading.Timer(interval, self.trigger).start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        self.g_out_sbc = {}
        self.g_ssid = ""
        self.g_debug_sbc = False

        interval = self._get_input_value(self.PIN_I_NINTERVALL)
        if interval > 0:
            self.trigger()

    def on_input_value(self, index, value):

        ssid = self._get_input_value(self.PIN_I_SSID)
        loop = 0

        if (index == self.PIN_I_NINTERVALL) and (value > 0):
            self.trigger()

        # If SID did not work, retry with new SID
        while loop < 2:
            loop += 1

            # Get SID if not available
            if (index == self.PIN_I_BONOFF) and (not ssid):

                ssid = self.get_sid(self._get_input_value(self.PIN_I_SUSERPW),
                                    self._get_input_value(self.PIN_I_SIP))
                self.DEBUG.set_value("11081 SID", ssid)

                if ssid == "":
                    self.DEBUG.add_message("11081 Could not receive valid SID")
                else:
                    self.set_output_value_sbc(self.PIN_O_SSID, ssid)

            # If new XML available or trigger arrived,
            # get and process new status data
            elif index == self.PIN_I_SXML:
                xml = ""

                if index == self.PIN_I_SXML:
                    xml = {"code": 200, "data": value}

                # Evaluate XML data
                self.get_dect_200_status(xml["data"], self._get_input_value(self.PIN_I_SAIN))

                if xml["code"] == 200:
                    self._set_output_value(self.PIN_O_SXML, xml["data"])
                    return
                else:
                    self.DEBUG.add_message("11081 Error processing XML, code:" +
                                           str(xml["code"]))
                    ssid = ""

            # Switch device on or of and report back new status
            elif index == self.PIN_I_BONOFF:
                # self.DEBUG.add_message("11081 Set switch: " + str(self._get_input_value(self.PIN_I_BONOFF)))

                res_on = self.set_dect_200(self._get_input_value(self.PIN_I_BONOFF),
                                           self._get_input_value(self.PIN_I_SIP),
                                           self._get_input_value(self.PIN_I_SAIN),
                                           ssid)

                self.set_output_value_sbc(self.PIN_O_BRMONOFF, bool(res_on["data"]))

                if res_on["code"] == 200:
                    self.DEBUG.add_message("11081 Switch set successfully.")
                    return
                else:
                    self.DEBUG.add_message("11081 Error setting switch, code:" +
                                           str(res_on["code"]))

                    ssid = ""
            elif index == self.PIN_I_NINTERVALL and value > 0:
                self.trigger()


############################################

import json

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

        self.tst._set_input_value(self.tst.PIN_I_NINTERVALL, 3)
        self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF] = -1
        self.tst.trigger()
        self.assertNotEqual(-1, self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF], "a")
        self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF] = -1
        self.tst.g_out_sbc = {}

        time.sleep(5)

        self.assertNotEqual(-1, self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF], "b")

    def test_no_route(self):
        print("\n### test_no_route")

        self.tst.debug_input_value[self.tst.PIN_I_SIP] = "192.168.100.100"

        self.tst.trigger()

    def test_interval(self):
        print("\n### test_interval")

        self.tst._set_input_value(self.tst.PIN_I_NINTERVALL, 3)
        self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF] = -1
        self.assertEqual(-1, self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF], "a")
        self.tst.on_init()

        self.assertNotEqual(-1, self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF], "b")
        self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF] = -1
        self.assertEqual(-1, self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF], "b1")

        time.sleep(5)

        self.assertNotEqual(-1, self.tst.g_out_sbc[self.tst.PIN_O_BRMONOFF], "c")

if __name__ == '__main__':
    unittest.main()
