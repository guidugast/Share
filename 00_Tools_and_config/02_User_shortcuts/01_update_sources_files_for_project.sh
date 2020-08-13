#!/bin/sh


#PROJECT_NAME = $1
if [[ -z "$1" ]]; then
    echo "No project name given as first script argument."
    exit 1
else
    PROJECT_NAME=$1
fi

#we are in ${WORKSPACE_ROOT_PATH}/00_Tools_and_config/02_User_shortcuts/
WORKSPACE_ROOT_PATH=$(pwd)/../..
PROJECT_PATHS=${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/02_Scripts/Project.paths

source $PROJECT_PATHS 
source $COMMON_CFG
source $COMMON_LIB
source $PROJECT_CFG

display_big_banner "Project update"

#BUILD_ID = $2
if [[ -z "$2" ]]; then
    #standalone build
    BUILD_ID="""$(date +"%Y%m%d%H%M")_standalone"""
    display_test_env_version
else
    #full manual or full auto builds
    BUILD_ID=$2
fi

JENKINS_OPTIONS="N/A"
SSH_USER="N/A"
#FROM_JENKINS = $3
if [[ -z "$3" ]]; then
    #standalone or full auto build
    JENKINS_OPTIONS=""
else
    #full auto build fom jenkins
    SSH_USER=$3
    JENKINS_OPTIONS="--ssh_username ${SSH_USER} --shallow_clone"
fi

mkdir -p $LOG_PATH  


cd ${COMMON_SCRIPTS_PATH}
./project_update.sh -m0 update -m4 update ${JENKINS_OPTIONS} -o ${PROJECT_C_SOURCES_PATH} -v ${MANIFEST_CFG} 2>&1 | tee -a ${LOG_PATH}/project_update.log
ret=${PIPESTATUS[0]}
if [[ ! $ret -eq 0 ]]; then
    echo "Project update aborted...Unexcepted error : $ret"
    exit $ret
fi

cd - 

display_end_banner "Project updated..."


