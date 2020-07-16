#!/bin/bash
BUILD_SCRIPT_VERSION=v0.55

#################################################
##########    DEFAULT CONFIGURATION    ##########
#################################################
print_cfg() {
    echo "-------------------------------------"
    echo "-------     Config is :    ----------"
    echo "-------------------------------------"
    echo "---- IAR toochain path : $(readlink -m """$IAR_PATH""")"
    echo "---- Workspace path : $(readlink -m """$WORKSPACE_ROOT_PATH""")"           # jenkins workspace path where LDD scripts are
    echo "---- Project path : $(readlink -m """$PROJECT_C_SOURCES_PATH""")"     # project files where sources are
    echo "---- Log path : $(readlink -m """$LOG_PATH""")"                       # output path to put log files
    echo "---- Target : STM32WB$STM32WB_VERSION"
    echo "---- Build script version : $BUILD_SCRIPT_VERSION"
    echo "---- Build script last update  : $(date -r ${COMMON_SCRIPTS_PATH}/build.sh)"
    echo "-------------------------------------"
}

init_variables() {
    
    CLEAN=0

    IDE_IAR=0
    
    total_error_count=0
    exit_status_build_error=1
    exit_status_build_warning=2

    current_ide="NA"
    current_board="NA"
    current_status="NA"
    current_mx_support="NA"
}

#################################################
##########         FUNCTIONS          ###########
#################################################
display_help() {  # TODO, update & clean this
    echo
    echo "*****************************************************************************"
    echo "*****************************************************************************"
    echo "     USAGE: $0 [option...] "                     
    echo "Options: "
    echo "    -m0 <iar_project_file>                              build M0 part "
    echo "    -m4 <iar_project_file>                              build M4 applications "
    echo "    -iar                                                build with IAR toolchain "
    echo "    -clean                                              clean before build "
    echo "    -p | --project_path <project_path>                  path for workspace where folders M0 firmware and M4 Firmware are, $PROJECT_C_SOURCES_PATH by default"
    echo "    -l | --log_path <log_path>                          path where to output compilation logs, $LOG_PATH by default"
    echo "*****************************************************************************"
    echo "*****************************************************************************"
    echo
    # echo some stuff here for the -a or --add-options 
    exit 1
}

reset_compil_var() {
    compil_status="OK"
    error_status=0
    warning_status=0
}

test_exit() {    
    exit_status=0
    echo "***************************************************************************"
    if [[ "$compil_status" = "KO" ]]; then
        if [[ "$error_status" = "1" ]]; then
            echo "*** COMPILATION KO (Error(s) reported)"    
            exit_status=$exit_status_build_error
        elif [[ "$warning_status" = "1" ]]; then
            echo "*** COMPILATION KO (Warning(s) reported)"
            exit_status=$exit_status_build_warning
        fi
    else
        echo "*** COMPILATION OK (0 Error and 0 Warning)"
    fi
    echo "***************************************************************************"

    if [[ "$exit_status" = "0" ]]; then
        current_status="OK"
    elif [[ "$exit_status" = $exit_status_build_error ]]; then
        current_status="ERROR(S)"
        exit 1
    elif [[ "$exit_status" = $exit_status_build_warning ]]; then
        current_status="WARNING(S)"
        exit 1
    fi
}

parse_compil_log() {  #compilation_log
    local compilation_log=$1
    echo "--> Starting parsing log."
    while  read -r line ; do
        if [[ -n $(echo "$line" | egrep '[Ee]rror\[') ]]; then
            compil_status="KO"
            error_status=1
            echo "error detected on following line : "
            echo $line
        fi
        if [[ -n $(echo "$line" | egrep '[Ww]arning\[') ]]; then
            compil_status="KO"
            warning_status=1
            echo "warning detected on following line : "
            echo $line
        fi
    done < $compilation_log        
    echo "--> Parsing log finished"
    
    test_exit
}

build_iar_project() { #target_id, project_dir, project_name
    local target_id=$1
    local project_dir=$2
    local project_name=$3
    
    cd $project_dir

    echo "--> Current application folder : $(readlink -m $project_dir)"
    echo "--> Current application : $project_name"
    ewp_file=$project_name
    
    configuration_tag="<configuration>"
    name_tag="<name>"

    #Array containing configurations
    ewp_configuration=()
    index_configuration=0

    #while loop read on standard output with read command
    while  read -r line ; do
        if [[ "$configuration_tag_found" = "1" ]]; then
            if [[ $line = *"$name_tag"* ]]; then
                #At this point line should be something like this: <name>CONFIGURATION_NAME</name>, we have to extract CONFIGURATION_NAME
                line=${line#*$name_tag}     #removes stuff upto <name> from beginning
                line=${line%<*}             #removes stuff from < all the way to end
                #CONFIGURATION_NAME 
                #echo "$line"
                ewp_configuration[$index_configuration]=$line
                #echo ${ewp_configuration[$i]}
                ((index_configuration++))
            fi
            configuration_tag_found=0
        fi
        if [[ $line = *"$configuration_tag"* ]]; then
            configuration_tag_found=1
        fi
    done < "${ewp_file}" 

    echo "${#ewp_configuration[@]} configuration(s) found."
    if [[ "${#ewp_configuration[@]}" = 0 ]]; then
        exit 2
    fi

    for config in ${ewp_configuration[@]}
    do
        reset_compil_var
        
        compilation_log_file=$(realpath  ${LOG_PATH}/build_TARGET_${target_id}.log)
        echo "" > "$compilation_log_file"
  
        echo "--> Building $project_name with configuration $config"
        if [[ "$CLEAN" = "1" ]]; then
            echo "--> cleaning before build"
                rm -rf "$project_dir/$config/*"
            echo "--> log file cleaned"
            "$IAR_PATH" ${ewp_file} -clean $config $LOG_ALL 2>&1 >>  "$compilation_log_file"
        fi
        echo "--> compiling ..."
        "$IAR_PATH" ${ewp_file} -make $config $LOG_ALL 2>&1 >>  "$compilation_log_file" 
        echo "--> Compilation log file can be found here: $(readlink -m $compilation_log_file)"
        echo "--> end of build"

        parse_compil_log $compilation_log_file
    done     
    
        
    cd -
}

build() { 
    if [[ -n "$M0_IAR_PROJECT" ]]; then
        project_dir=$(realpath  ${PROJECT_C_SOURCES_PATH}/${M0_TOP_DIR}/$(dirname $M0_IAR_PROJECT))
        project_name=$(basename $M0_IAR_PROJECT)
    elif [[ -n "$M4_IAR_PROJECT" ]];  then
        project_dir=$(realpath ${PROJECT_C_SOURCES_PATH}/${M4_TOP_DIR}/$(dirname $M4_IAR_PROJECT))
        project_name=$(basename $M4_IAR_PROJECT)
    else
        print_error "No project specified, need at leats M0 or M4 "
        exit 1        
    fi
    
    echo
    echo
    echo "project_dir : $(readlink -m $project_dir)" 
    if [[ ! -d "$project_dir" ]]; then
        print_error "Following path does not exist: project_dir "
        exit 1
    fi    
        
    echo "project_dir/project_name : $(readlink -m $project_dir/$project_name)"
    if [[ ! -f "$project_dir/$project_name" ]]; then
        print_error "Following file does not exist: project_dir/project_name "
        exit 1
    fi   
    

    build_iar_project WB55 $project_dir $project_name
    #TODO: add WB55 to argument

}

check_parameter() {    
    init_variables

    while :
    do
        case "$1" in
            -h | --help)
              display_help
              exit 0
              ;;
              
            -m0)
               M0_IAR_PROJECT=$2
               shift 2
               ;;

            -m4)
               M4_IAR_PROJECT=$2
               shift 2
               ;;
               
            -iar)
               IDE_IAR=1
               shift 1
               ;;
               
            -p | --project_path)
               PROJECT_C_SOURCES_PATH=$2
               shift 2
               ;;   
               
            -l | --log_path)
               LOG_PATH=$(realpath  $2)
               shift 2
               ;;
               
            -c | --clean)
               CLEAN=1
               shift 1
               ;;       
               
            --) # End of all options
              shift
              break
              ;;
            -*)
              print_error "Unknown option: $1" >&2
              display_help
              exit 1 
              ;;
            *)  # No more options
              break
              ;;
        esac
    done
}

parse_build_option() {

    if [[ -z "$(dirname $M0_IAR_PROJECT)" ]] && [[ -z "$(dirname $M4_IAR_PROJECT)" ]]; then
        print_error "M0 or M4 project not specified, you need at least one project specified"
        exit 1
    fi
   
    if [[ -z "$PROJECT_C_SOURCES_PATH" ]]; then
        print_error "Project path not specified"
        exit 1
    fi
    
    if [[ "$IDE_IAR" != "1" ]]; then
        print_error "Compiler not defined"
        exit 1
    fi
}

#################################################
##########            MAIN            ###########
#################################################

#we are in ${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/02_Scripts/
WORKSPACE_ROOT_PATH=$(realpath  $(pwd)/../../..)
COMMON_PATHS=$(realpath  ${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/02_Scripts/Common.paths)

source $COMMON_PATHS
source $COMMON_LIB
source $COMMON_CFG

check_parameter  $@

print_cfg
echo

parse_build_option
echo
build

echo 
exit 0