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
from UATL_implem.procedureModels import UATL_TestCase,UATL_Characterization,UATL_Endurance

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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0) and (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1)
        
        #out of range networkId (spec #1b)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1)
        
        #out of range networkId (spec #2)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6C6C6C6C")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6C6C6C6C")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1)
        
        #out of range networkId (spec #3)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x752D5525") #0x752D5525 or 0xB55A54AA
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x752D5525")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1)
                
        #out of range networkId (spec #4)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacket' = 0xc0.*") == 1)
        
        #back to in range networkId
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6CFABCDF") #0x6CFABCDF or 0x5A964129
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6CFABCDF")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
        
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0x00.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
    
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
                        
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
            
            txRxNotSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0) or (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 0) or (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 0) or (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [FAILED]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [FAILED]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[FAILED\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue.*?'HAL_BLE_SendPacket'.*?0xc0.*") == 1)
        
        #back to normal channel
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL D 1 D D D D D D")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL D 1 D D D D D D")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0x00.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)

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
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : HAL_BLE_ReceivePacket is used",self.numberOfRegexMatchesInLog(0,".*\'HAL_BLE_ReceivePacket\'.*") >= 1)
        self.checkThat("device 0 : HAL_BLE_ReceivePacketWithAck is not used",self.numberOfRegexMatchesInLog(0,".*HAL_BLE_ReceivePacketWithAck.*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is not [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0)
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #out of range networkId (spec #1b)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #out of range networkId (spec #2)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6C6C6C6C")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6C6C6C6C")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #out of range networkId (spec #3)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x752D5525") #0x752D5525 or 0xB55A54AA
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x752D5525")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        
        #out of range networkId (spec #4)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #back to in range networkId
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6CFABCDF") #0x6CFABCDF or 0x5A964129 or 0x71764129
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6CFABCDF")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
        
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0x00.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
                self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
                self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
                self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
                #self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacket' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacket' = 0xc0.*") == 1) #TODO, remove comment if spec is updated

                if (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1):
                    nwkIdEcCounter[networkIdErrorCode][0] += 1
                
                nwkIdEcCounter[networkIdErrorCode][1] += 1

                self.waitForEndOfCommand(1,60)
                self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
                self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)


        #out of range networkId (spec #1b)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAAFFABCD")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)


        #out of range networkId (spec #4)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFC0FC0FC")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        
        #out of range networkId (spec worst A1)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x00010001")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x00010001")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        

        #out of range networkId (spec worst A2)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFFFEFFFE")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFFFEFFFE")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)


        #out of range networkId (spec worst B1)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x000F000F")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x000F000F")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        

        #out of range networkId (spec worst B2)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFFF0FFF0")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFFF0FFF0")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        

        #out of range networkId (spec worst C)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFF00FF00")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFF00FF00")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #out of range networkId (spec worst D)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xFFFFFFFF")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xFFFFFFFF")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
        
        #out of range networkId (spec worst E)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xAAAAAAAA")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xAAAAAAAA")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
       
               
        #out of range networkId (spec worst F)
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0xCCCCCCCC")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0xCCCCCCCC")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)
           
               
        #not BLE compliant but works
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6c6c6c6c")
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6c6c6c6c")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")

        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0xc0.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : payloads are equal",self.numberOfRegexMatchesInLog(1,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 1 : returnValue for 'HAL_BLE_SendPacketWithAck' is INVALID_PARAMETER_C0",self.numberOfRegexMatchesInLog(1,".*returnValue for 'HAL_BLE_SendPacketWithAck' = 0xc0.*") == 1)  
        
        #back to in range networkId
        self.sendQuickCommand(0,"TFW_Command__SetParam networkId 0x6CFABCDF") #0x6CFABCDF or 0x5A964129 or 0x71764129
        self.sendQuickCommand(1,"TFW_Command__SetParam networkId 0x6CFABCDF")
        self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL")
        time.sleep(0.2)
        self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL")
        
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        self.checkThat("device 0 : returnValue for 'HAL_BLE_ReceivePacketWithAck' is SUCCESS_0 ",self.numberOfRegexMatchesInLog(0,".*returnValue for 'HAL_BLE_ReceivePacketWithAck' = 0x00.*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are not equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 0)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)

        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are not equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 0)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 0 : headers are equal",self.numberOfRegexMatchesInLog(0,".*Checking header.*\[OK\].*") == 1)
        self.checkThat("device 0 : lengths are equal",self.numberOfRegexMatchesInLog(0,".*Checking length.*\[OK\].*") == 1)
        
        self.waitForEndOfCommand(1,60)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("Number of rx window started should be around stressDurationInS/(txAckReceiveWindow + wakeupTime) +/- 10% ({} vs {:.1f})".format(sendCounter,expectedAsked), (sendCounter >= expectedAsked * 0.9) and (sendCounter <= expectedAsked * 1.1)) 
        
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
        commandTimeout = int(self.getTimeoutInS() - 3)
        stressDurationInS = int(self.getTimeoutInS() - 6) 
        
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(0,"TFW_Command__SetParam rxStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(0,"TFW_Command__SetParam rxReceiveWindow " + str(rxReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__RxStress_HAL")
        self.waitForEndOfCommand(0,commandTimeout)
        
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
        commandTimeout = int(self.getTimeoutInS() - 3)
        stressDurationInS = int(self.getTimeoutInS() - 6) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision

        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld")
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck FALSE")
        self.sendQuickCommand(0,"TFW_Command__SetParam stressDurationInS " + str(stressDurationInS))
        self.sendQuickCommand(0,"TFW_Command__SetParam txStressDeltaBlockingDelayInUs 0")
        self.sendQuickCommand(0,"TFW_Command__SetParam wakeupTime " + str(wakeupTime))
        self.sendQuickCommand(0,"TFW_Command__SetParam txAckReceiveWindow " + str(txAckReceiveWindow))
        
        self.sendCommandAndListen(0,"BLE_Command__TxStress_HAL")
        self.waitForEndOfCommand(0,commandTimeout)
        
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        
    def getBoardNumber(self):
        return 2
        
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [FAILED]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[FAILED\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [FAILED]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[FAILED\].*") == 1)
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
                    rssi[channel] = self.getIntFrom(".*?RSSI\s+:\s+\[(-*\d+)\].*?",0)
                    break
                if (failureCounter >= 10):
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

class RLV_TC__HAL_TXRX_WithAck__rssiOnAllChannels(UATL_TestCase):#ready
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
    
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam showRssi TRUE")
        
        rssi = [0xFFFFFFFF]*40
        for channel in range(0,40,1):
            failureCounter = 0
            while True:
                self.sendCommandAndListen(0,"BLE_Command__InitBoardThenWaitForAPacket_HAL P "+str(channel)+" D D D D D D",False,True)
                time.sleep(0.1)
                self.sendCommandAndListen(1,"BLE_Command__InitBoardThenSendOnePacket_HAL P "+str(channel)+" D D D D D D",False,True)
        
                self.waitForEndOfCommand(0,60)
                self.waitForEndOfCommand(1,60)
                txrxSuccess = (self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0) and (self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0) and (self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
                if not txrxSuccess:
                    failureCounter += 1
                    UATL_log("Channel {} retry".format(channel))
                else:
                    rssi[channel] = self.getIntFrom(".*?RSSI\s+:\s+\[(-*\d+)\].*?",0)
                    break
                if (failureCounter >= 10):
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
 
class RLV_TC__LLD_TxPower_simpleTx(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN

    def getObjective(self):
        return """Check that tx power is compliant with the following table and that rssi follows the table (by ignoring any dBm offsets) :
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
        
        Following packet chains used:
        
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
        return """When reading RSSI after a board that set its power signal following the reference table given in test objective,
        then the output table shall correspond with a precision of 20% to the reference table.
        """       
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        self.sendQuickCommand(0,"TFW_Command__SetParam withAck TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam withAck TRUE")
        
        self.sendQuickCommand(0,"TFW_Command__SetParam showRssi TRUE")
        

        expectedRssiForTxPowerLUT = []#  txPower  o rssi    e rssi
        expectedRssiForTxPowerLUT.append([0x0,  0xFFFFFFFF,  -18])
        expectedRssiForTxPowerLUT.append([0x1,  0xFFFFFFFF,  -15]) 
        expectedRssiForTxPowerLUT.append([0x2,  0xFFFFFFFF,  -12]) 
        expectedRssiForTxPowerLUT.append([0x3,  0xFFFFFFFF,  -9 ]) 
        expectedRssiForTxPowerLUT.append([0x4,  0xFFFFFFFF,  -6 ]) 
        expectedRssiForTxPowerLUT.append([0x5,  0xFFFFFFFF,  -2 ]) 
        expectedRssiForTxPowerLUT.append([0x6,  0xFFFFFFFF,  0  ]) 
        expectedRssiForTxPowerLUT.append([0x7,  0xFFFFFFFF,  5  ]) 
        expectedRssiForTxPowerLUT.append([0x8,  0xFFFFFFFF,  -14]) 
        expectedRssiForTxPowerLUT.append([0x9,  0xFFFFFFFF,  -11]) 
        expectedRssiForTxPowerLUT.append([0xA,  0xFFFFFFFF,  -8 ]) 
        expectedRssiForTxPowerLUT.append([0xB,  0xFFFFFFFF,  -5 ]) 
        expectedRssiForTxPowerLUT.append([0xC,  0xFFFFFFFF,  -2 ]) 
        expectedRssiForTxPowerLUT.append([0xD,  0xFFFFFFFF,  2  ]) 
        expectedRssiForTxPowerLUT.append([0xE,  0xFFFFFFFF,  4  ]) 
        expectedRssiForTxPowerLUT.append([0xF,  0xFFFFFFFF,  8  ])
        
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
        #build packet in buffer            
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
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x01,0x02,0x03} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        """
        Build it
        """
              
        for txPower in range(0,16,1):
            failureCounter = 0
            while True:
                
                self.sendQuickCommand(0,"TFW_Command__SetParam      txPower                        {}".format(txPower))
                self.sendQuickCommand(1,"TFW_Command__SetParam      txPower                        {}".format(txPower))
                
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
                self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
                self.waitForEndOfCommand(0,60)
                txrxSuccess = (self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0) and (self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0) and (self.numberOfRegexMatchesInLog(1,"\[OK\]") >= 1)
                if not txrxSuccess:
                    failureCounter += 1
                    UATL_log("TxPower {} retry".format(txPower))
                else:
                    expectedRssiForTxPowerLUT[txPower][1] = self.getIntFrom(".*?RSSI\s+:\s+\[(-*\d+)\].*?",0)
                    break
                if (failureCounter >= 5):
                    break
        spaceBeforeTxPowerArray=" "*10
        UATL_log(spaceBeforeTxPowerArray + "┌{:─^10}┬{:─^10}┬{:─^10}┐".format("","",""))
        UATL_log(spaceBeforeTxPowerArray + "|{: ^10}|{: ^10}|{: ^10}|".format("txPower","e rssi","o rssi"))
        UATL_log(spaceBeforeTxPowerArray + "├{:─^10}┼{:─^10}┼{:─^10}┤".format("","",""))
        for txPower in range(0,16,1):
            UATL_log(spaceBeforeTxPowerArray + "|{: ^10}|{: ^10}|{: ^10}|".format(expectedRssiForTxPowerLUT[txPower][0],"N.C." if (expectedRssiForTxPowerLUT[txPower][1] == 0xFFFFFFFF) else expectedRssiForTxPowerLUT[txPower][1],expectedRssiForTxPowerLUT[txPower][2]))
        UATL_log(spaceBeforeTxPowerArray + "└{:─^10}┴{:─^10}┴{:─^10}┘".format("","",""))

        for txPower in range(1,16,1):
            dbmRatio = (expectedRssiForTxPowerLUT[txPower][2] - expectedRssiForTxPowerLUT[txPower][1]) / (expectedRssiForTxPowerLUT[txPower-1][2] - expectedRssiForTxPowerLUT[txPower-1][1]) 
            self.checkThat("dBm (delta rssi) between rxtx with tx power {} and {} is as expected ".format(txPower,txPower-1), (expectedRssiForTxPowerLUT[txPower][1] != 0xFFFFFFFF) and (expectedRssiForTxPowerLUT[txPower][1] != 127) and (dbmRatio > 0.9) and (dbmRatio < 1.10))
   
   
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
            txRxSuccessful = (self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(0,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*Checking payload .*\[OK\].*") == 1) and (self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        #build packet in buffer            
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
        #build packet in buffer            
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
        
        
        #run only rx and wait more than rxReceiveWindow to check that nothing has been received but timeout has occured
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0)
        self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)
        
        
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : payloads are equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 1)
        
        
        #run only rx and wait more than rxReceiveWindow to check that nothing has been received but timeout has occured
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0)
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
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    []{0x01,0x02,0x03} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
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
        #build packet in buffer            
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
        
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        #build packet in buffer            
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
        #build packet in buffer            
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
        
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
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
        #build packet in buffer            
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
        #build packet in buffer            
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
        
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.sendCommandAndListen(0,"BLE_Command__CompareReceivedPacket")
        self.waitForEndOfCommand(0,60)
        self.checkThat("device 0 : payloads are not equal",self.numberOfRegexMatchesInLog(0,".*Checking payload.*\[OK\].*") == 0)

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
        return 1
    
    def __callCliCommandsAndDoChecks__(self):   
    
        #for all action packets
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        
        """
        Build and run : True, shall PASS
        """        
        ##Device 0, Action packet 2
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Device 0, Action packet 3, triggers success
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
                
        ##Device 0, Action packet 4, does not trigger success
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #init
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        
        #build action packet chain with head at AP2
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)

        #run built chain
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                5")
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)    
        
        """
        Build and run : False, shall PASS
        """   
        ##Device 0,, modify action packet 2
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_FALSE")    
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)  
                
        
        """
        Swap AP3 and AP4 but not trigger conditions, shall FAIL
        """ 
        ##Device 0, modify action packet 2
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
                
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0)
          
class RLV_TC__LLD_TXRX_chain__condRoutine_selfLoop(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check that the statemachine loops on a actionpacket until its CR returns True if 'next action packet if false' points to itself and 'next action packet if true' points to end
           
           Device 0                                      Device 1                                 
               ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐ 
           ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │      │ Ap 2 ├─T/F─►│ Ap 3 ├──T──►│ Ap 4 ├─T/F─►│ Ap 0 │ 
           └─F─┤  RX  │      │  TX  │      │  END │      │  TX  │◄──F──┤  TX  │      │  TX  │      │  END │ 
               └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘ 
                    |             |                           |          |               |                              
                    |             ↓                           |          |               ↓                       
                    |        DR triggers success              |          |           DR triggers success      
                    ↓        when TX action is done.          ↓          ↓           when TX action is done. 
        DR just returns True.                DR just returns True.      DR just returns True.                    
        CR returns true if RX                CR just returns True       CR returns true if  
        packet is as expected.                                          timeout occurs.
 
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
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    []{0xaa,0xbb,0xcc,0xdd,0xee,0xff} ")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      5000")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Device 0, Action packet 3
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      0")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        ##Build chain
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        


        """
        Device 1
        """
        
        #for all action packets
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        
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
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0xaa,0xbb,0xcc,0xdd,0xee,0xff} ")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        ##Device 1, Action packet 3
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       

        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)

        ##Device 1, Action packet 4
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_CLEAR_FLAG_IF_IRQ_DONE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0xFF} ")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Build chain
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        """
        Run it
        """
        #run built chain
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                15")
        self.sendQuickCommand(1,"TFW_Command__SetParam      requestTimeoutInS                15")
        
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(12)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
class RLV_TC__LLD_TXRX_chain__rxtxLoop_stress(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Stress using action packet chaining
        
                Device 0/1                             
                ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐ 
                │ Ap 2 ├─T/F─►│ Ap 3 ├──T──►│ Ap 4 ├──T──►│ Ap 0 │
                │  TX  │◄──F──┤  RX  │      │  TX  │      │  END │ 
                └──────┘      └──────┘      └──────┘      └──────┘ 
                     |          |              |           
                     |          |              ↓          
                     |          |             Triggers success to free   
                     ↓          ↓             the command prompt
       CR just returns True    CR returns true if timeout occurs 
       DR increment rx counter if rx, or tx counter if tx, and increment packet success counter if packet receive is as expected
       """
        
    def getExpectedResult(self):
        return "PER (tx counter - packet success counter / tx counter) shall be < 5/1000"
        
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
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_RXTX_COUNTER")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [251]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      5000")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_RXTX_COUNTER")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0xFF} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)


        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_RXTX_COUNTER")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      rxExpectedPayload                    []{0xFF} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set times
        self.sendQuickCommand(1,"TFW_Command__SetParam      rxReceiveWindow                      5000")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
                               
        #set storage indexes  
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_RXTX_COUNTER")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [251]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        """
        Run it
        """
        requestTimeoutInS = int(self.getTimeoutInS() - 3) #reduced because we want it to finish just before the procedure timeout happens. This value might be adjusted depending on the embedded delay precision
        stressDurationInS = requestTimeoutInS - 5
        
        
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS " + str(requestTimeoutInS))
        self.sendQuickCommand(0,"TFW_Command__SetParam      stressDurationInS " + str(stressDurationInS))
        #build each action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        #build action packet chain from buffer
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        self.sendQuickCommand(1,"TFW_Command__SetParam      requestTimeoutInS " + str(requestTimeoutInS))
        self.sendQuickCommand(1,"TFW_Command__SetParam      stressDurationInS " + str(stressDurationInS))
        #build each action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        #build action packet chain from buffer
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        #run built chain
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        
        
        self.waitForEndOfCommand(0,requestTimeoutInS)
        self.waitForEndOfCommand(1,requestTimeoutInS)
        
        self.checkThat("device 0 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") == 0)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : there is no [FAILED] in the test",self.numberOfRegexMatchesInLog(1,"\[FAILED\]") == 0)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        
        self.sendQuickCommand(0,"BLE_Command__ShowStressResults")
        self.sendQuickCommand(1,"BLE_Command__ShowStressResults")
        
        d0TxCounter = self.getIntFrom(".*?txSuccessCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","d0TxCounter: " + str(d0TxCounter))
        d1TxCounter = self.getIntFrom(".*?txSuccessCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","d1TxCounter: " + str(d1TxCounter))
        
        d0RxCounter = self.getIntFrom(".*?rxSuccessCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","d0RxCounter: " + str(d0RxCounter))
        d1RxCounter = self.getIntFrom(".*?rxSuccessCounter\s+(\d+).*?",1)
        UATL_debug("embeddedStress","d1RxCounter: " + str(d1RxCounter))
                
        self.checkThat("At least one packet was sent)".format(d0TxCounter + d1TxCounter), (d0TxCounter + d1TxCounter) != 0)  
        per = ((d0TxCounter + d1TxCounter)-(d0RxCounter + d1RxCounter))/(d0TxCounter + d1TxCounter)
        self.checkThat("PER is less than 5/1000 ({:.1f}/1000)".format(1000*per), per < (5/1000))  

class RLV_TC__LLD_TXRX_chain__channelMap(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Aim of test is check ACI (auto channel incrementation) previously configured by LLD_BLE_SetChannel and LLD_BLE_SetChannelMap
        
             Device 0                                                        Device 1                                 
                 ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐            ┌──────┐      ┌──────┐      ┌──────┐ 
             ┌──►│ Ap 2 ├──T──►│ Ap 3 ├──T──►│ Ap 4 ├─T/F─►│ Ap 0 │        ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │ 
             └─F─┤  RX  │◄──F──┤  TX  │      │  TX  │      │  END │        └─F─┤  TX  │      │  TX  │      │  END │ 
                 └──────┘      └──────┘      └──────┘      └──────┘            └──────┘      └──────┘      └──────┘ 
                     ↓             |            |                                  |              |                                     
          DR just returns True.    |            ↓                                  |              ↓                                  
          CR returns true if RX    |       DR triggers success                     |      DR triggers success    
          packet is as expected    ↓       when TX action is done.                 ↓      CR just returns True  
                            DR returns True                                 DR returns True                          
                            CR returns True if timeout                      CR returns True if timeout       
                                                                                              
        start D0 then D1, if the channel map is not the same for both, then it will not work
        """
        
    def getExpectedResult(self):
        return "PER (tx counter - packet success counter / tx counter) shall be < 5/1000"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        """
        Device 0
        """      
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
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [25]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      5000")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Build chain
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
                
        """
        Device 1
        """        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [25]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        

        ##Build chain
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
                
        """
        Run it
        """
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                    8")
        self.sendQuickCommand(0,"TFW_Command__SetParam      stressDurationInS                    5")
        self.sendQuickCommand(1,"TFW_Command__SetParam      requestTimeoutInS                    8")
        self.sendQuickCommand(1,"TFW_Command__SetParam      stressDurationInS                    5")
                     
        #run built chain, same channel map, no channel    
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelMap                           [5]{0x00*}")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)   
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)    
             
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelMap                           [5]{0x00*}")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 0)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        #run built chain, same channel map, all channels
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelMap                           [5]{0xFF*}")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)                           
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)            
                                                                                                 
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelMap                           [5]{0xFF*}")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        
        #run built chain, same channel map, not all channels
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelMap                          []{0xAA,0xBB,0xCC,0xDD,0xEE}")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
            
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelMap                          []{0xAA,0xBB,0xCC,0xDD,0xEE}")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        #run built chain, different channel map
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelMap                          []{0xAA,0xBB,0xCC,0xDD,0xEE}")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
            
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelMap                          []{0x11,0x22,0x33,0x44,0x55}")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(12)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 0)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
class RLV_TC__LLD_TXRX_chain__autoChannelIncrement(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Aim of test is check ACI (auto channel incrementation) previously configured by LLD_BLE_SetChannel and LLD_BLE_SetChannelMap
        
             Device 0                                                        Device 1                                 
                 ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐            ┌──────┐      ┌──────┐      ┌──────┐ 
             ┌──►│ Ap 2 ├──T──►│ Ap 3 ├──T──►│ Ap 4 ├─T/F─►│ Ap 0 │        ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │ 
             └─F─┤  RX  │◄──F──┤  TX  │      │  TX  │      │  END │        └─F─┤  TX  │      │  TX  │      │  END │ 
                 └──────┘      └──────┘      └──────┘      └──────┘            └──────┘      └──────┘      └──────┘ 
                     ↓             |            |                                  |              |                                     
          DR just returns True.    |            ↓                                  |              ↓                                  
          CR returns true if RX    |       DR triggers success                     |      DR triggers success    
          packet is as expected    ↓       when TX action is done.                 ↓      CR just returns True  
                            DR increments channel                           DR returns True                          
                            CR returns True if timeout                      CR returns True if timeout       
                                                                                              
        start D0 with channel 0 and ACI activated and D1 with channel 1 and ACI deactivated,
        it shall work with any odd increment but not with even increment.
       """
        
    def getExpectedResult(self):
        return "PER (tx counter - packet success counter / tx counter) shall be < 5/1000"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):

        """
        Device 0
        """      
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
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [25]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      5000")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_CHANNEL")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Build chain
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
                
        """
        Device 1
        """
        self.sendCommandAndListen(1,"BLE_Command__InitBoardWithLld")
        self.waitForEndOfCommand(1,60)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_CHANNEL")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [25]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        

        ##Build chain
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
                
        """
        Run it
        """
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                    8")
        self.sendQuickCommand(0,"TFW_Command__SetParam      stressDurationInS                    5")
        self.sendQuickCommand(1,"TFW_Command__SetParam      requestTimeoutInS                    8")
        self.sendQuickCommand(1,"TFW_Command__SetParam      stressDurationInS                    5")
                     
        #run built chain, same channel map, no channel    
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelMap                           [5]{0x00*}")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)   
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)    
             
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelMap                           [5]{0x00*}")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 0)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        #run built chain, same channel map, all channels
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelMap                           [5]{0xFF*}")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)                           
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)            
                                                                                                 
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelMap                           [5]{0xFF*}")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        
        #run built chain, same channel map, not all channels
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelMap                          []{0xAA,0xBB,0xCC,0xDD,0xEE}")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
            
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelMap                          []{0xAA,0xBB,0xCC,0xDD,0xEE}")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        #run built chain, different channel map
        self.sendQuickCommand(0,"TFW_Command__SetParam      channelMap                          []{0xAA,0xBB,0xCC,0xDD,0xEE}")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
            
        self.sendQuickCommand(1,"TFW_Command__SetParam      channelMap                          []{0x11,0x22,0x33,0x44,0x55}")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)
        
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(12)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 0)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is not [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 0)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
         
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
            
            #build packet in buffer            
            self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
            self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            #build action packet chain from buffer
            self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
            self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
            #build each action packet
            self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
            self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
            #build action packet chain from buffer
            self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)
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

class RLV_CH__LLD_TXRX_chain__minimum_backToBackTime_fromWakeupTime(UATL_Characterization): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Characterize minimum b2b time     
        
                              DR does not trigger succcess.
                               ↑ 
            Device 0      ┌──────┐        ┌──────┐ 
            ┌──────┐      │ Ap 4 ├┬─T/F──►│ Ap 0 │ 
            │ Ap 2 ├──F──►│  TX  ││       │  END │ 
            │  TX  ├─T─┐  └──────┘│       └──────┘ 
            └──────┘   │  ┌──────┐│
               |       └─►│ Ap 3 ├┘
               |          │  TX  │  
               ↓          └──────┘  
     DR just returns True.      ↓                                           
     CR returns True          DR triggers succcess.                                       
       """
        
    def getExpectedResult(self):
        return "maybe 0 is the minimum"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        
        backToBackTime_MAX = 35
        backToBackTime_MIN = 0
        backToBackTime_STEP = int(backToBackTime_MAX/10)    

        #for all action packets
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #WAKEUP TIME
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        
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
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        ##Device 0, Action packet 4, does not trigger success
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
               

        ##Device 0, Action packet 2
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                    30")
        for backToBackTime in range(backToBackTime_MAX,backToBackTime_MIN-1,-backToBackTime_STEP):
            
            self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       {}".format(backToBackTime))

            
            #build action packet chain from buffer
            self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
            self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
            #run built chain
            self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
            self.waitForEndOfCommand(0,60)
            
            if self.stopIf("device 0 : there is a [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") > 0,"backToBackTime",backToBackTime):
                break
 
class RLV_CH__LLD_TXRX_chain__minimum_backToBackTime_fromB2B(UATL_Characterization): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """When the TIMER_WAKEUP bit of the action tag is set to true, we shall not use backToBackTime,
                thus it would make sense that, by setting backToBackTime to 0 (knowing that with B2B enabled minimum time is 10us),
                the action packet still works.
        
                              DR does not trigger succcess.
                               ↑ 
            Device 0      ┌──────┐        ┌──────┐ 
            ┌──────┐      │ Ap 4 ├┬─T/F──►│ Ap 0 │ 
            │ Ap 2 ├──F──►│  TX  ││       │  END │ 
            │  TX  ├─T─┐  └──────┘│       └──────┘ 
            └──────┘   │  ┌──────┐│
               |       └─►│ Ap 3 ├┘
               |          │  TX  │  
               ↓          └──────┘  
     DR just returns True.      ↓                                           
     CR returns True          DR triggers succcess.                                       
       """
        ha
    def getExpectedResult(self):
        return "When the TIMER_WAKEUP bit of the action tag is set to true, we s"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        
        
        backToBackTime_MAX = 20
        backToBackTime_MIN = 0
        backToBackTime_STEP = int(backToBackTime_MAX/10)    

        #for all action packets
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   0") #B2B TIME
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        
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
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        ##Device 0, Action packet 4, does not trigger success
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
               

        ##Device 0, Action packet 2
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                    30")
        for backToBackTime in range(backToBackTime_MAX,backToBackTime_MIN-1,-backToBackTime_STEP):
            
            self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                      {}".format(backToBackTime))

            
            #build action packet chain from buffer
            self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)
            self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)
            #run built chain
            self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
            self.waitForEndOfCommand(0,60)
            
            if self.stopIf("device 0 : there is a [FAILED] in the test",self.numberOfRegexMatchesInLog(0,"\[FAILED\]") > 0,"backToBackTime",backToBackTime):
                break

class RLV_TC__LLD_TXRX_chain__b2bDisabled(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Aim of test is check that all the timings are as it should be 
        
               WUT--CR-DR-RXW-WUT-CR-DR----WUT-CR-DR------>
        
             Device 0  
                ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐       
                │ Ap 2 ├─T/F─►│ Ap 3 ├──T──►│ Ap 4 ├─T/F─►│ Ap 0 │       
                │  RX  │◄──F──┤  TX  │      │  TX  │      │  END │       
                └──────┘      └──────┘      └──────┘      └──────┘       
                   ↓               |            |                                        
          DR inc rx/tx counters    |            ↓                                     
          CR returns true          |       DR triggers success            
                                   ↓       when TX action is done.        
                            DR returns True                               
                            CR returns True if timeout                                        
        """
        
    def getExpectedResult(self):
        return "during stressDuration, we shall start around stressDurationInS/(rxReceiveWindow + 2 * wakeupTime) RXs windows "
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
       
        rxReceiveWindow=10000
        backToBackTime=100
        wakeupTime=10000
        requestTimeoutInS=(self.getTimeoutInS()-6)
        stressDurationInS=requestTimeoutInS-3
        """
        Device 0
        """      
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #WUT TIME
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      {}".format(int(rxReceiveWindow)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                    {}".format(int(requestTimeoutInS)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      stressDurationInS                    {}".format(int(stressDurationInS)))
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_RXTX_COUNTER")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [25]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Build chain
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
                
        """
        Run it
        """
                     
        #run built chain
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)   
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)    
             
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)

        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        self.sendQuickCommand(0,"BLE_Command__ShowStressResults",True) 
              
        rxCounter = self.getIntFrom(".*?rxCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxCounter: " + str(rxCounter))
        
        expectedAsked = (1000000 * stressDurationInS)  / (rxReceiveWindow + 2 * wakeupTime)
        self.checkThat("Number of rx window started should be around (stressDurationInS)  / (rxReceiveWindow + 2 * wakeupTime) +/- 10% ({} vs {:.1f})".format(rxCounter,expectedAsked), (rxCounter >= expectedAsked * 0.9) and (rxCounter <= expectedAsked * 1.1))

class RLV_TC__LLD_TXRX_chain__b2bDisabled_rxWindow_big(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Aim of test is check that rwWindow is used as it should be 
        
             Device 0                                                     
                ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐       
                │ Ap 2 ├─T/F─►│ Ap 3 ├──T──►│ Ap 4 ├─T/F─►│ Ap 0 │       
                │  RX  │◄──F──┤  TX  │      │  TX  │      │  END │       
                └──────┘      └──────┘      └──────┘      └──────┘       
                   ↓               |            |                                        
          DR inc rx/tx counters    |            ↓                                     
          CR returns true          |       DR triggers success            
                                   ↓       when TX action is done.        
                            DR returns True                               
                            CR returns True if timeout                    
                                                                                              
        start D0 then D1, if the channel map is not the same for both, then it will not work
        """
        
    def getExpectedResult(self):
        return "when running x times and RX, we shall be able to start around testDuration/(rxReceiveWindow + backToBackTime + wakeupTime) RXs "
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
    
    
        rxReceiveWindow=1000000
        backToBackTime=100
        wakeupTime=5000
        requestTimeoutInS=(self.getTimeoutInS()-6)
        stressDurationInS=requestTimeoutInS-3
        """
        Device 0
        """      
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #WUT TIME
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      {}".format(int(rxReceiveWindow)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                    {}".format(int(requestTimeoutInS)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      stressDurationInS                    {}".format(int(stressDurationInS)))
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_RXTX_COUNTER")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [25]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Build chain
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
                
        """
        Run it
        """
                     
        #run built chain
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)   
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)    
             
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)

        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        self.sendQuickCommand(0,"BLE_Command__ShowStressResults",True) 
              
        rxCounter = self.getIntFrom(".*?rxCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxCounter: " + str(rxCounter))
        
        expectedAsked = (1000000 * stressDurationInS - wakeupTime)  / (rxReceiveWindow + wakeupTime + backToBackTime)
        self.checkThat("Number of rx window started should be around (1000000 * stressDurationInS - wakeupTime) /(rxReceiveWindow + wakeupTime + backToBackTime) +/- 10% ({} vs {:.1f})".format(rxCounter,expectedAsked), (rxCounter >= expectedAsked * 0.9) and (rxCounter <= expectedAsked * 1.1))

class RLV_TC__LLD_TXRX_chain__b2bDisabled_backToBackTime_big(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Same topo as before, but test that B2Btime has no effect if timeout is on wakeup time and not B2B
        """
        
    def getExpectedResult(self):
        return "when running x times and RX, we shall be able to start around testDuration/(rxReceiveWindow + backToBackTime + wakeupTime) RXs "
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
    
    
        rxReceiveWindow=1000
        backToBackTime=1000000
        wakeupTime=5000
        requestTimeoutInS=(self.getTimeoutInS()-6)
        stressDurationInS=requestTimeoutInS-3
        """
        Device 0
        """      
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   1") #WUT TIME
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      {}".format(int(rxReceiveWindow)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                    {}".format(int(requestTimeoutInS)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      stressDurationInS                    {}".format(int(stressDurationInS)))
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_RXTX_COUNTER")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [25]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Build chain
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
                
        """
        Run it
        """
                     
        #run built chain
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)   
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)    
             
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)

        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        self.sendQuickCommand(0,"BLE_Command__ShowStressResults",True) 
              
        rxCounter = self.getIntFrom(".*?rxCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxCounter: " + str(rxCounter))
        
        expectedAsked =  (1000000 * stressDurationInS - wakeupTime)  / (rxReceiveWindow + wakeupTime)
        self.checkThat("Number of rx window started should be around (stressDurationInS - wakeupTime) /(rxReceiveWindow + wakeupTime) +/- 10% ({} vs {:.1f})".format(rxCounter,expectedAsked), (rxCounter >= expectedAsked * 0.9) and (rxCounter <= expectedAsked * 1.1))

class RLV_TC__LLD_TXRX_chain__b2bEnabled_wakeupTime_big(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Same topo as before, but test that WUT has no effect if timerWakeup is based on B2B"""
        
    def getExpectedResult(self):
        return "when running x times and RX, we shall be able to start around testDuration/(rxReceiveWindow + backToBackTime + wakeupTime) RXs "
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
    
    
        rxReceiveWindow=5000
        backToBackTime=5000
        wakeupTime=1000000
        requestTimeoutInS=(self.getTimeoutInS()-6)
        stressDurationInS=requestTimeoutInS-3
        """
        Device 0
        """      
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   0") #WUT TIME
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      {}".format(int(rxReceiveWindow)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                    {}".format(int(requestTimeoutInS)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      stressDurationInS                    {}".format(int(stressDurationInS)))
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_RXTX_COUNTER")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [25]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Build chain
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
                
        """
        Run it
        """
                     
        #run built chain
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)   
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)    
             
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)

        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        self.sendQuickCommand(0,"BLE_Command__ShowStressResults",True) 
              
        rxCounter = self.getIntFrom(".*?rxCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxCounter: " + str(rxCounter))

        expectedAsked =  (1000000 * stressDurationInS - wakeupTime) / (rxReceiveWindow + backToBackTime)
        self.checkThat("Number of rx window started should be around (stressDurationInS - wakeupTime)/(rxReceiveWindow + backToBackTime) +/- 10% ({} vs {:.1f})".format(rxCounter,expectedAsked), (rxCounter >= expectedAsked * 0.9) and (rxCounter <= expectedAsked * 1.1))

class RLV_TC__LLD_TXRX_chain__b2bEnabled_rxWindow_big(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Same topo as before, but test effect of rxWindow"""
        
    def getExpectedResult(self):
        return "when running x times and RX, we shall be able to start around testDuration/(rxReceiveWindow + backToBackTime + wakeupTime) RXs "
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
    
    
        rxReceiveWindow=1000000
        backToBackTime=5000
        wakeupTime=5000
        requestTimeoutInS=(self.getTimeoutInS()-6)
        stressDurationInS=requestTimeoutInS-3
        """
        Device 0
        """      
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   0") #B2B TIME
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      {}".format(int(rxReceiveWindow)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                    {}".format(int(requestTimeoutInS)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      stressDurationInS                    {}".format(int(stressDurationInS)))
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_RXTX_COUNTER")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [25]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Build chain
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
                
        """
        Run it
        """
                     
        #run built chain
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)   
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)    
             
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)

        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        self.sendQuickCommand(0,"BLE_Command__ShowStressResults",True) 
              
        rxCounter = self.getIntFrom(".*?rxCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxCounter: " + str(rxCounter))
        
        expectedAsked =  (1000000 * stressDurationInS - wakeupTime)  / (rxReceiveWindow + wakeupTime + backToBackTime)
        self.checkThat("Number of rx window started should be around (stressDurationInS - wakeupTime) /(rxReceiveWindow + wakeupTime + backToBackTime) +/- 10% ({} vs {:.1f})".format(rxCounter,expectedAsked), (rxCounter >= expectedAsked * 0.9) and (rxCounter <= expectedAsked * 1.1))

class RLV_TC__LLD_TXRX_chain__b2bEnabled_backToBackTime_big(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Same topo as before, but test that B2B time has an effect if timerWakeup is based on B2B"""
        
    def getExpectedResult(self):
        return "when running x times and RX, we shall be able to start around testDuration/(rxReceiveWindow + backToBackTime + wakeupTime) RXs "
        
    def getBoardNumber(self):
        return 1
    
    def __callCliCommandsAndDoChecks__(self):
    
    
        rxReceiveWindow=5000
        backToBackTime=1000000
        wakeupTime=5000
        requestTimeoutInS=(self.getTimeoutInS()-6)
        stressDurationInS=requestTimeoutInS-3
        """
        Device 0
        """      
        self.sendQuickCommand(0,"TFW_Command__SetParam      timerWakeupBasedOnWakeupTimeNotB2B   0") #WUT TIME
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      {}".format(int(rxReceiveWindow)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      requestTimeoutInS                    {}".format(int(requestTimeoutInS)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      stressDurationInS                    {}".format(int(stressDurationInS)))
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            3")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_INC_RXTX_COUNTER")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [25]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            []{0x00} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        ##Build chain
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
                
        """
        Run it
        """
                     
        #run built chain
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)   
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)    
             
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)

        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        
        self.sendQuickCommand(0,"BLE_Command__ShowStressResults",True) 
              
        rxCounter = self.getIntFrom(".*?rxCounter\s+(\d+).*?",0)
        UATL_debug("embeddedStress","rxCounter: " + str(rxCounter))

        expectedAsked =  (1000000 * stressDurationInS - wakeupTime) / (rxReceiveWindow + backToBackTime)
        self.checkThat("Number of rx window started should be around (stressDurationInS - wakeupTime)/(rxReceiveWindow + backToBackTime) +/- 10% ({} vs {:.1f})".format(rxCounter,expectedAsked), (rxCounter >= expectedAsked * 0.9) and (rxCounter <= expectedAsked * 1.1))

class RLV_TC__LLD_TXRX_chain__simple_stateMachine_channel(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check that the different statemachines are working, then use it simultaneously in another test
   
           Device 0                                         Device 1
            --> State machine 1, channel 27                --> State machine 3, channel 27           
               ┌──────┐      ┌──────┐      ┌──────┐               ┌──────┐      ┌──────┐      ┌──────┐       
           ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │           ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │       
           └─F─┤  RX  │      │  TX  │      │  END │           └─F─┤  TX  │      │  TX  │      │  END │       
               └──────┘      └──────┘      └──────┘               └──────┘      └──────┘      └──────┘       
                    |             |                                    |             |                       
                    |             ↓                                    |             ↓                       
                    |        DR triggers success.                      |        DR triggers success.         
                    ↓                                                  ↓                                     
        DR just returns True.                              DR just returns True.                                        
        CR returns true if RX                              CR returns true when                              
        packet is as expected.                             timeout has occured.                              
                                                                                                                                                                             
           --> State machine 5, channel 22                --> State machine 6, channel 22 
               ┌──────┐      ┌──────┐      ┌──────┐               ┌──────┐      ┌──────┐      ┌──────┐     
           ┌──►│ Ap 4 ├──T──►│ Ap 5 ├─T/F─►│ Ap 0 │           ┌──►│ Ap 4 ├──T──►│ Ap 5 ├─T/F─►│ Ap 0 │     
           └─F─┤  RX  │      │  TX  │      │  END │           └─F─┤  TX  │      │  TX  │      │  END │     
               └──────┘      └──────┘      └──────┘               └──────┘      └──────┘      └──────┘     
                    |             |                                    |             |                     
                    |             ↓                                    |             ↓                     
                    |        DR triggers success                       |        DR triggers success.       
                    ↓                                                  ↓                                   
        DR just returns True.                              DR just returns True.                            
        CR returns true if RX                              CR returns true when                            
        packet is as expected.                             timeout has occured.                            
        
        """
        
    def getExpectedResult(self):
        return "Data shall be received, no matter how many times it is run, because in case of failure, it will retry"
        
    def getBoardNumber(self):
        return 2
    
    def __callCliCommandsAndDoChecks__(self):
        backToBackTime=1000
        wakeupTime=10000
        requestTimeoutInS=8
        stressDurationInS=5
        
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      requestTimeoutInS                    {}".format(int(requestTimeoutInS)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      stressDurationInS                    {}".format(int(stressDurationInS)))
        
        """
        Device 0 : 1st State machine
        """
        #Init
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        
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
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [10]{0xAA*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      200000")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionId                             1")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apStateMachineId                     1")
        self.sendQuickCommand(0,"TFW_Command__SetParam      channel                              27")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
          
        """
        Device 1 : 1st State machine
        """
        
        #Init
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [10]{0xAA*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionId                             1")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apStateMachineId                     3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      channel                              27")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
        
     
        """
        Run D0 and D1 with 2nd SM
        """                     
        #run built chain  
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)

        """
        Device 0 : 2nd State machine
        """
        #Init
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             5")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_PACKET_AS_EXPECTED")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [10]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      200000")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                5")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionId                             2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apStateMachineId                     1")
        self.sendQuickCommand(0,"TFW_Command__SetParam      channel                              22")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
          
        """
        Device 1 : 1st State machine
        """
        
        #Init
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             5")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [10]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                5")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionId                             2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apStateMachineId                     3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      channel                              22")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
        
     
        """
        Run D0 and D1 with 2nd SM
        """                     
        #run built chain  
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
  
class RLV_TC__LLD_TXRX_chain__multiple_stateMachine_channel(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check that a multiple statemachine can work at the same time. 
   
           Device 0                                         Device 1
            --> State machine 1, channel 27                --> State machine 3, channel 27           
               ┌──────┐      ┌──────┐      ┌──────┐               ┌──────┐      ┌──────┐      ┌──────┐       
           ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │           ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │       
           └─F─┤  RX  │      │  TX  │      │  END │           └─F─┤  TX  │      │  TX  │      │  END │       
               └──────┘      └──────┘      └──────┘               └──────┘      └──────┘      └──────┘       
                    |             |                                    |             |                       
                    |             ↓                                    |             ↓                       
                    |        DR triggers success.                      |        DR triggers success.         
                    ↓                                                  ↓                                     
        DR just returns True.                              DR just returns True.                                        
        CR returns true if RX                              CR returns true when                              
        packet is as expected.                             timeout has occured.                              
                                                                                                                                                                             
            --> State machine 5, channel 22                --> State machine 6, channel 22 
               ┌──────┐      ┌──────┐      ┌──────┐               ┌──────┐      ┌──────┐      ┌──────┐     
           ┌──►│ Ap 4 ├──T──►│ Ap 5 ├─T/F─►│ Ap 0 │           ┌──►│ Ap 4 ├──T──►│ Ap 5 ├─T/F─►│ Ap 0 │     
           └─F─┤  RX  │      │  TX  │      │  END │           └─F─┤  TX  │      │  TX  │      │  END │     
               └──────┘      └──────┘      └──────┘               └──────┘      └──────┘      └──────┘     
                    |             |                                    |             |                     
                    |             ↓                                    |             ↓                     
                    |        DR triggers success                       |        DR triggers success.       
                    ↓                                                  ↓                                   
        DR just returns True.                              DR just returns True.                            
        CR returns true if RX                              CR returns true when                            
        packet is as expected.                             timeout has occured.                                 
        
        """
        
    def getExpectedResult(self):
        return "Data shall be received, no matter how many times it is run, because in case of failure, it will retry"
        
    def getBoardNumber(self):
        return 2
    
    
    def __callCliCommandsAndDoChecks__(self):
        backToBackTime=1000
        wakeupTime=10000
        requestTimeoutInS=8
        stressDurationInS=5
        
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      requestTimeoutInS                    {}".format(int(requestTimeoutInS)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      stressDurationInS                    {}".format(int(stressDurationInS)))
        
        """
        Device 0 : 1st State machine
        """
        #Init
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        
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
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [10]{0xAA*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      200000")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionId                             1")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apStateMachineId                     1")
        self.sendQuickCommand(0,"TFW_Command__SetParam      channel                              27")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
          
        """
        Device 1 : 1st State machine
        """
        
        #Init
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [10]{0xAA*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionId                             1")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apStateMachineId                     5")
        self.sendQuickCommand(1,"TFW_Command__SetParam      channel                              27")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
     
        """
        Device 0 : 2nd State machine
        """
        #Init
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             5")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_PACKET_AS_EXPECTED")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [10]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      200000")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                5")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionId                             2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apStateMachineId                     3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      channel                              22")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
          
        """
        Device 1 : 1st State machine
        """
        
        #Init
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             5")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [10]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                5")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionId                             2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apStateMachineId                     6")
        self.sendQuickCommand(1,"TFW_Command__SetParam      channel                              22")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
        
     
        """
        Run D0 and D1 with 2nd SM
        """                     
        #run built chain  
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
 
class RLV_TC__LLD_TXRX_chain__multiple_stateMachine_networkId(UATL_TestCase): #ready
    def getVersion(self):
        return "v1.0"
        
    def getImplementationStatus(self):
        return UATL_Procedure.ImplementationStatus.READY_TO_BE_RUN
        
    def getObjective(self):
        return """Check that a multiple statemachine can work at the same time.  using different networkId (BLE compliant network IDs: 0x6CFABCDF or 0x5A964129 or 0x71764129)
   
           Device 0                                         Device 1
            --> State machine 1, networkId 0x6CFABCDF       --> State machine 3, networkId 0x6CFABCDF          
               ┌──────┐      ┌──────┐      ┌──────┐               ┌──────┐      ┌──────┐      ┌──────┐       
           ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │           ┌──►│ Ap 2 ├──T──►│ Ap 3 ├─T/F─►│ Ap 0 │       
           └─F─┤  RX  │      │  TX  │      │  END │           └─F─┤  TX  │      │  TX  │      │  END │       
               └──────┘      └──────┘      └──────┘               └──────┘      └──────┘      └──────┘       
                    |             |                                    |             |                       
                    |             ↓                                    |             ↓                       
                    |        DR triggers success.                      |        DR triggers success.         
                    ↓                                                  ↓                                     
        DR just returns True.                              DR just returns True.                                        
        CR returns true if RX                              CR returns true when                              
        packet is as expected.                             timeout has occured.                              
                                                                                                                                                                             
            --> State machine 5, networkId 0x71764129      --> State machine 6, networkId 0x71764129 
               ┌──────┐      ┌──────┐      ┌──────┐               ┌──────┐      ┌──────┐      ┌──────┐     
           ┌──►│ Ap 4 ├──T──►│ Ap 5 ├─T/F─►│ Ap 0 │           ┌──►│ Ap 4 ├──T──►│ Ap 5 ├─T/F─►│ Ap 0 │     
           └─F─┤  RX  │      │  TX  │      │  END │           └─F─┤  TX  │      │  TX  │      │  END │     
               └──────┘      └──────┘      └──────┘               └──────┘      └──────┘      └──────┘     
                    |             |                                    |             |                     
                    |             ↓                                    |             ↓                     
                    |        DR triggers success                       |        DR triggers success.       
                    ↓                                                  ↓                                   
        DR just returns True.                              DR just returns True.                            
        CR returns true if RX                              CR returns true when                            
        packet is as expected.                             timeout has occured.                                 
        
        """
        
    def getExpectedResult(self):
        return "Data shall be received, no matter how many times it is run, because in case of failure, it will retry"
        
    def getBoardNumber(self):
        return 2
    
    
    def __callCliCommandsAndDoChecks__(self):
        backToBackTime=1000
        wakeupTime=10000
        requestTimeoutInS=8
        stressDurationInS=5
        
        self.sendQuickCommand(0,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(0,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      wakeupTime                           {}".format(int(wakeupTime)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      backToBackTime                       {}".format(int(backToBackTime)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      requestTimeoutInS                    {}".format(int(requestTimeoutInS)))
        self.sendQuickCommand(1,"TFW_Command__SetParam      stressDurationInS                    {}".format(int(stressDurationInS)))
        
        """
        Device 0 : 1st State machine
        """
        #Init
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        
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
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [10]{0xAA*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      200000")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionId                             1")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apStateMachineId                     1")
        self.sendQuickCommand(0,"TFW_Command__SetParam      networkId                            0x6CFABCDF")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
          
        """
        Device 1 : 1st State machine
        """
        
        #Init
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            2")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [10]{0xAA*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                3")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionId                             1")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apStateMachineId                     5")
        self.sendQuickCommand(0,"TFW_Command__SetParam      networkId                            0x6CFABCDF")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                2")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
     
        """
        Device 0 : 2nd State machine
        """
        #Init
        self.sendQuickCommand(0,"BLE_Command__InitBoardWithLld",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             5")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_PACKET_AS_EXPECTED")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      0") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxExpectedPayload                    [10]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #set times
        self.sendQuickCommand(0,"TFW_Command__SetParam      rxReceiveWindow                      200000")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                5")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(0,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(0,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(0,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(0,"TFW_Command__SetParam      actionId                             2")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apStateMachineId                     3")
        self.sendQuickCommand(0,"TFW_Command__SetParam      networkId                            0x71764129")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(0,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(0,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(0,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
          
        """
        Device 1 : 1st State machine
        """
        
        #Init
        self.sendQuickCommand(1,"BLE_Command__InitBoardWithLld",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             5")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            4")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_SIMPLE_RET_TRUE")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_RET_TRUE_IF_STRESS_TIMES_OUT")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [10]{0xFF*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        #set storage indexes
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                5")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfTrueStorageIndex             0")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apNextIfFalseStorageIndex            0")
        #set for current action packet - routines       
        self.sendQuickCommand(1,"TFW_Command__SetParam      apDataRoutineType                    APDR_JUST_CLEAR_FLAGS")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCondRoutineType                    APCR_SIMPLE_RET_TRUE")
        #set for current action packet - action tag
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionIsTxNotRx                      1") #TXRX
        #set for current action packet - packet       
        self.sendQuickCommand(1,"TFW_Command__SetParam      txPayload                            [0]{0x00*} ")
        #save current action packet
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        #build packet in buffer            
        self.sendQuickCommand(1,"BLE_Command__BuildCurrentActionPacketInBuffer",True)
        
        
        #Build 1st statemachine 
        self.sendQuickCommand(1,"TFW_Command__SetParam      actionId                             2")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apStateMachineId                     6")
        self.sendQuickCommand(0,"TFW_Command__SetParam      networkId                            0x71764129")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentType                        AP_TXRX")
        self.sendQuickCommand(1,"TFW_Command__SetParam      apCurrentStorageIndex                4")
        self.sendQuickCommand(1,"BLE_Command__BuildStateMachine",True)  
        self.sendQuickCommand(1,"BLE_Command__BuildActionPacketChainFromBuffer",True)   
        
     
        """
        Run D0 and D1 with 2nd SM
        """                     
        #run built chain  
        self.sendCommandAndListen(0,"BLE_Command__RunApChainAndWaitForItToFinish")
        time.sleep(1)
        self.sendCommandAndListen(1,"BLE_Command__RunApChainAndWaitForItToFinish")
        self.waitForEndOfCommand(0,60)
        self.waitForEndOfCommand(1,60)
        UATL_logCommandInfo("")
        self.checkThat("device 0 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 0 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(0,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_IsAnActionPending() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_IsAnActionPending.*\[OK\].*") == 1)
        self.checkThat("device 1 : RLV_TFW_HasAnActionFailed() is [OK]",self.numberOfRegexMatchesInLog(1,".*RLV_TFW_HasAnActionFailed.*\[OK\].*") == 1)
 
