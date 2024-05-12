# coding: UTF-8

# coding: UTF-8

import re
import socket
import threading
import fritz_lib.fritz as fritz


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class FritzDECT200_11081_11081(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "FritzBox")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_SIP=1
        self.PIN_I_USER=2
        self.PIN_I_PW=3
        self.PIN_I_SAIN=4
        self.PIN_I_BONOFF=5
        self.PIN_I_NINTERVALL=6
        self.PIN_O_NAME=1
        self.PIN_O_PRESENT=2
        self.PIN_O_BRMONOFF=3
        self.PIN_O_NMW=4
        self.PIN_O_NZAEHLERWH=5
        self.PIN_O_NTEMP=6

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

        self.g_out_sbc = {}
        self.g_debug_sbc = False
        self._ain = str()
        self.g_out_sbc = {}  # type: {int, object}
        self.time_out = 3  # type: int
        self.debug = False
        self.service_name = "urn:dslforum-org:service:X_AVM-DE_Homeauto:1"

    def set_output_value_sbc(self, pin, val):
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                if self.debug: print ("# SBC: " + str(val) + " @ pin " + str(pin) + ", data not send!")
                self.g_debug_sbc = True
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val
        self.g_debug_sbc = False

    def log_msg(self, text):
        self.DEBUG.add_message("11081 ({}): {}".format(self._ain, text))

    def log_data(self, key, value):
        self.DEBUG.set_value("11081 ({}) {}".format(self._ain, key), str(value))

    def get_device_status(self):
        """

        :return:
        """
        if self.debug: print("DEBUG | Entering get_device_status.")
        self.ensure_fritz_box_init()

        global fritz_box
        action = "GetSpecificDeviceInfos"
        attr_list = {"NewAIN": self._ain}
        data = fritz_box.set_soap_action(self.service_name, action, attr_list)

        attr = {self.PIN_O_NAME: "NewDeviceName",
                self.PIN_O_PRESENT: "NewPresent",
                self.PIN_O_BRMONOFF: "NewSwitchState",
                self.PIN_O_NMW: "NewMultimeterPower",
                self.PIN_O_NTEMP: "NewTemperatureCelsius",
                self.PIN_O_NZAEHLERWH: "NewMultimeterEnergy" }

        for pin in attr:
            try:
                param = attr[pin]
                if param not in data:
                    continue

                if pin is self.PIN_O_NAME:
                    result = str(data[param])
                elif pin is self.PIN_O_PRESENT:
                    result = (str(data[param]).upper() == "CONNECTED")
                elif pin is self.PIN_O_BRMONOFF:
                    result = (str(data[param]).upper() == "ON")
                elif pin is self.PIN_O_NMW:
                    result = float(data[param]) * 10.0
                elif pin is self.PIN_O_NTEMP:
                    if "NewTemperatureOffset" in data:
                        temp_offset = float(data["NewTemperatureOffset"])
                    else:
                        temp_offset = 0.0
                    result = (float(data["NewTemperatureCelsius"]) - temp_offset) / 10.0
                elif pin is self.PIN_O_NZAEHLERWH:
                    result = float(data[param])

                self.set_output_value_sbc(pin, result)

            except Exception as e:
                raise Exception("get_info | {}".format(e))

        self.log_msg("get_device_status | Completed.")

    def set_switch(self, state):
        """

        :param state:
        :return:
        """
        action = "SetSwitch"
        sw_state = "ON" if state else "OFF"
        attr_list = {"NewAIN": self._ain, "NewSwitchState": sw_state}

        self.ensure_fritz_box_init()
        global fritz_box
        ret = fritz_box.set_soap_action(self.service_name, action, attr_list)

        if 'u:SetSwitchResponse xmlns:u="urn:dslforum-org:service:X_AVM-DE_Homeauto:1"' in ret:
            self.set_output_value_sbc(self.PIN_O_BRMONOFF, state)
            self.log_msg("set_switch | OK")

    def ensure_fritz_box_init(self):
        """
        Takes care, that global variable exists and initialises the connection to FritzBox.
        :return: -
        :exception: Exception()
        """
        if "fritz_box" not in globals():
            global fritz_box
            fritz_box = fritz.FritzBox()
            try:
                fritz_box.user = str(self._get_input_value(self.PIN_I_USER))
                fritz_box.password = str(self._get_input_value(self.PIN_I_PW))
                fritz_box.discover(self.FRAMEWORK.get_homeserver_private_ip())
                self.log_data("FritzBox IP", "{}://{}:{}".format(fritz_box.protocol,
                                                                                     fritz_box.ip,
                                                                                     fritz_box.port))
            except Exception as e:
                raise Exception("Exception in ensure_fritz_box_init: {}".format(e))

    def update_status(self):
        """
        Regular triggger to fetch the switch status from the FritzBox.
        In case of error, try 1x a reconnect.

        :return: Nothing
        """
        if self.debug: print("DEUBG | Entering update_status.")
        interval = self._get_input_value(self.PIN_I_NINTERVALL)
        if interval == 0:
            return

        try:
            self.get_device_status()
            successful = True
        except Exception as e:
            successful = False
            self.log_msg("update_status | Exception in get_device_status: {}. "
                         "Trying to reset the fritz box connection.".format(e))

            if "fritz_box" in globals():
                global fritz_box
                del fritz_box
            self.ensure_fritz_box_init()

        if not successful:
            try:
                self.get_device_status()
            except Exception as e:
                self.log_msg("update_status | Exception in 2nd try get_device_status: {}".format(e))

        if interval > 0:
            t = threading.Timer(interval, self.update_status).start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.g_out_sbc = {}
        self.g_debug_sbc = False
        self._ain = str(self._get_input_value(self.PIN_I_SAIN))
        self.update_status()

    def on_input_value(self, index, value):
        try:
            if index == self.PIN_I_NINTERVALL and (value > 0):
                self.update_status()
            elif index == self.PIN_I_BONOFF:
                self.set_switch(value)
            elif index == self.PIN_I_USER or index == self.PIN_I_PW:
                self.ensure_fritz_box_init()
            elif index == self.PIN_I_SAIN and value:
                self._ain = str(self._get_input_value(self.PIN_I_SAIN))
        except Exception as e:
            self.log_msg("Exception in on_input_value: {}".format(e))


global fritz_box