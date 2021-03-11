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

class FritzDECT200_11081_11081(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "hsl20_3_FritzBox")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
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
        self.FRAMEWORK._run_in_context_thread(self.on_init)

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

    def get_sid(self, user_pw, ip):
        # split username from password
        pw = user_pw[user_pw.find('@') + 1:]
        user = user_pw.split('@')[0]

        response = urllib.urlopen('http://' + ip + '/login_sid.lua')
        challenge = response.read()
        challenge = re.findall('<Challenge>(.*?)</Challenge>', challenge)[0]

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
        resp = urllib.urlopen('http://' +
                              sIp +
                              '/webservices/homeautoswitch.lua?' +
                              'switchcmd=getdevicelistinfos' +
                              '&sid=' + sSid)
        self.DEBUG.set_value("11081 Get XML result", resp.getcode())
        return {"code": resp.getcode(), "data": resp.read()}

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
            sid = ""

        interval = self._get_input_value(self.PIN_I_NINTERVALL)

        if interval > 0:
            threading.Timer(interval, self.trigger).start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        self.g_out_sbc = {}
        self.g_ssid = ""
        self.g_debug_sbc = False

        if self._get_input_value(self.PIN_I_NINTERVALL > 0):
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
