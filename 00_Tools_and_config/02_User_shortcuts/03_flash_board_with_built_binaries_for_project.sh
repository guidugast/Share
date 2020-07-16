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
WORKSPACE_ROOT_PATH=$(realpath  $(pwd)/../..)	
PROJECT_PATHS=$(realpath  ${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/02_Scripts/Project.paths)

source $PROJECT_PATHS 
source $COMMON_CFG
source $COMMON_LIB
source $PROJECT_CFG


if [[ ! -f "$PROJECT_C_SOURCES_PATH/$M0_TOP_DIR/$M0_BINARY_FILE" ]]; then
    echo "M0 binary file does not exist ($(basename $M0_BINARY_FILE))"
    exit 1
fi

if [[ ! -f "$PROJECT_C_SOURCES_PATH/$M4_TOP_DIR/$M4_BINARY_FILE" ]]; then
    echo "M4 binary file does not exist ($(basename $M4_BINARY_FILE))"
    exit 1
fi


mkdir -p $LOG_PATH  

DEVICE1_FLASH_OPTION=" -id 0 "   
DEVICE2_FLASH_OPTION=" -id 1 "

display_big_banner "Project binaries build"

cd ${COMMON_SCRIPTS_PATH}

display_small_banner "Flashing device 1 with selected binaries"
echo "" > ${LOG_PATH}/flash_device1.log
./flash.sh -id 0 -m0 ${M0_BINARY_FILE} -m4 ${M4_BINARY_FILE} -p ${PROJECT_C_SOURCES_PATH}  -l ${LOG_PATH} 2>&1 | tee -a ${LOG_PATH}/flash_device1.log
ret=${PIPESTATUS[0]}
if [[ ! $ret -eq 0 ]]; then 
    exit $ret
fi

display_small_banner "Flashing device 2 with selected binaries"
echo "" > ${LOG_PATH}/flash_device2.log
./flash.sh -id 1 -m0 ${M0_BINARY_FILE} -m4 ${M4_BINARY_FILE} -p ${PROJECT_C_SOURCES_PATH} -l ${LOG_PATH} 2>&1 | tee -a ${LOG_PATH}/flash_device2.log; 
ret=${PIPESTATUS[0]}
if [[ ! $ret -eq 0 ]]; then 
    exit $ret
fi
cd - 

display_end_banner "Devices flashed..."
