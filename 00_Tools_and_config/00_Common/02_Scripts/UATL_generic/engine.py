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
from UATL_implem.testProcedureList import *
from UATL_implem.testToolProtocol import UATL_CustomProtocol
from UATL_implem.testConfig import UATL_isDebugEnabled

def UATL_printScriptVersion():
    version = "v1.0.RC1"
    print("\n" + UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW + '{:-^82}'.format('') + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET )
    print(UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW + '{:-^102}'.format(UATL_ShellPolice.Fore.YELLOW + UATL_ShellPolice.Back.BLACK + "      UATL (Unified Automatic Test Launcher) -- " + version + "      " + UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW )+ UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET )
    print(UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW + '{:-^82}'.format('') + UATL_ShellPolice.Fore.RESET + UATL_ShellPolice.Back.RESET )
  
class UATL_ResetManager:
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
        self.reset = UATL_ResetManager()
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
        self.__protocol = UATL_CustomProtocol()
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
        UATL_log(UATL_ShellPolice.Back.BLUE + UATL_ShellPolice.Fore.WHITE + "You have 13 seconds to load debugger" + UATL_ShellPolice.Back.RESET + UATL_ShellPolice.Fore.RESET)
        time.sleep(13)
                  
    def __checkSerialPorts(self,stLinkUtilityExe):
        portList = list(serial.tools.list_ports.comports())

        if (len(portList) == 0):
            UATL_error("Empty port list")
            sys.exit(255)
        elif (len(portList) == 1):
            UATL_error("Only one port available")
            sys.exit(255)
        else:
            UATL_log( str(len(portList)) + " available serial port(s) found")
            boardId = 0
            stDevices = 0
            for port in portList:
                if port.pid == 24577 or port.pid == 14155: # check if port product id is FTDI = 24577 / 14155 if STLink
                    stDevices += 1
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
        elif (len(self.boardList) != stDevices):
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
        retries = 0
        while True:
            try:
                self.serial.close()
                self.serial.open()
            except:
                retries += 1
            
            if self.serial.isOpen():
                UATL_log( "Port "+self.portId + " opened.")
                break
                
            if retries > 3:
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
            currentTime += ""
        except:
            currentTime = "---" 
        
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
            UATL_error("Testsuite is not well formatted. Please mind the quotes.")
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
            UATL_error("Testsuite is empty! please check the testsuite configuration file *.testsuite")
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
    def getBoardNumber(self):
        UATL_error("Procedure {} must override getBoardNumber(), please check your implementation of this testcase in TestCasesList.py".format(self.__class__.__name__))    
        sys.exit(10)
        
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
                sys.exit(255)
      
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
        
        report = "Procedure name" + ';' + "Version" + ';' + "Implementation status" + ';' + "Board number" + ';' + "Objective(s)" + ';' + "Expected result" + ';' + "Duration" + ';' + "Result"  + ';' + "Has been aborted?"  + ';' + "Reset counter"  + ';' + "Has timed out?"  + '\n'
        
        for procedure in self.testSuite.procedures:
            nameField = '{}'.format(procedure.__class__.__name__)
            versionField = '{}'.format(procedure.getVersion())
            implementationField = '{}'.format(procedure.getImplementationStatus().name)
            boardField = '{}'.format(procedure.getBoardNumber())
            objectiveField = '{}'.format(procedure.getObjective())
            expectedField = '{}'.format(procedure.getExpectedResult())
            durationField = '{}'.format(UATL_ShellPolice.stripAnsi(procedure.getDurationAsString()))
            resultField = '{}'.format(UATL_ShellPolice.stripAnsi(procedure.getStatus()))
            abortedField = '{}'.format(UATL_ShellPolice.stripAnsi(procedure.hasBeenAbortedAsString()))
            resetField = '{}'.format(UATL_ShellPolice.stripAnsi(procedure.getResetCounterAsString()))
            timedoutField = '{}'.format(UATL_ShellPolice.stripAnsi(procedure.getTimeoutCounterAsString()))
            report += '"' + nameField + '";"' + versionField + '";"' + implementationField + '";"' + boardField + '";"' + objectiveField + '";"' + expectedField + '";"' + durationField + '";"' + resultField + '";"' + abortedField + '";"' + resetField + '";"' + timedoutField + '"\n'
            
        try: 
            UATL_log("writting validation report in file : " + os.path.realpath(csvTestReportFile.name))
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
            UATL_log("writting validation report in file : " + os.path.realpath(junitReportFile.name))
            junitReportFile.write(report)
            UATL_log("Junit report written")
        except SystemExit as e:
            os._exit(int(str(e)))
        except:
            UATL_log("Junit report could not be written")
            UATL_log("")
            print("")
            print(report)