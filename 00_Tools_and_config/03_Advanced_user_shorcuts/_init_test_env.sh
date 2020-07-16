
script_path="$0"
script_name="$(basename "$script_path")"
workspace_path="$(pwd)"

# echo "script_path: $script_path "
# echo "script_name: $script_name "
# echo "workspace_path: $workspace_path "

echo "" 
echo "" 
echo "#######################################################################################"
echo "#######################################################################################"
echo "######################     Test env update/creation      ##############################"
echo "#######################################################################################"
echo "#######################################################################################"
echo ""
echo " --> This script version : v0.8"
echo ""

echo " --> Root folder used for test env : $workspace_path"
echo ""


if [[ ! -f "$(pwd)/stm32wb_ate/03_Advanced_user_shorcuts/${script_name}" && ! -f "${workspace_path}/stm32wb_ate" ]]; then
    echo "you should run the script from its grand-parent folder: cd <workspace>; ./stm32wb_ate/03_Advanced_user_shorcuts/_init_test_env.sh"
    exit 1
fi
mkdir -p 00_Tools_and_config
cp -ra ${PWD}/stm32wb_ate/* ${PWD}/00_Tools_and_config/
cp -ra ${PWD}/stm32wb_ate/. ${PWD}/00_Tools_and_config/
#rm -rf ${PWD}/stm32wb_ate/ 
mkdir -p 01_C_Sources/
cd 00_Tools_and_config/
echo "--> Test environment ready!"
