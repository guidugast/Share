STM32WB - ATE (Automatic Test Environment) GUIDELINE
============

## Overview
---

### Historical 
*   this file was created in early 2020 for the validation projects of the radio LLD of the STM32WBx5

### Project
*   The aim of this project is to provide an easy and fast way for writing tests, and keeping test procedure implementation flexible, and then easily automating tests through console or jenkins
*   There is two ways of using this environment: Shortcuts (console) or Jenkins 

## How to?
---
    
###  Run a validation campaign by choosing module versions
    1. Create your workspace in folder that should not be a git folder, and rather be empty, and rather be close to root like C:/STM32WB_WORKSPACE/ or C:/AUTOMATIC_TESTS/

    2. Clone the test env scripts repo in that folder:
    - url: ssh://gitolite@codex.cro.st.com/mcuembswappli/Test_Automation/stm32wb_ate.git
    - branch: master (or your branch if you have on)
        Note that;
        - master is intended for generic part
        - branches are used either for :
            - generic feature work in progress, name it feature/<feature_name>
            - project 'familly'. For instance, the 'LLD BLE' project familly would have the following projects with their own tests procedure (or not), or their own testsuites and configuration
                - WB55_M0_BLE
                - WB55_M4_BLE
                - WB35_M0_BLE
                - WB35_M4_BLE
                - WB15_M0_BLE
                - WB15_M4_BLE

    3. Open a bash in admin mode (to avoid risks of encountering git-maximum-path-length issues )

    4. Create your test environment, run :
        > cd <directory to your workspace>
        > ./stm32wb_ate/03_Advanced_user_shorcuts/_init_test_env.sh

    5. Configure your test environment here: ./00_Tools_and_config/00_Common/00_Config/Common.cfg

    6. Configure your manifest:
    
    6.1 If needed, correct, update, or create your manifest "<manifest_name>.manifest" in ./00_Tools_and_config/01_Projects/<wb-ate_project_name>/00_Config/<manifest_name>.manifest
        --> to add a module, add the following line: ```add_module ${core_name} ${module_name} ${module_version} ${module_git_url} ${module_output_path} ${sha_1 (optional)}  ```

    6.2 Configure your project here: ```./00_Tools_and_config/01_Projects/<wb-ate_project_name>/00_Config/Project.cfg```
    Pick the manifest you want:
    MANIFEST=<manifest_name>.manifest

    7. Configure your testsuite:
    
    7.1 If needed, correct, update, or create your testsuite "<testsuite_name>.testsuite" in ```./00_Tools_and_config/01_Projects/<wb-ate_project_name>/00_Config/<testsuite_name>.testsuite```
        --> comment with '#' the lines of the TC you don't want
        
    7.2 Configure your project here: ```./00_Tools_and_config/01_Projects/<wb-ate_project_name>/00_Config/Project.cfg```
    Pick the testsuite you want:
    TESTSUITE=<testsuite_name>.testsuite
    
    8. Update python, run :
        > cd <workspace>/00_Tools_and_config/03_Advanced_user_shorcuts
        > ./_configure_python.sh
    
    9. then either (9.1) or (9.2):

    9.1 run full build :
        > cd ./00_Tools_and_config/02_User_shortcuts/ && ./00_full_build_for_project.sh <wb-ate_project_name>

    9.2 run each step (source update, build, flash, validation) separately, starting by step 1 (script 01_xxxx)
    Go in 02_User_shortcuts/ folder to launch each script by using the following syntax: 
        > ./<script_name> <wb-ate_project_name>

    Thus, for instance, for starting again a validation for project WB55_BLE that you already have updated, configured, compiled and flashed binary on boards, 
    you should run:
        > ./04_run_full_campaign_for_project.sh WB55_BLE

    Note: you can enable or disable a test in the testsuite by commenting it, and run again the validation with the updated testsuite
    
###   Run a validation campaign on the latest RC tag
    Apply previous procedure by using the manifest called "Baseline.manifest" that should have been configured and the testsuite called "Full.testsuite"
    Baseline manifest shall contain modules that either are tags or branches with sha-1.
    
###   Run a validation campaign at a specific baseline
    Apply previous procedure by using the manifest called "<baseline_name>.manifest" and "<baseline_name>.testsuite".
    Baseline manifest shall contain modules that either are tags or branches with sha-1.
    Baseline testsuite shall contain all test procedure that shall be run on this baseline.
    
###   Run a validation campaign on the latest version for each modules
    Apply previous procedure by using the manifest called "Dynamic.manifest" and the testsuite called "Full.testsuite"
    All SHA-1 should be disabled with "" or "-" or "none" in the manifest.

###   Run a specific test
    Apply previous procedure by using your own testsuite.
    Create your own testsuite file "<Testsuite_name>.testsuite" or use Custom.testsuite rather than using existing testsuites to avoid commiting by mistake changes
    Comment with '#' the lines of the TC you don't want
    
###   Modify/Create a baseline
    Modifiy the git manifest here ```./00_Tools_and_config/01_Projects/<wb-ate_project_name>/00_Config/Baseline.manifest```
      or create your own <baseline_name>.manifest
    In a baseline, all modules shall be either tag or sha-1
    
    --> After committing && push this new folder in the test env repo. add a tag to it '<baseline_name>.baseline'

