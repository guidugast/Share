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
    #full manual build
    BUILD_ID="""$(date +"%Y%m%d%H%M")_full"""
else
    #jenkins auto build
    BUILD_ID=$2
fi

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
