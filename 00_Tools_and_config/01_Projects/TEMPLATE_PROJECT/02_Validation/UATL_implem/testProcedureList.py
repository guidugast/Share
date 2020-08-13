# -*- coding: utf-8 -*-
# python version 3.8.1
import os
import time
import serial
import shlex
import sys
from threading import Thread, Event, Lock
import re
import serial.tools.list_ports
import datetime
from junit_xml import TestSuite as JU_TS
from junit_xml import TestCase as JU_TC
import random
from abc import ABCMeta, abstractmethod
from typing import final
from enum import Enum, auto, unique
import subprocess
from datetime import datetime

from UATL_generic.misc import  *
from UATL_generic.models import UATL_Procedure
from UATL_implem.procedureModels import UATL_TestCase,UATL_Characterization,UATL_Endurance


#############################################################
##                        802.15.4                         ##
#############################################################

class RLV_TC__HAL_TXRX_NoAck__nominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a simple txrx with init works with default parameters."
        
    def getExpectedResult(self):
        return "The rx command shall return a correct payload and no error, the tx command shall no error"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D D D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D D D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)

