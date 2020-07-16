#!/bin/bash -u

#we are in ${WORKSPACE_ROOT_PATH}/00_Tools_and_config/02_User_shortcuts/
WORKSPACE_ROOT_PATH="$(pwd)/../.."	
eval COMMON_PATHS="${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/02_Scripts/Common.paths"

source $COMMON_PATHS
source $COMMON_LIB
source $COMMON_CFG



## RLV
if [[ "$1" = "DUG" ]]; then
    RLV_M4_BINARY_FILE="C:/_RF_LLD_VALIDATION/01_C_Sources\WB55BLE - Copy/m4/Firmware/__INTERNAL__Projects/P-NUCLEO-WB55.Nucleo/Applications/RLV\EWARM\RLV_m4_gateway\Exe\stm32wb55xx_RLV_m4_gateway.hex"
elif [[ "$1" = "CCO" ]]; then
    RLV_M4_BINARY_FILE="C:/_VALID_CLI_BLE/stm32wb_M4_Firmware/Firmware/__INTERNAL__Projects/P-NUCLEO-WB55.Nucleo/Applications/RF_LLD_tests/RF_LLD_tests/EWARM/LLD_tests_Cli_Cmd/Exe/stm32wb55xx_lld_tests_Cli_Cmd.hex"
else
    echo "no arg passed, error"
    exit 1
fi
RLV_M0_BINARY_FILE="C:/_RF_LLD_VALIDATION/01_C_Sources\WB55BLE - Copy/m0/Projects/Multi/Application/EWARM/stm32wbxx_rf_lld_validation_host/WB55_BLE/Exe/stm32wb55xx_ble_rf_lld_validation.hex"

## M4 cli gateway
VCB_M4_BINARY_FILE="C:/_CLEAN_PROJECT/20200203_JLC/stm32wb_M4_Firmware/Firmware/__INTERNAL__Projects/P-NUCLEO-WB55.Nucleo/Applications/RF_LLD_tests/RF_LLD_tests/EWARM/LLD_tests_Cli_Cmd/Exe/stm32wb55xx_lld_tests_Cli_Cmd.hex"

## M0 Valid cli ble 
VCB_M0_BINARY_FILE="C:/_VALID_CLI_BLE/stm32wb_M0_Firmware/Projects/Multi/Application/EWARM/stm32wbxx_phy_valid_host/BLE_PHY/Exe/stm32wb55xx_ble_phy_valid_fw.hex"

## M0 lld test ble + 154
LTB_M0_BINARY_FILE="C:/_M0_test_project_iso_LLD_valid/01_Projects/WB55_BLE/m0/Projects/Multi/Application/EWARM/stm32wbxx_lld_tests_host/WB55_BLE_lld_tests/Exe/stm32wb55xx_ble_lld_tests_fw.hex"
LT8_M0_BINARY_FILE="C:/_M0_test_project_iso_LLD_valid/01_Projects/WB55_BLE/m0/Projects/Multi/Application/EWARM/stm32wbxx_lld_tests_host/WB55_154_lld_tests/Exe/stm32wb55xx_802_15_4_lld_tests_fw.hex"

eval PROJECT_FLASH_PATH="C:/_LLD_scripts/__INTERNAL__Validation_Projects/LLD_validation/00_Common/04_flashing"


D0_M4_BINARY_FILE="$RLV_M4_BINARY_FILE"
D0_M0_BINARY_FILE="$RLV_M0_BINARY_FILE"

D1_M0_BINARY_FILE="$RLV_M0_BINARY_FILE"
D1_M4_BINARY_FILE="$RLV_M4_BINARY_FILE"


echo ""
echo ""
echo "-------------------------------------------"
echo "--              Flash boards             --"
echo "-------------------------------------------"
echo ""
echo "D0_M0_BINARY_FILE : $D0_M0_BINARY_FILE"
echo "D0_M4_BINARY_FILE : $D0_M4_BINARY_FILE"
echo "D1_M0_BINARY_FILE : $D1_M0_BINARY_FILE"
echo "D1_M4_BINARY_FILE : $D1_M4_BINARY_FILE"
echo ""
echo "Flashing device 1"
flash_this 0 ${D0_M0_BINARY_FILE} M0
flash_this 0 ${D0_M4_BINARY_FILE} M4

echo ""
echo "Flashing device 2"
flash_this 1 ${D1_M0_BINARY_FILE} M0
flash_this 1 ${D1_M4_BINARY_FILE} M4

echo ""
echo "Binaries flashed..."
echo ""
