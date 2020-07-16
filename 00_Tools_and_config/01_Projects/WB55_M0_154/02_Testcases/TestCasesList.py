# -*- coding: utf-8 -*-

import time
import serial
import shlex
import sys
import threading
import re
import serial.tools.list_ports
import datetime
import random # for debug purposes


class RLV_TC__Init154(_testCase):
    """
    Test case purpose:
        - Test LLD BLE initialisation
    Test case procedure:
        - unit test
    """
    def __callCliCommands__(self):
        RLV_log("currently doing RLV_TC__InitBle")

        self.sendCLICommandToBoardAndListen(0,"BLE_HelloWorld")
        time.sleep(1)
   
        self.sendCLICommandToBoardAndListen(1,"BLE_HelloWorld")
        time.sleep(1)

        self.sendCLICommandToBoardAndListen(0,"BLE_ByeWorld")
        time.sleep(1)
   
        self.sendCLICommandToBoardAndListen(1,"BLE_ByeWorld")
        time.sleep(1)