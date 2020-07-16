#!/bin/bash -u

PROJECT_CONFIG_PATH="$(pwd)/../00_config"    
WORKSPACE_ROOT_PATH="$(pwd)/../../../.."   

eval GLOBAL_CFG="C:/_LLD_scripts/__INTERNAL__Validation_Projects/LLD_validation/00_Common/00_config/Global.cfg"

source $GLOBAL_CFG

echo ""
echo ""
echo "-------------------------------------------"
echo "--         Fetching Applications         --"
echo "-------------------------------------------"
echo ""
echo ""

echo "fetching M4 Application"
cd "${WORKSPACE_ROOT_PATH}/01_Projects/WB55_BLE/m4/Firmware"

if [ -f $(git rev-parse --git-dir)/shallow ]; then
    echo "to work in, it must not be shallow. Unshallowing."
    git config remote.r_M4_Application.fetch "+refs/heads/*:refs/remotes/r_M4_Application/*"
    git fetch r_M4_Application --unshallow
else
    git fetch r_M4_Application 
fi
git reset --soft iso/LLD_validation 
cd -

echo "fetching M0 Application"
cd "${WORKSPACE_ROOT_PATH}/01_Projects/WB55_BLE/m0/Projects"
if [ -f $(git rev-parse --git-dir)/shallow ]; then
    echo "to work in, it must not be shallow. Unshallowing."
    git config remote.r_M0_Application.fetch "+refs/heads/*:refs/remotes/r_M0_Application/*"
    git fetch r_M0_Application --unshallow
else
    git fetch r_M0_Application 
fi
git reset --soft iso/LLD_validation
cd -


echo ""
echo "Binaries flashed..."
echo ""

