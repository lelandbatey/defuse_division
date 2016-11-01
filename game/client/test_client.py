
import unittest
import time

from . import client

class TestClient(unittest.TestCase):
    def test_local_address(self):
        print(client.local_address())
    def test_zeroconf(self):
        info = client.zeroconf_info()
        print("info:", info)
        time.sleep(3)
