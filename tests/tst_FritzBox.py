# coding: UTF-8
import time
import unittest
import json
import socket
import fritz_lib.fritz as fritz
import time

class TestSequenceFunctions(unittest.TestCase):
    cred = 0
    tst = 0

    def setUp(self):
        print("\n###setUp")

        hostname = socket.gethostname()
        self.my_ip = socket.gethostbyname(hostname)

        with open("credentials.txt") as f:
            self.cred = json.load(f)
            user = self.cred["PIN_I_USER"]
            password = self.cred["PIN_I_PW"]
            self.ain = self.cred["PIN_I_SAIN"]

        self.fritz = fritz.FritzBox()
        self.fritz.user = user
        self.fritz.password = password

    def test_discover(self):
        print("\n### test_discover")
        url = self.fritz.discover(self.my_ip)
        self.assertTrue(url)
        self.assertEqual(self.fritz.protocol, "https")

        print("### {}".format(self.fritz.protocol))
        print("### {}".format(self.fritz.ip))
        print("### {}".format(self.fritz.port))
        print("### {}".format(self.fritz.location_path))

    def test_soap_read(self):
        self.fritz.discover(self.my_ip)

        attr_list = {"NewAIN": self.ain}
        data = self.fritz.set_soap_action("urn:dslforum-org:service:X_AVM-DE_Homeauto:1", "GetSpecificDeviceInfos", attr_list)
        print("### {}".format(data))
        self.assertTrue("NewDeviceName" in data)

    def test_box_not_found(self):
        self.fritz.discover(self.my_ip)

        saved_ip = self.fritz.ip
        self.fritz.ip = "192.168.1.220"
        time.sleep(1)
        attr_list = {"NewAIN": self.ain}
        data = self.fritz.set_soap_action("urn:dslforum-org:service:X_AVM-DE_Homeauto:1", "GetSpecificDeviceInfos", attr_list)

        self.fritz.ip = saved_ip
        print("### 5 sec sleep. Disconnect test machine from network")
        time.sleep(5)
        print("### Continuing.")

        attr_list = {"NewAIN": self.ain}
        data = self.fritz.set_soap_action("urn:dslforum-org:service:X_AVM-DE_Homeauto:1", "GetSpecificDeviceInfos", attr_list)
        print("### {}".format(data))


if __name__ == '__main__':
    unittest.main()
