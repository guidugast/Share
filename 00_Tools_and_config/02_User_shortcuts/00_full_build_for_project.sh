#!/bin/sh

#PROJECT_NAME = $1
if [[ -z "$1" ]]; then
    echo "No project name given as first script argument."
    exit 1
else
    PROJECT_NAME=$1
fi


#we are in ${WORKSPACE_ROOT_PATH}/00_Tools_and_config/02_User_shortcuts/
WORKSPACE_ROOT_PATH="$(pwd)/../.."	
eval PROJECT_PATHS="${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/02_Scripts/Project.paths"

source $PROJECT_PATHS 
source $COMMON_CFG
source $COMMON_LIB
source $PROJECT_CFG


#BUILD_ID = $2

if [[ -z "$2" ]]; then
    #full manual build
    BUILD_ID="""$(date +"%Y%m%d%H%M")_full"""
else
    #jenkins auto build
    BUILD_ID=$2
fi

display_test_env_version

./01_update_sources_files_for_project.sh $PROJECT_NAME $BUILD_ID
if [[ ! "$?" = "0" ]]; then
    exit $?
fi
./02_build_binaries_for_project.sh $PROJECT_NAME $BUILD_ID
if [[ ! "$?" = "0" ]]; then
    exit $?
fi
./03_flash_board_with_built_binaries_for_project.sh $PROJECT_NAME $BUILD_ID
if [[ ! "$?" = "0" ]]; then
    exit $?
fi
./04_run_full_campaign_for_project.sh $PROJECT_NAME $BUILD_ID
if [[ ! "$?" = "0" ]]; then
    exit $?
fi

exit 0
