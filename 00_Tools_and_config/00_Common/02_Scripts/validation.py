# -*- coding: utf-8 -*-
# python version 3.8.1

import getopt
import sys
import time
import os.path
import io
#TODO import sh
from PyLib.UATL import *


def printHelp():
    UATL_log( " Usage : ")
    UATL_log( "    python " + os.path.basename(__file__) + " -s <testsuite> -r <reportPath> [-h|--help] ")
    UATL_log( "       -h|--help                                             Show this help")
    UATL_log( "       -s <testsuite>|--test_suite=<testsuite>               Specify test suite to load, mandatory argument.")
    UATL_log( "       -r <reportPath>|--report_path=<reportPath>            Define report path, mandatory argument.")
    UATL_log( "         ")
    UATL_log( "       ------------------                     ")
    UATL_log( " Return values : ")
    UATL_log( "      0) Exited without error.")
    UATL_log( "      1) Argument error.")
    UATL_log( "      2) No board found -- no port COM is available .")
    UATL_log( "      3) Unexpected error.")
    UATL_log( "      4) Test timeout error. Aborting test/campaign...") #??
    UATL_log( "      5) Serial communication started but board not responding.")
    UATL_log( "      6) Two board are need but only one is connected.")
    UATL_log( "      7) Terminal is in use.")
    UATL_log( "      8) nothing is read on port COM.")
    UATL_log( "      9) Error in testsuite (format, CLI command,...).")
    UATL_log( "     10) Error in testcase (implementation).")
    UATL_log( "       ------------------                     ")
    
def readUserArgs():
    stLinkUtilityExe = None
    testSuitePath = None
    testSuite = None
    reportPath = None
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:u:r:", ["help","test_suite=","st_link_utility=","report_path=" ])
    except getopt.GetoptError as err:
        UATL_error( err )
        printHelp()
        sys.exit(1)
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printHelp()
            sys.exit()
        elif opt in ("-t", "--test_suite"):
            testSuitePath = arg
        elif opt in ("-r", "--report_path"):
            reportPath = arg
        elif opt in ("-u", "--st_link_utility"):
            stLinkUtilityExe = arg
        else:
            UATL_error( "Unhandled option...")
            printHelp()
            sys.exit(1)

    if stLinkUtilityExe is None:
        UATL_log( "/!\ Warning: No ST-Link Utility has been provided, the board reset is disabled")
        
    if testSuitePath is None:
        UATL_log( "A testsuite should be provided")
        printHelp()
        sys.exit(1)
        
    if reportPath is None:
        UATL_log( "A report path should be provided")
        printHelp()
        sys.exit(1)
              
    return (testSuitePath, stLinkUtilityExe, reportPath)


if __name__ == '__main__':
    
    sys.stdout.reconfigure(encoding='utf-8')

    junitReportFile = None
        
    UATL_printScriptVersion()
        
    if len(sys.argv) <= 1:
        UATL_error( "Not enough arguments calling script")
        printHelp()
        sys.exit(1)

    (testSuitePath,stLinkUtilityExe,reportPath) = readUserArgs()
    
    testBench = UATL_TestBench(stLinkUtilityExe)
    
    try:
        csvTestReportFilePath = str(str(reportPath)+"/validationReport.csv")
        csvTestReportFile = io.open(csvTestReportFilePath,"w+", encoding="utf-8")
    except:
        UATL_log("An error occured while creating CSV test report file" + sys.exc_info()[0])
        sys.exit(1)
        
    try:
        junitReportFilePath = str(str(reportPath)+"/validationReport.xml")
        junitReportFile = io.open(junitReportFilePath,"w+", encoding="utf-8")
    except:
        UATL_log("An error occured while creating JUnit report file" + sys.exc_info()[0])
        sys.exit(1)

        
    testBench.launchTest(testSuitePath, csvTestReportFile, junitReportFile)
    
    csvTestReportFile.close()    
    junitReportFile.close()

    UATL_log("")
    UATL_log("End of script.")
    sys.exit(0)        