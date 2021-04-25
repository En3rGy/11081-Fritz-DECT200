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
import md5
import threading

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class FritzDECT200_11081_11081(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "11081_FritzBox_Dect200")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_SXML=1
        self.PIN_I_SSID=2
        self.PIN_I_SIP=3
        self.PIN_I_SUSERPW=4
        self.PIN_I_SAIN=5
        self.PIN_I_BONOFF=6
        self.PIN_I_NSIDTIMEOUT=7
        self.PIN_I_NINTERVALL=8
        self.PIN_O_BRMONOFF=1
        self.PIN_O_NMW=2
        self.PIN_O_NZAEHLERWH=3
        self.PIN_O_NTEMP=4
        self.PIN_O_SSID=5
        self.PIN_O_SXML=6

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

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

    def get_sid(self):
        user_pw = self._get_input_value(self.PIN_I_SUSERPW)
        ip = self._get_input_value(self.PIN_I_SIP)
        # split username from password
        pw = user_pw[user_pw.find('@') + 1:]
        user = user_pw.split('@')[0]
        challenge = ""

        try:
            response = urllib.urlopen('http://' + ip + '/login_sid.lua')
            challenge = response.read()
            challenge = re.findall('<Challenge>(.*?)</Challenge>', challenge)[0]
        except Exception as e:
            self.DEBUG.add_message(self._get_input_value(self.PIN_I_SAIN) + ": '" + str(e) + "' in get_sid()")
            pass

        if len(challenge) == 0:
            self.g_ssid = "0000000000000000"
            self._set_output_value(self.PIN_O_SSID, self.g_ssid)
            return False

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
            self.g_ssid = "0000000000000000"
            self._set_output_value(self.PIN_O_SSID, self.g_ssid)
            return False

        sid = sid[0]

        if sid == '0000000000000000':
            self.g_ssid = "0000000000000000"
            self._set_output_value(self.PIN_O_SSID, self.g_ssid)
            return False
        else:
            self.g_ssid = sid
            self._set_output_value(self.PIN_O_SSID, self.g_ssid)
            self.DEBUG.set_value(self._get_input_value(self.PIN_I_SAIN) + ": SID", sid)
            return True

    def set_dect_200(self, on_off, ip, ain, sid):
        code = 0
        data = ""
        for x in range(0, 2):
            if not sid or sid == "0000000000000000":
                if self.get_sid():
                    sid = self.g_ssid

            # Dect200 #1 on/off
            cmd = 'setswitchoff'
            if bool(on_off) is True:
                cmd = "setswitchon"

            url = str('http://' + ip +
                       '/webservices/homeautoswitch.lua?ain=' + ain + '&switchcmd=' + cmd + '&sid=' + sid)
            resp = urllib.urlopen(url)
            code = resp.getcode()
            data = resp.read()
            if code == 200:
                self.DEBUG.add_message(str(self._get_input_value(self.PIN_I_SAIN)) + ": Switch set successfully.")
                return {"code": code, "data": data}

            elif code == 403:
                print("1st try failed in set_dect_200 with 403")
                sid = "0000000000000000"

        self.DEBUG.add_message(str(self._get_input_value(self.PIN_I_SAIN)) + ": Error setting switch, code:" +
                               str(code))

        return {"code": code, "data": data}

    def get_xml(self, sIp, sSid):
        try:
            resp = urllib.urlopen('http://' +
                                  sIp +
                                  '/webservices/homeautoswitch.lua?' +
                                  'switchcmd=getdevicelistinfos' +
                                  '&sid=' + sSid)
            self.DEBUG.add_message(self._get_input_value(self.PIN_I_SAIN) + ": Get XML result: " + str(resp.getcode()))
            return {"code": resp.getcode(), "data": resp.read()}

        except Exception as e:
            return {"code": 999, "data": ""}

    def get_dect_200_status(self, xml):
        data = {}
        ain = self._get_input_value(self.PIN_I_SAIN)
        state = re.findall('<device identifier="' + ain +
                           '" id=.*?>.*?<state>(.*?)</state>', xml)

        if len(state) == 0:
            return {}
        else:
            state = state[0]

        if state != "":
            data["state"] = int(state)
            self.set_output_value_sbc(self.PIN_O_BRMONOFF, bool(data["state"]))

        try:
            power = re.findall('<device identifier="' + ain +
                               '" id=.*?>.*?<power>(.*?)</power>', xml)
            if len(power) > 0:
                data["power"] = int(power[0])
                self.set_output_value_sbc(self.PIN_O_NMW, float(data["power"]))
        except Exception as e:
            self.DEBUG.add_message(str(self._get_input_value(self.PIN_I_SAIN)) + ": '" + str(power[0]) + "' in power in get_dect_200_status()")

        try:
            energy = re.findall('<device identifier="' + ain +
                                '" id=.*?>.*?<energy>(.*?)</energy>', xml)
            if len(energy) > 0:
                data["energy"] = int(energy[0])
                self.set_output_value_sbc(self.PIN_O_NZAEHLERWH, float(data["energy"]))
        except Exception as e:
            self.DEBUG.add_message(str(self._get_input_value(self.PIN_I_SAIN)) + ": '" + str(energy[0]) + "' in energy in get_dect_200_status()")

        try:
            temp = re.findall('<device identifier="' + ain +
                              '" id=.*?>.*?<celsius>(.*?)</celsius>', xml)

            if len(temp) > 0:
                temp = int(temp[0])
                offset = re.findall('<device identifier="' + ain +
                                    '" id=.*?>.*?<offset>(.*?)</offset>', xml)

                if len(offset) != 0:
                    temp = temp + int(offset[0])

                data["temp"] = temp / 10.0
                self.set_output_value_sbc(self.PIN_O_NTEMP, float(data["temp"]))

        except Exception as e:
            self.DEBUG.add_message(str(self._get_input_value(self.PIN_I_SAIN)) + ": Error converting '" + str(temp[0]) + "' in temp in get_dect_200_status()")

        self.DEBUG.add_message(str(self._get_input_value(self.PIN_I_SAIN)) + ": XML processed successfully")

        return data

    def logout(self, ip, sid):
        http_client = httplib.HTTPConnection('http://' + ip, timeout=5)
        http_client.request("GET", '/login_sid.lua?logout=true&sid=' + sid)
        response = http_client.getresponse()
        return response.status

    def trigger(self):
        # Get SID if not available
        sid = self._get_input_value(self.PIN_I_SSID)

        for x in range(0, 2):
            if not sid or sid == "0000000000000000":
                if self.get_sid():
                    sid = self.g_ssid

            xml = self.get_xml(self._get_input_value(self.PIN_I_SIP), sid)

            if xml["code"] == 200:
                # Evaluate XML data
                self.get_dect_200_status(xml["data"])
                self.set_output_value_sbc(self.PIN_O_SXML, xml["data"])
                self.DEBUG.add_message(self._get_input_value(self.PIN_I_SAIN) + ": XML received")
                break
            elif xml["code"] == 403 or xml["code"] == 999:
                self.g_ssid = "0000000000000000"
                if x == 1:
                    self.DEBUG.add_message(self._get_input_value(self.PIN_I_SAIN) + ": Could not receive valid SID")
            else:
                if x == 1:
                    self.DEBUG.add_message(self._get_input_value(self.PIN_I_SAIN) + ": Error processing XML, code:" +
                                       str(xml["code"]))

        interval = self._get_input_value(self.PIN_I_NINTERVALL)
        if interval > 0:
            threading.Timer(interval, self.trigger).start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        self.g_out_sbc = {}
        self.g_ssid = "0000000000000000"
        self.g_debug_sbc = False

        interval = self._get_input_value(self.PIN_I_NINTERVALL)
        if interval > 0:
            self.trigger()

    def on_input_value(self, index, value):

        ssid = self.g_ssid

        if index == self.PIN_I_SSID:
            self.g_ssid = value

        elif (index == self.PIN_I_NINTERVALL) and (value > 0):
            self.trigger()

        # Switch device on or of and report back new status
        elif index == self.PIN_I_BONOFF:

            res_on = self.set_dect_200(self._get_input_value(self.PIN_I_BONOFF),
                                       self._get_input_value(self.PIN_I_SIP),
                                       self._get_input_value(self.PIN_I_SAIN),
                                       self.g_ssid)

            self.set_output_value_sbc(self.PIN_O_BRMONOFF, bool(res_on["data"]))

        # If new XML available or trigger arrived,
        # get and process new status data
        elif index == self.PIN_I_SXML:
            xml = ""

            if index == self.PIN_I_SXML:
                xml = {"code": 200, "data": value}

            # Evaluate XML data
            self.get_dect_200_status(xml["data"])
            self._set_output_value(self.PIN_O_SXML, xml["data"])

        elif index == self.PIN_I_NINTERVALL and value > 0:
            self.trigger()
