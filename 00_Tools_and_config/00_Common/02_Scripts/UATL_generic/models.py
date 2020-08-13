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
from UATL_implem.testConfig import UATL_isDebugEnabled,UATL_isResetBeforeEachTestEnabled

class UATL_Procedure(metaclass = ABCMeta):
    """
    manage testcase definition and result management
    """        

    @unique
    class ImplementationStatus(AutoEnum):
        CANCELLED = auto()          
        TO_BE_IMPLEMENTED = auto()  
        READY_TO_BE_RUN = auto()    
        NEED_SPEC_INFO = auto()     
        FOR_TEST_ENV_ONLY = auto()  
        FOR_INFO_ONLY = auto()      
        
    def __init__(self, timeout):
        self.__timeout = timeout #in minutes
        self.failure_message = "" 
        self.log = "" 
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
            
        if UATL_isResetBeforeEachTestEnabled():
            self.__performingReset = True
            UATL_log("**  " + "Resetting board(s)")
            for board in self._boardList:
                board.listener.reset.shouldBeDone.set()
            self.__performingReset = False
            while True:
                resetPerformed = True
                for board in self._boardList:
                    if board.listener.reset.shouldBeDone.is_set():
                        resetPerformed = False
                if resetPerformed:
                    break
            UATL_log("**  " + "Board(s) resetted")
        else:
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
        
class UATL_TestProtocol:
    """
     Object managing communication test protocol with any board (like ask for prompt, read ack, detect end of command, ...)
    """        
    
    @abstractmethod
    def isAutoResetEnabled(self):
        pass
        
    @abstractmethod
    def getEncoding(self):
        pass
        
    @abstractmethod
    def getRequestToWaitForCommand(self):
        pass
        
    @abstractmethod
    def getPromptRegex(self):
        pass
        
    @abstractmethod
    def getEndOfCommandRegex(self):
        pass
          
    @abstractmethod
    def hasCommandThrowedAnyError(self,testLog):
        pass

    @abstractmethod              
    def hasBoardReset(self,testLog):
        pass
        