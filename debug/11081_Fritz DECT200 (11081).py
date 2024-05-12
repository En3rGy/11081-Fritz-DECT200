try:
    if(hsl20_4_debug_page==None or hsl20_4.Framework.get_framework_index()<7):
        raise NameError
except NameError:
    global hsl20_4_debug_page
    global traceback
    import traceback
    global sys
    import sys
    global thread
    import thread
    class hsl20_4_debug_page:
        class Section:
            def __init__(self, section_key):
                self.__context_id = section_key
                self.__fields = {}
                self.__exceptions = []
                self.__messages = []
                self.__callbacks = []
                self.__lock = thread.allocate_lock()
            def set_value(self, key, value):
                with self.__lock:
                    self.__fields[key] = value
            def add_value_to_average_field(self, key, value):
                with self.__lock:
                    if not self.__fields.has_key(key):
                        self.__fields[key] = float(value)
                    else:
                        self.__fields[key] = float((self.__fields[key] + value) / 2)
            def increase_counter_field(self, key):
                with self.__lock:
                    if not self.__fields.has_key(key):
                        self.__fields[key] = 1
                    else:
                        self.__fields[key] += 1
            def add_message(self, message):
                with self.__lock:
                    for item in self.__messages:
                        if item[1]==message:
                            item[0] = time.time()
                            item[2]+=1
                            return
                    self.__messages.append([time.time(),message,1])
                    self.__messages.sort()
                    if len(self.__messages)>25:
                        del self.__messages[0]
            def add_exception(self, comment=None):
                try:
                    text = None
                    try:
                        exc = sys.exc_info()
                        if (exc!=None) and (len(exc)>=3) and (exc[0]!=None):
                            lines = traceback.format_exception(exc[0], exc[1], exc[2])
                            text = ''
                            for line in lines[1:]:
                                text = text + line
                    finally:
                        del exc
                    if text!=None:
                        with self.__lock:
                            for item in self.__exceptions:
                                if item[1]==text and item[3]==comment:
                                    item[0] = time.time()
                                    item[2]+=1
                                    return
                            self.__exceptions.append([time.time(),text,1,comment])
                            self.__exceptions.sort()
                            if len(self.__exceptions)>15:
                                del self.__exceptions[0]
                except Exception as e:
                    print "add_exception()", e
            def get_debug_information(self):
                result = {}
                result["fields"] = {}
                result["messages"] = []
                result["exceptions"] = []
                with self.__lock:
                    for key in self.__fields:
                        result["fields"][key] = self.__fields[key]
                    for msg in self.__messages:
                        result["messages"].append([msg[0], msg[1], msg[2]])
                    for exc in self.__exceptions:
                        result["exceptions"].append([exc[0], exc[1], exc[2], exc[3]])
                return result
            def _internal_register(self, callback):
                idx = None
                try:
                    idx = self.__callbacks.index(callback)
                except:
                    pass
                if idx==None:
                    self.__callbacks.append(callback)
            def _internal_get_callbacks(self):
                return self.__callbacks
try:
    if(hsl20_4.Framework.get_framework_index()<7):
        raise NameError
except NameError:
    global hsl20_4
    import thread
    global Queue
    import Queue
    global os
    import os
    global asyncore
    import asyncore
    import time
    class hsl20_4:
        LOGGING_NONE = 0
        LOGGING_SYSLOG = 1
        _CONTEXT_THREAD_QUEUE_MAX_SIZE = 0
        _ASYNCORE_LOOP_TIMEOUT = 1
        _HSCTX = None
        class BaseModule:
            def __init__(self, homeserver_context, module_context):
                if hsl20_4._HSCTX==None:
                    hsl20_4._HSCTX = homeserver_context[0]
                self._mc = homeserver_context[0]
                self._context_id = module_context
                self._lock = thread.allocate_lock()
                self._module_id = None
                self._framework = None
                self._refenerce = None
                self._last_timer_ts=0
                self._refenerce=homeserver_context[3]
                self._input_values = {}
                for i in range(len(homeserver_context[2])): #EN
                    if(i>0):
                        self._input_values[i] = homeserver_context[2][i]
                self._remanent_values = {}
                for i in range(len(homeserver_context[1])): #SN
                    if i>2:
                        self._remanent_values[i-2] = homeserver_context[1][i]
                self._output_values = []
                if self._mc!=None:
                    self._framework = hsl20_4.Framework(self._mc, self._context_id, self)
                    self._module_id = self._framework._get_module_instance_id()
            def _get_module_id(self):
                return self._module_id
            def _get_module_class_id(self):
                return self._refenerce.LogikItem.ID
            def _hslfw_check_input_values(self, ec, en):
                idx = ec.index(True)
                self._input_values[idx]=en[idx]
                self._framework._run_in_context_thread(self.on_input_value, (idx, en[idx]))
            def _hslfw_check_output_values(self, sc, sn, ac, an):
                remanent_value_changed=False
                with self._lock:
                    self._last_timer_ts = time.time()
                    try:
                        for item in self._remanent_values:
                            idx = int(item)
                            if (sn[idx+2]!=self._remanent_values[item]):
                                remanent_value_changed=True
                                sc[idx+2] = 1
                                sn[idx+2] = self._remanent_values[item]
                        outputs_set=[]
                        while(len(self._output_values)>0):
                            item, value=self._output_values[0]
                            idx = int(item)
                            if idx in outputs_set:
                                break
                            else:
                                outputs_set.append(idx)
                            ac[idx] = 1
                            an[idx] = value
                            del self._output_values[0]
                        if (len(self._output_values) > 0):
                            self._mc.ZyklusWork.addQueue([0, self._refenerce])
                    except Exception as e:
                        pass
                return remanent_value_changed
            def _get_framework(self):
                return self._framework
            def _get_logger(self, logType, param):
                return self._framework._context.get_logger((logType,param))
            def _get_input_value(self, index):
                    if self._input_values.has_key(index):
                        return self._input_values[index]
                    else:
                        return None
            def on_input_value(self, index, value):
                pass
            def on_init(self):
                pass
            def _set_output_value(self, index, value):
                with self._lock:
                    if(len(self._output_values)>100):
                        raise RuntimeError("Outputqueue overflow (index=%s)" % index)
                    self._output_values.append((index, value))
                    if len(self._output_values) == 1 or (time.time() - self._last_timer_ts>2):
                        if self._refenerce!=None:
                            self._mc.ZyklusWork.addQueue([0, self._refenerce])
            def _can_set_output(self):
                return len(self._output_values)<100
            def _get_remanent(self, index):
                if self._remanent_values.has_key(index):
                    return self._remanent_values[index]
                else:
                    return None
            def _set_remanent(self, index, value):
                if isinstance(value, str):
                    self._remanent_values[index] = value[:30000]
                else:
                    self._remanent_values[index] = value
                if self._refenerce!=None:
                    self._mc.ZyklusWork.addQueue([0, self._refenerce])
        class Framework:
            _timer_thread=None
            def __init__(self, homeserver_context, module_context, module_instance):
                self._mc = homeserver_context
                self._context_id = module_context
                self._logger = None
                hsl20_4.Framework._init_globals(self._mc)
                self._context=hsl20_4._Context.get_context(homeserver_context, module_context)
                self._module_instance_id=self._context.register_module_instance(module_instance)
            @staticmethod
            def _init_globals(homeserver_context):
                if not hasattr(homeserver_context, "HSL20ID"):
                    homeserver_context.HSL20ID = 0
                if not hasattr(homeserver_context, "HSL20DBG"):
                    homeserver_context.HSL20DBG = {}
                try:
                    hsl20_4_timer
                    if not hasattr(homeserver_context, "HSL20TIMERTHREAD_3"):
                        homeserver_context.HSL20TIMERTHREAD_3 = {}
                        homeserver_context.HSL20TIMERTHREAD_3["instance"] = hsl20_4_timer._TimerThread()
                    hsl20_4.Framework._timer_thread=homeserver_context.HSL20TIMERTHREAD_3["instance"]
                except NameError:
                    pass
            @staticmethod
            def _get_global_debug_section():
                if not hsl20_4._HSCTX.HSL20DBG.has_key("global"):
                    hsl20_4._HSCTX.HSL20DBG["global"] = hsl20_4_debug_page.Section("GLOBAL")
                return hsl20_4._HSCTX.HSL20DBG["global"]
            @staticmethod
            def get_framework_index():
                return 7
            def _run_in_context_thread(self, method_to_call, args=None):
                self._context.run_in_context_thread(method_to_call, args)
            def _get_module_instance_id(self):
                return self._module_instance_id
            def _signal_asyncore_select_interrupt(self):
                self._context.signal_asyncore_select_interrupt()
            def get_homeserver_version(self):
                return self._mc.Debug.Version
            def get_homeserver_version_major(self):
                return int(self._mc.Debug.Version.split('.')[0])
            def get_homeserver_version_minor(self):
                return int(self._mc.Debug.Version.split('.')[1])
            def get_homeserver_serial_id(self):
                return self._mc.SystemID
            def get_homeserver_private_ip(self):
                return self._mc.Ethernet.IPAdr
            def get_project_id(self):
                return self._mc.ProjectID
            def get_coordinates(self):
                return (self._mc.UhrenList.gradBreite, self._mc.UhrenList.gradLaenge)
            def get_context(self):
                return self._context_id
            def get_instance_by_id(self, instance_id):
                return self._context.get_module_instance(instance_id)
            def get_instance_from_module_by_id(self, module_context, instance_id):
                context = hsl20_4._Context.get_context(self._mc, module_context)
                if context!=None:
                    return context.get_module_instance(instance_id)
                return None
            def create_http_server(self):
                return hsl20_4_http_server.Server(self, self._context.get_socket_map())
            def create_http_client(self):
                return hsl20_4_http_client.Client(self, self._context.get_socket_map())
            def create_tcp_client(self):
                return hsl20_4_tcp.Client(self, self._context.get_socket_map())
            def create_udp_unicast(self):
                return hsl20_4_udp.Unicast(self, self._context.get_socket_map())
            def create_udp_broadcast(self):
                return hsl20_4_udp.Broadcast(self, self._context.get_socket_map())
            def create_udp_multicast(self):
                return hsl20_4_udp.Multicast(self, self._context.get_socket_map())
            def create_timer(self):
                return hsl20_4_timer.Timer(self)
            def create_interval(self):
                return hsl20_4_timer.Interval(self)
            def create_debug_section(self):
                return self._context.get_debug_section()
            def create_md5_hash(self):
                return hsl20_4_crypto.MD5Hash()
            def create_sha1_hash(self):
                return hsl20_4_crypto.SHA1Hash()
            def create_sha224_hash(self):
                return hsl20_4_crypto.SHA2Hash(224)
            def create_sha256_hash(self):
                return hsl20_4_crypto.SHA2Hash(256)
            def create_sha384_hash(self):
                return hsl20_4_crypto.SHA2Hash(384)
            def create_sha512_hash(self):
                return hsl20_4_crypto.SHA2Hash(512)
            def create_aes(self):
                return hsl20_4_crypto.AESCipher()
            def resolve_dns(self, host):
                ip = self._mc.DNSResolver.getHostIP(host)
                if (len(ip)==0):
                    return None
                else:
                    return ip
        class _Context:
            @staticmethod
            def get_context(homeserver_context, context_id):
                if hasattr(homeserver_context, "HSL20DATA") and homeserver_context.HSL20DATA.has_key(context_id):
                    return homeserver_context.HSL20DATA[context_id]["instance"]
                else:
                    return hsl20_4._Context(homeserver_context, context_id)
            def __init__(self, homeserver_context, context_id):
                self._mc = homeserver_context
                self._context_id = context_id
                if not hasattr(homeserver_context, "HSL20DATA"):
                    homeserver_context.HSL20DATA = {}
                homeserver_context.HSL20DATA[context_id] = {}
                homeserver_context.HSL20DATA[context_id]["debug"] = None
                homeserver_context.HSL20DATA[context_id]["logger"] = None
                homeserver_context.HSL20DATA[context_id]["instances"] = {}
                homeserver_context.HSL20DATA[context_id]["context_queue"] = Queue.Queue(hsl20_4._CONTEXT_THREAD_QUEUE_MAX_SIZE)
                self.__thread_queue=homeserver_context.HSL20DATA[context_id]["context_queue"]
                homeserver_context.HSL20DATA[context_id]["instance"]=self
                self._global_debug_section=hsl20_4.Framework._get_global_debug_section()
                self.__start_context_queue_thread()
                self.__start_asyncore_loop()
            def register_module_instance(self, instance):
                self._mc.HSL20ID+=1
                instance_id=self._mc.HSL20ID
                self._mc.HSL20DATA[self._context_id]["instances"][instance_id] = instance
                return instance_id
            def get_module_instance(self, instance_id):
                if (self._mc.HSL20DATA[self._context_id]["instances"].has_key(instance_id)):
                    return self._mc.HSL20DATA[self._context_id]["instances"][instance_id]
                else:
                    return None
            def get_debug_section(self):
                if self._mc.HSL20DATA[self._context_id]["debug"]==None:
                    self._mc.HSL20DATA[self._context_id]["debug"] = hsl20_4_debug_page.Section(self._context_id)
                return self._mc.HSL20DATA[self._context_id]["debug"]
            def get_logger(self, create=None):
                if self._mc.HSL20DATA[self._context_id]["logger"] != None:
                    return self._mc.HSL20DATA[self._context_id]["logger"]
                try:
                    if create:
                        logType, param = create
                    else:
                        logType = hsl20_4.LOGGING_NONE
                    if logType==hsl20_4.LOGGING_NONE:
                        self._mc.HSL20DATA[self._context_id]["logger"] = hsl20_4.Logger()
                    elif logType==hsl20_4.LOGGING_SYSLOG:
                        self._mc.HSL20DATA[self._context_id]["logger"] = hsl20_4_logging_syslog(self, self._context_id, param)
                except NameError:
                    self._mc.HSL20DATA[self._context_id]["logger"] = hsl20_4.Logger()
                return self._mc.HSL20DATA[self._context_id]["logger"]
            def get_thread_count(self):
                cnt=0
                if self._mc.HSL20DATA[self._context_id].has_key("context_thread_id"):
                    cnt+=1
                if self._mc.HSL20DATA[self._context_id].has_key("asyncore_loop_thread_id"):
                    cnt+=1
                return cnt
            def get_socket_map(self):
                if not self._mc.HSL20DATA[self._context_id].has_key("socket_map"):
                    self._mc.HSL20DATA[self._context_id]["socket_map"] = {}
                return self._mc.HSL20DATA[self._context_id]["socket_map"]
            def run_in_context_thread(self, method_to_call, args=None):
                self.__thread_queue.put_nowait((method_to_call, args))
            def __start_context_queue_thread(self):
                if not self._mc.HSL20DATA[self._context_id].has_key("context_thread_id"):
                    self._mc.HSL20DATA[self._context_id]["context_thread_id"] = thread.start_new_thread(self.__thread_queue_consumer,())
            def __thread_queue_consumer(self):
                while(True):
                    method_to_call, args = self.__thread_queue.get(block=True)
                    try:
                        if(args==None):
                            method_to_call()
                        else:
                            method_to_call(*args)
                    except:
                        self._global_debug_section.add_exception()
                    self.__thread_queue.task_done()
            def __start_asyncore_loop(self):
                if(os.name!="nt"):
                    self._signal_pipe_out,self._signal_pipe_in=os.pipe()
                    import fcntl
                    fcntl.fcntl(self._signal_pipe_out,fcntl.F_SETFL,os.O_NONBLOCK)
                    self._signal_pipe_out=os.fdopen(self._signal_pipe_out,'r',0)
                    self._signal_pipe_in=os.fdopen(self._signal_pipe_in,'a',0)
                    dd=hsl20_4._dummyDispatcher()
                    dd._signal_pipe_out=self._signal_pipe_out
                    self.get_socket_map()[self._signal_pipe_out]=dd
                if not self._mc.HSL20DATA[self._context_id].has_key("asyncore_loop_thread_id"):
                    self._mc.HSL20DATA[self._context_id]["asyncore_loop_thread_id"] = thread.start_new_thread(self.__thread_asyncore_loop,())
            def signal_asyncore_select_interrupt(self):
                if(os.name!="nt"):
                    self._signal_pipe_in.write('1')
                    self._signal_pipe_in.flush()
            def __thread_asyncore_loop(self):
                socket_map=self.get_socket_map()
                while(True):
                    try:
                        asyncore.loop(map=socket_map, timeout=hsl20_4._ASYNCORE_LOOP_TIMEOUT)
                        time.sleep(0.1)
                    except:
                        try:
                            dd=socket_map[self._signal_pipe_out]
                            for fd, obj in socket_map.items():
                                try:
                                    obj.handle_error()
                                except:
                                    self._global_debug_section.add_exception()
                            socket_map.clear()
                            socket_map[self._signal_pipe_out]=dd
                        except:
                            self._global_debug_section.add_exception()
                        time.sleep(0)
            def __on_debug(self):
                result = {}
                try:
                    result["Socket Map Size"]=str(len(self.get_socket_map().keys()))
                    result["Thread Queue Size"]=str(self.__thread_queue.qsize())
                except:
                    self._global_debug_section.add_exception()
                return result
        class _dummyDispatcher:
            def readable(self):
                return True
            def writable(self):
                return False
            def handle_read_event(self):
                data=self._signal_pipe_out.read()
            def handle_error(self):
                pass
        class Logger:
            DISABLE = 100
            CRITICAL = 50
            ERROR = 40
            WARNING = 30
            INFO = 20
            DEBUG = 10
            NOTSET = 0
            def set_level(self, level):
                pass
            def info(self, msg):
                pass
            def error(self, msg):
                pass
            def debug(self, msg):
                pass
            def warning(self, msg):
                pass
            def critical(self, msg):
                pass
            def exception(self, comment):
                pass
import sys
__hsl20_sys_modules_keys=set(sys.modules.keys())
sys.path.insert(0,"/tmp/FritzBoxFritzDECT200_11081_11081")
try:
    if(FritzDECT200_11081_11081==None):
        raise NameError
except NameError:
    global FritzDECT200_11081_11081
    import re
    import socket
    import threading
    import fritz_lib.fritz as fritz
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

SN[1]=FritzDECT200_11081_11081((MC, SN, EN, pItem))
SN[1].FRAMEWORK._run_in_context_thread(SN[1].on_init)
sys.path.remove("/tmp/FritzBoxFritzDECT200_11081_11081")
for m in (set(sys.modules.keys())-__hsl20_sys_modules_keys):
    del sys.modules[m]
