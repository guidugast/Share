#!/bin/bash -u

eval GLOBAL_CFG="C:/_LLD_scripts/__INTERNAL__Validation_Projects/LLD_validation/00_Common/00_Config/Common.cfg"
source $GLOBAL_CFG

echo ""
echo "-------------------------------------------"
echo "--              Reset boards             --"
echo "-------------------------------------------"
echo ""
echo ""
echo "Reseting device 1"
"${ST_LINK_UTILITY}" -c ID=0 -Rst
parse_st_link_error_code

echo "Reseting device 2"
"${ST_LINK_UTILITY}" -c ID=1 -Rst
parse_st_link_error_code


echo ""
echo "Boards reset..."
echo ""
