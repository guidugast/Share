# -*- coding: utf-8 -*-
"""
time = temps qui reste avant la prochaine activité RF
--> utiliser avec db7 et picoscope (cf thierry)


- prio sur chaining

- 2 semaines pour faire le chaining, je m'arrêt au bout de deux semaines (vers le 22/07)
- une semaine pour l'environnement de test + jenkins (vers le 29/07)
- une semaine pour la doc et préparation de la démo (vers le 08/08)
- faire les tests bonus et les tests avec matériel (oscillo, ...)


------------------------

TO_BE_IMPROVED: 
- reset the boards before each testcase procedure is started?
- instead of for loop for CH, use a dichotomic (lambda-based?) loop
- instead of for loop for CH, use multiple loop with statistic analysis to have min and max. (min : sure to work, max : sure to not work)
- put description, status, and objectives in an abstract function for TC, CH, and EN
- in test campaing and other locations, renamme "test case" by "procedure"? renamming to be done, to avoid misunderstandings

TODO: 
- call procedures from ${PROJECT_NAME}/03_testcases/TestCaseList.py (use .pymanage file that will call all modules from the tree root?)
- I need a BZ for UATL when it will be release for users
- test packet size effect on characterization procedures
- move timeout from testsuite config file to testcase.py file with asbtract attribute getter '__getTimeout__'
- reserve a file for custom procedures (by inheritance) for end customer, so the current procedures (tc, endurance, ...) are not changed by mistake
- fix reset when frozen
- remove UATL_EmbeddedStress
- add in UATL_Procedure proper error, reset and timeout counter (actually it is related to last command)
- now tests are stopped if an RLV error occurs, clean counter for endurance?
- script for extracting TC list from tc file?
- remove number of board in config file because it is not configurable, move it in an asbtract attribute getter 'getBoardNumber' 
- create a repo for test env, a repo for tests and for project config, keep the actual repo for M0 and M4.
- make in conf the procedure timeout optionnal (if nothing it put, a default value of 1 minute will be used)
- have a project list in the root of the test env and dl only projects that are listed (so we need to store projects in a specific repo, and keep the generic part in this repo)
- in the test env generation script, use tags or branches or sha-1 or master/head
- create branch lld_ble in the repo where all lld_ble projects would be, keep the master branch for all the generic part
- AP_TXRX and AP_TXRX are the same, replace by AP_TXRX
- actionPending flag --> get/set
- remove apCurrentType because it is useless, we use the index (0 for end, 1 for empty,...)
- For 1-board-test, use the board that is available, not systematically the first one. That would allow to run several tests in parallel for 1-board-tests

NEW TESTS
- check all "assert_param"
- networkId from AP[] in LLD (nominal / wrong)
- BLE_Step__RssiScan
- channel hop with chaining
- add bin test feature: LQI dataroutine
- check all bits of p->status, generate all error/cases/status bits
    - NS_EN enabled/disabled with sn/nesn? still some work to do in the binary, but will need some time to implement, is it worth doing it?
- StopActivity with chaining
- timing characterization?
- tx power / rssi with start tone
- tx power / rssi with send packet

HOW TO TEST?
- xtal check, what is to expect?
- the issue is for each test that serialize condition for a good transmission, there is a probability of failure, but the test should not be failed if PER is 5 < 1000, thus I think each test shall be run 1000th time

TICKET TO ADD:
- LLD BLE: EncryptPlainData
- LLD BLE: StopActivity
- LLD BLE: EPR 6.7 % ? run long tests
- LLD BLE: tx power no coherence in values 


TIPS:
- extract full TC list: 
  1/ search for all "class RLV_" in notepad ++ in the Testcase.py file
  2/ copy it in a new file
  3/ replace "^Line[\s\w\d]+: class (.*?)\([\w_]+\):[\s]*(?:#.*?)*$" by "\1"
  4/ remove first unit test in the obtained list 
- ┘┐┌└ ┤─├ ┴ ┬ ┼ │ ═ ║ ╒ ╓ ╔ ╕ ╖ ╗╘ ╙ ╚ ╛╜ ╝ ╞ ╟ ╠ ╡ ╢ ╣ ╤ ╥ ╦ ╧ ╨ ╩ ╪ ╫ ╬ ▲►▼◄ ♦ ■ ← ↑ → ↓ ↔ ↕ 
    
"""
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

def UATL_printScriptVersion():
    version = "v0.64 (dev)"
    print('\n' + UATL_ShellPolice.Fore.YELLOW + UATL_ShellPolice.Back.BLACK + "UATL (Unified Automatic Test Launcher) -- " + version + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET )
       
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

class UATL_Reset:
    """
     Object managing reset status for each (board,serial) couple
    """
    def __init__(self):
        self.shouldBeDone = Event()
        self.hasBeenDetected = Event()
        
class UATL_Board:
    """
     Object managing board connexion
    """
    def __init__(self, boardId, portId, protocol, stLinkUtilityExe):
        self.__isActive = True
        self.reset = UATL_Reset()
        self.boardId = boardId
        self.portId = portId
        self.stId = None
        self.serialNumber = None
        self.fwVersion = None
        self.listener = UATL_Listener(portId,protocol, self.reset)
        self.stLinkUtilityExe = stLinkUtilityExe
        self.__procedureResetCounter = 0
    
    def __watchdog(self):
        try:
            while self.__isActive:
                if self.reset.shouldBeDone.is_set():
                    if self.listener.isAutoResetEnabled():
                        self.resetFromShell()
                    else:
                        UATL_error("A serial I/O error has occured on board {} (st id {}, port {}, serial number {}, FW version {})".format(self.boardId,self.stId,self.portId,self.serialNumber,self.fwVersion))
                        sys.exit(255)
                else:
                    if self.reset.hasBeenDetected.is_set():
                        UATL_debug("reset","wait for reset to finish")
                        time.sleep(2)
                        self.reset.hasBeenDetected.clear()
                        self.__procedureResetCounter+=1

                time.sleep(3)
        except SystemExit as e:
            raise e
            
    def updateBoardInfo(self, stId, serialNumber, fwVersion):
        self.stId = stId
        self.serialNumber = serialNumber
        self.fwVersion = fwVersion
        UATL_debug("synchro","updating board info boardId: {}".format(self.boardId))
        UATL_debug("synchro","updating board info portId: {}".format(self.portId))
        UATL_debug("synchro","updating board info stId: {}".format(self.stId))
        UATL_debug("synchro","updating board info serialNumber: {}".format(self.serialNumber))
        UATL_debug("synchro","updating board info fwVersion: {}".format(self.fwVersion))
            
    def listen(self):
        self.listener.start()
        UATL_log("Listening now to board "+ str(self.boardId) + " (port " + str(self.portId) + ").")
        watchdog = Thread(target=self.__watchdog, daemon=True, name="Watchdog")
        watchdog.start()
        
    def resetFromShell(self):
        UATL_log("resetting board {} (port {}, st id {}).".format(self.boardId,self.portId,self.stId))
        UATL_debug("reset","wait for the end of any ongoing reset")
        
        try:
            while self.reset.hasBeenDetected.is_set():
                pass
        except SystemExit as e:
            raise e
        try:
            UATL_debug("reset","reconnect board")
            self.listener.reConnect()
            UATL_debug("reset","board reconnected")
        except SystemExit as e:
            os._exit(int(str(e)))
        except:
            pass
        try:
            UATL_debug("reset","shell command : {} -c ID={} -Rst".format(self.stLinkUtilityExe,self.stId))
            subprocess.run("{} -c ID={} -Rst".format(self.stLinkUtilityExe,self.stId), stdout=subprocess.DEVNULL, check=True)
        except SystemExit as e:
            os._exit(int(str(e)))
        except:
            UATL_error("Could not reset board, board might be disconnected")
            sys.exit(255)
            
        UATL_debug("reset","waiting for reset to be detected")
        try:
            while not self.reset.hasBeenDetected.is_set():
                pass
        except SystemExit as e:
            raise e
        UATL_debug("reset","reset has been detected, wait for it  to finish")
        time.sleep(2)
        self.reset.shouldBeDone.clear()
        self.reset.hasBeenDetected.clear()
        UATL_debug("reset","reset done")
        
    def __del__(self):
        self.__isActive = False
        UATL_log( "Stopping listening daemon for  board {} (port {})".format(self.boardId,self.portId))       
                
class UATL_TestBench:
    """
     Object managing all the boards used in the testcase(s)
    """
    def __init__(self, stLinkUtilityExe):
        self.boardList = []
        self.__protocol = UATL_TestProtocol()
        self.__checkSerialPorts(stLinkUtilityExe)
        self.__stLinkUtilityExe = stLinkUtilityExe
        UATL_log("Testbench initialized")
        
    def __del__(self): 
        UATL_log("Testbench closing board connexion")
        
    def synchronise(self):
        UATL_log("Synchronizing Testbench")
        # check if each board communication is working
        for board in self.boardList:
            board.listen()
            board.listener.askForPrompt()
            
        # list all board to affect a couple (serial number, ST id) to each couple (port COM, board Id)
        UATL_debug("synchro","shell command : {} -List".format(self.__stLinkUtilityExe))
        retVal = subprocess.run("{} -List".format(self.__stLinkUtilityExe), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
                    
        # parse board list to find data
        arrayResult = re.findall(r'(\d+):.*?SN:[\s]+([\dA-Z]+).*?FW:[\s]+([\dA-Z]+)', str(retVal.stdout), flags=re.DOTALL) 
        UATL_debug("synchro","arrayResult: {}".format(arrayResult))
        
        # fill data found
        for (stId, serialNumber, fwVersion) in arrayResult:
            for board in self.boardList:
                try:
                    while board.reset.hasBeenDetected.is_set():
                        pass     
                except SystemExit as e:
                    raise e
            UATL_debug("synchro","{} -c ID={} -Rst".format(self.__stLinkUtilityExe,stId))
            subprocess.run("{} -c ID={} -Rst".format(self.__stLinkUtilityExe,stId), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)   
            
            UATL_debug("synchro","looking for the board which has reset")
            boardUpToDate = False
            try:
                while not boardUpToDate:
                    for board in self.boardList:
                        if board.reset.hasBeenDetected.is_set():
                            UATL_debug("synchro","board found")
                            board.updateBoardInfo(stId,serialNumber,fwVersion)
                            boardUpToDate = True
                            board.reset.hasBeenDetected.clear()
                            break
                    time.sleep(0.1)
            except SystemExit as e:
                raise e
        time.sleep(2)
        UATL_log("Testbench synchronized")
                  
    def __checkSerialPorts(self,stLinkUtilityExe):
        portList = list(serial.tools.list_ports.comports())

        if (len(portList) == 0):
            UATL_error("Empty port list")
            sys.exit(2)
        elif (len(portList) == 1):
            UATL_error("Only one port available")
            sys.exit(2)
        else:
            UATL_log( str(len(portList)) + " available serial port(s) found")
            boardId = 0
            for port in portList:
                if port.pid == 24577 or port.pid == 14155: # check if port product id is FTDI = 24577 / 14155 if STLink
                    try:
                        s = serial.Serial(port.device)
                        s.close()
                        self.boardList.append(UATL_Board(boardId,port.device,self.__protocol,stLinkUtilityExe))
                        boardId = boardId+1
                    except (OSError, serial.SerialException):
                        pass
                    
        if (len(self.boardList) == 0):
            UATL_error("No board could be connected, check if board terminals are not already in use")
            sys.exit(7)
        elif (len(self.boardList) != len(portList)):
            UATL_error("At least one board could not connect, check if any board terminal is not already in use")
            sys.exit(7)
        else:
            UATL_log( str(len(self.boardList)) + " board(s) connected")
            
    def launchTest(self, testSuitePath, csvTestReportFile, junitReportFile):
        testSuite = UATL_TestSuite(testSuitePath)

        testCampaign = UATL_TestCampaign(testSuite, self)
        testCampaign.run()# for fast xml debug use ".run_stub()"
        testCampaign.displayResult()
        testCampaign.writeTestReportAsCsv(csvTestReportFile)
        testCampaign.writeJUnitResults(junitReportFile)
            
class UATL_SerialComCanal:
    """
     Object managing connexion with a port COM
    """
    def __init__(self, portId, reset):
        self.portId = portId
        self.serial = serial.Serial(
                                port = portId,
                                baudrate = 115200,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE,
                                bytesize = serial.EIGHTBITS, 
                                timeout = 0.1
                                )
        self.reOpen()
        self.reset = reset
    
    def reOpen(self):        
        try:
            self.serial.close()
        except SystemExit as e:
            os._exit(int(str(e)))
        except:
            pass
        self.serial.open()
        
        if self.serial.isOpen():
            UATL_log( "Port "+self.portId + " opened.")
        else:
            UATL_error("Failed to open port "+self.portId +".")
            sys.exit(7)
        
    def __del__(self):
        self.serial.close()
        UATL_log( "Port "+self.portId + " closed.")
  
class UATL_Command:
    """
     Object managing command(s) sent to boards and their response
    """
    @unique
    class __Status(AutoEnum):
        NOT_SENT = auto()
        SENT_WAITING_FOR_ANSWER = auto()
        END_RECEIVED = auto()
        TIMED_OUT = auto()
        ERROR = auto()      
    
    def __init__(self, procedure, sequenceNumber, commandAsAString, serialComCanal, protocol, reset, show = True):
        self.commandAsAString = commandAsAString
        self.response = ""
        self.__errorCounter = 0
        self.__resetCounter = 0
        self.__serialComCanal = serialComCanal
        self.__protocol = protocol
        self.reset = reset
        self.__status = self.__Status(self.__Status.NOT_SENT)
        self.__show = show
        self.__sequenceNumber = sequenceNumber
        if (self.commandAsAString != self.__protocol.getRequestToWaitForCommand()):
            UATL_debug("command","Running command {} (port:{} sqn:{})".format(repr(self.commandAsAString),self.__serialComCanal.portId,self.__sequenceNumber))
        self.__send(procedure)
        
    def __del__(self): 
        if (self.commandAsAString != self.__protocol.getRequestToWaitForCommand()):
            UATL_debug("command","End of command {} (port:{} sqn:{})".format(repr(self.commandAsAString),self.__serialComCanal.portId,self.__sequenceNumber))
        
    def __send(self,procedure):
        retries = 0
        while ((procedure is not None and not procedure.hasBeenAbortedByTimeout()) or procedure is None) and self.__status != self.__Status.SENT_WAITING_FOR_ANSWER and self.__status != self.__Status.TIMED_OUT and self.__status != self.__Status.ERROR:
            while self.reset.hasBeenDetected.is_set() or self.reset.shouldBeDone.is_set():
                pass
            try:
                self.__serialComCanal.serial.write(str.encode(self.commandAsAString +"\r"))
                self.__status = self.__Status.SENT_WAITING_FOR_ANSWER
            except SystemExit as e:
                os._exit(int(str(e)))
            except:
                retries += 1
                if(retries > 3):
                    UATL_error( "Could not write on port {}".format(self.__serialComCanal.portId))
                    self.reset.shouldBeDone.set()
                    retries = 0
                else:
                    UATL_logCommandInfo("Could not write on serial port {}, trying again...".format(self.__serialComCanal.portId))
                
    def shallBeShawn(self):
        return self.__show
        
    def isPending(self):
        return (self.__status == self.__Status.SENT_WAITING_FOR_ANSWER)
        
    def isFinished(self):
        return (self.__status == self.__Status.END_RECEIVED or self.__status == self.__Status.TIMED_OUT or self.__status == self.__Status.ERROR)
        
    def isTimedOut(self):
        return (self.__status == self.__Status.TIMED_OUT)
        
    def waitForEnd(self, procedure, endRegex, timeoutInSeconds):
        timeout = time.time() + timeoutInSeconds
        commandInfo = "command {} (port:{} sqn:{})".format(repr(self.commandAsAString),self.__serialComCanal.portId,self.__sequenceNumber)
        while (procedure is not None and not procedure.hasBeenAbortedByTimeout() or procedure is None) :
            commandDuration = "{:.1f} ms".format(1000*((timeoutInSeconds + time.time()) - timeout))
            commandInfo = "command {} (port:{} sqn:{}) -- duration:{}".format(repr(self.commandAsAString),self.__serialComCanal.portId,self.__sequenceNumber,commandDuration)
            if time.time() > timeout:
                self.__status = self.__Status.TIMED_OUT
                UATL_debug("command","{} => TIMED_OUT".format(commandInfo))
                break
            if self.reset.shouldBeDone.is_set():
                UATL_debug("reset","wait for reset request to be completed")
            if self.reset.hasBeenDetected.is_set():
                UATL_debug("reset","wait for reset to finish")
            while self.reset.shouldBeDone.is_set() or self.reset.hasBeenDetected.is_set():
                pass
            if self.__errorCounter > 0 or self.__resetCounter > 0:
                self.__status = self.__Status.ERROR
                UATL_debug("command","{} => ERROR".format(commandInfo))
                break
            if re.search(endRegex, self.response) is not None:
                break
        if self.__status != self.__Status.TIMED_OUT and self.__status != self.__Status.ERROR:
            self.__status = self.__Status.END_RECEIVED
            UATL_debug("command","{} => END_RECEIVED".format(commandInfo))
   
    def appendLine(self, line):
        self.response += "\n" + line
    
    def incrementResetCounter(self):
        self.__resetCounter += 1
        
    def incrementErrorCounter(self):
        self.__errorCounter += 1
    
    def getResetCounter(self):
        return self.__resetCounter
        
    def getErrorCounter(self):
        return self.__errorCounter
    
class UATL_Listener(Thread):
    """
     Object managing communication with a board, it can tell:
       - if board is ready to process a command
       - if a board is actually processing a command
       - if the current command response contains the specified regex
    """
        
    def __init__(self, portId, protocol, reset):
        self.__isActive = True
        Thread.__init__(self, daemon = True, name="Listener")
        self.__serialComCanal = UATL_SerialComCanal(portId,reset)
        self.__protocol = protocol
        self.__commandList = []
        self.__sequenceNumber = 0
        self.__mutex = Lock()
        self.reset = reset
        self.buf = bytearray()
        self.procedure = None
    
    def isAutoResetEnabled(self):
        return self.__protocol.isAutoResetEnabled()
        
    def getPort(self):
        """ For displaying port Id """
        return self.__serialComCanal.portId

    def reConnect(self):
        self.__serialComCanal.reOpen()
            
    def __addNewCommand(self,cmd):
        self.__mutex.acquire()
        self.__commandList.append(cmd)
        self.__mutex.release()
        UATL_debug("command","New command ({})".format(repr(self.__getCurrentCommand().commandAsAString)))
        
            
    def __getCurrentCommand(self):
        if self.__commandList != None:
            if len(self.__commandList) != 0:
                return self.__commandList[len(self.__commandList)-1]
            else:
                return None
        else:
            return None
            
    def __popCurrentCommand(self):
        self.__mutex.acquire()
        if self.__commandList != None:
            if len(self.__commandList) != 0:
                self.__commandList.pop()     
        self.__mutex.release()   
        
    def askForPrompt(self, procedure=None):
        """ Asking for prompt at the beginning of the test campaign to assure good board communication
            This step is not essential, but prevents desynchronization issues """   
        retries = 0
        try:
            while self.__isActive:
                while self.reset.hasBeenDetected.is_set() or self.reset.shouldBeDone.is_set():
                    pass
                UATL_debug("prompt","Asking for prompt to {}".format(self.getPort()))
                self.__addNewCommand(UATL_Command(procedure, 0,self.__protocol.getRequestToWaitForCommand(),self.__serialComCanal,self.__protocol, self.reset))
                try:
                    self.__getCurrentCommand().waitForEnd(procedure, self.__protocol.getPromptRegex(),2)
                    if (self.__getCurrentCommand().isTimedOut() or self.__getCurrentCommand().getResetCounter() > 0 or self.__getCurrentCommand().getErrorCounter() > 0):
                        raise
                    else:
                        UATL_debug("prompt","Port {} ready".format(self.getPort()))
                        self.__popCurrentCommand()
                        break
                except SystemExit as e:
                    os._exit(int(str(e)))
                except:
                    retries += 1
                    if(retries > 3):
                        UATL_error("Timeout while trying to read from port {}".format(self.getPort()))
                        self.reset.shouldBeDone.set()
                    else:
                        UATL_debug("prompt","retrying to ask for prompt to port {}".format(self.getPort()))
        
        except SystemExit as e:
            raise e

    def sendCommandAndListen(self, userCmd, procedure=None, show=True, quiet=False):
        if self.__getCurrentCommand() is not None and self.__getCurrentCommand().isFinished() or self.__getCurrentCommand() is None:
            if self.reset.hasBeenDetected.is_set():
                UATL_debug("reset","trying to send before flag hasBeenDetected has been cleared")
            if self.reset.shouldBeDone.is_set():
                UATL_debug("reset","trying to send before flag shouldBeDone has been cleared")
            while self.reset.hasBeenDetected.is_set() or self.reset.shouldBeDone.is_set():
                pass
            self.__sequenceNumber += 1
            if self.__commandList != None:
                if len(self.__commandList) == 0:
                    self.__popCurrentCommand()
            self.__addNewCommand(UATL_Command(procedure, self.__sequenceNumber, userCmd,self.__serialComCanal,self.__protocol,self.reset,show))
            if quiet != True:
                UATL_logCommandInfo("Command '{}' sent to {}.".format(userCmd,self.getPort()))
            else:
                UATL_debug("serialInput","Command '{}' sent to {}.".format(userCmd,self.getPort()))
                      
    def waitForEndOfCommand(self, timeoutInSeconds, procedure=None):
        self.__getCurrentCommand().waitForEnd(procedure, self.__protocol.getEndOfCommandRegex(),timeoutInSeconds)
            
    def getLastResponse(self):
        return str(self.__getCurrentCommand().response)
        
    def getCurrentCommandErrorCounter(self):
        return int(self.__getCurrentCommand().getErrorCounter())
        
    def getCurrentCommandResetCounter(self):
        return int(self.__getCurrentCommand().getResetCounter())

    def isCurrentCommandTimedout(self):
        return self.__getCurrentCommand().isTimedOut()
        
    def __readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            line = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return line
        while self.__isActive:
            i = max(1, min(2048, self.__serialComCanal.serial.in_waiting))
            data = self.__serialComCanal.serial.read(i)
            i = data.find(b"\n")
            if i >= 0:
                line = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return line
            else:
                self.buf.extend(data)
   
    def run(self):
        retries = 0
        try:
            while self.__isActive:
                line = None
                try:
                    line = self.__readline().decode(self.__protocol.getEncoding())
                except SystemExit as e:
                    os._exit(int(str(e)))
                except:
                    if not self.reset.shouldBeDone.is_set():
                        retries += 1
                        if(retries > 3):
                            UATL_error("Could not read on port {}".format(self.getPort()))
                            self.reset.shouldBeDone.set()
                            retries = 0
                        else:
                            UATL_logCommandInfo("Could not read serial port {}, trying again...".format(self.getPort()))
                            
                if line is not None:
                    if self.__protocol.hasCommandThrowedAnyError(line):
                        UATL_error("Error in log: ")
                        UATL_logCommandOutput(currentTime + self.getPort() + "@ " + line)
                        sys.exit(255)
                        # for command in self.__commandList:
                            # if command.isFinished() == False:
                                # command.incrementErrorCounter()
                        UATL_debug("reset","Error in log")
                    if self.__protocol.hasBoardReset(line):
                        self.reset.hasBeenDetected.set()
                        for command in self.__commandList:
                            if command.isFinished() == False:
                                command.incrementResetCounter()  
                        UATL_debug("reset","Board on port {} has initiated a reset".format(self.getPort()))
                    if self.__getCurrentCommand() is not None and self.__getCurrentCommand().isPending():
                        line = line.strip("\r\n ")
                        self.__getCurrentCommand().appendLine(line)
                        if line != '':
                            currentTime =  "[{:02}\"{:02}\'{:03}] ".format(datetime.now().minute,datetime.now().second,int(datetime.now().microsecond/1000))
                            if self.__getCurrentCommand().commandAsAString != '\n'and line != '\n' and self.__getCurrentCommand().shallBeShawn():
                                UATL_logCommandOutput(currentTime + self.getPort() + "@ " + line)
                            else:
                                UATL_debug("serialOutput","*     " + currentTime + self.getPort() + "@ " + line)
        except SystemExit as e:
            os._exit(int(str(e)))
    
    def __del__(self):
        self.__isActive = False
        UATL_log("Killing listener")

class UATL_TestSuite:
    def __init__(self, testSuitePath):
        self.procedures = []
        self.path = testSuitePath
        self.__loadConfigFile(testSuitePath)
        self.__pConfigFile = None
  
    def __del__(self): 
        if self.__pConfigFile != None:
            self.__pConfigFile.close() 
    
    def __loadConfigFile(self,path):
        UATL_log("Loading testsuite")
        try:
            self.__pConfigFile = open(path, 'r') 
            for line in self.__pConfigFile:
                if '#' in line :
                    pass
                elif re.match('^[\s]+$',line):
                    pass
                else:
                    testConfig = shlex.split(line)
                    if len(testConfig) != 2:
                        UATL_error("Error in format ({})".format(line))
                        sys.exit(9)
                    else:
                        try:
                            self.procedures.append(globals()[testConfig[0]](int(testConfig[1])))
                        except KeyError as err:
                            UATL_error("Testcase not found ({}) ".format(testConfig[0]))
                            sys.exit(9)
                        except TypeError as err:
                            UATL_error("Unexpected error while creating procedure : " + str(err))
                            sys.exit(9)
                        except SystemExit as e:
                            os._exit(int(str(e)))
                        except :
                            UATL_error("Unexpected error while creating procedure : " + sys.exc_info()[0])
                            sys.exit(9)
            self.__pConfigFile.close()
            
        except OSError as err:
            UATL_error("OS error: {0}".format(err))    
            sys.exit(9)
            return
        except IOError as err:
            UATL_error("IO error: {0}".format(err))
            sys.exit(9)
            return
        except ValueError as err:
            LDV_error("Testsuite is not well formatted. Please mind the quotes.")
            sys.exit(9)
            return
        except SystemExit as e:
            os._exit(int(str(e)))
        except:
            UATL_error("Unexpected error in loadConfigFile"+ sys.exc_info()[0])
            sys.exit(9)
            return
        
        UATL_log("Testsuite loaded")
        if len(self.procedures) == 0:
            UATL_error("Testsuite is empty! please check the testsuite configuration file Testsuite.cfg")
            sys.exit(9)
            return
            
class UATL_Procedure(metaclass = ABCMeta):
    """
    manage testcase definition and result management
    """        

    @unique
    class ImplementationStatus(AutoEnum):
        CANCELLED = auto()         # TODO
        TO_BE_IMPLEMENTED = auto() # TODO
        READY_TO_BE_RUN = auto()   # TODO
        NEED_SPEC_INFO = auto()    # TODO
        FOR_TEST_ENV_ONLY = auto() # TODO
        FOR_INFO_ONLY = auto()     # TODO
        
    def __init__(self, timeout):
        self.__timeout = timeout #in minutes
        self.failure_message = None #TODO : fill failure_message + could failure_message be private? check
        self.log = "" #TODO : use log
        self._boardList = []
        self._isActive = True
        self.__hasBeenAbortedByTimeout = False
        self.__startTime = None
        self.__endTime = None
        
        
    @abstractmethod
    def getVersion(self):
        UATL_error("Procedure {} must override getVersion(), please check your implementation of this testcase in TestCasesList.py".format(self.__class__.__name__))    
        sys.exit(255)
        
    @abstractmethod
    def getImplementationStatus(self):
        UATL_error("Procedure {} must override getImplementationStatus() by returning one UATL_Procedure.ImplementationStatus.<VALUE>, please check your implementation of this testcase in TestCasesList.py".format(self.__class__.__name__))    
        sys.exit(255)
        
    @abstractmethod
    def getObjective(self):
        UATL_error("Procedure {} must override getObjective(), please check your implementation of this testcase in TestCasesList.py".format(self.__class__.__name__))    
        sys.exit(255)
        
    @abstractmethod
    def getExpectedResult(self):
        UATL_error("Procedure {} must override getExpectedResult(), please check your implementation of this testcase in TestCasesList.py".format(self.__class__.__name__))    
        sys.exit(255)

    @abstractmethod
    def __callCliCommandsAndDoChecks__(self):
        UATL_error("Procedure {} must override __callCliCommandsAndDoChecks__(), please check your implementation of this testcase in TestCasesList.py".format(self.__class__.__name__))    
        sys.exit(10)
    
    @final
    def __resetBoard(self, boardId):
        self._boardList[boardId].resetFromShell()

    @final
    def sendCommandAndListen(self, boardId, command, show=True, quiet=False):
        self.currentCommandName = command
        return self._boardList[boardId].listener.sendCommandAndListen(command, self, show, quiet)

    @final
    def waitForEndOfCommand(self, boardId, timeoutInSeconds):
        self._boardList[boardId].listener.waitForEndOfCommand(timeoutInSeconds, self)
        self.log += """################### Board Id '{}', Command name '{}' ###################
        {}
        ###########################################################""".format(boardId,self.currentCommandName,self._boardList[boardId].listener.getLastResponse())

    @final
    def numberOfRegexMatchesInLog(self, boardId, regex):
        UATL_debug("regex","regex:" + str(regex))
        UATL_debug("regex","getLastResponse:" + str(self._boardList[boardId].listener.getLastResponse()))
        UATL_debug("regex","len:" + str(len(re.findall(regex, self._boardList[boardId].listener.getLastResponse())))) 
        return len(re.findall(regex, self._boardList[boardId].listener.getLastResponse()))

    @final
    def sendQuickCommand(self, boardId, userCmd, quiet=False):
        self.sendCommandAndListen(boardId, userCmd, False, quiet)
        self.waitForEndOfCommand(boardId, 4)
        
    @final
    def __waitForEnd(self):    
        try:
            self.__callCliCommandsAndDoChecks__()
        except IndexError as err:
            UATL_error( "Error in procedure '{}', you ask for a board that is not available ".format(self.__class__.__name__))
            sys.exit(255)
        except (NameError, TypeError, AttributeError) as err:
            UATL_error( "Error in procedure '{}' syntax: {} ".format(self.__class__.__name__,err))
            sys.exit(255)
        except SystemExit as e:
            os._exit(int(str(e)))
        except :
            UATL_error( "Error in procedure '{}' syntax: {} ".format(self.__class__.__name__,sys.exc_info()[0]))
            sys.exit(255)

    @final
    def run(self):
        self._isActive = True
        
        UATL_log("")
        UATL_log("")
        UATL_log("**" + '{:*^100}'.format('') + "**")
        UATL_log("**" + '{: ^100}'.format('Procedure : ' + str(self.__class__.__name__) + " begins") + "**")
        UATL_log("**" + '{:*^100}'.format('') + "**")
            
        if len(self._boardList) != self.getBoardNumber():
            UATL_error("board number is not consistent with board list, unexpected error") 
            sys.exit(255)
            
        for board in self._boardList:
            board.listener.askForPrompt()
            UATL_log("**" + '{: ^100}'.format("Board #{} : port {}".format(board.boardId,board.listener.getPort()))+ "**")

        UATL_log("**" + '{:*^100}'.format('') + "**")
        UATL_log("*" + '{: ^102}'.format('') + "*")
        
        self.__startTime = time.time()
        
        if self.getImplementationStatus() != self.ImplementationStatus.CANCELLED and self.getImplementationStatus() != self.ImplementationStatus.TO_BE_IMPLEMENTED:
            self.__setup__()
            procedureThread = Thread(target=self.__waitForEnd, daemon=True, name="Procedure")
            procedureThread.start()
            procedureThread.join(timeout = self.__timeout * 60)
        
            self._isActive = False
            
            if procedureThread.is_alive():
                procedureThread.join()
                self.__hasBeenAbortedByTimeout = True
                
            self.__teardown__()
        
            for board in self._boardList:
                if self.__hasBeenAbortedByTimeout:
                    self.waitForEndOfCommand(board.boardId,30)
                board.listener.askForPrompt()# to check if board has not frozen
            
        self.__endTime = time.time()
       
        self.__displayResult()
        
    @final   
    def __displayResult(self):
        UATL_log("*" + '{: ^102}'.format('') + "*")
        UATL_log("**" + '{:*^100}'.format('') + "**")
        UATL_log("**" + self.__getResult__(100) + "**")
        UATL_log("**" + '{:*^100}'.format('') + "**")
        UATL_log("")
        UATL_log("")
        
    @final   
    def isActive(self):
        return (self._isActive == True)
    
    @final   
    def stop(self):
        self._isActive = False
        
    @final   
    def getStatus(self):
        status = ""
        if self.getImplementationStatus() == self.ImplementationStatus.CANCELLED or self.getImplementationStatus() == self.ImplementationStatus.TO_BE_IMPLEMENTED or self.getImplementationStatus() == self.ImplementationStatus.FOR_INFO_ONLY:
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.WHITE + "N/A" + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 
        else:
            status = self.__getStatus__() 
        return status
        
    @abstractmethod   
    def __getStatus__(self):
        UATL_error("Procedure model must override __getStatus__(), please check your model ".format(self.__class__.__name__))    
        sys.exit(255)

    @abstractmethod   
    def __getResult__(self):
        UATL_error("Procedure model must override __getResult__(), please check your model ".format(self.__class__.__name__))    
        sys.exit(255)

    @abstractmethod   
    def __setup__(self):
        UATL_error("Procedure model must override __setup__(), please check your model ".format(self.__class__.__name__))    
        sys.exit(255)
        
    @abstractmethod   
    def __teardown__(self):
        UATL_error("Procedure model must override __teardown__(), please check your model ".format(self.__class__.__name__))    
        sys.exit(255)
        
    @abstractmethod   
    def getJunitProcedureFormat(self):
        UATL_error("Procedure model must override getJunitProcedureFormat(), please check your model ".format(self.__class__.__name__))    
        sys.exit(255)

    @final     
    def printJUnitResults(self,testSuite):

        junitTestSuite = JU_TS(testSuite.path,[self.getJunitProcedureFormat()])

        print(JU_TS.to_xml_string([junitTestSuite]))
        
    @final   
    def assignBoard(self,testBench):
        boardCounter = 0
        for board in testBench.boardList:
            try:
                self._boardList.append(board)
                boardCounter = boardCounter + 1
                if boardCounter >= self.getBoardNumber(): 
                    break
            except SystemExit as e:
                os._exit(int(str(e)))
            except:
                UATL_error("No board found in board list")
                sys.exit(2)
      
    @final
    def hasBeenAbortedByTimeout(self):
        return self.__hasBeenAbortedByTimeout
        
    @final
    def hasBeenAbortedAsString(self):
        return "yes" if self.hasBeenAbortedByTimeout() else "no"
        
    @final
    def getIntFrom(self,regex,boardId):
        searchResult = re.search(regex,self._boardList[boardId].listener.getLastResponse())
        if searchResult != None:
            return int(searchResult.group(1))
        else:
            UATL_error("Regex '{}' not found".format(regex))
            return 1#avoid /0 divisions
        
    @final
    def getTimeoutInS(self):
        return self.__timeout * 60

    @final
    def getTimeoutAsString(self):
        return UATL_getTimeAsString(self.getTimeoutInS())
        
    @final
    def getDurationInS(self):
        return float(self.__endTime - self.__startTime)
        
    @final
    def getDurationAsString(self):

        durationAsString = UATL_getTimeAsString(self.getDurationInS())
            
        if self.__hasBeenAbortedByTimeout:
            durationAsString = UATL_ShellPolice.Fore.RED + UATL_ShellPolice.Back.RESET + "{}".format(durationAsString) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        else:
            durationAsString =  UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + durationAsString + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
            
        return durationAsString
        
        
    #@abstract
    def getErrorCounterAsString(self):
        #TODO: the following code only takes into account the last command. Make a proper counter for this
        # counter = ""
        # errorCounter = 0
        # for board in self._boardList:
            # errorCounter += board.listener.getCurrentCommandErrorCounter()
        # if errorCounter > 0:
            # counter = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.RED + "{}".format(errorCounter)  + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 
        # else:
            # counter = UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "{}".format(errorCounter) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        # return counter
        return UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "TBI" + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
            
    #@abstract
    def getResetCounterAsString(self):
        #TODO: the following code only takes into account the last command. Make a proper counter for this
        # counter = ""
        # errorCounter = 0
        # for board in self._boardList:
            # errorCounter += board.listener.getCurrentCommandErrorCounter()
        # if resetCounter > 0:
            # counter = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.RED + "{}".format(resetCounter)  + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 
        # else:
            # counter = UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "{}".format(resetCounter) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        # return counter
        return UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "TBI" + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 

    #@abstract
    def getTimeoutCounterAsString(self):
        #TODO: the following code only takes into account the last command. Make a proper counter for this
        # counter = ""
        # timeoutCounter = 0
        # for board in self._boardList:
            # timeoutCounter += board.listener.isCurrentCommandTimedout()
        # if timeoutCounter > 0:
            # return UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW + "{}".format(timeoutCounter)  + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 
        # else:
            # return UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "{}".format(timeoutCounter) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        # return counter
        return UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "TBI" + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        
class UATL_TestCase(UATL_Procedure):
    """
    manage testcase definition and result management
    """    
    
    @unique
    class Status(AutoEnum): #TODO put Status in private
        NO_CHECK_DONE = auto() # no check with method "checkThat" has been done, no result can be determined though
        PASSED = auto()        # all checks passed
        FAILED = auto()        # al least one check failed
        TIMED_OUT = auto()     # at least one command timedout
        
    def __init__(self, timeout):
        super(UATL_TestCase, self).__init__(timeout)
        self.__status = self.Status(self.Status.NO_CHECK_DONE)
        
    @final 
    def checkThat(self, description, condition):
        
        try:
            dummy = condition
        except SystemExit as e:
            os._exit(int(str(e)))
        except:
            condition = false
            
        checkStatus = UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "Failed"
        
        if self.__status == self.Status.TIMED_OUT:
            checkStatus = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.MAGENTA + "Skipped"
        else:
            if condition == False :
                checkStatus = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.RED + "Failed"
                self.__status = self.Status.FAILED
            else:
                checkStatus = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.GREEN + "Passed"
                if self.__status != self.Status.FAILED:
                    self.__status = self.Status.PASSED
        
            for board in self._boardList:
                if board.listener.isCurrentCommandTimedout():
                    checkStatus = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW + "Timed out"
                    self.__status = self.Status.TIMED_OUT
                    
        UATL_logCommandInfo("--> Expects '{}' : {}{}".format(description,checkStatus,UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET)) 
        
        
    @final
    def __getStatus__(self):
        status = ""
        if (self.__status == self.Status.PASSED and not self.hasBeenAbortedByTimeout()):
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.GREEN + "PASSED"
        elif (self.__status == self.Status.FAILED and not self.hasBeenAbortedByTimeout()):
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.RED + "FAILED"
        elif (self.__status == self.Status.TIMED_OUT or self.hasBeenAbortedByTimeout()):
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW + "TIMED OUT"
        else:
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.WHITE + "NO CHECK DONE" 
        return status + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 
        
    @final
    def getJunitProcedureFormat(self):
        junitTestCase = JU_TC(
                name = "{}".format(self.__class__.__name__), 
                category = "{}".format(super().__class__.__name__),
                #classname = "{}".format(self.getBoardNumber()),
                log = "{}".format(self.log),
                elapsed_sec = self.getDurationInS()
                )
            
        if self.__status != self.Status.PASSED or self.hasBeenAbortedByTimeout():
            junitTestCase.add_failure_info(self.failure_message) # TODO: fill failure_message
        
        return junitTestCase
        
    @final   
    def __setup__(self):
        for boardId in range(0,len(self._boardList)):
            #self.__resetBoard(boardId)
            self.sendQuickCommand(boardId,"TFW_Command__ResetTestEnvParametersToDefaultValues")#reset param to default value
        
    @final   
    def __teardown__(self):
        pass
                
    @final   
    def __getResult__(self,windowLength):
        return '{: ^{formattedLength}}'.format("Result of testcase " + str(self.__class__.__name__) + " is : " + str(self.getStatus()),formattedLength=UATL_ShellPolice.getFormattedLength(windowLength))

class UATL_Characterization(UATL_Procedure):
    """
    manage characterization procedures definition and result management
    """   
    @unique
    class Status(AutoEnum):#TODO put Status in private
        NOT_STARTED_YET = auto()      # procedure has not started yet (no stopIf has been performed)
        VALUE_NOT_FOUND_YET = auto()  # doing, no value has been found yet (condition always true)
        VALUE_FOUND = auto()          # value has been found (last command failed)
        FAILED_AT_FIRST = auto()      # first command failed
        ERROR = auto()                # error or reset occured during charactezization!
        
    def __init__(self, timeout):
        super(UATL_Characterization, self).__init__(timeout)
        self.__status = self.Status(self.Status.NOT_STARTED_YET)
        self.__parameterName = None
        self.__parameterValue = None
        self.__firstCommandFailed = True
        
    @final
    def stopIf(self, description, stopCondition, parameterName, parameterValue):
        for board in self._boardList:
            if (board.listener.getCurrentCommandErrorCounter() + board.listener.getCurrentCommandResetCounter() > 0):
                UATL_log("Abort current procedure because of error or reset")
                self.__status = self.Status.ERROR
                break
        
        if self.__parameterName == None or parameterName != self.__parameterName:
            self.__status = self.Status.VALUE_NOT_FOUND_YET
            self.__parameterName = str(parameterName)
          
            
        for board in self._boardList:
            if board.listener.isCurrentCommandTimedout():
                self.__status = self.Status.VALUE_FOUND
        
        if stopCondition:
            if self.__firstCommandFailed:
                self.__status = self.Status.FAILED_AT_FIRST
            else:
                self.__status = self.Status.VALUE_FOUND
        else:
            self.__parameterValue = float(parameterValue)
            self.__firstCommandFailed = False
            
        return True if self.__status == self.Status.VALUE_FOUND else False
        
    @final
    def __getStatus__(self):
        status = None
        if (self.__status == self.Status.VALUE_FOUND):
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.GREEN + "OK:" + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + " {}".format(self.__parameterValue)
        elif (self.__status == self.Status.VALUE_NOT_FOUND_YET and not self.hasBeenAbortedByTimeout()):
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW + "NOT FOUND" + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        elif (self.__status == self.Status.FAILED_AT_FIRST):
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.RED + "FAILED AT FIRST" + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        else:
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.WHITE + "NOT STARTED YET" + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 
        return str(status)
        
    @final
    def getJunitProcedureFormat(self):
        junitTestCase = JU_TC(
                name = "{}".format(self.__class__.__name__), 
                category = "{}".format(super().__class__.__name__),
                #classname = "{}".format(self.getBoardNumber()),
                log = "{}".format(self.log),
                elapsed_sec = self.getDurationInS()
                )
            
        if self.__status != self.Status.VALUE_FOUND or self.hasBeenAbortedByTimeout():
            junitTestCase.add_failure_info(self.failure_message)# TODO: fill failure_message
        
        # if self.__status == self.Status.SKIPPED:
        #       junitTestCase.add_skipped_info(self.skipped_message)
            
        return junitTestCase
        
    @final   
    def __setup__(self):
        for boardId in range(0,len(self._boardList)):
            #self.__resetBoard(boardId)
            self.sendQuickCommand(boardId,"TFW_Command__ResetTestEnvParametersToDefaultValues")#reset param to default value
                    
    @final   
    def __teardown__(self):
        for boardId in range(0,len(self._boardList)):
            self.waitForEndOfCommand(boardId,60)
         
    @final   
    def __getResult__(self,windowLength):
        return '{: ^{formattedLength}}'.format("Result of characterization " + str(self.__class__.__name__) + " is : " + str(self.getStatus()),formattedLength=UATL_ShellPolice.getFormattedLength(windowLength))

class UATL_Endurance(UATL_Procedure):
    """
    manage endurance procedures definition and result management
    """       
    def __init__(self, timeout):
        super(UATL_Endurance, self).__init__( timeout)
        self.__passedCounter = 0
        self.__failedCounter = 0
        self.__timeoutCounter = 0
        self.__errorCounter = 0
        self.__resetCounter = 0
        
    @final 
    def parallelLoopStep(self, boardId, description, condition):# TODO: show the description only if it failes           
        self.__passedCounter += 1 if condition is True else 0
        self.__failedCounter += 1 if condition is False else 0
        self.__timeoutCounter += 1 if self._boardList[boardId].listener.isCurrentCommandTimedout() else 0
        self.__errorCounter += self._boardList[boardId].listener.getCurrentCommandErrorCounter()
        self.__resetCounter += self._boardList[boardId].listener.getCurrentCommandResetCounter()
        
        if not condition or self._boardList[boardId].listener.isCurrentCommandTimedout() or (self._boardList[boardId].listener.getCurrentCommandErrorCounter() > 0)  or (self._boardList[boardId].listener.getCurrentCommandResetCounter() > 0):
            UATL_log("*  Description '{}' boardId [{}] passed:{} failed:{} timeout:{} error:{} reset:{}".format(description,boardId,self.__passedCounter,self.__failedCounter,self.__timeoutCounter,self.__errorCounter,self.__resetCounter))
        else:
            UATL_debug("endurance","Description '{}' boardId [{}] passed:{} failed:{} timeout:{} error:{} reset:{}".format(description,boardId,self.__passedCounter,self.__failedCounter,self.__timeoutCounter,self.__errorCounter,self.__resetCounter))
        
        if (self.__errorCounter + self.__resetCounter > 0):
            UATL_log("Abort current procedure because of error or reset")
            self.stop()

    @final 
    def serialLoopStep(self, description, condition):# TODO: show the description only if it failes   
        """ can only be called once a loop iteration and without any parallelLoopStep called """
        isNotInError = True
        if condition is True:
            UATL_debug("endurance","serialLoopStep PASSED")
        else:
            UATL_debug("endurance","serialLoopStep FAILED")
            
        self.__passedCounter += 1 if condition is True else 0
        self.__failedCounter += 1 if condition is False else 0
        for board in self._boardList:
            self.__timeoutCounter += 1 if board.listener.isCurrentCommandTimedout() else 0
            self.__errorCounter += board.listener.getCurrentCommandErrorCounter()
            self.__resetCounter += board.listener.getCurrentCommandResetCounter()
            isNotInError = not condition or board.listener.isCurrentCommandTimedout() or (board.listener.getCurrentCommandErrorCounter() > 0) or (board.listener.getCurrentCommandResetCounter() > 0)
            
        if isNotInError:
            UATL_log("*  Description '{}' passed:{} failed:{} timeout:{} error:{} reset:{}".format(description,self.__passedCounter,self.__failedCounter,self.__timeoutCounter,self.__errorCounter,self.__resetCounter))
        else:
            UATL_debug("endurance","Description '{}' passed:{} failed:{} timeout:{} error:{} reset:{}".format(description,self.__passedCounter,self.__failedCounter,self.__timeoutCounter,self.__errorCounter,self.__resetCounter))
        
        #self.__serialLoopStepHasBeenCalled = True
        
        if (self.__errorCounter + self.__resetCounter > 0):
            UATL_log("Abort current procedure because of error or reset")
            self.stop()

    @final
    def __getStatus__(self):
        status = ""
        ratio = "{}/{}".format(self.__passedCounter,self.__passedCounter + self.__failedCounter)
        if self.__resetCounter > 0 or self.__errorCounter > 0 :
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.RED + "{}".format(ratio) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 
        elif self.__timeoutCounter > 0:
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW + "{}".format(ratio) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        else:
            status = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.GREEN + "{}".format(ratio) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET     
        return status
        
    @final
    def getErrorCounterAsString(self):
        counter = ""
        if self.__errorCounter > 0:
            counter = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.RED + "{}".format(self.__errorCounter)  + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 
        else:
            counter = UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "{}".format(self.__errorCounter) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        return counter
        
    @final
    def getResetCounterAsString(self):
        counter = ""
        if self.__resetCounter > 0:
            counter = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.RED + "{}".format(self.__resetCounter)  + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 
        else:
            counter = UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "{}".format(self.__resetCounter) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        return counter
        
    @final
    def getTimeoutCounterAsString(self):
        counter = ""
        if self.__timeoutCounter > 0:
            counter = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW + "{}".format(self.__timeoutCounter)  + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET 
        else:
            counter = UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET + "{}".format(self.__timeoutCounter) + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET
        return counter

    @final
    def getJunitProcedureFormat(self):
        junitTestCase = JU_TC(
                name = "{}".format(self.__class__.__name__), 
                category = "{}".format(super().__class__.__name__),
                #classname = "{}".format(self.getBoardNumber()),
                log = "{}".format(self.log),
                elapsed_sec = self.getDurationInS()
                )
            
        if self.__errorCounter != 0 or self.__timeoutCounter != 0 or self.__resetCounter != 0:
            junitTestCase.add_failure_info(self.failure_message)# TODO: fill failure_message
        
        return junitTestCase
        
    @final   
    def __setup__(self):
        for boardId in range(0,len(self._boardList)):
            #self.__resetBoard(boardId)
            self.sendQuickCommand(boardId,"TFW_Command__ResetTestEnvParametersToDefaultValues")#reset param to default value
        UATL_logCommandInfo("Endurance test in progress, please wait...")
        
    @final   
    def __teardown__(self):
        pass
         
    @final   
    def __getResult__(self,windowLength):
        return '{: ^{formattedLength}}'.format("Result of endurance test " + str(self.__class__.__name__) + " is : " + str(self.getStatus()),formattedLength=UATL_ShellPolice.getFormattedLength(windowLength))
              
class UATL_TestCampaign:
    """
    manage test campaign run
    """
    def __init__(self, testSuite, testBench):
        self.testSuite = testSuite
        self.testBench = testBench
        UATL_log("{}".format(datetime.now().strftime("Starting campaign %d/%m/%Y %H:%M:%S")))
    
    def __del__(self):
        UATL_log("{}".format(datetime.now().strftime("End of campaign %d/%m/%Y %H:%M:%S")))
        
    def run(self):
        self.testBench.synchronise()
        for procedure in self.testSuite.procedures:
            procedure.assignBoard(self.testBench)
            procedure.run()
                        
    def displayResult(self):      
        UATL_log("All tests were done")
        UATL_log("")

        nameLength = 62
        versionLength = 7
        implementationLength = 17
        boardLength = 9
        timeoutLength = 9
        resultLength = 15
        durationLength = 8
        abortedLength = 5
        resetLength = 3
        timedoutLength = 3
        totalLength = nameLength + versionLength + implementationLength + boardLength + timeoutLength + resultLength + durationLength + abortedLength + resetLength + timedoutLength + 9
        
        nameField = '{: ^{nameLength}}'.format("Procedure name",nameLength=nameLength)
        versionField = '{: ^{versionLength}}'.format("Version",versionLength=versionLength)
        implementationField = '{: ^{implementationLength}}'.format("Implem. status",implementationLength=implementationLength)
        boardField = '{: ^{boardLength}}'.format("Board(s)",boardLength=boardLength)
        timeoutField = '{: ^{timeoutLength}}'.format("Timeout",timeoutLength=timeoutLength)
        resultField = '{: ^{resultLength}}'.format("Result",resultLength=resultLength)
        durationField = '{: ^{durationLength}}'.format("Duration",durationLength=durationLength)
        abortedField = '{: ^{abortedLength}}'.format("Abort",abortedLength=abortedLength)
        resetField = '{: ^{resetLength}}'.format("RST",resetLength=resetLength)
        timedoutField = '{: ^{timedoutLength}}'.format("CTO",timedoutLength=timedoutLength)#CTO = command time out


        UATL_log('╔' + '{:{d}^{l}}'.format('',d='═',l=nameLength) + '╤' + '{:{d}^{l}}'.format('',d='═',l=versionLength) + '╤' + '{:{d}^{l}}'.format('',d='═',l=implementationLength) + '╤' + '{:{d}^{l}}'.format('',d='═',l=boardLength) + '╤' + '{:{d}^{l}}'.format('',d='═',l=timeoutLength) + '╤' + '{:{d}^{l}}'.format('',d='═',l=resultLength) + '╤' + '{:{d}^{l}}'.format('',d='═',l=durationLength) + '╤' + '{:{d}^{l}}'.format('',d='═',l=abortedLength) + '╤' + '{:{d}^{l}}'.format('',d='═',l=resetLength) + '╤' + '{:{d}^{l}}'.format('',d='═',l=timedoutLength) + '╗')
        UATL_log('║' + nameField + '│' + versionField + '│' + implementationField + '│' + boardField + '│' + timeoutField + '│' + resultField + '│' + durationField + '│' + abortedField + '│' + resetField + '│' + timedoutField + '║')
        UATL_log('╠' + '{:{d}^{l}}'.format('',d='═',l=nameLength) + '╪' + '{:{d}^{l}}'.format('',d='═',l=versionLength) + '╪' + '{:{d}^{l}}'.format('',d='═',l=implementationLength) + '╪' + '{:{d}^{l}}'.format('',d='═',l=boardLength) + '╪' + '{:{d}^{l}}'.format('',d='═',l=timeoutLength) + '╪' + '{:{d}^{l}}'.format('',d='═',l=resultLength) + '╪' + '{:{d}^{l}}'.format('',d='═',l=durationLength) + '╪' + '{:{d}^{l}}'.format('',d='═',l=abortedLength) + '╪' + '{:{d}^{l}}'.format('',d='═',l=resetLength) + '╪' + '{:{d}^{l}}'.format('',d='═',l=timedoutLength) + '╣')
 
        for procedure in self.testSuite.procedures:
            nameField = '{: <{nameLength}}'.format(str(procedure.__class__.__name__),nameLength=nameLength)
            versionField = '{: ^{versionLength}}'.format(str(procedure.getVersion()),versionLength=versionLength)
            implementationField = '{: ^{implementationLength}}'.format(procedure.getImplementationStatus().name,implementationLength=implementationLength)
            boardField = '{: ^{boardLength}}'.format(str(procedure.getBoardNumber()),boardLength=boardLength)
            timeoutField = '{: ^{timeoutLength}}'.format(procedure.getTimeoutAsString(),timeoutLength=timeoutLength)
            resultField = '{: ^{resultLength}}'.format(str(procedure.getStatus()),resultLength=UATL_ShellPolice.getFormattedLength(resultLength))
            durationField = '{: ^{durationLength}}'.format(procedure.getDurationAsString(),durationLength=UATL_ShellPolice.getFormattedLength(durationLength))
            abortedField = '{: ^{abortedLength}}'.format(procedure.hasBeenAbortedAsString(),abortedLength=abortedLength)
            resetField = '{: ^{resetLength}}'.format(procedure.getResetCounterAsString(),resetLength=UATL_ShellPolice.getFormattedLength(resetLength))
            timedoutField = '{: ^{timedoutLength}}'.format(procedure.getTimeoutCounterAsString(),timedoutLength=UATL_ShellPolice.getFormattedLength(timedoutLength))
            UATL_log('║' + nameField + '│' + versionField + '│' + implementationField + '│' + boardField + '│' + timeoutField + '│' + resultField + '│' + durationField + '│' + abortedField + '│' + resetField + '│' + timedoutField + '║')
            UATL_log('╟' + '{:{d}^{l}}'.format('',d='─',l=nameLength) + '┼' + '{:{d}^{l}}'.format('',d='─',l=versionLength) + '┼' + '{:{d}^{l}}'.format('',d='─',l=implementationLength) + '┼' + '{:{d}^{l}}'.format('',d='─',l=boardLength) + '┼' + '{:{d}^{l}}'.format('',d='─',l=timeoutLength) + '┼' + '{:{d}^{l}}'.format('',d='─',l=resultLength) + '┼' + '{:{d}^{l}}'.format('',d='─',l=durationLength) + '┼' + '{:{d}^{l}}'.format('',d='─',l=abortedLength) + '┼' + '{:{d}^{l}}'.format('',d='─',l=resetLength) + '┼' + '{:{d}^{l}}'.format('',d='─',l=timedoutLength) + '╢')
            
        UATL_log('╚' + '{:{d}^{l}}'.format('',d='═',l=nameLength) + '╧' + '{:{d}^{l}}'.format('',d='═',l=versionLength) + '╧' + '{:{d}^{l}}'.format('',d='═',l=implementationLength) + '╧' + '{:{d}^{l}}'.format('',d='═',l=boardLength) + '╧' + '{:{d}^{l}}'.format('',d='═',l=timeoutLength) + '╧' + '{:{d}^{l}}'.format('',d='═',l=resultLength) + '╧' + '{:{d}^{l}}'.format('',d='═',l=durationLength) + '╧' + '{:{d}^{l}}'.format('',d='═',l=abortedLength) + '╧' + '{:{d}^{l}}'.format('',d='═',l=resetLength) + '╧' + '{:{d}^{l}}'.format('',d='═',l=timedoutLength) + '╝')
        UATL_log("")
    

    def writeTestReportAsCsv(self, csvTestReportFile):
        
        report = "Procedure name" + ';' + "Version" + ';' + "Implementation status" + ';' + "Board number" + ';' + "Objective(s)" + ';' + "Expected result" + ';' + "Duration" + ';' + "Result"  + ';' + "Log" + ';' + "Has been aborted?"  + ';' + "Reset counter"  + ';' + "Has timed out?"  + '\n'
        
        for procedure in self.testSuite.procedures:
            nameField = '{}'.format(procedure.__class__.__name__)
            versionField = '{}'.format(procedure.getVersion())
            implementationField = '{}'.format(procedure.getImplementationStatus().name)
            boardField = '{}'.format(procedure.getBoardNumber())
            objectiveField = '{}'.format(procedure.getObjective())
            expectedField = '{}'.format(procedure.getExpectedResult())
            durationField = '{}'.format(UATL_ShellPolice.stripAnsi(procedure.getDurationAsString()))
            resultField = '{}'.format(UATL_ShellPolice.stripAnsi(procedure.getStatus()))
            logField = '{}'.format(procedure.log)
            abortedField = '{}'.format(UATL_ShellPolice.stripAnsi(procedure.hasBeenAbortedAsString()))
            resetField = '{}'.format(UATL_ShellPolice.stripAnsi(procedure.getResetCounterAsString()))
            timedoutField = '{}'.format(UATL_ShellPolice.stripAnsi(procedure.getTimeoutCounterAsString()))
            report += '"' + nameField + '";"' + versionField + '";"' + implementationField + '";"' + boardField + '";"' + objectiveField + '";"' + expectedField + '";"' + durationField + '";"' + resultField + '";"' + logField + '";"' + abortedField + '";"' + resetField + '";"' + timedoutField + '"\n'
            
        try: 
            UATL_log("writting validation report in file : " + csvTestReportFile.name)
            csvTestReportFile.write(report)
            UATL_log("CSV report written")
        except SystemExit as e:
            os._exit(int(str(e)))
        except:
            UATL_log("CSV report could not be written")
            UATL_log("")
            print("")
            print(report)
        
    def writeJUnitResults(self,junitReportFile):
        
        junitProcedures = []
           
        for procedure in self.testSuite.procedures:
            junitProcedures.append(procedure.getJunitProcedureFormat()) 
            
        junitTestSuite = JU_TS(self.testSuite.path,junitProcedures)
        
        report = JU_TS.to_xml_string([junitTestSuite])
        
        try:
            UATL_log("writting validation report in file : " + junitReportFile.name) 
            junitReportFile.write(report)
            UATL_log("Junit report written")
        except SystemExit as e:
            os._exit(int(str(e)))
        except:
            UATL_log("Junit report could not be written")
            UATL_log("")
            print("")
            print(report)
            
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
        active = False
    elif "reset" in str(region):
        active = False
    elif "command" in str(region):
        active = False
    elif "serialInput" in str(region):
        active = False
    elif "serialOutput" in str(region):
        active = True
    elif "endurance" in str(region):
        active = True
    elif "regex" in str(region):
        active = False
    elif "embeddedStress" in str(region):
        active = False
    elif "synchro" in str(region):
        active = False
    elif "optim" in str(region):
        active = False
    else:
        active = False
        UATL_error("log region unknown '{}'".format(region))
        sys.exit(255)
        
    if active:
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
 
"""
-------------------------------------------------------------------------------------------------------------------------------------
AFTER THIS LINE, the following code is UnitTests which are example for filling test cases in TestCasesList.py
BUT, this is strongly dependant to BLE binaries, so it will not remain in the final release of UATL
TODO: remove from final release of UATL
-------------------------------------------------------------------------------------------------------------------------------------
"""
#############################################################
##                           UATL                          ##
#############################################################
class UATL_TC__Simplest(UATL_TestCase):
    def getVersion(self):
        return "v1.0"
                
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic UATL TC feature: sendCommandAndListen, waitForEndOfCommand, checkThat, and characterize the minimum time for a testcase (python overhead)"
        
    def getExpectedResult(self):
        return "this test shall wait for end of command and return 'passed'  for the command, PASSED for the procedure, and duration shall be quite short (less than 500ms)"
        
    def getBoardNumber(self):
        return 1
        
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"TFW_Command__HelloWorld")
        self.waitForEndOfCommand(0,8)
        self.checkThat("This shall return passed",True)
       
class UATL_TC__TestSimpleCheck(UATL_TestCase):
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic UATL TC feature: send multiple commands and wait for end between each"
        
    def getExpectedResult(self):
        return "the test env shall wait the end of each command before sending the next command"
        
    def getBoardNumber(self):
        return 2
        
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"TFW_Command__HelloWorld")
        self.waitForEndOfCommand(0,20)
        self.checkThat("device 0 displays hello world",self.numberOfRegexMatchesInLog(0,"Hello World ! \(from command\)") == 1)
        
        self.sendCommandAndListen(0,"TFW_Command__PrintTestEnvParameters")
        self.waitForEndOfCommand(0,20)
        self.checkThat("device 0 displays the list of test env param that shall contain 'delayedPrint'",self.numberOfRegexMatchesInLog(0,"delayedPrint") == 1)

        self.sendCommandAndListen(1,"TFW_Command__HelloWorld")
        self.waitForEndOfCommand(1,20)
        self.checkThat("device 1 displays hello world",self.numberOfRegexMatchesInLog(1,"Hello World ! \(from command\)") == 1)
                
class UATL_TC__TestMultipleChecksPerCommand_AllPassed(UATL_TestCase):
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic UATL TC feature: do multiple checks (that return true)"
        
    def getExpectedResult(self):
        return "the test env shall return 'passed' for each passed command, and PASSED for the procedure"
        
    def getBoardNumber(self):
        return 2
        
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"TFW_Command__HelloWorld")
        self.waitForEndOfCommand(0,20)
        self.checkThat("This shall return passed",True)
        self.checkThat("This shall return passed",True)
        self.checkThat("This shall return passed",True)
        self.checkThat("This shall return passed",self.numberOfRegexMatchesInLog(0,"Hello World ! \(from command\)") == 1)
        
        self.sendCommandAndListen(1,"TFW_Command__HelloWorld")
        self.waitForEndOfCommand(1,20)
        self.checkThat("This shall return passed",True)
        self.checkThat("This shall return passed",True)
        self.checkThat("This shall return passed",True)
        self.checkThat("This shall return passed",self.numberOfRegexMatchesInLog(1,"Hello World ! \(from command\)") == 1)
        
class UATL_TC__TestMultipleChecksPerCommand_WithAFailed(UATL_TestCase):  
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic UATL TC feature: do multiple checks (that return true except one)"
        
    def getExpectedResult(self):
        return "the test env shall return 'passed' for each passed command, 'failed' for each failed command, and FAILED for the procedure" 
        
    
    def getBoardNumber(self):
        return 2
        
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"TFW_Command__HelloWorld")
        self.waitForEndOfCommand(0,20)
        self.checkThat("This shall return passed",True)
        self.checkThat("This shall return passed",True)
        self.checkThat("This shall return failed",False)
        self.checkThat("This shall return passed",self.numberOfRegexMatchesInLog(0,"Hello World ! \(from command\)") == 1)
        
        self.sendCommandAndListen(1,"TFW_Command__HelloWorld")
        self.waitForEndOfCommand(1,20)
        self.checkThat("This shall return passed",True)
        self.checkThat("This shall return failed",False)
        self.checkThat("This shall return passed",True)
        self.checkThat("This shall return passed",self.numberOfRegexMatchesInLog(1,"Hello World ! \(from command\)") == 1)
           
class UATL_TC__Timeout1(UATL_TestCase):
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic UATL TC feature: when there is no 'end of command', the test reaches the timeout"
        
    def getExpectedResult(self):
        return "the test env shall return 'timed out' for the first command, then 'skipped' for the next commands, then TIMED_OUT for the procedure"
        
    def getBoardNumber(self):
        return 1
        
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"list")
        self.waitForEndOfCommand(0,20)
        self.checkThat("This shall return timeout",self.numberOfRegexMatchesInLog(0,"Hello World ! \(from command\)") == 0)
        
        self.sendCommandAndListen(0,"") #nothing sent
        self.waitForEndOfCommand(0,20)
        self.checkThat("This shall return skipped",self.numberOfRegexMatchesInLog(0,"Hello World ! \(from command\)") == 0)

class UATL_TC__Timeout2(UATL_TestCase):
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic UATL TC feature: when forcing timeout with short timeout time, timeout happens"
        
    def getExpectedResult(self):
        return "the test env shall return 'timed out' for the command where there is no time for it to read the end of command regex, then TIMED_OUT for the procedure"
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"TFW_Command__HelloWorld")
        self.waitForEndOfCommand(0,20)
        self.checkThat("This shall return passed",self.numberOfRegexMatchesInLog(0,"Hello World ! \(from command\)") == 1)

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenSendOnePacket")
        self.waitForEndOfCommand(0,1)
        self.checkThat("This shall return timeout",self.numberOfRegexMatchesInLog(0,"Hello World ! \(from command\)") == 0)

class UATL_TC__Freeze1(UATL_TestCase):
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic UATL TC feature: when forcing timeout with freezing device 0 and then sending another command, timeout happens"
        
    def getExpectedResult(self):
        return "the test env shall return 'timed out' for the first command, then 'skipped' for the next commands, then TIMED_OUT for the procedure"
        
    def getBoardNumber(self):
        return 1

    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__FreezeAndNotFinish")
        self.waitForEndOfCommand(0,20)
        self.checkThat("This shall return timeout",True)

        self.sendCommandAndListen(0,"TFW_Command__HelloWorld")
        self.waitForEndOfCommand(0,20)
        self.checkThat("This shall return skipped",True)
        
class UATL_TC__Freeze2(UATL_TestCase):
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic UATL TC feature: when forcing timeout  with freezing device 0 and then sending a successful command on another device, timeout happens"
        
    def getExpectedResult(self):
        return "the test env shall return 'timed out' for the first command, then 'skipped' for the next commands, then TIMED_OUT for the procedure"

    def getBoardNumber(self):
        return 2
        
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__FreezeAndNotFinish")
        self.waitForEndOfCommand(0,20)
        self.checkThat("This shall return timeout",True)

        self.sendCommandAndListen(1,"TFW_Command__HelloWorld")
        self.waitForEndOfCommand(1,20)
        self.checkThat("This shall return skipped",True)

class UATL_TC__Freeze3(UATL_TestCase):
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic UATL TC feature: when forcing timeout after returning end of command, timeout happens too"
        
    def getExpectedResult(self):
        return "the test env shall return 'timed out' for the first command, then 'skipped' for the next commands, then TIMED_OUT for the procedure"

    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"BLE_Command__FinishAndFreeze")
        self.waitForEndOfCommand(0,20)
        self.checkThat("This shall return passed",True)

class UATL_TC__Unknown(UATL_TestCase):
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic UATL TC feature: when entering an unknown command, the TC returns FAILED or ERROR"
        
    def getExpectedResult(self):
        return "the test env shall return FAILED or FATAL ERROR"
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command_UNKNOWN")
        self.waitForEndOfCommand(0,20)
        self.checkThat("This shall return passed",True)     
        
"""
-------------------------------------------------------------------------------------------------------------------------------------
AFTER THIS LINE, the following code are RLV engine validation procedures
TODO: remove from final release of UATL
-------------------------------------------------------------------------------------------------------------------------------------
"""
#############################################################
##                           RLV                           ##
#############################################################
class RLV_TC__RLV_noParam(UATL_TestCase):#ready 
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic RLV feature: RLV shall be able to send a command without any argument so it uses default argument"
        
    def getExpectedResult(self):
        return "the test env shall return return passed for each step and then PASSED for the procedure"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
class RLV_TC__RLV_withParam(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "this test aim is to validate basic RLV feature: RLV shall be able to send a command with specific arguments "
        
    def getExpectedResult(self):
        return "the test env shall return return passed for each step and then PASSED for the procedure"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL False 30 4000 0x95 []{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} 4000000 D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL False 30 4000 0x95 []{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : HAL_BLE_ReceivePacketWithAck is not used",self.numberOfRegexMatchesInLog(0,"HAL_BLE_ReceivePacketWithAck") == 0)
        self.checkThat("device 0 : withAck is FALSE",self.numberOfRegexMatchesInLog(0,".*withAck = FALSE.*") == 1)
        self.checkThat("device 0 : channel is 30",self.numberOfRegexMatchesInLog(0,".*channel = 30.*") == 1)
        self.checkThat("device 0 : wakeupTime is 4000",self.numberOfRegexMatchesInLog(0,".*wakeupTime = 4000.*") == 1)
        self.checkThat("device 0 : rxExpectedHeader is 149",self.numberOfRegexMatchesInLog(0,".*rxExpectedHeader = 149.*") == 1)
        self.checkThat("device 0 : rxExpectedPayload is {0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45}",self.numberOfRegexMatchesInLog(0,".*rxExpectedPayload.*\{0x54\,0x45\,0x53\,0x54\,0x5f\,0x42\,0x4c\,0x45\}.*") == 1)
        self.checkThat("device 0 : rxReceiveWindow is 4000000",self.numberOfRegexMatchesInLog(0,".*rxReceiveWindow = 4000000.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        self.checkThat("device 1 : HAL_BLE_SendPacketWithAck is not used",self.numberOfRegexMatchesInLog(1,"HAL_BLE_SendPacketWithAck") == 0)
        self.checkThat("device 1 : withAck is FALSE",self.numberOfRegexMatchesInLog(1,".*withAck = FALSE.*") == 1)
        self.checkThat("device 1 : channel is 30",self.numberOfRegexMatchesInLog(1,".*channel = 30.*") == 1)
        self.checkThat("device 1 : wakeupTime is 4000",self.numberOfRegexMatchesInLog(1,".*wakeupTime = 4000.*") == 1)
        self.checkThat("device 1 : txAckExpectedHeader is 149",self.numberOfRegexMatchesInLog(1,".*txAckExpectedHeader = 149.*") == 1)
        self.checkThat("device 1 : txAckExpectedPayload is {0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45}",self.numberOfRegexMatchesInLog(1,".*txAckExpectedPayload.*\{0x54\,0x45\,0x53\,0x54\,0x5f\,0x42\,0x4c\,0x45\}.*") == 1)
        self.checkThat("device 1 : txAckReceiveWindow is 4000000",self.numberOfRegexMatchesInLog(1,".*txAckReceiveWindow = 4000000.*") == 1)
               
class RLV_CH__RLV_doWithTimeout(UATL_Characterization):#ready
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "Check that all TC HAL_TXRX_Stress_xxx that use embedded timeout (RLV_TFW__DO_WITH_TIMEOUT) can use it on this range without any bug from RLV"
        
    def getExpectedResult(self):
        return "Procedure should return FAILED, not found. -- Note that actually (05/06/20) it does not work for values between 2s and 3s (weird though)"
        
    def getBoardNumber(self):
        return 1
        
    def __callCliCommandsAndDoChecks__(self):
       
        stressDeltaBlockingDelayInUs_MAX = 4000000
        stressDeltaBlockingDelayInUs_MIN = 0
        stressDeltaBlockingDelayInUs_STEP = int(stressDeltaBlockingDelayInUs_MAX/10)    
        
        commandTimeout = 60
        stressDurationInS = int(commandTimeout - 3) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
       
        for stressDeltaBlockingDelayInUs in range(stressDeltaBlockingDelayInUs_MIN,stressDeltaBlockingDelayInUs_MAX-1,stressDeltaBlockingDelayInUs_STEP):
            self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs " + str(stressDeltaBlockingDelayInUs))
            self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
            self.sendCommandAndListen(0,"BLE_Command__DoWithTimeout")
            self.waitForEndOfCommand(0,commandTimeout)   

            if self.stopIf("iteration was a success",self.numberOfRegexMatchesInLog(0,".*?iteration success.*?") >= 1,"stressDeltaBlockingDelayInUs",stressDeltaBlockingDelayInUs):
                break
               
class RLV_TC__RLV_timerTest(UATL_TestCase):#ready
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "Testing TIM2 implementation"
        
    def getExpectedResult(self):
        return "Command shall print 'end of 10s' after 10s"
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
        commandTimeout = 60
        stressDurationInS = int(commandTimeout - 3)
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 1000000")
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        
        self.sendCommandAndListen(0,"BLE_Command__TimerTest")
        self.waitForEndOfCommand(0,commandTimeout)   
        self.checkThat("iteration was a success",self.numberOfRegexMatchesInLog(0,"iteration success") == 1)

class RLV_TC__RLV_wrongParam(UATL_TestCase):#ready
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_TEST_ENV_ONLY
        
    def getObjective(self):
        return "Testing error management"
        
    def getExpectedResult(self):
        return "Shall return 'Error : unknown parameter'"
        
    def getBoardNumber(self):
        return 1
        
    def __callCliCommandsAndDoChecks__(self):
        
        self.sendQuickCommand(0,"TFW_Command__SetParam qsdflkjqhsdflq 12")
        self.checkThat("error was printed",self.numberOfRegexMatchesInLog(0,"Error : unknown parameter") == 1)
        
        self.sendQuickCommand(0,"TFW_Command__GetParam qsdflkjqhsdflq")
        self.checkThat("error was printed",self.numberOfRegexMatchesInLog(0,"Error : unknown parameter") == 1)


"""
-------------------------------------------------------------------------------------------------------------------------------------
AFTER THIS LINE, the following code should be in TestCasesList.py
-------------------------------------------------------------------------------------------------------------------------------------
"""
#############################################################
##                        LLD BLE                          ##
#############################################################

"""
INFO
"""
class RLV_TC__GetInfo(UATL_TestCase):   
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.FOR_INFO_ONLY
        
    def getObjective(self):
        return "This is not a test case, this is used to show test env information, before the campaign starts, to be sure which default parameter value are used "
        
    def getExpectedResult(self):
        return "N/A"
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"info")
        self.waitForEndOfCommand(0,2)
        self.sendCommandAndListen(0,"list")
        self.waitForEndOfCommand(0,2)
        self.sendCommandAndListen(0,"TFW_Command__PrintTestEnvParameters")
        self.waitForEndOfCommand(0,2)
        self.sendCommandAndListen(0,"BLE_Command__PrintTestEnvParameters")
        self.waitForEndOfCommand(0,2)

"""
Inits
"""
class RLV_TC__HAL_Init__nominal(UATL_TestCase):#ready
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
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithHal")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithHal")
        
        self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__SendOnePacket_HAL")
        
        
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
         
class RLV_TC__LLD_Init__nominal(UATL_TestCase):#ready
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
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__SendOnePacket_HAL")
               

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)

"""
HAL without ACK
"""      
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
 
class RLV_EN__HAL_TXRX_NoAck__nominal(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a simple txrx with init works with default parameters, and repeat operation over time. Board are initialized before each rx/tx"
        
    def getExpectedResult(self):
        return "The rx command shall return a correct payload and no error and the tx command shall return no error, otherwise endurance counter is incremented. "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
                
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL",False,True)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL",False,True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)
            
class RLV_EN__HAL_TXRX_NoAck__onlyFirstInitWithLLD(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a simple txrx with ONE init works with default parameters, and repeat operation over time. Boards are only initialized at the beginning of the procedure."
        
    def getExpectedResult(self):
        return "The rx command shall return a correct payload and no error and the tx command shall return no error, otherwise endurance counter is incremented. "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
                
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket_HAL",False,True)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__SendOnePacket_HAL",False,True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)

class RLV_EN__HAL_TXRX_NoAck__pyStress(UATL_Endurance):#ready

    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a simple txrx with ONE init works with default parameters, and repeat operation over time as fast as python allows it. Boards are only initialized at the beginning of the procedure."
        
    def getExpectedResult(self):
        return "The rx command shall return a correct payload and no error and the tx command shall return no error, otherwise endurance counter is incremented. "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
                
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket_HAL",False,True)
            self.sendCommandAndListen(1,"BLE_Command__SendOnePacket_HAL",False,True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)

class RLV_EN__HAL_TXRX_NoAck__lowPowerDisabled(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a simple txrx with ONE init works with default parameters, and repeat operation over time. Low power is disabled."
        
    def getExpectedResult(self):
        return "The rx command shall return a correct payload and no error and the tx command shall return no error, otherwise endurance counter is incremented. "
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"TFW_Command__SetParam lowPowerEnabled FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam lowPowerEnabled FALSE")
        
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL",False,True)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL",False,True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)
            
class RLV_EN__HAL_TXRX_NoAck__worstCase_longAAA(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that withening has no effect on 0101010101... sequences."
        
    def getExpectedResult(self):
        return "The rx command shall return a correct payload and no error and the tx command shall return no error, otherwise endurance counter is incremented. "
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        #change interal RC (1 by default) to external xtal (0)
        self.sendQuickCommand(0,"TFW_Command__SetParam lowSpeedOsc 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam lowSpeedOsc 0")
        
        #change crystal check enabled after a tx or a rx (true by default) to false
        self.sendQuickCommand(0,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        
        #change whitening to disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam whitening DISABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam whitening DISABLE")
        
        #change whitening to disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam whitening DISABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam whitening DISABLE")
          
        #change payload to long AAAAAAA (010101010101010....)
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [240]{0xAA*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [240]{0xAA*}")
        
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL",False,True)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL",False,True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)
          
class RLV_EN__HAL_TXRX_NoAck__worstCase_longCCC(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that withening has no effect on 00110011001100... sequences."
        
    def getExpectedResult(self):
        return "The rx command shall return a correct payload and no error and the tx command shall return no error, otherwise endurance counter is incremented. "
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        #change interal RC (1 by default) to external xtal (0)
        self.sendQuickCommand(0,"TFW_Command__SetParam lowSpeedOsc 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam lowSpeedOsc 0")
        
        #change crystal check enabled after a tx or a rx (true by default) to false
        self.sendQuickCommand(0,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        
        #change whitening to disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam whitening DISABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam whitening DISABLE")
    
        #change payload to long CCCCCC (11001100110011001100110011....)
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [240]{0xCC*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [240]{0xCC*}")
        
        while self.isActive():
            
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL",False,True)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL",False,True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)
                   
class RLV_EN__HAL_TXRX_NoAck__worstCase_longFFF(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that withening has an effect on 111111111111... sequences by disabling it"
        
    def getExpectedResult(self):
        return "The rx command shall not receive payload and the tx command shall return no error, otherwise endurance counter is incremented. "
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        #change interal RC (1 by default) to external xtal (0)
        self.sendQuickCommand(0,"TFW_Command__SetParam lowSpeedOsc 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam lowSpeedOsc 0")
        
        #change crystal check enabled after a tx or a rx (true by default) to false
        self.sendQuickCommand(0,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        
        #change whitening to disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam whitening DISABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam whitening DISABLE")
    
        #change payload to long FFFFF (11111111111111111111111....)
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [240]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [240]{0xFF*}")
        
        while self.isActive():
            
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL",False,True)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL",False,True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 0) and (self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)

class RLV_TC__HAL_TXRX_NoAck__wrong_networkId(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a simple txrx does not work if we have the wrong network Id between rx and tx devices"
        
    def getExpectedResult(self):
        return "We should expect the tx to succeed but the rx to fail"
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFFFFFFFF")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x00000000")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
             
class RLV_TC__HAL_TXRX_NoAck__limits_networkId_null(UATL_TestCase):#cancelled
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return """Check that a simple txrx does work if we have a network Id set to 0. 
        Edit: cancelled after CCB 30/06/20 network id shall not be tested (BZ tickets 87878 and 88960)"""
        
    def getExpectedResult(self):
        return "We should expect the tx tand rx to succeed"
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        #to be sure that TFW_Command__SetParam networkId works
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x5A964129")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x5A964129")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
        #now let's set it to 0
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x00000000")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x00000000")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
class RLV_TC__HAL_TXRX_NoAck__outOfRange_networkId(UATL_TestCase): #cancelled
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return """Check that when calling HAL_BLE_SetNetworkId with a networkId out of range (regarding to BLE spec), 
          then the HAL_BLE_SetNetworkId returns an error code
                ID: network ID based on bluetooth specification:
                1. It shall have no more than six consecutive zeros (1.a) or ones (1.b).
                2. It shall not have all four octets equal.
                3. It shall have no more than 24 transitions.
                4. It shall have a minimum of two transitions in the most significant six bits.
          Edit: cancelled after CCB 30/06/20 network id shall not be tested (BZ tickets 87878 and 88960)"""
        
    def getExpectedResult(self):
        return "HAL_SetNetworkId shall return INVALID_PARAMETER_C0 (0xc0) and the transmission shall work"
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        #out of range networkId (spec #1a)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAA00ABCD")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAA00ABCD")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1)
        
        #out of range networkId (spec #1b)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1)
        
        #out of range networkId (spec #2)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6C6C6C6C")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6C6C6C6C")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1)
        
        #out of range networkId (spec #3)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x752D5525") #0x752D5525 or 0xB55A54AA
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x752D5525")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1)
                
        #out of range networkId (spec #4)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1)
        
        #back to in range networkId
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6CFABCDF") #0x6CFABCDF or 0x5A964129
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6CFABCDF")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
        
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0x00.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0x00.*") == 1)
          
class RLV_TC__HAL_TXRX_NoAck__xtal_disabled(UATL_TestCase):#cancelled
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return "Check that a simple txrx works with default parameters and without calling LLD_BLE_CrystalCheck "
        
    def getExpectedResult(self):
        return "This test is cancelled because this should be done in an endurance test to see effects. Not sure what to expect....I guess this shall work worse than with calling LLD_BLE_CrystalCheck. "
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        #change interal RC (1 by default) to external xtal (0)
        self.sendQuickCommand(0,"TFW_Command__SetParam lowSpeedOsc 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam lowSpeedOsc 0")
        
        #change crystal check enabled after a tx or a rx (true by default) to false
        self.sendQuickCommand(0,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D D D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D D D D D D D D")
    
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
    
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
                        
class RLV_EN__HAL_TXRX_NoAck__pyStress_xtal_disabled(UATL_Endurance):#cancelled
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return """Check effect of LLD_BLE_CrystalCheck over a long period of time.
        Edit: cancelled after CCB , xtal check shall not be checked from the M0 side"""
        
    def getExpectedResult(self):
        return "Still not sure what to expect....I guess this shall work worse than with calling LLD_BLE_CrystalCheck. But how long shall we test it to see any difference? "
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        #change interal RC (1 by default) to external xtal (0)
        self.sendQuickCommand(0,"TFW_Command__SetParam lowSpeedOsc 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam lowSpeedOsc 0")
        
        #change crystal check enabled after a tx or a rx (true by default) to false
        self.sendQuickCommand(0,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket_HAL",False,True)
            self.sendCommandAndListen(1,"BLE_Command__SendOnePacket_HAL",False,True)
            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            
            txRxNotSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 0) or (self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 0) or (self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 0) or (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 0)
            self.serialLoopStep("TX RX not successful",txRxNotSuccessful)
                  
class RLV_TC__HAL_TXRX_NoAck__fullCover_channel(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that every channel works"
        
    def getExpectedResult(self):
        return "For each step, there shall be no error and packet shall be received "
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
    
        testPassed = True
        for channel in range(0,40,1):
            failureCounter = 0
            while True:
                self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D " + str(channel) + " D D D D D D",False)
                time.sleep(0.1)
                self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D " + str(channel) + " D D D D D D",False)
        
                self.waitForEndOfCommand(0,60)
                self.waitForEndOfCommand(1,60)
                txrxSuccess = (self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0) and (self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0) and (self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
                if not txrxSuccess:
                    failureCounter += 1
                    UATL_log("Channel retry")
                else:
                    break
                if (failureCounter >= 3):
                    testPassed = False
                    break
            
        self.checkThat("Transmission has been at least successful once on each channel",testPassed)
 
class RLV_TC__HAL_TXRX_NoAck__wrong_channel(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that the transmission fails if the channel from tx packet is not the same as the one that rx expects"
        
    def getExpectedResult(self):
        return "This test should fail when reading packet"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D 31 D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D 30 D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
       
class RLV_TC__HAL_TXRX_NoAck__outOfRange_channel(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that the transmission fails if the channel for rx and tx is out of range"
        
    def getExpectedResult(self):
        return "This test should fail when reading packet and return an error code of 0xC0 (INVALID_PARAMETER_C0) when calling API function with channel out of range"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        #out of range channel
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D 40 D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D 40 D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [FAILED]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[FAILED\].*") == 1)
        self.checkThat("device 0 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [FAILED]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[FAILED\].*") == 1)
        self.checkThat("device 1 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue.*?'HAL_BLE_SendPacket'.*?0xc0.*") == 1)
        
        #back to normal channel
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D 1 D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D 1 D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0x00.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(1,".*returnValue.*?'HAL_BLE_SendPacket'.*?0x00.*") == 1)

class RLV_TC__HAL_TXRX_NoAck__wrong_header(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that the raw transmission works if the header from tx packet is not the same as the one that rx expects, but that rx command fails."
        
    def getExpectedResult(self):
        return "This test should fail when reading packet (headers not equal)"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D D D 0xFF D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D D D 0x00 D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are not equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
class RLV_TC__HAL_TXRX_NoAck__wrong_payloadContent(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that the raw transmission works if the payload from tx packet is not the same as the one that rx expects, but that rx command fails."
        
    def getExpectedResult(self):
        return "This test should fail when reading packet (payloads not equal)"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D D D D [8]{0xFF*} D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D D D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[FAILED\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)

class RLV_TC__HAL_TXRX_NoAck__wrong_payloadLength_shorter(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that when the length differs from the transmitted packet and the expected packet, command should fail checking length"
        
    def getExpectedResult(self):
        return "This test should fail when reading packet (payloadLength not equal)"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D D D D [5]{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D D D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[FAILED\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)

class RLV_TC__HAL_TXRX_NoAck__outOfRange_payloadLength_longer(UATL_TestCase):#cancelled

    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return """This test is useless. 
        It will not cause crash, because it will read the last elements, of the test array buffer that is 10 bytes long, that were initialized to 0.
        Even if the buffer has not been not initialized to 0, there is no way to prevent this undefined behavior from happening.        
        """
        
    def getExpectedResult(self):
        return "?"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D D D D [10]{0x54,0x45,0x53} D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D D D D [10]{0x54,0x45,0x53} D D D ")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(0,"\[OK\]") >= 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
   
class RLV_TC__HAL_TXRX_NoAck__limits_payloadLength_max(UATL_TestCase):#cancelled
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check that program does not crash if payload length is reaching max limit.
          After CCB of 09/06/2020 (ticket 85848), limit is now 255 when not encrypting"""        
        
    def getExpectedResult(self):
        return """This test should not crash nor fail when reading packets with length from 250 to 255.
        However, note that undefined behavior cannot be tested.
        This test should be completed with code analysis.
        
        Furthermore, what is max limit?
        - according to §26 of "blue baseband hw spec (rev0.14)"
          in a packet, the length is a byte, so we could theorically put 255 (without encryption that takes 4 bytes for MIC)
          and BLE driver is hardcoded to 255+2
        - according to BLUETOOTH SPECIFICATION Version 5.0 | Vol 6, Part B page 2588:
            "The Length field of the Header indicates the length of the Payload and MIC if
            included. The length field has the range of 0 to 255 octets. The Payload field
            shall be less than or equal to 251 octets in length. The MIC is 4 octets in length."
            
        Thus, MAX payload length for unencrypted and encrypted packet is 251.
        
        Therefore we could expect the API function to return an error code (INVALID_PARAMETER_C0) but carry on transmission/reception at user's risks.
        To be defined.
        """
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        for payloadLength in range(250,256,1):
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D D D D [" + str(payloadLength) + "]{0xFF*} D D D",False)
            time.sleep(0.2) 
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D D D D [" + str(payloadLength) +"]{0xFF*} D D D ",False)
        
            self.waitForEndOfCommand(0,60)
            self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
            self.checkThat("device 0 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(0,"\[OK\]") >= 1)
            self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is not INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 0)

            self.waitForEndOfCommand(1,60)
            self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
            self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
            self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is not INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 0)                    
            
class RLV_TC__HAL_TXRX_NoAck__limits_payloadLength_null(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that the transmission nor the command do not fail if the payloadLength is null for tx and for what rx expects"
        
    def getExpectedResult(self):
        return "This test should not fail when reading packet headers and lengths (payload will not be read as length is 0)"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D D D D [0]{0xFF} D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D D D D [0]{0xFF} D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
 
class RLV_CH__HAL_TXRX_NoAck__minimum_txRxDelay(UATL_Characterization):#cancelled
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return "Find the shortest tx rx possible delay"
        
    def getExpectedResult(self):
        return "This test will not find the shortest as it is limited by python and OS limits. At least it showed that packet can be send even if no delay is put between rx and tx"

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        for txRxDelayInMs in range(10,-1,-1):
        
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL", False)
            time.sleep(float(int(txRxDelayInMs)/1000))
            UATL_log("TX/RX Delay: "+str(float(int(txRxDelayInMs)/1000))+" s")
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL", False)

            self.waitForEndOfCommand(0,60)
            if self.stopIf("device 0 : there is at least one [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") >= 1,"txRxDelayInMs",txRxDelayInMs):
                break

            self.waitForEndOfCommand(1,60)
            if self.stopIf("device 1 : there is at least one [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") >= 1,"txRxDelayInMs",txRxDelayInMs):
                break
 
class RLV_CH__HAL_TXRX_NoAck__minimum_wakeupTime(UATL_Characterization):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Find the shortest possible wake up time"
        
    def getExpectedResult(self):
        return "Shortest wakeup time. This test should be improved with statistic analysis because it might start failing with a square edge but more with a slope"

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        for wakeupTime in range(250,-1,-1):
            
            UATL_log("Wake Up Time: "+str(wakeupTime)+" us")
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D D "+str(wakeupTime)+" D D D D D", False)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D D "+str(wakeupTime)+" D D D D D", False)

            self.waitForEndOfCommand(0,60)
            if self.stopIf("device 0 : there is at least one [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") >= 1,"wakeupTime",wakeupTime):
                break
            self.waitForEndOfCommand(1,60)
            if self.stopIf("device 1 : there is at least one [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") >= 1,"wakeupTime",wakeupTime):
                break
 
class RLV_CH__HAL_TXRX_NoAck__minimum_startUpTime(UATL_Characterization):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Find the shortest possible start up time"
        
    def getExpectedResult(self):
        return "Shortest start up time. This test should be improved with statistic analysis because it might start failing with a square edge but more with a slope"

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        for hsStartupTime in range(26,-1,-1):
            
            UATL_log("Start Up Time: "+str(float(hsStartupTime)*625.0/256.0)+" us") # 64µs is 0x1A (26)
            self.sendQuickCommand(0,"TFW_Command__SetParam hsStartupTime " + str(hsStartupTime))
            self.sendQuickCommand(1,"TFW_Command__SetParam hsStartupTime " + str(hsStartupTime))          
            
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL", False)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL", False)

            self.waitForEndOfCommand(0,60)
            if self.stopIf("device 0 : there is at least one [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") >= 1,"hsStartupTime",hsStartupTime):
                break
            self.waitForEndOfCommand(1,60)
            if self.stopIf("device 1 : there is at least one [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") >= 1,"hsStartupTime",hsStartupTime):
                break
       
class RLV_TC__HAL_TXRX_NoAck__outOfRange_hotAnaTableLength_shorter(UATL_TestCase):#cancelled
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return "Check that a simple txrx works after initializing with a shorter hotAnaTable than expected (15)"
        
    def getExpectedResult(self):
        return """Not sure what to expect here, as it will throw undefined behavior, but let's say we don't want it to crash.
          Anyway there is no way for the LLD BLE to check the length of the pointer, so this test is useless."""

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendQuickCommand(0,"TFW_Command__SetParam hotAnaTable []{0x0}")
        self.sendQuickCommand(1,"TFW_Command__SetParam hotAnaTable []{0x0}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
        
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
class RLV_TC__HAL_TXRX_NoAck__wrong_hotAnaTableContent(UATL_TestCase):#need info
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.NEED_SPEC_INFO
        
    def getObjective(self):
        return "Check that a simple txrx works?/does not work? after initializing with a different hotAnaTable for both sides"
        
    def getExpectedResult(self):
        return "Not sure what to expect here"

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        #different
        self.sendQuickCommand(0,"TFW_Command__SetParam hotAnaTable [15]{0x0000*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam hotAnaTable [15]{0xFFFF*}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
        #same
        self.sendQuickCommand(0,"TFW_Command__SetParam hotAnaTable [15]{0xFFFF*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam hotAnaTable [15]{0xFFFF*}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
       
class RLV_TC__HAL_TXRX_NoAck__whitening(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a simple txrx works with and without whitening. Prove that whitening has an effect on payload"
        
    def getExpectedResult(self):
        return "if whitening is enabled or disabled from both sides, transmission should work, if whitening is disabled in one side and enabled on the other, transmission should fail"

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
    
        #whitening is enabled by default
        self.sendQuickCommand(0,"TFW_Command__SetParam whitening DISABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        #whitening is set only on one side, receive shall not work at all (the whole packet including CRC is whitened)
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[FAILED\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
        #whitening is disabled on both sides, this shall work
        self.sendQuickCommand(1,"TFW_Command__SetParam whitening DISABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)

"""
HAL with ACK
"""
class RLV_TC__HAL_TXRX_Ack__nominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a txrx with ack works"
        
    def getExpectedResult(self):
        return """tx with ack to rx with no ack, this should fail, 
          then tx with ack to rx with ack, this should work
          then tx with no ack to rx with ack, this should work (useless though)"""

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        #try tx w/ ack, rx w/ ack
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
       
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : HAL_BLE_ReceivePacketWithAck is used",self.numberOfRegexMatchesInLog(0,".*HAL_BLE_ReceivePacketWithAck.*") >= 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : HAL_BLE_SendPacket is not used",self.numberOfRegexMatchesInLog(1,".*\'HAL_BLE_SendPacket\'.*") == 0)
        self.checkThat("device 1 : HAL_BLE_SendPacketWithAck is used",self.numberOfRegexMatchesInLog(1,".*HAL_BLE_SendPacketWithAck.*") >= 1)
        
        #try tx w/ ack, rx w/o ack
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL P D D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL P D D D D D D D")
       
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : HAL_BLE_ReceivePacket is used",self.numberOfRegexMatchesInLog(0,".*\'HAL_BLE_ReceivePacket\'.*") >= 1)
        self.checkThat("device 0 : HAL_BLE_ReceivePacketWithAck is not used",self.numberOfRegexMatchesInLog(0,".*HAL_BLE_ReceivePacketWithAck.*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : actionFailed is not [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 0)
        self.checkThat("device 1 : payloads are not equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 0)
        self.checkThat("device 1 : HAL_BLE_SendPacket is not used",self.numberOfRegexMatchesInLog(1,".*\'HAL_BLE_SendPacket\'.*") == 0)
        self.checkThat("device 1 : HAL_BLE_SendPacketWithAck is used",self.numberOfRegexMatchesInLog(1,".*HAL_BLE_SendPacketWithAck.*") >= 1)
        
        
        #back to tx w/ ack, rx w/ ack
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL P D D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL P D D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : HAL_BLE_ReceivePacket is not used",self.numberOfRegexMatchesInLog(0,".*\'HAL_BLE_ReceivePacket\'.*") == 0)
        self.checkThat("device 0 : HAL_BLE_ReceivePacketWithAck is used",self.numberOfRegexMatchesInLog(0,".*HAL_BLE_ReceivePacketWithAck.*") >= 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : HAL_BLE_SendPacket is not used",self.numberOfRegexMatchesInLog(1,".*\'HAL_BLE_SendPacket\'.*") == 0)
        self.checkThat("device 1 : HAL_BLE_SendPacketWithAck is used",self.numberOfRegexMatchesInLog(1,".*HAL_BLE_SendPacketWithAck.*") >= 1)
        
        
        #try to tx w/o ack, rx w/ ack (useless)
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck FALSE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL P D D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL P D D D D D D D")

       
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : HAL_BLE_ReceivePacket is not used",self.numberOfRegexMatchesInLog(0,".*\'HAL_BLE_ReceivePacket\'.*") == 0)
        self.checkThat("device 0 : HAL_BLE_ReceivePacketWithAck is used",self.numberOfRegexMatchesInLog(0,".*HAL_BLE_ReceivePacketWithAck.*") >= 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : HAL_BLE_SendPacket is used",self.numberOfRegexMatchesInLog(1,".*\'HAL_BLE_SendPacket\'.*") >= 1)
        self.checkThat("device 1 : HAL_BLE_SendPacketWithAck is not used",self.numberOfRegexMatchesInLog(1,".*HAL_BLE_SendPacketWithAck.*") == 0)
        
        
        #try tx w/o ack, rx w/o ack
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck FALSE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL P D D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL P D D D D D D D")

       
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : HAL_BLE_ReceivePacket is used",self.numberOfRegexMatchesInLog(0,".*\'HAL_BLE_ReceivePacket\'.*") >= 1)
        self.checkThat("device 0 : HAL_BLE_ReceivePacketWithAck is not used",self.numberOfRegexMatchesInLog(0,".*HAL_BLE_ReceivePacketWithAck.*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : HAL_BLE_SendPacket is used",self.numberOfRegexMatchesInLog(1,".*\'HAL_BLE_SendPacket\'.*") >= 1)
        self.checkThat("device 1 : HAL_BLE_SendPacketWithAck is not used",self.numberOfRegexMatchesInLog(1,".*HAL_BLE_SendPacketWithAck.*") == 0)

class RLV_EN__HAL_TXRX_Ack__nominal(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that an init + tx with ack and init + rx with ack works for a long period of time. "
        
    def getExpectedResult(self):
        return "The rx and tx command shall receive payload and return no error , otherwise endurance counter is incremented. PER shall be < 5/1000"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
      
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL", False, True)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL", False, True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)

class RLV_EN__HAL_TXRX_Ack__onlyFirstInit(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a tx and rx with ack works for a long period of time without reinitializing at ech step"
        
    def getExpectedResult(self):
        return "The rx and tx command shall receive payload and return no error , otherwise endurance counter is incremented. PER shall be < 5/1000"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
                
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket_HAL",False,True)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__SendOnePacket_HAL",False,True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)
           
class RLV_EN__HAL_TXRX_Ack__pyStress(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a simple txrx with ack works, and repeat operation over time as fast as python allows it. Boards are only initialized at the beginning of the procedure."
        
    def getExpectedResult(self):
        return "The rx and tx command shall return a correct payload and no error, otherwise endurance counter is incremented. "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
                
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket_HAL", False, True)
            self.sendCommandAndListen(1,"BLE_Command__SendOnePacket_HAL", False, True)
            
            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)
                  
class RLV_TC__HAL_TXRX_Ack__wrong_networkId(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a txrx with ack does not work if we have the wrong network Id between rx and tx devices."
        
    def getExpectedResult(self):
        return "The rx and tx command shall fail "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFFFFFFFF")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x00000000")

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 1 : payloads are not equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 0)
                       
class RLV_TC__HAL_TXRX_Ack__outOfRange_networkId(UATL_TestCase): #cancelled
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return """There is interest in doing this test as Ip seems to not set the IRQ_RCV_OK bit of the status register when txrx happens...
        Edit: cancelled after CCB 30/06/20 network id shall not be tested (BZ tickets 87878 and 88960)"""
        
    def getExpectedResult(self):
        return "HAL_SetNetworkId shall return INVALID_PARAMETER_C0 (0xc0) and the transmission shall work"
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
                
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
                
        #out of range networkId (spec #1a)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAA00ABCD")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAA00ABCD")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #out of range networkId (spec #1b)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #out of range networkId (spec #2)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6C6C6C6C")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6C6C6C6C")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #out of range networkId (spec #3)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x752D5525") #0x752D5525 or 0xB55A54AA
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x752D5525")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        
        #out of range networkId (spec #4)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #back to in range networkId
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6CFABCDF") #0x6CFABCDF or 0x5A964129 or 0x71764129
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6CFABCDF")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
        
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0x00.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0x00.*") == 1)
                 
class RLV_TC__HAL_TXRX_Ack__randomCover_networkId(UATL_TestCase): #cancelled
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return """There is interest in doing this test as Ip seems to not set the IRQ_RCV_OK bit of the status register when txrx happens...
        Edit: cancelled after CCB 30/06/20 network id shall not be tested (BZ tickets 87878 and 88960)"""
        
    def getExpectedResult(self):
        return "?"
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        

        networkIdList = """
        1 0xAA00ABCD
        0 0x6CFABCDF
        1 0xAAFFABCD
        3 0x752D5525
        4 0xFC0FC0FC
        2 0x6C6C6C6C 
        0 0xb8b4567
        0 0xae8944a
        0 0x9e2a9e3
        0 0xbd062c2
        0 0xbefd79f
        0 0x8edbdab
        0 0x9838cb2
        0 0xb03e0c6
        0 0x89a769b
        0 0x836c40e
        0 0xa95f874
        0 0x8138641
        0 0x855585c
        0 0xa2342ec
        0 0xa487cb0
        0 0xa6d8d3c
        0 0xb588f54
        0 0x84a481a
        0 0x9a1deaa
        0 0x9386575
        0 0xad084e9
        0 0x98a3148
        0 0x99d0247
        0 0xbd3ee7b
        0 0xbf72b14
        0 0x8f2b15e
        0 0xa32234b
        0 0xb0fd379
        0 0x8eb2f63
        0 0x962813b
        0 0xa27709e
        0 0x94211f2
        0 0x8ebc550
        0 0xa2ac315
        0 0x9da307d
        0 0xa5f7029
        0 0xa3dd3e8
        0 0x9daf632
        0 0x9adea3d
        0 0x88f1a34
        0 0xa155dbc
        0 0x97e1b4e
        0 0xbd8591a
        0 0x8df6a55
        0 0x9b7aaa2
        0 0xb0d8dbe
        0 0xaa7b75c
        0 0xb25ace2
        0 0xa082c70
        0 0x9e21bb2
        0 0xbee5a5b
        0 0xa31b62d
        0 0x849c29b
        0 0x816f8c4
        0 0xab49daf
        0 0x97b4d84
        0 0x8b5e776
        0 0xa0dde32
        0 0x9c0e823
        0 0x9934699
        0 0xb1d2c14
        0 0x8b867d3
        0 0xae05a34
        0 0x94927a8
        0 0xa6ad9be
        0 0xbaac1b4
        0 0xab26e78
        0 0xa9a9e69
        0 0xa3b714c
        0 0x9bacf25
        0 0xb4b8b53
        0 0x97c46bc
        0 0xa9cc3e5
        0 0xa966cd0
        0 0x895f5fa
        0 0x8a5d054
        0 0xb793735
        0 0xa10b4e8
        0 0xa37288a
        0 0x8f8b73f
        0 0x9d3947c
        0 0x84eed59
        0 0xb057295
        0 0x958bd17
        0 0x9a52566
        0 0x8677b7c
        0 0x953172f
        0 0x822c0ef
        0 0x9a377b6
        0 0x8aeb063
        0 0x817e7ec
        0 0xa1b45e5
        0 0x876589d
        0 0xa606509
        0 0x835626c
        0 0x835b2ae
        0 0x98a92ba
        0 0xb697c7a
        0 0xa1d606e
        0 0x9b76e28
        1 0xa954aa5
        1 0xa2aaaad
        1 0xab55525
        1 0xab55295
        1 0x9569555
        1 0xaaaa2aa
        1 0xaad9555
        1 0xb4aaaab
        1 0xaaa556a
        1 0xaab5556
        1 0xb5b5555
        1 0xaad5aa9
        1 0xa955a55
        1 0x954b555
        1 0xaaa4aad
        1 0xa555552
        1 0xaaeaaaa
        1 0x95ad555
        1 0xaa554aa
        1 0x8aaaaad
        1 0xb5aa555
        1 0xaaa52ab
        1 0x8ad5555
        1 0x95aaaa5
        1 0xb5aaad5
        1 0xaab2d55
        1 0xaaaaaa7
        1 0xb56aa55
        1 0xaa95355
        1 0xa555529
        1 0xaaa2b55
        1 0xaaa5355
        1 0xab556ad
        1 0xaaa2ad5
        1 0xaaaab2a
        1 0xadaaaaa
        1 0xad5aa55
        1 0xb5554a9
        1 0x9552a55
        1 0xaaab5ad
        1 0xa552ab5
        1 0xa954955
        1 0xaaa5755
        1 0x8a55555
        1 0xaa956d5
        1 0xaa92a95
        1 0xaab5155
        1 0xb552ab5
        1 0xb555555
        1 0xb455555
        1 0xaab5525
        1 0xad6aa55
        1 0x9555529
        1 0x955555b
        1 0xaaac555
        1 0xb2aaaaa
        1 0xaaa552a
        1 0xaad2a55
        1 0xad2d555
        1 0xaaaf555
        1 0xaa555ab
        1 0xa555556
        1 0xb5aaaad
        1 0xab56955
        1 0xb4aaa55
        1 0xaad54aa
        1 0xb556555
        1 0xaab5295
        1 0x956aad5
        1 0xaaa9556
        1 0x952ab55
        1 0xaaaaa53
        1 0xad52d55
        1 0xb554aad
        1 0xb5555ad
        1 0xa2a5555
        1 0xaa55569
        1 0xab6aad5
        1 0xaad5555
        1 0xaaaa4a9
        1 0xaaab4a5
        1 0xaab2555
        1 0xaa554a9
        1 0xab556aa
        1 0xaad552d
        1 0xa552b55
        1 0xaa9555a
        1 0xaaaa965
        1 0xaaaa9ab
        1 0xaaa54a5
        1 0xaa56aa5
        1 0x9552aa5
        1 0xa9554ad
        1 0x9554d55
        1 0xaaa52d5
        1 0xaaab545
        1 0xbaaaaaa
        1 0xaaad52a
        1 0xaaadab5
        1 0xa555255
        2 0x9090909
        2 0xb0b0b0b
        2 0xa0a0a0a
        2 0x6C6C6C6C
        3 0x9495cff
        3 0xb68079a
        3 0x804823e
        3 0x80bd78f
        3 0x8437fdb
        3 0xba026fa
        3 0x80115be
        3 0xa0382c5
        3 0x9ee015c
        3 0xaa78f7f
        3 0x915ff32
        3 0xb37e80a
        3 0xbffae18
        3 0x9d0feac
        3 0x9e7f3e5
        3 0xa6de806
        3 0xb594807
        3 0xb47f63e
        3 0xafe3625
        3 0x803d089
        3 0xbb180d8
        3 0x80ea5d1
        3 0xa9554fe
        3 0x822cb01
        3 0xaf7f0ea
        3 0xbdd53fd
        3 0x92b8401
        3 0xbfd4210
        3 0xb1dd403
        3 0x90802be
        3 0x8781401
        3 0x82dfed6
        3 0x992a02e
        3 0x80e6897
        3 0xa0201c7
        3 0x95fc93b
        3 0xaa8580e
        3 0xa0ffa11
        3 0x8070222
        3 0x8bb805a
        3 0x9f06dfd
        3 0xac68ffb
        3 0x805b331
        3 0x9454021
        3 0xb727f19
        3 0x8100a9c
        3 0x9d30dfd
        3 0x8b59eff
        3 0x9d1fea0
        3 0x8a35fe3
        3 0x800e34b
        3 0xad7fca2
        3 0x973f88f
        3 0x8c05b8a
        3 0xbf876ee
        3 0xa541011
        3 0x9e2bfcc
        3 0xb34dfe8
        3 0x88bfb19
        3 0x95b37f3
        3 0x806546b
        3 0x8d7f9d7
        3 0x9629ffa
        3 0x82ff375
        3 0xb8fa025
        3 0x97bfd38
        3 0x837f1df
        3 0xbe02a44
        3 0xa35bf85
        3 0x8c0a800
        3 0x9180ee2
        3 0x8e13f8e
        3 0x8ebd301
        3 0x97fd5b0
        3 0xa577fd6
        3 0xb37f412
        3 0xabb00c4
        3 0x80e78c3
        3 0x953f85f
        3 0xb80c94f
        3 0xb4004ee
        3 0x8017db8
        3 0xbd80000
        3 0xb1047fc
        3 0x9797f44
        3 0xb4ff9db
        3 0x900c91c
        3 0xa5fc05d
        3 0xba207f7
        3 0x97f6285
        3 0x87266fe
        3 0xb620264
        3 0x9a03e66
        3 0x927d00e
        3 0xa59ff72
        3 0xb6bfc95
        3 0xa46009e
        3 0x88cefe8
        3 0xa80b139
        3 0x80ea44a
        4 0x27b23c6
        4 0x43c9869
        4 0x6334873
        4 0x4b0dc51
        4 0x25558ec
        4 0x38e1f29
        4 0x6e87ccd
        4 0xd1b58ba
        4 0xeb141f2
        4 0x545e146
        4 0x216231b
        4 0xf16e9e8
        4 0x6ef438d
        4 0x40e0f76
        4 0x352255a
        4 0xded7263
        4 0xfdcc233
        4 0xe6afb66
        4 0x5e45d32
        4 0x31bd7b7
        4 0xf2dba31
        4 0xc83e458
        4 0x57130a3
        4 0x2bbd95a
        4 0x36c6125
        4 0x28c895d
        4 0x33ab105
        4 0x21da317
        4 0x443a858
        4 0xd1d5ae9
        4 0x763845e
        4 0x5a2a8d4
        4 0x353d0cd
        4 0x4e49eb4
        4 0xca88611
        4 0xc3dbd3d
        4 0x37b8ddc
        4 0xceaf087
        4 0x2221a70
        4 0x516dde9
        4 0x5072367
        4 0x724c67e
        4 0xc482a97
        4 0x463b9ea
        4 0xe884adc
        4 0xd517796
        4 0x53ea438
        4 0xd4ed43b
        4 0x25a06fb
        4 0xcd89a32
        4 0x7e4ccaf
        4 0x42289ec
        4 0xde91b18
        4 0x644a45c
        4 0x49abb43
        4 0xdc240fb
        4 0x5c6c33a
        4 0x2e685fb
        4 0x20eedd1
        4 0x49bb77c
        4 0x75ac794
        4 0xcf10fd8
        4 0x35ba861
        4 0x7398c89
        4 0x5b5af5c
        4 0x41226bb
        4 0xd34b6a8
        4 0xf6ab60f
        4 0xe0c57b1
        4 0x7ae35eb
        4 0x79be4f1
        4 0xf305def
        4 0x5a70bf7
        4 0xf48eaa1
        4 0x381823a
        4 0xdb70ae5
        4 0x6b94764
        4 0x2c296bd
        4 0x68e121f
        4 0xeba5d23
        4 0x61e3f1e
        4 0xdc79ea8
        4 0x40a471c
        4 0x2963e5a
        4 0x6a5ee64
        4 0x4330624
        4 0xfb7e0aa
        4 0x6eb5bd4
        4 0xf6dd9ac
        4 0x6272110
        4 0x716703b
        4 0x4e17e33
        4 0x222e7cd
        4 0x4de0ee3
        4 0xdf6d648
        4 0x6b7d447
        4 0x3f18422
        4 0x6f324ba
        4 0xfb8370b
        4 0x488ac1a
        1 0xAA00ABCD
        1 0xAAFFABCD
        2 0x6C6C6C6C
        3 0x752D5525
        4 0xFC0FC0FC
        0 0x6CFABCDF
        """
        
        nwkIdEcCounter = [[0,0],[0,0],[0,0],[0,0],[0,0]]
 
        for line in networkIdList.splitlines():
            if line is None:
                pass
            elif re.match('^[\s]+$',line):
                pass
            elif len(shlex.split(line)) != 2:
                pass
            else:
                UATL_log(line)
                (networkIdErrorCode, networkId) = shlex.split(line)
                networkIdErrorCode = int(networkIdErrorCode)
                
                #UATL_log("expected networkIdErrorCode: {} networkId: {}".format(networkIdErrorCode,networkId))
                
                self.sendQuickCommand(0,"TFW_Command__SetParam networkId " + networkId)
                self.sendQuickCommand(1,"TFW_Command__SetParam networkId " + networkId)
                
                self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
                self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

                self.waitForEndOfCommand(0,60)
                self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
                self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
                self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
                #self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1) #TODO, remove comment if spec is updated

                if (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1):
                    nwkIdEcCounter[networkIdErrorCode][0] += 1
                
                nwkIdEcCounter[networkIdErrorCode][1] += 1

                self.waitForEndOfCommand(1,60)
                self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
                self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
                self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
                #self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1) #TODO, remove comment if spec is updated
                
        UATL_log("0 : {}/{}".format(nwkIdEcCounter[0][0],nwkIdEcCounter[0][1]))
        UATL_log("1 : {}/{}".format(nwkIdEcCounter[1][0],nwkIdEcCounter[1][1]))
        UATL_log("2 : {}/{}".format(nwkIdEcCounter[2][0],nwkIdEcCounter[2][1]))
        UATL_log("3 : {}/{}".format(nwkIdEcCounter[3][0],nwkIdEcCounter[3][1]))
        UATL_log("4 : {}/{}".format(nwkIdEcCounter[4][0],nwkIdEcCounter[4][1]))
        
class RLV_TC__HAL_TXRX_Ack__worstCase_networkId(UATL_TestCase): #cancelled
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return """There is interest in doing this test as Ip seems to not set the IRQ_RCV_OK bit of the status register when txrx happens...
        Edit: cancelled after CCB 30/06/20 network id shall not be tested (BZ tickets 87878 and 88960)"""
        
    def getExpectedResult(self):
        return "HAL_SetNetworkId shall return INVALID_PARAMETER_C0 (0xc0) and the transmission shall work"
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
              
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
                
        #out of range networkId (spec #1a)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAA00ABCD")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAA00ABCD")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)


        #out of range networkId (spec #1b)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)


        #out of range networkId (spec #4)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        
        #out of range networkId (spec worst A1)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x00010001")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x00010001")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        

        #out of range networkId (spec worst A2)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFFFEFFFE")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFFFEFFFE")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)


        #out of range networkId (spec worst B1)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x000F000F")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x000F000F")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        

        #out of range networkId (spec worst B2)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFFF0FFF0")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFFF0FFF0")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        

        #out of range networkId (spec worst C)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFF00FF00")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFF00FF00")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #out of range networkId (spec worst D)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFFFFFFFF")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFFFFFFFF")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #out of range networkId (spec worst E)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAAAAAAAA")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAAAAAAAA")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
       
               
        #out of range networkId (spec worst F)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xCCCCCCCC")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xCCCCCCCC")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
           
               
        #not BLE compliant but works
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6c6c6c6c")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6c6c6c6c")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)  
        
        #back to in range networkId
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6CFABCDF") #0x6CFABCDF or 0x5A964129 or 0x71764129
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6CFABCDF")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
        
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0x00.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0x00.*") == 1)
                    
class RLV_TC__HAL_TXRX_Ack__wrong_channel(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a txrx with ack does not work if the channel from tx packet is not the same as the one that rx expects."
        
    def getExpectedResult(self):
        return "The rx and tx command shall fail "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL TRUE 31 D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL TRUE 30 D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 1 : payloads are not equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 0)

class RLV_TC__HAL_TXRX_Ack__wrong_txHeader(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a txrx with ack does not work if the header from tx packet is not the same as the one that rx board expects."
        
    def getExpectedResult(self):
        return "The rx and tx command shall fail "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL TRUE D D 0xFF D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL TRUE D D 0x00 D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are not equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : headers are equal",self.numberOfRegexMatchesInLog(1,".*Checking header.*\[OK\].*") == 1)
        
class RLV_TC__HAL_TXRX_Ack__wrong_ackHeader(UATL_TestCase):#ready

    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a txrx with ack does not work if the header from ack packet is not the same as the one that tx board expects."
        
    def getExpectedResult(self):
        return "The rx payload shall be received and correct and the tx command shall fail when reading header"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL TRUE D D D D D 0xFF D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL TRUE D D D D D 0x00 D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : headers are not equal",self.numberOfRegexMatchesInLog(1,".*Checking header.*\[OK\].*") == 0)
       
class RLV_TC__HAL_TXRX_Ack__wrong_txPayloadContent(UATL_TestCase):#ready

    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a txrx with ack does not work if the payloadContent from tx packet is not the same as the one that rx board expects."
        
    def getExpectedResult(self):
        return "The packet payload shall be received and not correct and the ack payload shall be received and correct "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL TRUE D D D []{0x54,0x45,0x53,0x54,0x5f,0xFF,0x4c,0x45} D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL TRUE D D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : headers are equal",self.numberOfRegexMatchesInLog(1,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 1 : lengths are equal",self.numberOfRegexMatchesInLog(1,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        
class RLV_TC__HAL_TXRX_Ack__wrong_ackPayloadContent(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a txrx with ack does not work if the payloadContent from tx ack is not the same as the one that tx board expects."
        
    def getExpectedResult(self):
        return "The packet payload shall be received and correct and the ack payload shall be received and not correct "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL TRUE D D D D D D []{0x54,0x45,0x53,0x54,0x5f,0xFF,0x4c,0x45}")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL TRUE D D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : headers are equal",self.numberOfRegexMatchesInLog(1,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 1 : lengths are equal",self.numberOfRegexMatchesInLog(1,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are not equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 0)

class RLV_TC__HAL_TXRX_Ack__wrong_txPayloadLength_shorter(UATL_TestCase):#ready

    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that when the length differs from the transmitted packet and the expected packet, command should fail checking length"
        
    def getExpectedResult(self):
        return "The packet payload shall be received and not correct and the ack payload shall be received and correct "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL TRUE D D D [5]{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL TRUE D D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : headers are equal",self.numberOfRegexMatchesInLog(1,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 1 : lengths are equal",self.numberOfRegexMatchesInLog(1,".*Checking length.*\[OK\].*") == 1)
        
class RLV_TC__HAL_TXRX_Ack__wrong_ackPayloadLength_shorter(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that when the length differs from the transmitted ack and the expected ack, command should fail checking length"
        
    def getExpectedResult(self):
        return "The packet payload shall be received and correct and the ack payload shall be received and not correct "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL TRUE D D D D D D [5]{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45}")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL TRUE D D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : headers are equal",self.numberOfRegexMatchesInLog(1,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 1 : lengths are not equal",self.numberOfRegexMatchesInLog(1,".*Checking length.*\[OK\].*") == 0)

class RLV_TC__HAL_TXRX_Ack__limits_txPayloadLength_null(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check when the length is null for the packet payload"
        
    def getExpectedResult(self):
        return "The packet payload shall be received and be none and the ack payload shall be received and correct "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL TRUE D D D [0]{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL TRUE D D D [0]{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : headers are equal",self.numberOfRegexMatchesInLog(1,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 1 : lengths are equal",self.numberOfRegexMatchesInLog(1,".*Checking length.*\[OK\].*") == 1)
         
class RLV_TC__HAL_TXRX_Ack__limits_ackPayloadLength_null(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check when the length is null for the packet ack"
        
    def getExpectedResult(self):
        return "The ack payload shall be received and be none and the packet payload shall be received and correct "

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL TRUE D D D D D D [0]{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45}")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL TRUE D D D D D D [0]{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45}")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : headers are equal",self.numberOfRegexMatchesInLog(1,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 1 : lengths are equal",self.numberOfRegexMatchesInLog(1,".*Checking length.*\[OK\].*") == 1)
 
class RLV_TC__HAL_TXRX_Ack__limits_txPayloadLength_max(UATL_TestCase):#cancelled
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED

    def getObjective(self):
        return "Check that program does not crash if payload length is reaching max limit."
        
    def getExpectedResult(self):
        return """This test should not crash nor fail when reading packets with length from 250 to 255.
        However, note that undefined behavior cannot be tested.
        This test should be completed with code analysis.
        
        Furthermore, what is max limit?
        - according to §26 of "blue baseband hw spec (rev0.14)"
          in a packet, the length is a byte, so we could theorically put 255 (without encryption that takes 4 bytes for MIC)
          and BLE driver is hardcoded to 255+2
        - according to BLUETOOTH SPECIFICATION Version 5.0 | Vol 6, Part B page 2588:
            "The Length field of the Header indicates the length of the Payload and MIC if
            included. The length field has the range of 0 to 255 octets. The Payload field
            shall be less than or equal to 251 octets in length. The MIC is 4 octets in length."
            
        Thus, MAX payload length for unencrypted and encrypted packet is 251.
        
        Therefore we could expect the API function to return an error code (INVALID_PARAMETER_C0) but carry on transmission/reception at user's risks.
        To be defined.
        """
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        for payloadLength in range(250,256,1):
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D D D D [" + str(payloadLength) + "]{0xFF*} D D D",False)
            time.sleep(0.2) 
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D D D D [" + str(payloadLength) +"]{0xFF*} D D D ",False)
            self.waitForEndOfCommand(0,60)
            self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
            self.checkThat("device 0 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(0,"\[OK\]") >= 1)
            self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is not INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 0)

            self.waitForEndOfCommand(1,60)
            self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
            self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
            self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is not INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 0)                    
  
class RLV_TC__HAL_TXRX_Ack__limits_ackPayloadLength_max(UATL_TestCase):#cancelled
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED

    def getObjective(self):
        return "Check that program does not crash if ack length is reaching max limit."
        
    def getExpectedResult(self):
        return """This test should not crash nor fail when reading packets with length from 250 to 255.
        However, note that undefined behavior cannot be tested.
        This test should be completed with code analysis.
        
        Furthermore, what is max limit?
        - according to §26 of "blue baseband hw spec (rev0.14)"
          in a packet, the length is a byte, so we could theorically put 255 (without encryption that takes 4 bytes for MIC)
          and BLE driver is hardcoded to 255+2
        - according to BLUETOOTH SPECIFICATION Version 5.0 | Vol 6, Part B page 2588:
            "The Length field of the Header indicates the length of the Payload and MIC if
            included. The length field has the range of 0 to 255 octets. The Payload field
            shall be less than or equal to 251 octets in length. The MIC is 4 octets in length."
            
        Thus, MAX payload length for unencrypted and encrypted packet is 251.
        
        Therefore we could expect the API function to return an error code (INVALID_PARAMETER_C0) but carry on transmission/reception at user's risks.
        To be defined.
        """
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        for payloadLength in range(250,256,1):
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL TRUE D D D D D D [" + str(payloadLength) + "]{0xFF*}",False)
            time.sleep(0.2) 
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL TRUE D D D D D D [" + str(payloadLength) +"]{0xFF*}",False)
                
            self.waitForEndOfCommand(0,60)
            self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
            self.checkThat("device 0 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(0,"\[OK\]") >= 1)
            self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is not INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 0)

            self.waitForEndOfCommand(1,60)
            self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
            self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
            self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is not INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 0)                    

"""
Stress 
"""
class RLV_TC__HAL_TXRX_Stress_Ack__nominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Characterize packet rate and check PER for regular txrx with ack and with default wakeup time and rcv windows"
        
    def getExpectedResult(self):
        return "PER should be < 5/1000"
 
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        rxReceiveWindow = 50000
        wakeupTime = 4000
        stressDurationInS = int(self.getTimeoutInS() - 10) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision

        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")

        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(int(stressDurationInS-rxReceiveWindow/(2*1000000))))
        self.sendQuickCommand(1,"TFW_Command__SetParam stressDurationInS " + str(int(stressDurationInS+rxReceiveWindow/(2*1000000))))#to be sure rx ends before tx to avoid infinite wait for rx
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(1,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        self.sendQuickCommand(1,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__RxStress_HAL")
        self.sendCommandAndListen(1,"BLE_Command__TxStress_HAL")   
        
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        self.waitForEndOfCommand(1,self.getTimeoutInS())
        
        receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","receiveCounter: " + str(receiveCounter))
        packetEqualCounter = self.getIntFrom(".*?packetEqualCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","packetEqualCounter: " + str(packetEqualCounter))
        
        sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","sendCounter: " + str(sendCounter))
        ackEqualCounter = self.getIntFrom(".*?ackEqualCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","ackEqualCounter: " + str(ackEqualCounter))
        
        rxPer = ((receiveCounter-packetEqualCounter)/receiveCounter)
        txPer = ((sendCounter-ackEqualCounter)/sendCounter)
        self.checkThat("RX PER is less than 5/1000 ({:.1f}/1000)".format(1000*rxPer), rxPer < (5/1000))
        self.checkThat("TX PER is less than 5/1000 ({:.1f}/1000)".format(1000*txPer), txPer < (5/1000))
        
class RLV_TC__HAL_TXRX_Stress_Ack__onlyRx(UATL_TestCase):#ready
  
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Characterize rx speed"
        
    def getExpectedResult(self):
        return "number of rx window started should be around stressDurationInS/(rxReceiveWindow+wakeupTime) +/- 10%"

    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
        

        rxReceiveWindow = 50000
        wakeupTime = 4000
        stressDurationInS = int(self.getTimeoutInS() - 20) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
       
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__RxStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
               
        receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","receiveCounter: " + str(receiveCounter))
        
        expectedAsked = 1000000 * stressDurationInS / (rxReceiveWindow + wakeupTime)
        self.checkThat("Number of rx window started should be around stressDurationInS/(rxReceiveWindow + wakeupTime) +/- 10% ({} vs {:.1f})".format(receiveCounter,expectedAsked), (receiveCounter >= expectedAsked * 0.9) and (receiveCounter <= expectedAsked * 1.1))

class RLV_TC__HAL_TXRX_Stress_Ack__onlyTx(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Characterize tx speed"
        
    def getExpectedResult(self):
        return "number of tx sequence started should be around stressDurationInS/wakeupTime +/- 10%"

    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
    
        txAckReceiveWindow = 50000
        wakeupTime = 4000
        stressDurationInS = int(self.getTimeoutInS() - 6) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
        
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(0,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(0,"TFW_Command__SetParam txAckReceiveWindow " + str(txAckReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__TxStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        
        sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","sendCounter: " + str(sendCounter))
        
        expectedAsked = 1000000 * stressDurationInS / (txAckReceiveWindow + wakeupTime)
        self.checkThat("Number of rx window started should be around stressDurationInS/txAckReceiveWindow + wakeupTime) +/- 10% ({} vs {:.1f})".format(sendCounter,expectedAsked), (sendCounter >= expectedAsked * 0.9) and (sendCounter <= expectedAsked * 1.1)) 
        
class RLV_CH__HAL_TXRX_Stress_Ack__rxDeltaTime_min(UATL_Characterization):#cancelled
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED

    def getObjective(self):
        return """Characterize minimum delay between 2 successfull rx,
        this test was created because there is a timeout on: RLV_TC__HAL_TXRX_Stress_Ack__onlyRx, RLV_TC__HAL_TXRX_Stress_Ack__nominal, RLV_TC__HAL_TXRX_PingPongStress_Ack__nominal
        See update, notes in RLV test: 'RLV_CH__RLV_doWithTimeout' that covers that bug.
        edit: After test env correction the stress test does succeed, this test is cancelled.
        """
        
    def getExpectedResult(self):
        return "If minimum delay is 0, ack timeouts from API (see procedure objectives) are still not expected but happen"

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        rxReceiveWindow = 50000
        txAckReceiveWindow = 50000
        wakeupTime = 4000
        
        rxStressDeltaBlockingDelayInUs_MAX = 100000
        rxStressDeltaBlockingDelayInUs_MIN = 0
        rxStressDeltaBlockingDelayInUs_STEP = int(rxStressDeltaBlockingDelayInUs_MAX/10)    
        
        commandTimeout = int(self.getTimeoutInS()/(rxStressDeltaBlockingDelayInUs_MAX/rxStressDeltaBlockingDelayInUs_STEP))
        stressDurationInS = int(commandTimeout - 3)  #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(1,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(1,"TFW_Command__SetParam txAckReceiveWindow " + str(txAckReceiveWindow))

        for rxStressDeltaBlockingDelayInUs in range(rxStressDeltaBlockingDelayInUs_MAX,rxStressDeltaBlockingDelayInUs_MIN-1,-rxStressDeltaBlockingDelayInUs_STEP):
            self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs " + str(rxStressDeltaBlockingDelayInUs))
            self.sendCommandAndListen(0,"BLE_Command__RxStress_HAL")
            self.sendCommandAndListen(1,"BLE_Command__TxStress_HAL")
            self.waitForEndOfCommand(0,self.getTimeoutInS())              
            self.waitForEndOfCommand(1,self.getTimeoutInS())
            
            receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
            UATL_debug("embeddedStress","receiveCounter: " + str(receiveCounter))

            if self.stopIf("RX device : we find receiveCounter, command has finished with success",self.numberOfRegexMatchesInLog(0,".*?receiveCounter\s+(\d+).*?") >= 1,"rxStressDeltaBlockingDelayInUs",rxStressDeltaBlockingDelayInUs):
                break

class RLV_TC__HAL_TXRX_Stress_NoAck__nominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Characterize packet rate and check PER for regular txrx with no ack and with default wakeup time and rcv windows."
        
    def getExpectedResult(self):
        return "PER should be < 5/1000.  Note that in this test, there will be a lot more tx than rx. tx are send as a long burst, we should see no timeout error"

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        rxReceiveWindow = 500000
        wakeupTime = 4000
        stressDurationInS = int(self.getTimeoutInS() - 3) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
        
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck FALSE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(1,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(1,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        self.sendQuickCommand(1,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        # self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [8]{0xFF*}")
        # self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [8]{0xFF*}")
        
        self.sendCommandAndListen(0,"BLE_Command__RxStress_HAL")
        time.sleep(0.2) 
        self.sendCommandAndListen(1,"BLE_Command__TxStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        self.waitForEndOfCommand(1,self.getTimeoutInS())
        
        receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","receiveCounter: " + str(receiveCounter))
        rxPacketEqualCounter = self.getIntFrom(".*?packetEqualCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxPacketEqualCounter: " + str(rxPacketEqualCounter))
        rxTimeoutErrorCounter = self.getIntFrom(".*?rxTimeoutErrorCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxTimeoutErrorCounter: " + str(rxTimeoutErrorCounter))
        
        sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","sendCounter: " + str(sendCounter))
        txSuccessCounter = self.getIntFrom(".*?txSuccessCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","txSuccessCounter: " + str(txSuccessCounter))
        
        per = ((receiveCounter-rxPacketEqualCounter)/sendCounter)
        self.checkThat("PER is less than 5/1000 ({:.1f}/1000)".format(1000*per), per < (5/1000))  
        self.checkThat("There is no timeout error", rxTimeoutErrorCounter == 0)  
              
class RLV_TC__HAL_TXRX_Stress_NoAck__onlyRx(UATL_TestCase):#ready
  
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Characterize rx speed when no ack"
        
    def getExpectedResult(self):
        return "number of rx window started should be around stressDurationInS/(rxReceiveWindow + wakeupTime) +/- 10%"
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
        
        rxReceiveWindow = 500000
        wakeupTime = 4000
        stressDurationInS = int(self.getTimeoutInS() - 3) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
        
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__RxStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        
        receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","receiveCounter: " + str(receiveCounter))
        
        expectedAsked = 1000000 * stressDurationInS / (rxReceiveWindow + wakeupTime)
        self.checkThat("Number of rx window started should be around stressDurationInS/(rxReceiveWindow + wakeupTime) +/- 10% ({} vs {:.1f})".format(receiveCounter,expectedAsked), (receiveCounter >= expectedAsked * 0.9) and (receiveCounter <= expectedAsked * 1.1))

class RLV_TC__HAL_TXRX_Stress_NoAck__onlyTx(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Characterize rx speed when no ack"
        
    def getExpectedResult(self):
        return "number of tx started should be around stressDurationInS/(wakeupTime) +/- 10%"
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
        
        txAckReceiveWindow = 0
        wakeupTime = 4000
        stressDurationInS = int(self.getTimeoutInS() - 3) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
        
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(0,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(0,"TFW_Command__SetParam txAckReceiveWindow " + str(txAckReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__TxStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        
        sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","sendCounter: " + str(sendCounter))
        
        expectedAsked = 1000000 * stressDurationInS / wakeupTime
        self.checkThat("Number of tx started should be around stressDurationInS/wakeupTime +/- 10% ({:.1f} vs {:.1f})".format(sendCounter,expectedAsked), (sendCounter >= expectedAsked * 0.9) and (sendCounter <= expectedAsked * 1.1))   

class RLV_TC__HAL_TXRX_PingPongStress_Ack__nominal(UATL_TestCase):#cancelled
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED

    def getObjective(self):
        return """Characterize packet rate rx and tx and check PER for regular txrx with ack and with default wakeup time and rcv windows.
        Ping pong method (we do not wait more than what we should). 
        However these test conditions are not correct as a tx + rx ack will follow a rx + tx ack then followed back by a tx + rx ack,
        thus, 2 tx and 2 rx will be following, which forbid any kind of synchronisation. For stress test with ack, only the classic stress test shall be used (one board for rx, one for tx)
        """
        
    def getExpectedResult(self):
        return "PER should be < 5/1000"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        rxReceiveWindow = 500000
        txAckReceiveWindow = 500000
        wakeupTime = 4000
        stressDurationInS = int(self.getTimeoutInS() - 3) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision

        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(1,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam txFirstInPingPong FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam txFirstInPingPong TRUE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(0,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(1,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        self.sendQuickCommand(0,"TFW_Command__SetParam txAckReceiveWindow " + str(txAckReceiveWindow))
        self.sendQuickCommand(1,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        self.sendQuickCommand(1,"TFW_Command__SetParam txAckReceiveWindow " + str(txAckReceiveWindow))
                
        self.sendCommandAndListen(0,"BLE_Command__PingPongStress_HAL")
        time.sleep(0.2) 
        self.sendCommandAndListen(1,"BLE_Command__PingPongStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        self.waitForEndOfCommand(1,self.getTimeoutInS())
        
        board1receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","board1receiveCounter: " + str(board1receiveCounter))
        board1RxPacketEqualCounter = self.getIntFrom(".*?packetEqualCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","board1RxPacketEqualCounter: " + str(board1RxPacketEqualCounter))
        
        board1sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","board1sendCounter: " + str(board1sendCounter))
        board1TxAckPacketEqualCounter = self.getIntFrom(".*?ackEqualCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","board1TxAckPacketEqualCounter: " + str(board1TxAckPacketEqualCounter))
                
        board2receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","board2receiveCounter: " + str(board2receiveCounter))
        board2RxPacketEqualCounter = self.getIntFrom(".*?packetEqualCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","board2RxPacketEqualCounter: " + str(board2RxPacketEqualCounter))
        
        board2sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","board2sendCounter: " + str(board2sendCounter))
        board2TxAckPacketEqualCounter = self.getIntFrom(".*?ackEqualCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","board2TxAckPacketEqualCounter: " + str(board2TxAckPacketEqualCounter))
        
        rxPer = ((board1receiveCounter + board2receiveCounter - board1RxPacketEqualCounter - board2RxPacketEqualCounter)/ (board1receiveCounter + board2receiveCounter))
        txPer = ((board1sendCounter + board2sendCounter - board1TxAckPacketEqualCounter - board2TxAckPacketEqualCounter)/ (board1sendCounter + board2sendCounter))
        self.checkThat("RX PER is less than 5/1000 ({:.1f}/1000)".format(1000*rxPer), rxPer < (5/1000))
        self.checkThat("TX PER is less than 5/1000 ({:.1f}/1000)".format(1000*txPer), txPer < (5/1000))              

class RLV_TC__HAL_TXRX_PingPongStress_NoAck__nominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Characterize packet rate rx and tx and check PER for regular txrx without ack and with default wakeup time and rcv windows. Ping pong method (we do not wait more than what we should)"
        
    def getExpectedResult(self):
        return "PER should be < 5/1000"

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        rxReceiveWindow = 500000
        txAckReceiveWindow = 500000
        wakeupTime = 4000
        stressDurationInS = int(self.getTimeoutInS() - 3) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
        
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck FALSE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(1,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam txFirstInPingPong FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam txFirstInPingPong TRUE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(0,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")

        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(1,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        self.sendQuickCommand(0,"TFW_Command__SetParam txAckReceiveWindow " + str(txAckReceiveWindow))
        self.sendQuickCommand(1,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        self.sendQuickCommand(1,"TFW_Command__SetParam txAckReceiveWindow " + str(txAckReceiveWindow))
                
        self.sendCommandAndListen(0,"BLE_Command__PingPongStress_HAL")
        time.sleep(0.2) 
        self.sendCommandAndListen(1,"BLE_Command__PingPongStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        self.waitForEndOfCommand(1,self.getTimeoutInS())
        
        board1receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","board1receiveCounter: " + str(board1receiveCounter))
        board1RxPacketEqualCounter = self.getIntFrom(".*?packetEqualCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","board1RxPacketEqualCounter: " + str(board1RxPacketEqualCounter))
        
        board1sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","board1sendCounter: " + str(board1sendCounter))
                
        board2receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","board2receiveCounter: " + str(board2receiveCounter))
        board2RxPacketEqualCounter = self.getIntFrom(".*?packetEqualCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","board2RxPacketEqualCounter: " + str(board2RxPacketEqualCounter))
        
        board2sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","board2sendCounter: " + str(board2sendCounter))
        
        per = (((board1sendCounter + board2sendCounter) - (board1RxPacketEqualCounter + board2RxPacketEqualCounter)) / (board1sendCounter + board2sendCounter))
        self.checkThat("PER is less than 5/1000 ({:.1f}/1000)".format(1000*per), per < (5/1000))
       
class RLV_TC__HAL_TXRX_Stress_WithEncrypt_NoAck__nominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Characterize packet rate and check PER for encrypted txrx with no ack and with default wakeup time and rcv windows."
        
    def getExpectedResult(self):
        return "PER should be < 5/1000.  Note that in this test, there will be a lot more tx than rx. tx are send as a long burst, we should see no timeout error"

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        rxReceiveWindow = 500000
        wakeupTime = 4000
        stressDurationInS = int(self.getTimeoutInS() - 3) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
        
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus ENABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck FALSE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(1,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(1,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        self.sendQuickCommand(1,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__RxStress_HAL")
        time.sleep(0.2) 
        self.sendCommandAndListen(1,"BLE_Command__TxStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        self.waitForEndOfCommand(1,self.getTimeoutInS())
        
        receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","receiveCounter: " + str(receiveCounter))
        rxPacketEqualCounter = self.getIntFrom(".*?packetEqualCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxPacketEqualCounter: " + str(rxPacketEqualCounter))
        rxTimeoutErrorCounter = self.getIntFrom(".*?rxTimeoutErrorCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxTimeoutErrorCounter: " + str(rxTimeoutErrorCounter))
        
        
        
        sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","sendCounter: " + str(sendCounter))
        txSuccessCounter = self.getIntFrom(".*?txSuccessCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","txSuccessCounter: " + str(txSuccessCounter))
        
        per = ((receiveCounter-rxPacketEqualCounter)/sendCounter)
        self.checkThat("PER is less than 5/1000 ({:.1f}/1000)".format(1000*per), per < (5/1000))  
        self.checkThat("There is no timeout error", rxTimeoutErrorCounter == 0)  
        
class RLV_TC__HAL_TXRX_Stress_NoAck_xtal_disabled(UATL_TestCase):#ready, but only on WB35 and WB15
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check effect of LLD_BLE_CrystalCheck over a long period of time in stress conditions. 
        Warning: on WB35 and WB15 only, will not work on WB55: 'For Dory and LittleDory the LSI2 won’t be used, 
        due to a jitter issue that leads to a low accuracy of the LSI2 frequency on some units.
        In TinyDory the design has been improved and the frequency accuracy is better. 
        So, for TinyDory the plan is to allow the customer use the LSI2' (quote from E.CHATAIGNER 17/06/20) """
        
    def getExpectedResult(self):
        return "Still not sure what to expect....I guess this shall work worse than with calling LLD_BLE_CrystalCheck. But how long shall we test it to see any difference? "
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
            
        rxReceiveWindow = 100000
        wakeupTime = 4000000
        stressDurationInS = int((self.getTimeoutInS() - 3)/3) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
        
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
                
        #change interal RC (1 by default) to external xtal (0)
        self.sendQuickCommand(0,"TFW_Command__SetParam lowSpeedOsc 1")
        self.sendQuickCommand(1,"TFW_Command__SetParam lowSpeedOsc 1")
        
        #change crystal check enabled after a tx or a rx (true by default) to false
        self.sendQuickCommand(0,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck FALSE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(1,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(1,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        self.sendQuickCommand(1,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__RxStress_HAL")
        self.sendCommandAndListen(1,"BLE_Command__TxStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        self.waitForEndOfCommand(1,self.getTimeoutInS())
        
        receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","receiveCounter: " + str(receiveCounter))
        rxPacketEqualCounter = self.getIntFrom(".*?packetEqualCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxPacketEqualCounter: " + str(rxPacketEqualCounter))
        rxTimeoutErrorCounter = self.getIntFrom(".*?rxTimeoutErrorCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxTimeoutErrorCounter: " + str(rxTimeoutErrorCounter))
        
        sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","sendCounter: " + str(sendCounter))
        txSuccessCounter = self.getIntFrom(".*?txSuccessCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","txSuccessCounter: " + str(txSuccessCounter))
        
        per = ((receiveCounter-rxPacketEqualCounter)/sendCounter)
        self.checkThat("PER is less than 5/1000 ({:.1f}/1000)".format(1000*per), per < (5/1000))
        self.checkThat("There is no timeout error", rxTimeoutErrorCounter == 0)  
        
        
        #change interal RC (1 by default) to external xtal (0)
        self.sendQuickCommand(0,"TFW_Command__SetParam lowSpeedOsc 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam lowSpeedOsc 0")
        
        #change crystal check enabled after a tx or a rx (true by default) to false
        self.sendQuickCommand(0,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam crystalCheckEnabled FALSE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck FALSE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(1,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(1,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        self.sendQuickCommand(1,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__RxStress_HAL")
        self.sendCommandAndListen(1,"BLE_Command__TxStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        self.waitForEndOfCommand(1,self.getTimeoutInS())
        
        receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","receiveCounter: " + str(receiveCounter))
        rxPacketEqualCounter = self.getIntFrom(".*?packetEqualCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxPacketEqualCounter: " + str(rxPacketEqualCounter))
        rxTimeoutErrorCounter = self.getIntFrom(".*?rxTimeoutErrorCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxTimeoutErrorCounter: " + str(rxTimeoutErrorCounter))
        
        sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","sendCounter: " + str(sendCounter))
        txSuccessCounter = self.getIntFrom(".*?txSuccessCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","txSuccessCounter: " + str(txSuccessCounter))
        
        per = ((receiveCounter-rxPacketEqualCounter)/sendCounter)
        self.checkThat("PER is more than 5/1000 ({:.1f}/1000)".format(1000*per), per > (5/1000))
        self.checkThat("There is no timeout error", rxTimeoutErrorCounter == 0)  
        
        
        #change interal RC (1 by default) to external xtal (0)
        self.sendQuickCommand(0,"TFW_Command__SetParam lowSpeedOsc 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam lowSpeedOsc 0")
        
        #change crystal check enabled after a tx or a rx (true by default) to false
        self.sendQuickCommand(0,"TFW_Command__SetParam crystalCheckEnabled TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam crystalCheckEnabled TRUE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck FALSE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(1,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(1,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(1,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        self.sendQuickCommand(1,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__RxStress_HAL")
        self.sendCommandAndListen(1,"BLE_Command__TxStress_HAL")
        self.waitForEndOfCommand(0,self.getTimeoutInS())
        self.waitForEndOfCommand(1,self.getTimeoutInS())
        
        receiveCounter = self.getIntFrom(".*?receiveCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","receiveCounter: " + str(receiveCounter))
        rxPacketEqualCounter = self.getIntFrom(".*?packetEqualCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxPacketEqualCounter: " + str(rxPacketEqualCounter))
        rxTimeoutErrorCounter = self.getIntFrom(".*?rxTimeoutErrorCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxTimeoutErrorCounter: " + str(rxTimeoutErrorCounter))
        
        sendCounter = self.getIntFrom(".*?sendCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","sendCounter: " + str(sendCounter))
        txSuccessCounter = self.getIntFrom(".*?txSuccessCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","txSuccessCounter: " + str(txSuccessCounter))
        
        per = ((receiveCounter-rxPacketEqualCounter)/sendCounter)
        self.checkThat("PER is less than 5/1000 ({:.1f}/1000)".format(1000*per), per < (5/1000))
        self.checkThat("There is no timeout error", rxTimeoutErrorCounter == 0)  
"""
LLD NO AP CHAINING
--------------------------
RLV_TC__LLD_TXRX_Simple__nominal
RLV_EN__LLD_TXRX_Simple__nominal
RLV_TC__LLD_TXRX_Simple__wrong_channel
RLV_TC__LLD_TXRX_Simple__wrong_header
RLV_TC__LLD_TXRX_Simple__wrong_payloadLength
RLV_TC__LLD_TXRX_Simple__wrong_payloadContent
"""


"""
LLD rxtx
"""
class RLV_TC__LLD_TXRX_Simple__nominal(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Check that a simple txrx works with predefined embedded default value using lld functions"
        
    def getExpectedResult(self):
        return "The rx command shall return a correct payload and no error, the tx command shall no error"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)

class RLV_EN__LLD_TXRX_Simple__nominal(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a simple txrx using LLD works, and repeat operation over time. Board are initialized before each rx/tx"
        
    def getExpectedResult(self):
        return "The rx command shall return a correct payload and no error and the tx command shall return no error, otherwise endurance counter is incremented. "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
      
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket", False, True)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket", False, True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)
          
class RLV_TC__LLD_TXRX_Simple__wrong_channel(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that, when using lld, the transmission fails if the channel from tx packet is not the same as the one that rx expects"
        
    def getExpectedResult(self):
        return "This test should fail when reading packet and pass when sending packet"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"TFW_Command__SetParam channel 30")
        self.sendQuickCommand(1,"TFW_Command__SetParam channel 31")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
       
class RLV_TC__LLD_TXRX_Simple__wrong_header(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that, when using lld, the transmission fails if the header from tx packet is not the same as the one that rx expects"
        
    def getExpectedResult(self):
        return "This test should fail when reading packet and pass when sending packet"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedHeader 0xFF")
        self.sendQuickCommand(1,"TFW_Command__SetParam txHeader 0x00")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are not equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
class RLV_TC__LLD_TXRX_Simple__wrong_payloadLength(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that, using lld, when the length differs from the transmitted packet and the expected packet, command should fail checking length"
        
    def getExpectedResult(self):
        return "This test should fail when reading packet (payloadLength not equal)"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [7]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [8]{0xFF*}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [8]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [7]{0xFF*}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [8]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [8]{0xFF*}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
class RLV_TC__LLD_TXRX_Simple__wrong_payloadContent(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that, using lld, when the payload differs from the transmitted packet and the expected packet, command should fail checking payload"
        
    def getExpectedResult(self):
        return "This test should fail when reading packet (payload content not equal)"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
    
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [30]{0x55*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [30]{0xAA*}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[FAILED\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
                 
class RLV_TC__LLD_TXRX_simple__limits_stateMachine(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Check that state machine can be changed within its range"
        
    def getExpectedResult(self):
        return "TX RX shall work on each channel in the range [0;7]"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        for apStateMachineId in range(0,8):
            self.sendQuickCommand(0,"TFW_Command__SetParam apStateMachineId " + str(apStateMachineId))
            self.sendQuickCommand(1,"TFW_Command__SetParam apStateMachineId " + str(apStateMachineId))
            
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*pendingAction .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.checkThat("TX RX successful with apStateMachineId ({})".format(apStateMachineId),txRxSuccessful)
            
class RLV_TC__LLD_TXRX_simple__different_stateMachine(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Check that state machine can different between rx and tx for it to work"
        
    def getExpectedResult(self):
        return "Start a RX with state machine 3, start a TX with state machine 5, RX shall be successful."
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendQuickCommand(0,"TFW_Command__SetParam apStateMachineId 3")
        self.sendQuickCommand(1,"TFW_Command__SetParam apStateMachineId 5")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
            
class RLV_TC__LLD_TXRX_simple__multiple_stateMachine(UATL_TestCase): #TBI with chaining
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.TO_BE_IMPLEMENTED

    def getObjective(self):
        return "Check that multiple state machines can run at the same time"
        
    def getExpectedResult(self):
        return "xxxxx."
        
    def __callCliCommandsAndDoChecks__(self):
        UATL_log("To be implemented with chaining")


"""
LLD get status
"""
class RLV_TC__LLD_GetStatus__idle(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Check that blue controller is in BLUE_IDLE_0 after a successful init"
        
    def getExpectedResult(self):
        return "init shall be successful, and then a get status shall return BLUE_IDLE_0"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        self.checkThat("device 0 : no FAILED during init",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 1 : no FAILED during init",self.numberOfRegexMatchesInLog(1,".*\[FAILED\].*") == 0)

        self.sendCommandAndListen(0,"BLE_Command__GetStatus")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_IDLE_0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x00.*") == 1)
              
class RLV_TC__LLD_GetStatus__wakeup(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Make a get status when blue controller is in wakeup status, so we can have the return code: 'BLUE_BUSY_WAKEUP'"
        
    def getExpectedResult(self):
        return """After a successful init, when calling get status just after the rx action is called, 
        and before the end of the wakeup, get status shall return 'BLUE_BUSY_WAKEUP'"""
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        rxReceiveWindow = 4000000
      
        self.sendQuickCommand(0,"TFW_Command__SetParam isGetStatusWhileBlockingCommandEnabled TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam delayBeforeCallingFlashCommand 0") 
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket")
        #self.sendCommandAndListen(0,"BLE_Command__GetStatus")  --> see isGetStatusWhileBlockingCommandEnabled
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_BUSY_WAKEUP",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x03.*") == 1)
        self.sendCommandAndListen(1,"BLE_Command__SendOnePacket")
        self.waitForEndOfCommand(1,60)
        self.sendCommandAndListen(0,"BLE_Command__GetStatus")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_IDLE_0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x00.*") == 1)
    
class RLV_TC__LLD_GetStatus__noWakeupT1(UATL_TestCase): #need spec info, to be run only on WB35 and WB15 
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.NEED_SPEC_INFO

    def getObjective(self):
        return "Check that blue controller is in BLUE_BUSY_NOWAKEUP_T1 after '??'."
        
    def getExpectedResult(self):
        return "init shall be successful, and then, after '??', a get status shall return BLUE_BUSY_NOWAKEUP_T1"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        rxReceiveWindow = 4000000
        
        self.sendQuickCommand(0,"TFW_Command__SetParam isGetStatusWhileBlockingCommandEnabled TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam delayBeforeCallingFlashCommand " + str(int(rxReceiveWindow*2)))# more than rxReceiveWindow 
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket")
        #self.sendCommandAndListen(0,"BLE_Command__GetStatus") --> see isGetStatusWhileBlockingCommandEnabled
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_BUSY_NOWAKEUP_T1",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x02.*") == 1)
        self.sendCommandAndListen(1,"BLE_Command__SendOnePacket")
        self.waitForEndOfCommand(1,60)
        self.sendCommandAndListen(0,"BLE_Command__GetStatus")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_IDLE_0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x00.*") == 1)
                           
class RLV_TC__LLD_GetStatus__noWakeupT2_duringWindow(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN


    def getObjective(self):
        return "Check that blue controller is in BLUE_BUSY_NOWAKEUP_T2 during a rx window"
        
    def getExpectedResult(self):
        return "init shall be successful, and then, during a rx window, a get status shall return BLUE_BUSY_NOWAKEUP_T2"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        rxReceiveWindow = 4000000
                        
        self.sendQuickCommand(0,"TFW_Command__SetParam isGetStatusWhileBlockingCommandEnabled TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam delayBeforeCallingFlashCommand " + str(int(rxReceiveWindow*0.5)))# less than rxReceiveWindow 
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket")
        #self.sendCommandAndListen(0,"BLE_Command__GetStatus") --> see isGetStatusWhileBlockingCommandEnabled
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_BUSY_NOWAKEUP_T2",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x02.*") == 1)
        self.sendCommandAndListen(1,"BLE_Command__SendOnePacket")
        self.waitForEndOfCommand(1,60)
        self.sendCommandAndListen(0,"BLE_Command__GetStatus")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_IDLE_0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x00.*") == 1)

class RLV_TC__LLD_GetStatus__noWakeupT2_betweenPackets(UATL_TestCase): #TBI with chaining
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.TO_BE_IMPLEMENTED


    def getObjective(self):
        return """Check that blue controller is in BLUE_BUSY_NOWAKEUP_T2 during a packet chain, between two action packet 
        
        Device 0                                      Device 1                                 
            ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐ 
        ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │      │ Ap 2 ├─T/F─►│ Ap 3 ├──T──►│ Ap 4 ├─T/F─►│ Ap 0 │ 
        └─F─┤  RX  │      │  TX  │      │  END │      │  TX  │◄──F──┤  RX  │      │  TX  │      │  END │ 
         ↓  └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘ 
      Call       |             |                           |          |               |                               
      GetStatus  |             ↓                           |          |               ↓                       
      here       |        DR triggers success              |          |           DR triggers success      
                 ↓             to release cmd              ↓          ↓                to release cmd
     DR just returns True.                             DR just returns True.                          
     CR returns true if RX                             CR just returns True                       
     packet is as expected.                                
        
        1/ First, we try with a backToBackTime at 0, and a rxReceiveWindow at 4s, and we start the D1/AP2/TX,
        so we can have the D0 (AP3) success easily triggered, getStatus shall not be called
        
        2/ Then we run only D0/AP2/RX and we don't start the D0/AP2/TX so we can see that D0 (AP3) success is not triggered.
        
        3/ Then we run the D0/AP2/RX and we start the D0/AP2/TX during the backToBackTime 
        For this case, rxWindows of D0/AP2 is very very short (0 would do it)
        and backToBackTime of D0/AP2 is very long (4s is correct)
        The aim is to have a getStatus called during those 4s of B2B (D0/AP2-AP2) so we can get BLUE_BUSY_NOWAKEUP_T2.
        So it will be easy to call the D1 a few ms after we called the D0 so we can get success triggered on both devices,
        and then check getStatus.
        
       """
        
    def getExpectedResult(self):
        return "init shall be successful, and then, during a packet chain, between 2 packets, a get status shall return BLUE_BUSY_NOWAKEUP_T2"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam backToBackTime 0")
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow 4000000")
        
        """
        Device 0
        """
        self.sendCommandAndListen(0,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(0,60)
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(0,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(0,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x04,0x05,0x06} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    []{0x01,0x02,0x03} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [0]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      rxExpectedPayload                    []{0x04,0x05,0x06} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x01,0x02,0x03} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        
        
        """
        Run it
        """
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #build action packet chain from buffer
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction.*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction.*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        
        
        #run only rx and wait more than rxReceiveWindow and less than rxReceiveWindow + backToBackTime
        self.sendQuickCommand(0,"TFW_Command__SetParam backToBackTime 4000000")
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow 0")
        
        
        self.sendQuickCommand(0,"TFW_Command__SetParam backToBackTime 4000000")
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        
        self.checkThat("this will not work, we need to insert getStatus call during the wait of the command.",False)
        
        #self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_BUSY_NOWAKEUP_T2",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x02.*") == 1)

        
"""
LLD stop activity
"""             
class RLV_TC__LLD_StopActivity__duringTone(UATL_TestCase): #need spec info: In what status shall controller be during a tone?
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.NEED_SPEC_INFO

    def getObjective(self):
        return "Check that stop activity stops the tone"
        
    def getExpectedResult(self):
        return "TBC"
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):        
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendCommandAndListen(0,"BLE_Command__StartTone")
        self.waitForEndOfCommand(0,60)
        self.sendCommandAndListen(0,"BLE_Command__GetStatus")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is not BLUE_IDLE_0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x00.*") == 0)
        self.sendCommandAndListen(0,"BLE_Command__StopActivity")
        self.waitForEndOfCommand(0,60)
        self.sendCommandAndListen(0,"BLE_Command__GetStatus")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_IDLE_0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x00.*") == 1)

class RLV_TC__LLD_StopActivity__duringWindow(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Check that stop activity stops a pending rx"
        
    def getExpectedResult(self):
        return "when stopping activity during a rx window and then sending a packet, packet shall not be received"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        rxReceiveWindow = 4000000
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket")
        self.sendCommandAndListen(1,"BLE_Command__SendOnePacket")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
        
        self.sendQuickCommand(0,"TFW_Command__SetParam isStopActivityWhileBlockingCommandEnabled TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam delayBeforeCallingFlashCommand " + str(int(rxReceiveWindow*0.5)))# less than rxReceiveWindow 
        
        self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket")
        #self.sendCommandAndListen(0,"BLE_Command__StopActivity") --> see isStopActivityWhileBlockingCommandEnabled
        self.sendCommandAndListen(1,"BLE_Command__SendOnePacket")
        time.sleep(rxReceiveWindow/1000000) #to be sure window has expired
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0 : pendingAction is [FAILED]",self.numberOfRegexMatchesInLog(0,".*pendingAction .*\[FAILED\].*") == 1)
        self.checkThat("device 0 : actionFailed is [FAILED]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
             
class RLV_TC__LLD_StopActivity__betweenPackets(UATL_TestCase): #TBI with chaining
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.TO_BE_IMPLEMENTED

    def getObjective(self):
        return "Check that stop activity stops a chained rx between two rx window"
        
    def getExpectedResult(self):
        return "when stopping activity during a rx window and then sending a packet, packet shall not be received"
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        rxReceiveWindow = 4000000
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
                
        self.sendQuickCommand(0,"TFW_Command__SetParam isStopActivityWhileBlockingCommandEnabled TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam delayBeforeCallingFlashCommand " + str(int(rxReceiveWindow*0.5)))# less than rxReceiveWindow 


"""
LLD start and stop tone
"""      
class RLV_TC__LLD_Tone(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return "Check that stop tone stops the start tone"
        
    def getExpectedResult(self):
        return """Before a start tone, get status shall return idle,
        after doing a start tone, get status shall not return idle,
        then after a following stop tone, get status shall return idle."""
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")        
        self.sendCommandAndListen(0,"BLE_Command__GetStatus")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_IDLE_0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x00.*") == 1)
        self.sendCommandAndListen(0,"BLE_Command__StartTone")
        self.waitForEndOfCommand(0,60)
        self.sendCommandAndListen(0,"BLE_Command__GetStatus")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is not BLUE_IDLE_0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x00.*") == 0)
        self.sendCommandAndListen(0,"BLE_Command__StopTone")
        self.waitForEndOfCommand(0,60)
        self.sendCommandAndListen(0,"BLE_Command__GetStatus")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : returnValue for 'LLD_BLE_GetStatus' is BLUE_IDLE_0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'LLD_BLE_GetStatus' = 0x00.*") == 1)
  
"""
tx power and RSSI
"""    
class RLV_TC__HAL_TXRX_NoAck__rssiOnAllChannels(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that every channel works"
        
    def getExpectedResult(self):
        return "For each step, there shall be no error and packet shall be received "
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
    
        self.sendQuickCommand(0,"TFW_Command__SetParam showRssi TRUE")
        
        rssi = [0xFFFFFFFF]*40
        for channel in range(0,40,1):
            failureCounter = 0
            while True:
                self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D "+str(channel)+" D D D D D D",False,True)
                time.sleep(0.1)
                self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D "+str(channel)+" D D D D D D",False,True)
        
                self.waitForEndOfCommand(0,60)
                self.waitForEndOfCommand(1,60)
                txrxSuccess = (self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0) and (self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0) and (self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
                if not txrxSuccess:
                    failureCounter += 1
                    UATL_log("Channel {} retry".format(channel))
                else:
                    rssi[channel] = self.getIntFrom(".*?RSSI\s+:\s+\[(\d+)\].*?",0)
                    break
                if (failureCounter >= 3):
                    break
        spaceBeforeRssiArray=" "*10
        UATL_log(spaceBeforeRssiArray + "┌{:─^10}┬{:─^10}┐".format("",""))
        UATL_log(spaceBeforeRssiArray + "|{: ^10}|{: ^10}|".format("RSSI","Channel"))
        UATL_log(spaceBeforeRssiArray + "├{:─^10}┼{:─^10}┤".format("",""))
        for channel in range(0,40,1):
            UATL_log(spaceBeforeRssiArray + "|{: ^10}|{: ^10}|".format("N.C." if rssi[channel] == 0xFFFFFFFF else rssi[channel],channel))
        UATL_log(spaceBeforeRssiArray + "└{:─^10}┴{:─^10}┘".format("",""))
        for channel in range(0,40,1):
            self.checkThat("RSSI is valid for channel {}".format(channel), (rssi[channel] != 0xFFFFFFFF) and (rssi[channel] != 127))

class RLV_TC__LLD_TxPower_startTone(UATL_TestCase): #TBI - get with RSSI
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.TO_BE_IMPLEMENTED

    def getObjective(self):
        return """Check that tx power is compliant with the following table and that rssi gives 'correct' results :
        int   power
        0x0    -18  dBm
        0x1    -15  dBm
        0x2    -12  dBm
        0x3    -9   dBm
        0x4    -6   dBm
        0x5    -2   dBm
        0x6    0    dBm
        0x7    5    dBm
        0x8    -14  dBm
        0x9    -11  dBm
        0xA    -8   dBm
        0xB    -5   dBm
        0xC    -2   dBm
        0xD    2    dBm
        0xE    4    dBm
        0xF    8    dBm   
        
        Functions tests shall be LLD_BLE_StartTone() and LLD_BLE_SetTxPower()
        """
        
    def getExpectedResult(self):
        return """When reading RSSI after a board that set its power signal following the reference table given in test objective,
        then the output table shall correspond with a precision of 20% to the reference table.
        """
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        # self.sendQuickCommand(0,"LLD_BLE_StartTone")
        # self.sendQuickCommand(0,"LLD_BLE_SetTxPower")
        self.checkThat("To be implemented",False)
 
class RLV_TC__LLD_TxPower_simpleTx(UATL_TestCase): #TBI - get with RSSI
    def getVersion(self):
        return "v0.1"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.TO_BE_IMPLEMENTED

    def getObjective(self):
        return """Check that tx power is compliant with the following table and that rssi gives 'correct' results :
        int   power
        0x0    -18  dBm
        0x1    -15  dBm
        0x2    -12  dBm
        0x3    -9   dBm
        0x4    -6   dBm
        0x5    -2   dBm
        0x6    0    dBm
        0x7    5    dBm
        0x8    -14  dBm
        0x9    -11  dBm
        0xA    -8   dBm
        0xB    -5   dBm
        0xC    -2   dBm
        0xD    2    dBm
        0xE    4    dBm
        0xF    8    dBm   
        
        Functions tests shall be LLD_BLE_StartTone() and LLD_BLE_SetTxPower()
        """
        
    def getExpectedResult(self):
        return """When reading RSSI after a board that set its power signal following the reference table given in test objective,
        then the output table shall correspond with a precision of 20% to the reference table.
        """
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        # self.sendQuickCommand(0,"LLD_BLE_StartTone")
        # self.sendQuickCommand(0,"LLD_BLE_SetTxPower")
        self.checkThat("To be implemented",False)
   
   
"""
LLD Encryption
"""
class RLV_TC__HAL_TXRX_WithEncrypt_NoAck__nominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a simple txrx with init works with and without encryption."
        
    def getExpectedResult(self):
        return "The rx command shall return a correct payload and no error, the tx command shall no error when both sides are using encryption or not using encryption, otherwise it shall fail"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
    
        #both disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus DISABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus DISABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
               
        #both enabled
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus ENABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
        # rx enabled, tx disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus ENABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus DISABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
        
        
        # tx enabled, rx disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus DISABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
  
class RLV_EN__HAL_TXRX_WithEncrypt_NoAck__nominal(UATL_Endurance):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that an init + tx with ack and init + rx with ack (both encryption enabled) works for a long period of time. "
        
    def getExpectedResult(self):
        return "The rx and tx command shall receive payload and return no error , otherwise endurance counter is incremented. PER shall be < 5/1000"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
      
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus ENABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
     
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld")
        
        while self.isActive():
            self.sendCommandAndListen(0,"BLE_Command__WaitForAPacket_HAL", False, True)
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__SendOnePacket_HAL", False, True)

            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.serialLoopStep("TX RX successful",txRxSuccessful)

class RLV_TC__HAL_TXRX_WithEncrypt_NoAck__wrong_encryptKey(UATL_TestCase):#ready 
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that encryption does not work when encryption key differs from rx to tx."
        
    def getExpectedResult(self):
        return "The full packet shall not be received and decrypted if rx and tx do not share the same encrypt key, otherwise full packet shall be received and decrypted "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload     [30]{0xFF*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus         ENABLE")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptKey            []{0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0xFF,0xFF}")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload             [30]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus         ENABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptKey            []{0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0xFF,0xFF}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
        #changing only one encryption key
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptKey            []{0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0xAA,0xAA}")     
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
  
class RLV_TC__HAL_TXRX_WithEncrypt_NoAck__wrong_initVector(UATL_TestCase):#ready 
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that encryption does not work when IV differs from rx to tx."
        
    def getExpectedResult(self):
        return "The full packet shall not be received and decrypted if rx and tx do not share the same IV, otherwise full packet shall be received and decrypted "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload     [30]{0xFF*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus         ENABLE")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptInitVector     [8]{0xFF*}")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload             [30]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus         ENABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptInitVector     [8]{0xFF*}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
        #changing only one IV
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptInitVector     [8]{0x0F*}")    
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
        #changing the second IV to the same as the first
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptInitVector     [8]{0x0F*}")    
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
         
class RLV_TC__HAL_TXRX_WithEncrypt_NoAck__standaloneEncryption(UATL_TestCase):#cancelled
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return "Compare encryption via HAL_BLE_SendPacket and LLD_BLE_EncryptPlainData. Cancelled, this does not work this way, see RLV_TC__LLD_standaloneEncryption__nominal"
        
    def getExpectedResult(self):
        return "This test should not crash program."
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        data = "[32]{0xFF*}"
        
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptRxDataAndCompareWithExpected TRUE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam txPayload " + data)
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload " + data)
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus DISABLE")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload " + data)
        self.sendQuickCommand(1,"TFW_Command__SetParam rxExpectedPayload " + data)
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
class RLV_TC__HAL_TXRX_WithEncrypt_Ack__nominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that a txrx with ack works"
        
    def getExpectedResult(self):
        return """tx with ack to rx with no ack, this should fail, 
          then tx with ack to rx with ack, this should work
          then tx with no ack to rx with ack, this should work (useless though)"""

    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        
        
        #both disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus DISABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus DISABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
       
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        
        
        #both enabled
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus ENABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
       
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        
        
        # rx enabled, tx disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus ENABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus DISABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
       
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : headers are equal",self.numberOfRegexMatchesInLog(1,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 1 : lengths are not equal",self.numberOfRegexMatchesInLog(1,".*Checking length.*\[OK\].*") == 0)
        self.checkThat("device 1 : payloads are not equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 0)
        
        
        # tx enabled, rx disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus DISABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
       
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : headers are equal",self.numberOfRegexMatchesInLog(1,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 1 : lengths are not equal",self.numberOfRegexMatchesInLog(1,".*Checking length.*\[OK\].*") == 0)
        self.checkThat("device 1 : payloads are not equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 0)

class RLV_TC__LLD_TXRX_WithEncrypt__nominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that encryption does work for simple use case. Warning, when using encryption the user shall add 4 bytes to the length when sending and remove 4 bytes when receiving"
        
    def getExpectedResult(self):
        return "The full packet shall be received and decrypted if rx and tx are both , using encryption or are both not using encryption, otherwise error shall occur "
       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        #tx rx flags enabled
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload     [30]{0xFF*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus         ENABLE")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptRxCounter      []{0x0,0x0,0x0,0x0,0x0}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptTxCounter      []{0x0,0x0,0x0,0x0,0x0}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptInitVector     []{0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptKey            []{0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0xFF,0xFF}")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload             [30]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus         ENABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptRxCounter      []{0x0,0x0,0x0,0x0,0x0}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptTxCounter      []{0x0,0x0,0x0,0x0,0x0}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptInitVector     []{0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptKey            []{0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0xFF,0xFF}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
        #tx rx flags disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [30]{0xFF*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus DISABLE")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [30]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus DISABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
        
        #tx flags enabled rx flags disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [30]{0xFF*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus DISABLE")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [30]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
        
        #tx flags enabled rx flags disabled
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [30]{0xFF*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [30]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus DISABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
        
        
        #tx flags enabled for TX device, rx flags enabled for RX device
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [30]{0xFF*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [30]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
class RLV_TC__LLD_TXRX_WithEncrypt__wrong_encryptKey(UATL_TestCase):#ready 
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that encryption does not work when encryption key differs from rx to tx."
        
    def getExpectedResult(self):
        return "The full packet shall not be received and decrypted if rx and tx do not share the same encrypt key, otherwise full packet shall be received and decrypted "
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload     [30]{0xFF*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus         ENABLE")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptKey            []{0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0xFF,0xFF}")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload             [30]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus         ENABLE")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptKey            []{0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0xFF,0xFF}")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
        #changing only one encryption key
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptKey            []{0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0xAA,0xAA}")     
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 
        
class RLV_TC__LLD_TXRX_WithEncrypt__limits_payloadLength_max(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that program does not crash if payload length is reaching max limit while using encryption, encryption use part of the payload (4 bytes for MIC). Max lenght is 251 when encryption is enabled."
        
    def getExpectedResult(self):
        return "This test should not crash program."
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        for payloadLength in range(247,252,1):
            self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [" + str(payloadLength) + "]{0xFF*}")
            self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus ENABLE")
            
            self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [" + str(payloadLength) + "]{0xFF*}")
            self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
            
            self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
            time.sleep(0.2)
            self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

            self.waitForEndOfCommand(0,60)
            self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
            self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
            self.waitForEndOfCommand(1,60)
            self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
            self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 

class RLV_TC__LLD_TXRX_WithEncrypt__limits_payloadLength_null(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that program does not crash if payload length is null while using encryption, encryption use part of the payload (4 bytes for MIC)."
        
    def getExpectedResult(self):
        return "This test should not crash program."
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload [0]{0xFF*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload [0]{0xFF*}")
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 

class RLV_TC__LLD_TXRX_WithEncrypt__standaloneEncryption(UATL_TestCase):#cancelled
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.CANCELLED
        
    def getObjective(self):
        return "Compare encryption via LLD (with encrypt flags) and LLD_BLE_EncryptPlainData"
        
    def getExpectedResult(self):
        return "This test should not crash program."
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
    
        data = "[32]{0xFF*}"
        
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptRxDataAndCompareWithExpected TRUE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam txPayload " + data)
        self.sendQuickCommand(0,"TFW_Command__SetParam rxExpectedPayload " + data)
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptStatus DISABLE")
        
        self.sendQuickCommand(1,"TFW_Command__SetParam txPayload " + data)
        self.sendQuickCommand(1,"TFW_Command__SetParam rxExpectedPayload " + data)
        self.sendQuickCommand(1,"TFW_Command__SetParam encryptStatus ENABLE")
        
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : there is at least one [OK] in the test", self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1) 

class RLV_TC__LLD_standaloneEncryption__nominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Test if LLD_BLE_EncryptPlainData does produce encrypt as expected by standard"
        
    def getExpectedResult(self):
        return """LLD_BLE_EncryptPlainData shall produce with the following key: 000102030405060708090a0b0c0d0e0f
        and the following plain text:  00112233445566778899aabbccddeeff
        the following output: 69c4e0d86a7b0430d8cdb78070b4c55a"""
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
                    
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptKey []{0x0f,0x0e,0x0d,0x0c,0x0b,0x0a,0x09,0x08,0x07,0x06,0x05,0x04,0x03,0x02,0x01,0x00}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptPlainData []{0xff,0xee,0xdd,0xcc,0xbb,0xaa,0x99,0x88,0x77,0x66,0x55,0x44,0x33,0x22,0x11,0x00}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptExpectedData []{0x5a,0xc5,0xb4,0x70,0x80,0xb7,0xcd,0xd8,0x30,0x04,0x7b,0x6a,0xd8,0xe0,0xc4,0x69}")

        self.sendQuickCommand(0,"BLE_Command__InitBoardWithHal")
        
        self.sendCommandAndListen(0,"BLE_Command__EncryptPlainData")
        self.waitForEndOfCommand(0,60)
        self.checkThat("Data encryption is working as expected in standard (see FIPS 197)",self.numberOfRegexMatchesInLog(0,".*Checking plain data encryption.*\[OK\].*") == 1)

class RLV_TC__LLD_standaloneEncryption__wrongKey(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "Check that LLD_BLE_EncryptPlainData is not producing output as the standard pattern when the key is different from the one specified in the standard pattern"
        
    def getExpectedResult(self):
        return """LLD_BLE_EncryptPlainData shall produce with the following key: 000102030405060708090a0b0c0d0e0f
        and the following plain text:  00112233445566778899aabbccddeeff
        the following output: 69c4e0d86a7b0430d8cdb78070b4c55a, 
        if the key differs, output shall not be equal"""
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
                    
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptKey [16]{0xff*}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptPlainData []{0xff,0xee,0xdd,0xcc,0xbb,0xaa,0x99,0x88,0x77,0x66,0x55,0x44,0x33,0x22,0x11,0x00}")
        self.sendQuickCommand(0,"TFW_Command__SetParam encryptExpectedData []{0x5a,0xc5,0xb4,0x70,0x80,0xb7,0xcd,0xd8,0x30,0x04,0x7b,0x6a,0xd8,0xe0,0xc4,0x69}")

        self.sendQuickCommand(0,"BLE_Command__InitBoardWithHal")
        
        self.sendCommandAndListen(0,"BLE_Command__EncryptPlainData")
        self.waitForEndOfCommand(0,60)
        self.checkThat("Data encryption is not producing standard pattern when having a key different from the specified one",self.numberOfRegexMatchesInLog(0,".*Checking plain data encryption.*\[FAILED\].*") == 1)

"""
LLD AP chaining
"""
class RLV_TC__LLD_TXRX_chain__simpleTxRx_nominal(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check that a simple txrx works with chaining commands:
        
        Device 0                       Device 1                    
        ┌──────┐           ┌──────┐    ┌──────┐           ┌──────┐ 
        │ Ap 2 ├────T/F───►│ Ap 0 │    │ Ap 2 ├────T/F───►│ Ap 0 │ 
        │  RX  │           │  END │    │  TX  │           │  END │ 
        └──────┘           └──────┘    └──────┘           └──────┘ 
            |                              |                        
            |                              | 
            ↓                              ↓          
        DR triggers succcess          DR triggers succcess 
        when RX action is done.       when TX action is done.
        CR just returns True.          CR just returns True.
       """
        
    def getExpectedResult(self):
        return "Data shall be received and shall be equal to expected"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        """
        Device 0
        """
        self.sendCommandAndListen(0,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(0,60)
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")#we just want to check that the packet is sent
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(0,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(0,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    []{0x01,0x02,0x03} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)


        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")#we just want to check that the packet is received
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x01,0x02,0x03} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        """
        Run it
        """
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #build action packet chain from buffer
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction.*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction.*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        
        
        #run only rx and wait more than rxReceiveWindow to check that nothing has been received but timeout has occured
        self.sendQuickCommand(1,"TFW_Command__SetParam      rxReceiveWindow                  1000000")
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction.*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is not [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 0)
        self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
        
class RLV_TC__LLD_TXRX_chain__simpleTxRx_wrong_header(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """same as RLV_TC__LLD_TXRX_chain__simpleTxRx_nominal but header shall differ from expected to avoid having a test PASSED because of default values
       """
        
    def getExpectedResult(self):
        return "Data shall be received and header shall not be equal to expected"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        """
        Device 0
        """
        self.sendCommandAndListen(0,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(0,60)
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")#we just want to check that the packet is sent
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(0,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(0,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [[]{0x01,0x02,0x03} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)


        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")#we just want to check that the packet is received
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0xFF ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x01,0x02,0x03} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
              
        """
        Run it : different payloads
        """
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #build each action packet
        #build action packet chain from buffer
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        
        
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : header are not equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 0)

class RLV_TC__LLD_TXRX_chain__simpleTxRx_wrong_payloadLength(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """same as RLV_TC__LLD_TXRX_chain__simpleTxRx_nominal but length shall differ from expected to avoid having a test PASSED because of default values
       """
        
    def getExpectedResult(self):
        return "Data shall be received and length shall not be equal to expected"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        """
        Device 0
        """
        self.sendCommandAndListen(0,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(0,60)
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")#we just want to check that the packet is sent
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(0,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(0,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [3]{0x01,0x02,0x03,0x04} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)


        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")#we just want to check that the packet is received
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [4]{0x01,0x02,0x03,0x04} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
              
        """
        Run it : different payloads
        """
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #build action packet chain from buffer
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        
        
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : length are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
 
class RLV_TC__LLD_TXRX_chain__simpleTxRx_wrong_payloadContent(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """same as RLV_TC__LLD_TXRX_chain__simpleTxRx_nominal but payload shall differ from expected to avoid having a test PASSED because of default values
       """
        
    def getExpectedResult(self):
        return "Data shall be received and payload shall not be equal to expected"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        """
        Device 0
        """
        self.sendCommandAndListen(0,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(0,60)
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")#we just want to check that the packet is sent
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(0,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(0,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    []{0x01,0x02,0x03,0x04} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)


        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")#we just want to check that the packet is received
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [4]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
              
        """
        Run it : different payloads
        """
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #build action packet chain from buffer
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        
        
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
       
class RLV_CH__LLD_TXRX_chain__minimum_rxWindow(UATL_Characterization): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Find the shortest rx window value where txrx starts to fail, then we can use this to trigger rxtx failures in later tests

         Device 0                       Device 1                          
         ┌──────┐           ┌──────┐    ┌──────┐           ┌──────┐       
         │ Ap 2 ├────T/F───►│ Ap 0 │    │ Ap 2 ├────T/F───►│ Ap 0 │       
         │  RX  │           │  END │    │  TX  │           │  END │       
         └──────┘           └──────┘    └──────┘           └──────┘       
            |                               |                             
            |                               |                             
            ↓                               ↓                             
        DR triggers succcess            DR triggers succcess
        when RX action is done.         when TX action is done.            
        Whatever CR returns,            Whatever CR returns,              
        we end chain.                   we end chain.                     
        """
        
    def getExpectedResult(self):
        return "Data shall be received, no matter how many times it is run, because in case of failure, it will retry"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        """
        Device 0
        """
        self.sendCommandAndListen(0,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(0,60)
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_SUCCESS")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(0,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(0,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    []{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")


        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_SUCCESS")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        
        
        
        """
        Run it
        """
        for rxReceiveWindow in range(4000,-1,-100):
            
            self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow " + str(rxReceiveWindow))
            
            #build each action packet
            self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
            self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            #build action packet chain from buffer
            self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
            self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
            #build each action packet
            self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
            self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            #build action packet chain from buffer
            self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
            self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
            #run built chain
            self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
            self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
            
            
            self.waitForEndOfCommand(0,60)
            if self.stopIf("device 0 : there is at least one [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") >= 1,"rxReceiveWindow",rxReceiveWindow):
                break

            self.waitForEndOfCommand(1,60)
            if self.stopIf("device 1 : there is at least one [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") >= 1,"rxReceiveWindow",rxReceiveWindow):
                break
                
            self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
            self.waitForEndOfCommand(0,60)
            if self.stopIf("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0,"rxReceiveWindow",rxReceiveWindow):
                break

class RLV_TC__LLD_TXRX_chain__condRoutine_condition(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check that the statemachine goes in 'next packet if false' if Cr returns false, and 'next packet if true' if Cr returns true
        
                              DR does not trigger succcess.
                               ↑ 
            Device 0      ┌──────┐        ┌──────┐ 
            ┌──────┐      │ Ap 4 ├┬─T/F──►│ Ap 0 │ 
            │ Ap 2 ├──T──►│  TX  ││       │  END │ 
            │  TX  ├─F─┐  └──────┘│       └──────┘ 
            └──────┘   │  ┌──────┐│
               |       └─►│ Ap 3 ├┘
               |          │  TX  │  
               ↓          └──────┘  
     DR just returns True.      ↓                                           
     CR returns T or F        DR triggers succcess.                                
                       
        
        For this test, when test is run once, Ap 3 and 4 are swapped (the condition for going in AP 3, which triggers the success, is was False and is now True)
       """
        
    def getExpectedResult(self):
        return "Data shall be received, no matter how many times it is run, because in case of failure, it will retry"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
                
        #for all action packets
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        
        """
        Build and run : True, shall PASS
        """
        self.sendCommandAndListen(0,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(0,60)
        
        ##Device 0, Action packet 3, triggers success
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        ##Device 0, Action packet 4, does not trigger success
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Device 0, Action packet 2
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)    
        
        """
        Build and run : False, shall PASS
        """   
        ##Device 0,, modify action packet 2
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_FALSE")    
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)  
                
        
        """
        Swap AP3 and AP4 but not trigger conditions, shall FAIL
        """ 
        ##Device 0, modify action packet 2
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
                
        self.checkThat("device 0 : actionFailed is not [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 0)



class RLV_TC__LLD_TXRX_chain__condRoutine_selfLoop(UATL_TestCase): #TBI
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check that the statemachine loops on a actionpacket until its CR returns True if 'next action packet if false' points to itself and 'next action packet if true' points to end
           
           Device 0                                      Device 1                                 
               ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐ 
           ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │      │ Ap 2 ├─T/F─►│ Ap 3 ├──T──►│ Ap 4 ├─T/F─►│ Ap 0 │ 
           └─F─┤  RX  │      │  TX  │      │  END │      │  TX  │◄──F──┤  RX  │      │  TX  │      │  END │ 
               └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘ 
                    |             |                           |          |               |                              
                    |             ↓                           |          |               ↓                       
                    |        DR triggers success              |          |           DR triggers success      
                    ↓        when TX action is done.          ↓          ↓           when TX action is done. 
        DR just returns True.                DR just returns True.      DR just returns True.                    
        CR returns true if RX                CR just returns True       CR returns true if RX 
        packet is as expected.                                          packet is as expected.
 
        We start the RX chain which will start in loop short rx windows (D0/AP2/RX-AP2/RX)
        We wait a bit, more than 10 times 'rx window + B2B time', then we start TX that will retry until it gets the D0 ACK (D0/AP3/TX)
        Device 0's success shall be triggered and then D1's success as well.
        """
        
    def getExpectedResult(self):
        return "Successes shall be triggered on both devices after D0's chain, then D1's chain are started"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        """
        Device 0
        """        
        ##Device 0, Action packet 3
        #set current action packet type
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(0,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(0,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00}")#0x01,0x02,0x03,0x04,0x05} ")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       0")
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Device 0, Action packet 2
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_PACKET_AS_EXPECTED")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    []{0x00}")#0xaa,0xbb,0xcc,0xdd,0xee,0xff} ")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      4000000")
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Build chain
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        


        """
        Device 1
        """
        ##Device 1, Action packet 4
        #set current action packet type
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x00}")#0xFF} ")
        #set times
        self.sendQuickCommand(1,"TFW_Command__SetParam      backToBackTime                       0")
        #build action packet chain from buffer
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Device 1, Action packet 3
        #set current action packet type
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_PACKET_AS_EXPECTED")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      rxExpectedPayload                    []{0x00}")#0x01,0x02,0x03,0x04,0x05} ")
        #set times            
        self.sendQuickCommand(1,"TFW_Command__SetParam      backToBackTime                       0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      rxReceiveWindow                      4000000")
        #build action packet chain from buffer
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Device 1, Action packet 2
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x00}")#0xaa,0xbb,0xcc,0xdd,0xee,0xff} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        
        ##Build chain
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        """
        Run it
        """
        #run built chain
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                40")
        self.sendQuickCommand(1,"TFW_Command__SetParam      requestTimeoutInS                40")
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        time.sleep(12)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(0,".*pendingAction.*\[OK\].*") == 1)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : pendingAction is [OK]",self.numberOfRegexMatchesInLog(1,".*pendingAction.*\[OK\].*") == 1)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        


class RLV_TC__LLD_TXRX_chain__rxtxLoop_stress(UATL_TestCase): #TBI
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.TO_BE_IMPLEMENTED
        
    def getObjective(self):
        return """Check that if a condroutine is false, the next job of the chained AP is not called:
        Nominal case:
            Device 1                                         Device 0
             ______           ______       ______            ______           ______       ______        
            |      |----|--->|      |  T  |      |          |      |----|--->|      |  T  |      |  
            | Ap 2 |   T/F   | Ap 3 |--|->| Ap 0 |          | Ap 2 |   T/F   | Ap 3 |--|->| Ap 0 |  
            |  TX  |<---|----|  RX  |  |  |  END |          |  TX  |<---|----|  RX  |  |  |  END |  
            |______|    F    |______|  |  |______|          |______|    F    |______|  |  |______|  
                                       |                                               |                  
                                       |                                               |                  
                                       v                                               v                  
                                   CR triggers succcess                          DR triggers succcess   
                                   when TX action is done                        when TX action is done 
                                                            

       """
        
    def getExpectedResult(self):
        return "Data shall be received and shall be equal to expected"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        """
        Device 0
        """
        self.sendCommandAndListen(0,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(0,60)
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")#we just want to check that the packet is sent
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(0,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(0,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    []{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")


        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")#we just want to check that the packet is received
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        
        
        """
        Run it
        """
        #build each action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #build each action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        #build action packet chain from buffer
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        
        
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
        self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
 
class RLV_TC__LLD_TXRX_chain__multiple_stateMachine_channel(UATL_TestCase): #TBI
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check that a multiple statemachine can work at the same time. 
        
        Device 0                                                             Device 1
         ______             ______          ______             ______         ______             ______      ______             ______   
    ┌--►|      |           |      |    ┌--►|      |           |      |       |      |           |      |    |      |           |      |  
    F   | Ap 2 |-----T----►| Ap 0 |    F   | Ap 2 |-----T----►| Ap 0 |       | Ap 2 |---T/F----►| Ap 0 |    | Ap 2 |-----T----►| Ap 0 |  
    └---|  RX  |           |  END |    └---|  RX  |           |  END |       |  TX  |           |  END |    |  TX  |           |  END |  
        |______|           |______|        |______|           |______|       |______|           |______|    |______|           |______|  
            |                                 |                                 |                              |                        
            |  state_machine 1                |   state_machine 5               |   state_machine 3            |   state_machine 6
            |  channel 27                     |   channel 22                    |   channel 27                 |   channel 22     
            ↓                                 ↓                                 ↓                              ↓                        
        DR just returns True.              DR just returns True.              DR just returns True.           DR just returns True.         
        CR triggered when TX              CR triggered when RX              CR triggered when TX           CR triggered when TX         
        action is done.                   action is done.                   action is done.                action is done.              
        CR triggers succcess.             CR triggers succcess.             CR triggers succcess.          CR triggers succcess.   
        """
        
    def getExpectedResult(self):
        return "Data shall be received, no matter how many times it is run, because in case of failure, it will retry"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        """
        Device 0
        """
        self.sendCommandAndListen(0,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(0,60)
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_SUCCESS")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(0,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(0,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    []{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      1000")


        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_SUCCESS")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        
        
        
        """
        Run it
        """
        while self.__isActive():
            #build each action packet
            self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
            self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            #build action packet chain from buffer
            self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
            self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
            #build each action packet
            self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
            self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            #build action packet chain from buffer
            self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
            self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
            #run built chain
            self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
            self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
            
            
            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            
            self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
            self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
            self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
            self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
            self.waitForEndOfCommand(0,60)
            self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
"""
-------------------------------------------------------------------------------------------------------------------------------------
AFTER THIS LINE, the following code should be in TestProtocol.py? and some part in TestConfiguration.py?
-------------------------------------------------------------------------------------------------------------------------------------
"""
"""
TODO: make inheritance and force UATL_TestProtocol methods to be implemented. ?
"""

class RLV_TC__LLD_TXRX_chain__multiple_stateMachine_networkId(UATL_TestCase): #TBI
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check that a multiple statemachine can work at the same time. 
        
        Device 0                                                             Device 1
         ______             ______          ______             ______         ______             ______      ______             ______   
    ┌--►|      |           |      |    ┌--►|      |           |      |       |      |           |      |    |      |           |      |  
    F   | Ap 2 |-----T----►| Ap 0 |    F   | Ap 2 |-----T----►| Ap 0 |       | Ap 2 |---T/F----►| Ap 0 |    | Ap 2 |-----T----►| Ap 0 |  
    └---|  RX  |           |  END |    └---|  RX  |           |  END |       |  TX  |           |  END |    |  TX  |           |  END |  
        |______|           |______|        |______|           |______|       |______|           |______|    |______|           |______|  
            |                                 |                                 |                              |                        
            |  state_machine 1                |   state_machine 5               |   state_machine 3            |   state_machine 6
            |  channel 27                     |   channel 22                    |   channel 27                 |   channel 22     
            ↓                                 ↓                                 ↓                              ↓                        
        DR just returns True.              DR just returns True.              DR just returns True.           DR just returns True.         
        CR triggered when TX              CR triggered when RX              CR triggered when TX           CR triggered when TX         
        action is done.                   action is done.                   action is done.                action is done.              
        CR triggers succcess.             CR triggers succcess.             CR triggers succcess.          CR triggers succcess.   
        """
        
    def getExpectedResult(self):
        return "Data shall be received, no matter how many times it is run, because in case of failure, it will retry"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        """
        Device 0
        """
        self.sendCommandAndListen(0,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(0,60)
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_SUCCESS")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(0,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(0,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedHeader                     0x95 ")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    []{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      1000")


        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_SUCCESS")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      radioFrequencyCalibrationEnabled     1") #PPL_TRIG
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(1,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #TIMER_WAKEUP
        self.sendQuickCommand(1,"TFW_Command__SetParam      nsEn                                 0") #NS_EN
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelAutoIncrementEnabled          0") #INC_CHAN
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTimeIsRelativeNotAbsolute      1") #RELATIVE
        self.sendQuickCommand(1,"TFW_Command__SetParam      timestampFromPacketStartNotEnd       0") #TIMESTAMP_POSITION
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txHeader                             0x95 ")
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x54,0x45,0x53,0x54,0x5f,0x42,0x4c,0x45} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        
        
        
        """
        Run it
        """
        while self.__isActive():
            #build each action packet
            self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
            self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            #build action packet chain from buffer
            self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
            self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
            #build each action packet
            self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
            self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            #build action packet chain from buffer
            self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
            self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
            #run built chain
            self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
            self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
            
            
            self.waitForEndOfCommand(0,60)
            self.waitForEndOfCommand(1,60)
            
            self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
            self.checkThat("device 0 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(0,".*actionFailed.*\[OK\].*") == 1)
            self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
            self.checkThat("device 1 : actionFailed is [OK]",self.numberOfRegexMatchesInLog(1,".*actionFailed.*\[OK\].*") == 1)
            self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
            self.waitForEndOfCommand(0,60)
            self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
"""
-------------------------------------------------------------------------------------------------------------------------------------
AFTER THIS LINE, the following code should be in TestProtocol.py? and some part in TestConfiguration.py?
-------------------------------------------------------------------------------------------------------------------------------------
"""
"""
TODO: make inheritance and force UATL_TestProtocol methods to be implemented. ?
"""

#encryptOnceEvery2Packets
#actionTags

class UATL_TestProtocol:
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
        return r'.*Waiting for command.*'
        #return r'.*lld.*\>.*'
        
    def getEndOfCommandRegex(self):
        """
        usefull if you want to know if the last result can be parsed and if the next command can be send
        """
        #return self.getPromptRegex()
        return r'.*End of command.*'
        #return r'.*finished with.*'
          
    def hasCommandThrowedAnyError(self,testLog):
        """
        usefull if you want to abort a test campaign / test case in case of error (error, not failure)
        I think I should to something like 
        if board.listener.protocol.hasCommandThrowedAnyError() :
            result = "skipped"
            endOfTest = True
        """
        return (re.search('.*(Error :).*', testLog) is not None) #RLV
        #return (re.search('.*(ERROR :).*', testLog) is not None) #LLD tests

                        
    def hasBoardReset(self,testLog):
        """
        usefull if you want to know if board has reset during this log
        """
        return (re.search('.*(Board reset\.\.\.).*', testLog) is not None) #RLV

                        
