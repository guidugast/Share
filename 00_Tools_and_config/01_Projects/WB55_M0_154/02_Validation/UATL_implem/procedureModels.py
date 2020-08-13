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
                self.failure_message += "Condition '{}' failed \r\n&#13;".format(description)
            else:
                checkStatus = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.GREEN + "Passed"
                if self.__status != self.Status.FAILED:
                    self.__status = self.Status.PASSED
        
            for board in self._boardList:
                if board.listener.isCurrentCommandTimedout():
                    checkStatus = UATL_ShellPolice.Fore.BLACK + UATL_ShellPolice.Back.YELLOW + "Timed out"
                    self.__status = self.Status.TIMED_OUT
                    self.failure_message += "Timed out\r\n&#13;"
                    
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
                #log = "{}".format(self.log),
                elapsed_sec = self.getDurationInS()
                )
            
        if self.__getStatus__() is self.hasBeenAbortedByTimeout():
            self.failure_message += "Has been aborted by timeout\r\n&#13;"

        if self.failure_message != "":
            junitTestCase.add_failure_info(self.failure_message)
        
        return junitTestCase
        
    @final   
    def __setup__(self):
        for boardId in range(0,len(self._boardList)):
            #self.__resetBoard(boardId) --> TODO: fix feature 'reset boards before starting each procedure'
            # --> TODO: use HW reset
            self.sendQuickCommand(boardId,"TFW_Command__ResetTestEnvParametersToDefaultValues")#reset param to default value
            # --> TODO: add feature 'choose in options between resetting boards or resetting test env parameters'
        
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
    class Status(AutoEnum):# --> TODO: put Status in private
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
            
        return True if (self.__status == self.Status.FAILED_AT_FIRST or self.__status == self.Status.VALUE_FOUND) else False
        
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
                #log = "{}".format(self.log),
                elapsed_sec = self.getDurationInS()
                )
            
        if self.__getStatus__() is VALUE_NOT_FOUND_YET:
            self.failure_message += "Value not found\r\n&#13;"
        if self.__getStatus__() is FAILED_AT_FIRST:
            self.failure_message += "Failed at first\r\n&#13;"
        if self.__getStatus__() is self.hasBeenAbortedByTimeout():
            self.failure_message += "Has been aborted by timeout\r\n&#13;"

        if self.failure_message != "":
            junitTestCase.add_failure_info(self.failure_message)

            
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
