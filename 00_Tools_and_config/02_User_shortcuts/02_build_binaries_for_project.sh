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


if [[ ! -f "$PROJECT_C_SOURCES_PATH/$M0_TOP_DIR/$M0_IAR_PROJECT" ]]; then
    echo "M0 project file does not exist ($(basename $M0_IAR_PROJECT))"
    exit 1
fi

if [[ ! -f "$PROJECT_C_SOURCES_PATH/$M4_TOP_DIR/$M4_IAR_PROJECT" ]]; then
    echo "M4 project file does not exist ($(basename $M4_IAR_PROJECT))"
    exit 1
fi


mkdir -p $LOG_PATH  


display_big_banner "Project binaries build"

cd ${COMMON_SCRIPTS_PATH}

display_small_banner "Compiling and linking M0 sources"
./build.sh -m0 ${M0_IAR_PROJECT} -p ${PROJECT_C_SOURCES_PATH} -l ${LOG_PATH} -iar -c  2>&1 | tee -a ${LOG_PATH}/m0_build.log
ret=${PIPESTATUS[0]}
if [[ ! $ret -eq 0 ]]; then
    echo "Project build aborted...Unexcepted error : $ret"
    exit $ret
fi

display_small_banner "Compiling and linking M4 sources"
./build.sh -m4 ${M4_IAR_PROJECT} -p ${PROJECT_C_SOURCES_PATH} -l ${LOG_PATH} -iar -c  2>&1 | tee -a ${LOG_PATH}/m4_build.log
ret=${PIPESTATUS[0]}
if [[ ! $ret -eq 0 ]]; then
    echo "Project build aborted...Unexcepted error : $ret"
    exit $ret
fi

cd - 

display_end_banner "Binaries built..."