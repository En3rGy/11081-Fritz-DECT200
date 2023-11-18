# coding: UTF-8

# coding: UTF-8

# Copyright 2021 T. Paul</p>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

import re
import httplib
import urllib
import codecs
import hashlib
import threading


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class FritzDECT200_11081_11081(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "11081_FritzBox_Dect200")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE, ())
        self.PIN_I_SXML = 1
        self.PIN_I_SSID = 2
        self.PIN_I_SIP = 3
        self.PIN_I_SUSERPW = 4
        self.PIN_I_SAIN = 5
        self.PIN_I_BONOFF = 6
        self.PIN_I_NSIDTIMEOUT = 7
        self.PIN_I_NINTERVALL = 8
        self.PIN_O_NAME = 1
        self.PIN_O_PRESENT = 2
        self.PIN_O_BRMONOFF = 3
        self.PIN_O_NMW = 4
        self.PIN_O_NZAEHLERWH = 5
        self.PIN_O_NTEMP = 6
        self.PIN_O_SSID = 7
        self.PIN_O_SXML = 8

    ########################################################################################################
    #### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
    ###################################################################################################!!!##

        self.g_out_sbc = {}
        self._sid = ""
        self.g_debug_sbc = False
        self.init_sid = "0000000000000000"
        self._ain = ""

    def set_output_value_sbc(self, pin, val):
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print ("# SBC: " + str(val) + " @ pin " + str(pin) + ", data not send!")
                self.g_debug_sbc = True
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val
        self.g_debug_sbc = False

    def get_sid(self):
        user_pw = self._get_input_value(self.PIN_I_SUSERPW)
        ip = self._get_input_value(self.PIN_I_SIP)
        # split username from password
        pw = user_pw[user_pw.find('@') + 1:]
        user = user_pw.split('@')[0]
        challenge = ""

        try:
            response = urllib.urlopen('http://{}/login_sid.lua'.format(ip))
            challenge = response.read()
            challenge = re.findall('<Challenge>(.*?)</Challenge>', challenge)[0]
        except IOError as e:
            self.DEBUG.add_message("{ain}: '{e}' in get_sid()".format(ain=self._ain, e=e))

        if len(challenge) == 0:
            self._sid = self.init_sid
            self._set_output_value(self.PIN_O_SSID, self._sid)
            return False

        challenge_resp = codecs.utf_16_le_encode(unicode('%s-%s' % (challenge, pw)))[0]
        challenge_resp = ("{}-{}".format(challenge, hashlib.md5(challenge_resp).hexdigest().lower()))

        data = {"response": challenge_resp, "username": user}
        response = urllib.urlopen('http://{}/login_sid.lua'.format(ip), urllib.urlencode(data))
        sid = response.read()
        sid = re.findall('<SID>(.*?)</SID>', sid)

        if len(sid) == 0:
            self._sid = self.init_sid
            self._set_output_value(self.PIN_O_SSID, self._sid)
            return False

        sid = sid[0]

        if sid == self.init_sid:
            self._sid = self.init_sid
            self._set_output_value(self.PIN_O_SSID, self._sid)
            return False
        else:
            self._sid = sid
            self._set_output_value(self.PIN_O_SSID, self._sid)
            self.DEBUG.set_value(self._ain + ": SID", sid)
            return True

    def set_dect_200(self, on_off, ip, ain, sid):
        """

        :type on_off: bool
        :type ip: string
        :type ain: string
        :type sid: string
        :return: True if set was successfully, otherwise False
        :rtype: bool
        """
        code = 0

        for x in range(0, 2):
            if not sid or sid == self.init_sid:
                if self.get_sid():
                    sid = self._sid

            # Dect200 #1 on/off
            if bool(on_off) is True:
                cmd = "setswitchon"
            else:
                cmd = 'setswitchoff'

            url = 'http://{}/webservices/homeautoswitch.lua'.format(ip)
            data = {"ain": ain, "switchcmd": cmd, "sid": sid}
            param = urllib.urlencode(data).replace("+", "")
            url = "{}?{}".format(url, param)
            print(url)
            resp = urllib.urlopen(url)
            code = resp.getcode()
            if code == 200:
                self.DEBUG.add_message(self._ain + ": Switch set successfully.")
                return True
            elif code == 403:
                print("Try #" + str(x+1) + " failed in set_dect_200 with 403")
                sid = self.init_sid
            else:
                print("Try #" + str(x+1) + " failed in set_dect_200 with " + str(code))

        self.DEBUG.add_message(self._ain + ": Error setting switch, code:" + str(code))
        return False

    def get_xml(self, ip, sid):
        try:
            params = urllib.urlencode({"switchcmd": "getdevicelistinfos", "sid": sid})
            resp = urllib.urlopen('http://{}/webservices/homeautoswitch.lua?{}'.format(ip, params))
            code = resp.getcode()
            self.DEBUG.add_message("{}: Get XML returned {}".format(self._ain, code))
            return {"code": code, "data": resp.read()}

        except IOError as e:
            self.DEBUG.add_exception("{}: Error XML result: {}".format(self._ain, e))
            return {"code": 408, "data": ""}

    def process_xml(self, xml):
        """

        :param xml: XML string of FritzBox devices.
        :return: Dictionary of attribute value sets.
        :rtype: dict
        """
        data = {}
        attributes = ["state", "power", "energy", "celsius", "present", "name"]

        ain_xml = re.search('<device identifier="{}".*?>(.*?)</device>'.format(self._ain), xml).group(0)
        if not ain_xml:
            self.DEBUG.add_message("{}: AIN not found in XML reply".format(self._ain))
            return {}

        for attribute in attributes:
            try:
                value = re.search('<{}>(.*?)</{}>'.format(attribute, attribute), ain_xml).group(1)

                if attribute == "state":
                    data[attribute] = int(value)
                    self.set_output_value_sbc(self.PIN_O_BRMONOFF, bool(data[attribute]))
                elif attribute == "power":
                    data[attribute] = float(value)
                    self.set_output_value_sbc(self.PIN_O_NMW, float(data[attribute]))
                elif attribute == "energy":
                    data[attribute] = int(value)
                    self.set_output_value_sbc(self.PIN_O_NZAEHLERWH, float(data[attribute]))
                elif attribute == "celsius":
                    value = int(value)
                    offset = re.search('<device identifier="' + self._ain + '".*?><offset>(.*?)</offset>', xml)
                    if offset:
                        value += int(offset.group(1))
                    data[attribute] = value / 10.0
                    self.set_output_value_sbc(self.PIN_O_NTEMP, float(data[attribute]))
                elif attribute == "present":
                    data[attribute] = int(value)
                    self.set_output_value_sbc(self.PIN_O_PRESENT, float(data[attribute]))
                elif attribute == "name":
                    data[attribute] = str(value)
                    self.set_output_value_sbc(self.PIN_O_NAME, data[attribute])
            except Exception as e:
                self.DEBUG.add_message("{}: Error '{}' in attribute '{}' in get_dect_200_status()".format(
                    self._ain, e, attribute))

        self.DEBUG.add_message("{}: XML processed successfully".format(self._ain))

        return data

    def logout(self, ip, sid):
        http_client = httplib.HTTPConnection('http://' + ip, timeout=5)
        http_client.request("GET", '/login_sid.lua?logout=true&sid=' + sid)
        response = http_client.getresponse()
        self.DEBUG.add_message("{}: Gently logged out.".format(self._ain))
        return response.status

    def trigger(self):
        # Get SID if not available
        sid = self._get_input_value(self.PIN_I_SSID)

        for x in range(0, 2):
            if not sid or sid == self.init_sid:
                if self.get_sid():
                    sid = self._sid

            xml = self.get_xml(self._get_input_value(self.PIN_I_SIP), sid)

            if xml["code"] == 200:
                # Evaluate XML data
                self.process_xml(xml["data"])
                self.set_output_value_sbc(self.PIN_O_SXML, xml["data"])
                self.DEBUG.add_message(self._ain + ": XML received")
                break
            elif xml["code"] == 403 or xml["code"] == 408:
                self._sid = self.init_sid
                if x == 1:
                    self.DEBUG.add_message(self._ain + ": Could not receive valid SID")
            else:
                if x == 1:
                    self.DEBUG.add_message(self._ain + ": Error processing XML, code:" + str(xml["code"]))

        interval = self._get_input_value(self.PIN_I_NINTERVALL)
        if interval > 0:
            threading.Timer(interval, self.trigger).start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        self.g_out_sbc = {}
        self._sid = self.init_sid
        self.g_debug_sbc = False

        interval = self._get_input_value(self.PIN_I_NINTERVALL)
        if interval > 0:
            self.trigger()

    def on_input_value(self, index, value):
        self._ain = str(self._get_input_value(self.PIN_I_SAIN))  # convert from unicode
        if index == self.PIN_I_SSID:
            self._sid = value
        elif index == self.PIN_I_NINTERVALL and (value > 0):
            self.trigger()
        # Switch device on or off and report back new status
        elif index == self.PIN_I_BONOFF:
            res = self.set_dect_200(value, self._get_input_value(self.PIN_I_SIP), self._ain, self._sid)
            if res:
                self.set_output_value_sbc(self.PIN_O_BRMONOFF, value)

        # If new XML available or trigger arrived,
        # get and process new status data
        elif index == self.PIN_I_SXML and value:
            # Evaluate XML data
            self.process_xml(value)
            self._set_output_value(self.PIN_O_SXML, value)


