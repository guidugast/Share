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

from UATL_implem.testConfig import UATL_isDebugEnabled

class AutoEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
        
class UATL_ShellPolice:
    """
    ESC [ 0 m       # reset all (colors and brightness)
    ESC [ 1 m       # bright
    ESC [ 2 m       # dim (looks same as normal brightness)
    ESC [ 22 m      # normal brightness

    # FOREGROUND:
    ESC [ 30 m      # black
    ESC [ 31 m      # red
    ESC [ 32 m      # green
    ESC [ 33 m      # yellow
    ESC [ 34 m      # blue
    ESC [ 35 m      # magenta
    ESC [ 36 m      # cyan
    ESC [ 37 m      # white
    ESC [ 39 m      # reset

    # BACKGROUND
    ESC [ 40 m      # black
    ESC [ 41 m      # red
    ESC [ 42 m      # green
    ESC [ 43 m      # yellow
    ESC [ 44 m      # blue
    ESC [ 45 m      # magenta
    ESC [ 46 m      # cyan
    ESC [ 47 m      # white
    ESC [ 49 m      # reset

    # cursor positioning
    ESC [ y;x H     # position cursor at x across, y down
    ESC [ y;x f     # position cursor at x across, y down
    ESC [ n A       # move cursor n lines up
    ESC [ n B       # move cursor n lines down
    ESC [ n C       # move cursor n characters forward
    ESC [ n D       # move cursor n characters backward

    # clear the screen
    ESC [ mode J    # clear the screen

    # clear the line
    ESC [ mode K    # clear the line
    """
    class Brightness:
        BRIGHT =     '\033[1m'      # black
        RESET =       '\033[22m'    # reset brightness
        
    class Back:
        BLACK =     '\033[40m'      # black
        RED =       '\033[41m'      # red
        GREEN =     '\033[42m'      # green
        YELLOW =    '\033[43m'      # yellow
        BLUE =      '\033[44m'      # blue
        MAGENTA =   '\033[45m'      # magenta
        CYAN =      '\033[46m'      # cyan
        WHITE =     '\033[47m'      # white
        RESET  =    '\033[49m'      # reset background
        
    class Fore:
        BLACK =     '\033[30m'      # black
        RED =       '\033[31m'      # red
        GREEN =     '\033[32m'      # green
        YELLOW =    '\033[33m'      # yellow
        BLUE =      '\033[34m'      # blue
        MAGENTA =   '\033[35m'      # magenta
        CYAN =      '\033[36m'      # cyan
        WHITE =     '\033[37m'      # white
        RESET  =    '\033[39m'      # reset foreground
 
    def getFormattedLength(desiredLength):
        """
        quick and dirty pass around as len('\033[40m') is 5
        """
        return 4*5 + desiredLength
    
    def stripAnsi(text):
        return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', text)

def UATL_log(x):
    print("\nPy@   " + str(x), end='')

def UATL_logCommandInfo(x):
    UATL_log("*  " + str(x))

def UATL_logCommandOutput(x):
    UATL_log("*     "+ UATL_ShellPolice.Brightness.BRIGHT + str(x) + UATL_ShellPolice.Brightness.RESET)
    
def UATL_error(x):
    UATL_log("Error! : " +  UATL_ShellPolice.Fore.RED + UATL_ShellPolice.Back.BLACK + str(x) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "\n")

def UATL_debug(region, x):
    active = None
    if "prompt" in str(region):
        active = True
    elif "reset" in str(region):
        active = True
    elif "command" in str(region):
        active = True
    elif "serialInput" in str(region):
        active = True
    elif "serialOutput" in str(region):
        active = True
    elif "endurance" in str(region):
        active = True
    elif "regex" in str(region):
        active = True
    elif "embeddedStress" in str(region):
        active = True
    elif "synchro" in str(region):
        active = True
    elif "optim" in str(region):
        active = True
    else:
        active = True
        UATL_error("log region unknown '{}'".format(region))
        sys.exit(255)
        
    if active and UATL_isDebugEnabled():
        regionString = ""
        if str(region) != "serialOutput":
            regionString = UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "  " + UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.CYAN + "[{}]".format(region)
        print("\n" + UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.CYAN + "DBG:" + regionString + UATL_ShellPolice.Fore.CYAN + UATL_ShellPolice.Back.BLACK + "  " + str(x) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET, end='')
                  
def UATL_getTimeAsString(timeInS):

    if timeInS > 60*60:
        return "{}h{}min".format(int(timeInS/3600),int(timeInS/60) % 60)
    elif timeInS > 60*10:
        return "{}min".format(int(timeInS/60))
    elif timeInS > 60:
        return "{}min{}s".format(int(timeInS/60),int(timeInS) % 60)
    elif timeInS < 1.:
        return "{}ms".format(int(timeInS*1000))
    elif timeInS < 10.:
        return "{}s".format(round(timeInS,2))
    else:
        return "{}s".format(round(timeInS,1))