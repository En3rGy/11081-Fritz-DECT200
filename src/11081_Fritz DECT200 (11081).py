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
import urllib2
import ssl
import urlparse
import socket
import struct
import hashlib
import threading
import json


def do_regex(match_str, text):
    match = re.findall(match_str, text, flags=re.S)

    if len(match) == 0:
        return ""

    return match[0]


def interface_addresses(family=socket.AF_INET):
    for fam, _, _, _, sockaddr in socket.getaddrinfo('', None, 0, 0, 0, socket.AI_NUMERICHOST):
        if family == fam:
            yield sockaddr[0]


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class FritzDECT200_11081_11081(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "11081_FritzBox_Dect200")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_AUTH_DATA=1
        self.PIN_I_SIP=2
        self.PIN_I_USER=3
        self.PIN_I_PW=4
        self.PIN_I_SAIN=5
        self.PIN_I_BONOFF=6
        self.PIN_I_NINTERVALL=7
        self.PIN_O_NAME=1
        self.PIN_O_PRESENT=2
        self.PIN_O_BRMONOFF=3
        self.PIN_O_NMW=4
        self.PIN_O_NZAEHLERWH=5
        self.PIN_O_NTEMP=6
        self.PIN_O_AUTH_DATA=7

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

        self.g_out_sbc = {}
        self.g_debug_sbc = False
        self._ain = ""
        self.g_out_sbc = {}  # type: {int, object}
        self.fb_ip = self._get_input_value(self.PIN_I_SIP)
        self.url_parsed = ""  # type: urlparse
        self.service_descr = ""  # type: str
        self._service_data = ""  # type: str
        self.nonce = ""  # type: str
        self.realm = ""  # type: str
        self.auth = ""  # type: str
        self.time_out = 3  # type: int

    def set_output_value_sbc(self, pin, val):
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print ("# SBC: " + str(val) + " @ pin " + str(pin) + ", data not send!")
                self.g_debug_sbc = True
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val
        self.g_debug_sbc = False

    def log_msg(self, text):
        self.DEBUG.add_message("11081 ({}): {}".format(self._ain, text))

    def log_data(self, key, value):
        self.DEBUG.set_value("11081 ({}) {}".format(self._ain, key), str(value))

    def get_service_data(self, data, service_type):
        try:
            service_id = \
                re.findall('<serviceType>' + service_type + '<\\/serviceType>.*?<serviceId>(.*?)<\\/serviceId>', data,
                           flags=re.S)[0]
            control_url = \
                re.findall('<serviceType>' + service_type + '<\\/serviceType>.*?<controlURL>(.*?)<\\/controlURL>', data,
                           flags=re.S)[0]
            event_sub_url = \
                re.findall('<serviceType>' + service_type + '<\\/serviceType>.*?<eventSubURL>(.*?)<\\/eventSubURL>',
                           data, flags=re.S)[0]
            scpdurl = \
                re.findall('<serviceType>' + service_type + '<\\/serviceType>.*?<SCPDURL>(.*?)<\\/SCPDURL>', data,
                           flags=re.S)[0]

            return {"serviceType": service_type,
                    "serviceId": service_id,
                    "controlURL": control_url,
                    "eventSubURL": event_sub_url,
                    "SCPDURL": scpdurl}
        except Exception as e:
            self.log_data("Error", "get_service_data: " + str(e))
            return {}

    def discover_fb(self):
        """
        Checks if an IP is set on PIN_I_IP and uses this. If no IP is set, multicast is used for discovery.
        :return: IP to FRitzBox
        :rtype: urlparse.ParseResult
        """
        fb_ip = str(self._get_input_value(self.PIN_I_SIP))
        if fb_ip:
            url_unparsed = "http://{}:49000/tr64desc.xml".format(fb_ip)
            url_parsed = urlparse.urlparse(url_unparsed)

            if url_parsed.netloc:
                return url_parsed

        # SSDP request msg from application
        MCAST_MSG = ('M-SEARCH * HTTP/1.1\r\n' +
                     'HOST: 239.255.255.250:1900\r\n' +
                     'MAN: "ssdp:discover"\r\n' +
                     'MX: 5\r\n' +
                     'ST: urn:dslforum-org:device:InternetGatewayDevice:1\r\n')

        MCAST_GRP = '239.255.255.250'
        MCAST_PORT = 1900

        # hsl20_3.Framework.get_homeserver_private_ip
        hs_ip = self.FRAMEWORK.get_homeserver_private_ip()

        # for address in self.interface_addresses():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # time to life for multicast msg
        ttl = struct.pack('b', 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        # specify interface to use for multicast msg
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(hs_ip))

        sock.settimeout(1)

        try:
            sock.sendto(MCAST_MSG, (MCAST_GRP, MCAST_PORT))
        except socket.error as e:
            self.add_exception("In discover_fb, {} ".format(e))
            sock.close()
            return

        while True:
            try:
                data = sock.recv(1024)

                url_unparsed = do_regex('(?i)LOCATION: (.*)(?:\\n\\r|\\r\\n)SERVER:.*FRITZ!Box', data)
                url_parsed = urlparse.urlparse(url_unparsed)

                # (scheme='http', netloc='192.168.178.1:49000', path='/tr64desc.xml', params='', query='', fragment='')
                if url_parsed.netloc:
                    print("Found FritzBox at {}".format(url_parsed.netloc))
                    sock.close()
                    return url_parsed

            except socket.timeout:
                self.DEBUG.add_exception("Socket timed out while discovering FritzBox. Functionality of module not "
                                         "available!")
                break

        sock.close()

    def get_security_port(self, p_url_parsed):
        """
        :param p_url_parsed:
        :type p_url_parsed:
        :return:
        """

        url = p_url_parsed.geturl() + "/upnp/control/deviceinfo"
        url_parsed = urlparse.urlparse(url)

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()
        response_data = ""

        headers = {'Host': url_parsed.hostname,
                   'CONTENT-TYPE': 'text/xml; charset="utf-8',
                   'SOAPACTION': "urn:dslforum-org:service:DeviceInfo:1#GetSecurityPort"}

        data = ('<?xml version="1.0"?>' +
                '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" ' +
                's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">' +
                '<s:Body><u:GetSecurityPort xmlns:u="urn:dslforum-' +
                'org:service:DeviceInfo:1"></u:GetSecurityPort>' +
                '</s:Body></s:Envelope>')

        try:
            # Build a http request and overwrite host header with the original hostname.
            request = urllib2.Request(url, data=data, headers=headers)

            # Open the URL and read the response.
            response = urllib2.urlopen(request, timeout=self.time_out, context=ctx)
            response_data = response.read()
        except Exception as e:
            self.log_data("Error", "getSecurityPort: " + str(e))

        return do_regex('<NewSecurityPort>(.*?)<\\/NewSecurityPort>', response_data)

    def get_data(self, url):
        url_parsed = urlparse.urlparse(url)

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()
        response_data = ""

        try:
            # Build a http request and overwrite host header with the original hostname.
            request = urllib2.Request(url, headers={'Host': url_parsed.hostname})
            # Open the URL and read the response.
            response = urllib2.urlopen(request, timeout=self.time_out, context=ctx)
            response_data = response.read()
        except Exception as e:
            self.log_data("Error", "getData: " + str(e))
        return response_data

    def init_com(self):
        if self._service_data:
            return True

        if not self.url_parsed:
            self.url_parsed = self.discover_fb()
            self.log_data("Fritz!Box URL", self.url_parsed.geturl())

        if not self.url_parsed:
            self.log_msg("inti_com | Could not discover Fritz!Box. Check network.")
            return False

        self.fb_ip = self.url_parsed.geturl()

        self.service_descr = self.get_data(self.url_parsed.geturl())
        if not self.service_descr:
            self.log_msg("init_com | Could not retrieve service description. Check if Dect200 is connected.")
            return False

        self.url_parsed = urlparse.urlparse(self.url_parsed.scheme + "://" + self.url_parsed.netloc)
        self.fb_ip = self.url_parsed.geturl()

        # work with device info
        service_data = self.get_service_data(self.service_descr, "urn:dslforum-org:service:DeviceInfo:1")

        # get security port
        data = self.set_soap_action(self.url_parsed, service_data, "GetSecurityPort", {})

        if 'NewSecurityPort' not in data:
            self.log_msg("Could retrieve security port from Fritz!Box. Create a bug report. "
                         "The protocol might have changed.")
        else:
            sec_port = data['NewSecurityPort']
            url = 'https://' + self.url_parsed.hostname + ":" + sec_port
            self.url_parsed = urlparse.urlparse(url)
            self.fb_ip = self.url_parsed.geturl()
            self.log_data("Fritz!Box URL", self.url_parsed.geturl())

        urn = "urn:dslforum-org:service:X_AVM-DE_Homeauto:1"
        self._service_data = self.get_service_data(self.service_descr, urn)

        return True

    def get_soap_header(self):
        user = str(self._get_input_value(self.PIN_I_USER))
        # pw = str(self._get_input_value(self.PIN_I_PW))

        if self.auth == "":
            header = ('<s:Header>\n\t<h:InitChallenge ' +
                      'xmlns:h="http://soap-authentication.org/digest/2001/10/" ' +
                      's:mustUnderstand="1">\n\t\t' +
                      '<UserID>' + user + '</UserID>\n\t</h:InitChallenge >\n' +
                      '</s:Header>')

        else:
            header = ('<s:Header>\n\t<h:ClientAuth ' +
                      'xmlns:h="http://soap-authentication.org/digest/2001/10/" ' +
                      's:mustUnderstand="1">' +
                      '\n\t\t<Nonce>' + self.nonce + '</Nonce>' +
                      '\n\t\t<Auth>' + self.auth + '</Auth>' +
                      '\n\t\t<UserID>' + user + '</UserID>' +
                      '\n\t\t<Realm>' + self.realm + '</Realm>\n\t</h:ClientAuth>\n</s:Header>')

        return header

    # @attr p_sFormerResp Response from a previous request
    def get_soap_req(self, url_parsed, service_data, action, attr_list):
        if not "controlURL" in service_data or not "serviceType" in service_data:
            self.log_msg("get_soap_req | Expecting 'controlURL' and 'serviceType' in parameter service_data, "
                         "which is '{}'".format(service_data))
            return

        url = (url_parsed.geturl() + service_data["controlURL"])
        url_parsed = urlparse.urlparse(url)

        # Build a SSL Context to disable certificate verification.
        html_hdr = {'Host': url_parsed.hostname,
                    'CONTENT-TYPE': 'text/xml; charset="utf-8"',
                    'SOAPACTION': '"' + service_data["serviceType"] + "#" + action + '"'}

        soap_hdr = self.get_soap_header()

        data = ('<?xml version="1.0" encoding="utf-8"?>\n' +
                '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" ' +
                's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\n' +
                soap_hdr + '\n<s:Body>\n\t<u:' + action + ' xmlns:u="' +
                service_data["serviceType"] + '">')

        for key in attr_list:
            data += ('\n\t\t<' + key + '>' + attr_list[key] + '</' + key + '>')

        data += ('\n\t</u:{}>\n</s:Body>\n</s:Envelope>'.format(action))

        return urllib2.Request(url_parsed.geturl(), data=data, headers=html_hdr)

    def get_auth_data(self, data):
        if self.nonce and self.realm and self.auth:
            print("Auth data already existing. Will be deleted if a connection attempt fails.")
            return False

        self.nonce = do_regex("<Nonce>(.*?)<\\/Nonce>", data)
        self.realm = do_regex("<Realm>(.*?)<\\/Realm>", data)

        user = str(self._get_input_value(self.PIN_I_USER))
        pw = str(self._get_input_value(self.PIN_I_PW))
        if not user or not pw:
            self.log_msg("get_auth_data | User or Password not set.")
            return False

        secret = hashlib.md5("{user}:{realm}:{pw}".format(user=user, realm=self.realm, pw=pw))
        response = hashlib.md5(secret.hexdigest() + ":" + self.nonce)

        self.auth = response.hexdigest()
        if self.nonce:
            auth_data = {"fb": self.url_parsed.geturl(), "nonce": self.nonce, "realm": self.realm, "auth": self.auth}
            self.set_output_value_sbc(self.PIN_O_AUTH_DATA, json.dumps(auth_data))
            return True

        return False

    def set_soap_action(self, url_parsed, service_data, action, attr_list):
        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()
        response_data = ""

        for x in range(0, 2):
            request = self.get_soap_req(url_parsed, service_data, action, attr_list)
            if not request:
                continue

            try:
                response = urllib2.urlopen(request, timeout=self.time_out, context=ctx)
                response_data = response.read()

                got_new_auth_data = self.get_auth_data(response_data)
                auth_stat = do_regex('<Status>(.*?)<\\/Status>', response_data)
                if auth_stat != "Unauthenticated":
                    self.log_msg("set_soap_action | '{}'".format(auth_stat))
                    break
                else:
                    if not got_new_auth_data or x == 1:
                        self._service_data = ""
                        self.realm = ""
                        self.auth = ""
                        self.nonce = ""
                    if x == 1:
                        error_code = do_regex('<errorCode>(.*?)</errorCode>', response_data)
                        error_descr = do_regex('<errorDescription>(.*?)</errorDescription>', response_data)
                        self.log_msg("set_soap_action | "
                                     "{}. Error code {}. Aborting after 2nd try. "
                                     "Check authentication data".format(error_descr, error_code))

            except urllib2.HTTPError as e:
                response_data = e.read()
                error_code = re.findall('<errorCode>(.*?)</errorCode>', response_data, flags=re.S)
                error_descr = re.findall('<errorDescription>(.*?)</errorDescription>', response_data, flags=re.S)
                self.log_msg("Error:         \t" + error_descr[0] + " (" + error_code[0] + ")" +
                             "\nservice_data:\t" + json.dumps(service_data) +
                             "\naction:      \t" + action +
                             "\nattr_list:   \t" + json.dumps(attr_list))

        dic = {}
        response_data = do_regex('<u:{}Response.*?>(?:\\n|)(.*?)(?:\\n|)<\\/u:{}Response>'.format(action, action),
                                 response_data)
        # if response data is available; e.g. if a set command has been send, no return value is provided
        if response_data:
            response_data = re.findall('(<.*?<\\/.*?>)', response_data, flags=re.S)
            for i in range(0, len(response_data)):
                key = do_regex('<(.*?)>', response_data[i])
                val = do_regex('>(.*?)<', response_data[i])
                dic.update({key: val})
        return dic

    def get_info(self):
        attr_list = {"NewAIN": self._ain}
        data = self.set_soap_action(self.url_parsed, self._service_data, "GetSpecificDeviceInfos", attr_list)

        attr = [self.PIN_O_NAME,
                self.PIN_O_PRESENT,
                self.PIN_O_BRMONOFF,
                self.PIN_O_NMW,
                self.PIN_O_NTEMP,
                self.PIN_O_NZAEHLERWH]

        for pin in attr:
            try:
                if pin is self.PIN_O_NAME:
                    self.set_output_value_sbc(self.PIN_O_NAME, str(data["NewDeviceName"]))
                elif pin is self.PIN_O_PRESENT:
                    self.set_output_value_sbc(self.PIN_O_PRESENT, str(data["NewPresent"]) == "CONNECTED")
                elif pin is self.PIN_O_BRMONOFF:
                    self.set_output_value_sbc(self.PIN_O_BRMONOFF, str(data["NewSwitchState"]) == "ON")
                elif pin is self.PIN_O_NMW:
                    self.set_output_value_sbc(self.PIN_O_NMW, float(data["NewMultimeterPower"]) * 10.0)
                elif pin is self.PIN_O_NTEMP:
                    temp_offset = float(data["NewTemperatureOffset"])
                    temp = (float(data["NewTemperatureCelsius"]) - temp_offset) / 10.0
                    self.set_output_value_sbc(self.PIN_O_NTEMP, temp)
                elif pin is self.PIN_O_NZAEHLERWH:
                    self.set_output_value_sbc(self.PIN_O_NZAEHLERWH, float(data["NewMultimeterEnergy"]))
            except Exception as e:
                print(e)

    def set_switch(self, state):
        sw_state = "ON" if state else "OFF"

        attr_list = {"NewAIN": self._ain, "NewSwitchState": sw_state}
        ret = self.set_soap_action(self.url_parsed, self._service_data, "SetSwitch", attr_list)

        if ret == {}:
            self.set_output_value_sbc(self.PIN_O_BRMONOFF, state)

    def update_status(self):
        if not self.init_com():
            self.log_msg("update_status | Init_com failed.")
            return

        self.get_info()

        interval = self._get_input_value(self.PIN_I_NINTERVALL)
        if interval > 0:
            t = threading.Timer(interval, self.update_status).start()

    def load_auth_data(self):
        auth_data_s = str(self._get_input_value(self.PIN_I_AUTH_DATA))
        if auth_data_s:
            try:
                auth_data = json.loads(auth_data_s)
                self.url_parsed = urlparse.urlparse(auth_data["fb"])
                self.nonce = auth_data["nonce"]
                self.realm = auth_data["realm"]
                self.auth = auth_data["auth"]
            except Exception as e:
                print("load_auth_data | '{}' with auth_data_s '{}'".format(e, auth_data_s))

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.g_out_sbc = {}
        self.g_debug_sbc = False
        self._ain = str(self._get_input_value(self.PIN_I_SAIN))  # convert from unicode
        self.load_auth_data()
        self.update_status()

    def on_input_value(self, index, value):

        if index == self.PIN_I_NINTERVALL and (value > 0):
            self.update_status()
        elif index == self.PIN_I_BONOFF:
            self.set_switch(value)
        elif index == self.PIN_I_AUTH_DATA and value:
            self.load_auth_data()
        elif index == self.PIN_I_SAIN and value:
            self._ain = str(self._get_input_value(self.PIN_I_SAIN))  # convert from unicode
