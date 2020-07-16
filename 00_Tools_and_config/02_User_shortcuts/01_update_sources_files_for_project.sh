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

eval SSH_USERNAME="$(whoami)"
mkdir -p $LOG_PATH  


display_big_banner "Project update"
display_small_banner "Updating project sources so up-to-date binaries can be built"

cd ${COMMON_SCRIPTS_PATH}
./project_update.sh -m0 update -m4 update -u ${SSH_USERNAME} -o ${PROJECT_C_SOURCES_PATH} -v ${MANIFEST_CFG} 2>&1 | tee -a ${LOG_PATH}/project_update.log
ret=${PIPESTATUS[0]}
if [[ ! $ret -eq 0 ]]; then
    echo "Project update aborted...Unexcepted error : $ret"
    exit $ret
fi

cd - 

display_end_banner "Project updated..."


