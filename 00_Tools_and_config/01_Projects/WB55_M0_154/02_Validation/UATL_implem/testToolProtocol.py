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

from UATL_generic.misc import *
from UATL_generic.models import UATL_TestProtocol

class UATL_CustomProtocol(UATL_TestProtocol):
    """
     Object managing communication test protocol with any board (like ask for prompt, read ack, detect end of command, ...)
    """        
    
    def isAutoResetEnabled(self):
        return True
        
    def getEncoding(self):
        """
        TODO: add a parameter in the global config file for this?
        """
        return 'windows-1252'
        
    def getRequestToWaitForCommand(self):
        """
        usefull if you want to ask the board if it is ready to hear for commands
        """
        return "\n"
        
    def getPromptRegex(self):
        """
        usefull if you want to know when the board acks the request "waiting for command"
        """
        return r'802\.15\.4 TESTS \>'
        
    def getEndOfCommandRegex(self):
        """
        usefull if you want to know if the last result can be parsed and if the next command can be send
        """
        #return self.getPromptRegex()
        return r'.*finished with.*'
          
    def hasCommandThrowedAnyError(self,testLog):
        """
        usefull if you want to abort a test campaign / test case in case of error (error, not failure)
        I think I should to something like 
        if board.listener.protocol.hasCommandThrowedAnyError() :
            result = "skipped"
            endOfTest = True
        """
        return (re.search('.*(ERROR :).*', testLog) is not None)

                        
    def hasBoardReset(self,testLog):
        """
        usefull if you want to know if board has reset during this log
        """
        return (re.search('.*RF LLDs test CLI.*', testLog) is not None) 

                        