# -*- coding: utf-8 -*-
# python version 3.8.1
import os
import time
import serial
import shlex
import sys
import re
import datetime
import random

from UATL_generic.misc import  *
from UATL_generic.models import UATL_Procedure
from UATL_implem.procedureModels import UATL_TestCase

class LLD_CLI_TC_registerAccess(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 1
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"0")
        self.waitForEndOfCommand(0,60)
        self.checkThat("test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
 
class LLD_CLI_TC_api(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 1
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"1")
        self.waitForEndOfCommand(0,60)
        self.checkThat("test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        
class LLD_CLI_TC_standaloneTraffic(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 1
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"2")
        self.waitForEndOfCommand(0,60)
        self.checkThat("test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        
class LLD_CLI_TC_txRxNominal(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"200")
        self.sendCommandAndListen(1,"100")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
                      
class LLD_CLI_TC_interference(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"201")
        self.sendCommandAndListen(1,"101")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
        
class LLD_CLI_TC_txRxFiltering(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"202")
        self.sendCommandAndListen(1,"102")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
                     
class LLD_CLI_TC_lowPower(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"203")
        self.sendCommandAndListen(1,"103")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
                        
class LLD_CLI_TC_txRx_shortBurts_withoutAck_txIdle(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"204")
        self.sendCommandAndListen(1,"104")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
             
class LLD_CLI_TC_txRx_longBurts_withoutAck_txIdle(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"205")
        self.sendCommandAndListen(1,"105")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
             
class LLD_CLI_TC_txRx_shortBurts_withAck_txIdle(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"206")
        self.sendCommandAndListen(1,"106")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
        
class LLD_CLI_TC_txRx_longBurts_withAck_txIdle(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"207")
        self.sendCommandAndListen(1,"107")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
              
class LLD_CLI_TC_txRx_shortBurts_withoutAck_rx(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"208")
        self.sendCommandAndListen(1,"108")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
                
class LLD_CLI_TC_txRx_longBurts_withoutAck_rx(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"209")
        self.sendCommandAndListen(1,"109")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
              
class LLD_CLI_TC_txRx_shortBurts_withAck_rx(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"210")
        self.sendCommandAndListen(1,"110")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
               
class LLD_CLI_TC_txRx_longBurts_withAck_rx(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"211")
        self.sendCommandAndListen(1,"111")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
                
class LLD_CLI_TC_txRx_encryptedFrames(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"212")
        self.sendCommandAndListen(1,"112")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
        
class LLD_CLI_TC_txRx_shortBurts_withoutAck_robustness(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"213")
        self.sendCommandAndListen(1,"113")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
               
class LLD_CLI_TC_txRx_longBurts_withoutAck_robustness(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"214")
        self.sendCommandAndListen(1,"114")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
        
class LLD_CLI_TC_txRx_shortBurts_withAck_robustness(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"215")
        self.sendCommandAndListen(1,"115")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
              
class LLD_CLI_TC_txRx_longBurts_withAck_robustness(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"216")
        self.sendCommandAndListen(1,"116")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
             
class LLD_CLI_TC_txRx_macFrameSizes_withoutAck(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"217")
        self.sendCommandAndListen(1,"117")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
        
class LLD_CLI_TC_txRx_macFrameSizes_withAck(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"218")
        self.sendCommandAndListen(1,"118")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
        
class LLD_CLI_TC_txRx_pendingBits(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"219")
        self.sendCommandAndListen(1,"119")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
               
class LLD_CLI_TC_txRx_channelChange(UATL_TestCase):#ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return "TODO"
        
    def getExpectedResult(self):
        return "TODO"
        
    def getBoardNumber(self):
        return 2
       
    def __callCliCommandsAndDoChecks__(self):
        self.sendCommandAndListen(0,"220")
        self.sendCommandAndListen(1,"120")
        self.waitForEndOfCommand(0,5*60)
        self.waitForEndOfCommand(1,5*60)
        self.checkThat("device 0: test is passed",self.numberOfRegexMatchesInLog(0,".*finished with all tests PASSED.*") == 1)
        self.checkThat("device 1: test is passed",self.numberOfRegexMatchesInLog(1,".*finished with all tests PASSED.*") == 1)
        
