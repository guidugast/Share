#!/bin/bash -u

WORKSPACE_ROOT_PATH="$(pwd)/../../../.."   
eval GLOBAL_CFG="${WORKSPACE_ROOT_PATH}/00_scripts_and_tools/00_Common/00_config/Global.cfg"

source $GLOBAL_CFG

echo ""
echo "-------------------------------------------"
echo "--              Reset boards             --"
echo "-------------------------------------------"
echo ""
echo ""
echo "Reseting device 1"
"$ST_LINK_UTILITY" -c ID=0 -Rst
parse_st_link_error_code

echo "Reseting device 2"
"$ST_LINK_UTILITY" -c ID=1 -Rst
parse_st_link_error_code


echo ""
echo "Boards reset..."
echo ""
