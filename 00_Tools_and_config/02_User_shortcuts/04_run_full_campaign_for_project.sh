#!/bin/sh

#PROJECT_NAME = $1
if [[ -z "$1" ]]; then
    echo "No project name given as first script argument."
    exit 1
else
    PROJECT_NAME=$1
fi

#BUILD_ID = $2
if [[ -z "$2" ]]; then
    #standalone build
    BUILD_ID="""$(date +"%Y%m%d%H%M")_standalone"""
else
    #full manual or full auto builds
    BUILD_ID=$2
fi

#we are in ${WORKSPACE_ROOT_PATH}/00_Tools_and_config/02_User_shortcuts/
WORKSPACE_ROOT_PATH="$(pwd)/../.."	
eval PROJECT_PATHS="${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/02_Scripts/Project.paths"

source $PROJECT_PATHS 
source $COMMON_CFG
source $COMMON_LIB
source $PROJECT_CFG


if [[ ! -f "$VALIDATION_TESTSUITE" ]]; then
    echo "No testsuite was given in the project config folder"
    exit 1
fi

mkdir -p $LOG_PATH  

display_big_banner "Starting validation campaign with selected Testsuite"

cd ${COMMON_SCRIPTS_PATH}
echo "Work in progress... please wait."
while true
do
    ${PYTHON38} -u validation.py -t "${VALIDATION_TESTSUITE}" -u "${ST_LINK_UTILITY}" -r "${LOG_PATH}" 2>&1 | tee -a "${LOG_PATH}/validationReport.log"
    ret=${PIPESTATUS[0]}
    if [[ $ret -eq 0 ]]; then 
        echo "Script exited with no error"
        break
    elif [[ $ret -eq 2 ]]; then 
        # then kill process python
        echo "No port com Found"
        echo "Maybe python was not ended with a clean exit."
        echo "Killing python process"
        taskkill -IM python.exe -F
        sleep 5
        echo "Trying again..."
    else
        echo "Unexpected error during validation: $ret"
        exit $ret
    fi
done  
sed -r "s/\x1B\[([0-9]{1,3}(;[0-9]{1,2})?)?[mGK]//g" "${LOG_PATH}/validationReport.log" > "${LOG_PATH}/validationReport.temp"  
mv "${LOG_PATH}/validationReport.temp"  "${LOG_PATH}/validationReport.log" 

cd - 

display_end_banner "Testcampaign finished..."