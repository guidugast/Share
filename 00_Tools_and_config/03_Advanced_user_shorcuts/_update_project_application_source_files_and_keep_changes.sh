#!/bin/sh
PROJECT_CONFIG_PATH="$(pwd)/../00_config"	
WORKSPACE_ROOT_PATH="$(pwd)/../../../.."	

eval GLOBAL_CFG="${WORKSPACE_ROOT_PATH}/00_scripts_and_tools/00_Common/00_config/Global.cfg"
eval PROJECT_CFG="${PROJECT_CONFIG_PATH}/Project.cfg"
eval MANIFEST_CFG="${PROJECT_CONFIG_PATH}/GitManifest.cfg"

source $GLOBAL_CFG
source $PROJECT_CFG

eval PROJECT_WORKSPACE="${WORKSPACE_ROOT_PATH}/01_Projects/${PROJECT_NAME}"
eval SSH_USERNAME="$(whoami)"
eval PROJECT_UPDATE_PATH="${WORKSPACE_ROOT_PATH}/00_scripts_and_tools/00_Common/02_project_update"


if [[ -z "$BUILD_ID" ]]; then
    BUILD_ID=$(date +"%Y%m%d%H%M")
fi

eval LOG_PATH="$(pwd)/../02_log/${BUILD_ID}"  
mkdir -p $LOG_PATH  

echo ""
echo ""
echo "-------------------------------------------"
echo "--              Update project           --"
echo "-------------------------------------------"
echo ""
cd ${PROJECT_UPDATE_PATH}
./project_update.sh -m0 update -m4 update -u ${SSH_USERNAME} -o ${PROJECT_WORKSPACE} -v ${MANIFEST_CFG} 2>&1 | tee -a ${LOG_PATH}/project_update.log
ret=${PIPESTATUS[0]}
if [[ ! $ret -eq 0 ]]; then
    echo "Project update aborted...Unexcepted error : $ret"
    exit $ret
fi

cd - 

echo ""
echo "Project updated..."
echo ""

