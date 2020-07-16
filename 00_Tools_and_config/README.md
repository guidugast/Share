STM32WB - ATE (Automatic Test Environment) GUIDELINE
============


## TODO:
---
    TO BE WRITTEN

## Overview
---

### Historical 
*   this file was created in early 2020 for the validation projects of the radio LLD of the STM32WBx5

### Project overview
*   The aim of this project is to provide an easy and fast way for writing tests, and keeping test procedure implementation flexible, and then easily automating tests through console or jenkins
*   There is two ways of using this environment: Shortcuts (console) or Jenkins 

## How to?
---

###   Run the project with jenkins
    TO BE WRITTEN
    
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
    
    6.1 Correct, update, or create your manifest "<manifest_name>.manifest" in ./00_Tools_and_config/01_Projects/<project_name>/00_Config/<manifest_name>.manifest
        
    6.2 Configure your project here: ./00_Tools_and_config/01_Projects/<project_name>/00_Config/Project.cfg
    Pick the manifest you want:
    MANIFEST=<manifest_name>.manifest

    7. Configure your testsuite:
    
    7.1 Correct, update, or create your testsuite "<testsuite_name>.testsuite" in ./00_Tools_and_config/01_Projects/<project_name>/00_Config/<testsuite_name>.testsuite
        --> comment with '#' the lines of the TC you don't want
        
    7.2 Configure your project here: ./00_Tools_and_config/01_Projects/<project_name>/00_Config/Project.cfg
    Pick the testsuite you want:
    TESTSUITE=<testsuite_name>.testsuite
    
    8. Update python, run :
        > cd <workspace>/00_Tools_and_config/03_Advanced_user_shorcuts
        > ./_configure_python.sh
    
    9. then either (9.1) or (9.2):

    9.1 run full build :
        > cd ./00_Tools_and_config/02_User_shortcuts/ && ./00_full_build_for_project.sh <project_name>

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

###   Modify a testcase (in python)
    TO BE WRITTEN (UATL.py need to be splitted first)
    
###   Create a custom project (for jenkins and UATL)
    TO BE WRITTEN
    
###   Modify/Create a baseline
    Modifiy the git manifest here ./00_Tools_and_config/01_Projects/<project_name>/00_Config/Baseline.manifest
      or create your own <baseline_name>.manifest
    In a baseline, all modules shall be either tag or sha-1
    
    --> After committing && push this new folder in the test env repo. add a tag to it '<baseline_name>.baseline'

    
###   Configure your environment
    TO BE WRITTEN

###   Configure your project
    TO BE WRITTEN

## Scripts
---

### Script types
*   library (.sh, .py)
*   configuration file (.cfg)
*   script with "project name" as an argument: ```./script.xx "project name"```, configurable by project config files (common and/or project cfg), to be run in "${workspace}/00_Tools_and_config/02_User_shortcuts"
*   script with no argument, ```./_script.xx ``` configurable by modifiying the script itself : ```./script.xx```, to be run in "${workspace}/00_Tools_and_config/03_Advanced_user_shorcuts"
*   script with no argument, ```./script.xx ```, special behavior, please refer to this documentation
*   Description ### TODO: translate
    Au niveau des scripts manuels, qui peuvent être lancés individuellement ou de manière automatique, et qui ont des paramètres à rentrer:
    - scripts shells project update: pour mettre à jour en fonction d'UN git manifest (liste de couples module/version) le code source du projet 
    - scripts shell de build : pour builder UN code en un couple de binaires m0/m4
    - scripts shell de flash : pour flasher UN couple de binaire dans une liste prédéfinie de board (pour RLV v1 c'est le même binaire pour toutes les boards)
    - scripts pythons: pour automatiser l'envoi de commande de test vers le binaire afin de lancer les tests et de parser les résultats pour les traduire au format jenkins

    Il existe un script qui va mettre à jour les scripts ci dessus en allant chercher dans la DB git:
    - scripts shells environement update: pour mettre à jour les outils projets (buid, flash, validation,...)

    Il existe un certain nombre de scripts faciles d'utilisation, ce sont les scripts shell "shortcuts"
    qui sont des "alias", c-à-d un script simple d'appel sans argument appelant un script complexe avec arguments 
    chaque script shortcut correspond à une action simple:
    - "reset all boards"
    - update project
    - build project
    - flash project
    - validate project

    Au niveau de l'automatisation ces scripts utilisent les scripts ci-dessus:
    - un script shell d'automatisation du build complet lançable depuis un poste local :
        - MAJ des sources projet
        - build
        - flash
        - lancement des test
        - affichage terminal des résultats sur le terminal
        - parsing des résultats pour traduction vers jenkins (.xml) et vers fichier xls (.csv)
    - un script jenkins pipeline d'automatisation du build complet étendu lançable depuis un serveur:
        - MAJ de l'environnement
        - MAJ des sources projet
        - build
        - flash
        - lancement des test
        - affichage terminal des résultats sur le terminal
        - parsing des résultats pour traduction vers jenkins
        - affichage sous jenkins des courbes en fonction du temps

### Test env
*   test env creation script 'init_LLD_valid_env_in_this_folder.sh', to be run in the folder where you want to create your test env, shall be close to root
*   test env update script 'update_scripts.sh', to be run in ${workspace}/00_Tools_and_config/

### Shortcuts
*   find it here : "${workspace}/00_Tools_and_config/02_User_shortcuts"

