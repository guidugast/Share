echo "" 
echo "" 
echo "#######################################################################################"
echo "#######################################################################################"
echo "######################         Python Configuration      ##############################"
echo "#######################################################################################"
echo "#######################################################################################"
echo ""
echo " --> This script version : v0.3"
echo ""

script_path="$0"
script_name="$(basename "$script_path")"
folder_name="${PWD##*/}"

if [[ ! -f "$(pwd)/${script_name}" ]]; then
    print_error "you should run the script from its folder: cd <workspace>/00_Tools_and_config/03_Advanced_user_shorcuts; ./_configure_python.sh"
    exit 1
fi

eval WORKSPACE_ROOT_PATH="$(pwd)/../.."

echo " --> Root folder used for test env : $WORKSPACE_ROOT_PATH"
echo ""

eval COMMON_CFG="${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/00_Config/Common.cfg"
eval COMMON_LIB="${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/02_Scripts/Common.lib"
source $COMMON_CFG
source $COMMON_LIB

if [[ -z $($PYTHON38 --version | grep "Python 3.8") ]]; then
    print_error "you should have python at version 3.8.0 <= v < 3.9.*"
    exit 1
fi

export http_proxy=165.225.76.32
export https_proxy=165.225.76.32
export HTTP_PROXY=165.225.76.32
export HTTPS_PROXY=165.225.76.32
export proxy_port=8080

if [[ ! -z $($PYTHON38 -m pip install --upgrade --force-reinstall --trusted-host=pypi.org --no-warn-script-location --trusted-host=files.pythonhosted.org pip | grep "ERROR") ]];then 
    print_error "error while connecting to proxy"
    exit 1
elif [[ ! -z $($PYTHON38 -m pip install --upgrade --force-reinstall --trusted-host=pypi.org --no-warn-script-location --trusted-host=files.pythonhosted.org pyserial | grep "ERROR") ]];then
    print_error "error while connecting to proxy"
    exit 1
elif [[ ! -z $($PYTHON38 -m pip install --upgrade --force-reinstall --trusted-host=pypi.org --no-warn-script-location --trusted-host=files.pythonhosted.org junit_xml | grep "ERROR") ]];then
    print_error "error while connecting to proxy"
    exit 1
else
    echo "--> Python ready!"
fi
