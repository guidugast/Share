# ATE/UATL/RLV:
    - Start a BZ topic for UATL when it will be released for users
    - reset the boards before each testcase procedure is started (to be fixed)
    - Add an option in test tool protocol of BLE for resetting boards or resetting test env
    - use HW reset for resetting boards through ST link utility
    - for each test that serialize condition for a good transmission, there is a probability of failure, but the TC should not be failed if PER is 5 < 1000, thus I think each TC shall be run 1000th time
    - instead of for loop for CH, use a dichotomic loop
    - instead of for loop for CH, use multiple loop with statistic analysis to have min and max. (min : sure to work, max : sure to not work)
    - fix bug that sometimes prevent from resetting (USB connexion issue?)
    - fix bug that sometimes prevent from exiting directly after an UATL error + sys.exit.
    - add in UATL_Procedure reset and timeout counter (actually it is related only to last command)
    - now tests are stopped if an RLV error occurs, clean counter for endurance? remove it?
    - make in conf the procedure timeout optionnal (if nothing it put, a default value of (for instance) 2 minutes will be used)
    - have a project list in the root of the test env and dl only projects that are listed (so we need to store projects in a specific repo, and keep the generic part in this repo)
    - For 1-board-test, use the board that is available, not systematically the first one. That would allow to run several tests in parallel for 1-board-tests
    - correct error return codes help for UATL (search for printHelp in main.py), create/correct error return codes for each sys.exit
    - for jenkins use, add the possibility to read arg from the project name.
       For instance, use ProjectName__ManifestName__TestsuiteName, that would be splitted in ProjectName, ManifestName and TestsuiteName.
       e.g.: WB55_M0_BLE__Baseline__Full, WB55_M0_BLE__Custom__Custom, WB55_M0_BLE__Dynamic__NonReg, WB55_M0_BLE__Baseline__NonReg
       Then modify the project.cfg localy before running further stages (after script update)
    - writting validation report in file: not in folder anymore! /01_Logs/${BUILD_ID}/file.xxx ; BUILD_ID is ""
    - split user shortcuts folder in : all users, tester shorcuts, dev shortcuts, jenkins shorcuts, admin shorcuts. Remove advanced user shorcut
    
# LLD BLE:

    ## BUG TO ANALYZE:
        - In RLV_TC__HAL_TXRX_Stress_WithEncrypt_NoAck__nominal, D0 and D1 stop answering, then "resetting board 0 (port COM8, st id 0).Unexpected error during validation: 139"
    ## ENV:
        - REBASE FROM "V.1.9.RC3" TO "V.1.9.RC3-"
        - test packet size effect on characterization procedures
        - remove apCurrentType because it is useless, we could instead use the index (0 for end, 1 for empty, 2 for TXRX)- fix test RLV_TC__HAL_TXRX_Stress_Ack__onlyRx
    ## NEW TESTS:
        - check all "assert_param"
        - encryptOnceEvery2Packets
        - check for all actionTags fields
        - all state machines busy
        - call LLD_BLE_MakeActionPacketPending when busy
        - set reserved area during a packet chain that changes the packet that is running
        - check all bits of p->status, generate all error/cases/status bits
        - NS_EN enabled/disabled with sn/nesn? still some work to do in the binary, but will need some time to implement, is it worth doing it?
        - StopActivity during a packet chain
        - timing characterization?
        - tx power / rssi with start tone
        - tx power / rssi with send packet
        - time remaining before next RF activity, check it with db7 and picoscope (Cf. Thierry GASQUET)
    ## BZ TICKET TO ADD:
        - EPR 6.7 % ? run long tests
        - tx power no coherence in values 