#!/bin/bash
GIT_SCRIPT_VERSION=v0.71

#################################################
##########    DEFAULT CONFIGURATION    ##########
#################################################
set_user_cfg() {
    #"clone" to clone, "fetch" to fetch, "clean" to clean, anything else to do nothing.
    M0_GIT_DO="do_nothing"
    M4_GIT_DO="do_nothing"
    SHALLOW_CLONE="no"
    #eval PROJECT_C_SOURCE_PATH=$PROJECT_C_SOURCE_PATH
    eval SSH_USERNAME=$(whoami)
}

print_cfg() {
    echo "-------------------------------------"
    echo "-------     Config is :    ----------"
    echo "-------------------------------------"
    echo "---- This script version : $GIT_SCRIPT_VERSION"
    echo "---- User is : $SSH_USERNAME"
    echo "---- Workspace path : $(readlink -m $WORKSPACE_ROOT_PATH)"       #jenkins workspace path where LDD scripts are
    echo "---- C source path : $(readlink -m $PROJECT_C_SOURCE_PATH)"      #output path to put project files
    echo "---- M0 job : $M0_GIT_DO"
    echo "---- M4 job : $M4_GIT_DO"
    echo "---- manifest file  : $(readlink -m $GIT_MANIFEST)"
    echo "---- manifest last update  : $(date -r $GIT_MANIFEST)"
    echo "-------------------------------------"
}

init_variables() {
    declare -a MODULE_LIST
    MODULE_NUMBER=0
    
    unset M0_GIT_DO
    unset M4_GIT_DO
    unset SSH_USERNAME
}

#################################################
##########         FUNCTIONS          ###########
#################################################
get_configured_remote_url() { # module_name
    local module_name=$1
    git remote -v | grep "r_${module_name}"
}

print_wait_for_DL() {
    echo "please wait, downloading files..."
}

fetch_this_module() { # module_name, module_version, module_git_url, module_output_path, sha_1
    local module_name=$1
    local module_version=$2
    eval local module_git_url=$3
    local module_output_path=$(realpath  $4)
    local sha_1=$5

    cd $module_output_path
    
    if [[ ! -z """$(echo "$(get_configured_remote_url $module_name)" | grep "$module_git_url" )""" ]]; then
        echo "url up to date"
    else
        echo "(get_configured_remote_url module_name): $(get_configured_remote_url $module_name)"
        echo "module_git_url : $module_git_url"
        
        if [[ -z "$(get_configured_remote_url $module_name)" ]]; then
            git remote add r_${module_name} $module_git_url
        else
            git remote set-url r_${module_name} $module_git_url
        fi
        echo "url was not up to date, now updated"
    fi

    local mode="error"
    if [[ $(git ls-remote r_${module_name} | grep "heads/$module_version") ]]; then
        mode="branch"
    elif [[ $(git ls-remote r_${module_name} | grep "tags/$module_version") ]]; then
        mode="tag"
    else
        print_error "Tag or branch not found"
        exit 1
    fi
    
    if [[ $mode = "branch" ]]; then
        echo "branch/tag : branch"
        if [[ "${SHALLOW_CLONE}" = "yes" ]]; then
            echo "/!\ warning : shallow cloning"
            print_wait_for_DL
            git fetch r_${module_name} $module_version --depth 1
        else
            if [ -f $(git rev-parse --git-dir)/shallow ]; then
            #if [[ ! -z "$(git rev-parse --is-shallow-repository)" ]]; then --> for git version > 2.5
                echo "unshallowing"
                print_wait_for_DL
                git fetch r_${module_name} $module_version --unshallow
            else
                echo "not shallow"
                print_wait_for_DL
                git fetch r_${module_name} $module_version
            fi
        fi
        ret=$?
        if [[ ! $ret -eq 0 ]]; then 
            print_error "Error while fecthing sources"
            exit $ret
        fi        
    else
        echo "branch/tag : tag"
        print_wait_for_DL
        git fetch r_${module_name} tag $module_version --no-tags
        ret=$? 
        if [[ ! $ret -eq 0 ]]; then 
            print_error "Error while fecthing sources"
            exit $ret
        fi
    fi
    if [[ "40" = "$(echo -n $sha_1 | wc -m)" ]]; then
        echo "checkout to specified sha-1"
        git reset --hard $sha_1
        ret=$? 
        if [[ ! $ret -eq 0 ]]; then 
            print_error "SHA-1 not found"
            exit 1
        fi
    else
        echo "sha-1 field is: $sha_1, len is $(echo -n $sha_1 | wc -m)" #TODO to be removed
        if [[ $mode = "branch" ]]; then
            echo "checkout to end of specified branch"        
            git reset --hard r_${module_name}/$module_version
        else
            echo "checkout to specified tag"    
            git reset --hard $module_version
        fi
    fi
    ls -lisa
    
    cd -
}

clone_this_module() { # module_version, module_git_url, module_output_path, sha_1
    local module_name=$1
    local module_version=$2
    eval local module_git_url=$3
    local module_output_path=$(realpath  $4)
    local sha_1=$5
    
    if [ ! -d "$module_output_path" ]; then
        mkdir -p $module_output_path
    fi
    
    cd $module_output_path        
    git init 
    if [[  $(get_configured_remote_url) ]]; then
        echo "url already exists, skipping."
    else
        git remote add r_${module_name} $module_git_url
    fi
    cd -
    fetch_this_module $module_name $module_version  $module_git_url $module_output_path $sha_1
}

git_work_this_module() { #core_name, module_name, module_version, module_git_url, module_output_path, sha_1
    local core_name=$1
    local module_name=$2
    local module_version=$3
    eval local module_git_url=$4
    local module_output_path=$(realpath  $5)
    local sha_1=$6
    local git_work="do_nothing"
    
    
    case "$core_name" in
      "M0" | "m0")
          git_work=$M0_GIT_DO
          ;;
          
      "M4" | "m4")
          git_work=$M4_GIT_DO
          ;;
          
      *)
          print_error "Unknown target or target undefined, see config file"
          exit 1 
          ;;
    esac
        
    echo "core_name : $core_name"    
    echo "module_name : $module_name"
    echo "module_version : $module_version"
    echo "module_git_url : $module_git_url"
    echo "module_output_path : $(readlink -m $module_output_path)"  
    echo "sha_1 : $sha_1"
    echo "git_work : $git_work"    
    
    case $git_work in
        "update")
            if [[ ! -d "$module_output_path" ]] || [[ ! -d "$module_output_path/.git" ]]; then
                if [[ ! -d "$module_output_path" ]] ; then
                echo "folder $(readlink -m $module_output_path) doesn't exist, creating..."
                fi
                if [[ !  -d "$module_output_path/.git" ]] ; then
                echo "folder $(readlink -m $module_output_path/.git) doesn't exist, creating..."
                fi
                clone_this_module $module_name $module_version $module_git_url $module_output_path $sha_1
            else
                fetch_this_module  $module_name $module_version $module_git_url $module_output_path $sha_1
            fi
            ;;
        "status")
            echo ">> to be implemented"
            #TODO: to implement, give git status for each module
            ;;
        "clean")
            echo ">> cleaning this module folder"
            echo ">> to be implemented"
            #rm -rf $module_output_path --> this will delete another module that uses the folder, use smoething like "git clean -dfx"
            ;;
        *)
            #doing nothing for M0
            ;;
    esac
}

git_work() {
    echo 
    echo 
    git config --system core.longpaths true
    if [[ $? != 0 ]]; then
        read -p "--> WARNING: You should run this script in admin mode (right clic on bash and choose 'run as administrator') to avoid path issues. Please press 'Enter' to continue... "
        exit 1
    fi
    echo 
    for (( module_id = 0 ; module_id < $MODULE_NUMBER ; module_id++ ))
    do
        IFS=";" read -r -a module_data <<< "${MODULE_LIST[$module_id]}"
        git_work_this_module ${module_data[@]}
        echo "module ${module_data[1]} for ${module_data[0]} up-to-date"
        echo 
        echo 
    done
}

display_help() {
    echo
    echo "*****************************************************************************************************************************************"
    echo "*        USAGE: $0 [option...]                                                                                                          *"             
    echo "* Mandatory:                                                                                                                            *"
    echo "*     --module_version_file | -v <module_version_file>            Module version file, mandatory.                                       *"                    
    echo "* Options:                                                                                                                              *"
    echo "*     --output_custom_path | -o  <output_custom_path>             Output/workspace path for git repositories.                           *"
    echo "*                                                                 $PROJECT_C_SOURCE_PATH by default  "
    echo "*     --ssh_username | -u  <ssh_username>                         SSH user name for git access. User's shell loggin by default          *"
    echo "*     --shallow_clone | -s  <ssh_username>                        enable shallow clone when reading project only (like with jenkins)    *"
    echo "*     -m0 <job>                                                   to update, clean or get git status for M0 sources                     *"
    echo "*     -m4 <job>                                                   to update, clean or get git status for M4 sources                     *"
    echo "*                                                                 job can be 'update', 'clean' or 'status'                              *"
    echo "*****************************************************************************************************************************************"
    echo
}

check_parameter() {

    init_variables
    set_user_cfg
    
    while :
    do
        case "$1" in
          -m0)
              M0_GIT_DO=$2
              shift 2
              ;;
              
          -m4)
              M4_GIT_DO=$2
              shift 2
              ;;               
            
          --module_version_file|-v)
              GIT_MANIFEST=$2
              shift 2
              ;;    
              
          --output_custom_path|-o)
              PROJECT_C_SOURCE_PATH="$2"
              shift 2
              ;;    
              
          --ssh_username|-u)
              SSH_USERNAME="$2"
              shift 2
              ;;    
              
          --shallow_clone|-s)
              SHALLOW_CLONE="yes"
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
    

    
    source $GIT_MANIFEST
    
}

add_module() { #core_name, module_name,module_version, module_git_url,module_output_path,$sha_1    
    local core_name=$1
    local module_name=$2
    local module_version=$3
    eval local module_git_url=$4
    local module_output_path=$(realpath  $5)
    local sha_1=$6

    MODULE_LIST[$MODULE_NUMBER]="$core_name;$module_name;$module_version;$module_git_url;$module_output_path;$sha_1"
    MODULE_NUMBER=$(($MODULE_NUMBER+1))
}

parse_update_options() {

    if [[ -z "$GIT_MANIFEST" ]]; then
        print_error "Git manifest is not given as an argument."
        display_help
        exit 1
    fi
    
    MAX_CHAR_FOR_IAR_DEEPEST_PATH=75
    local path_string=$(realpath  $(readlink -m $PROJECT_C_SOURCE_PATH/$M4_TOP_DIR))
    eval local path_length="$(echo -n $path_string | wc -m)"
    if [[ "$path_length" > "$MAX_CHAR_FOR_IAR_DEEPEST_PATH" ]]; then
        print_error "Please move your test env folder closer to the root, project path ($path_string) too long: Current path length(=$path_length) > Max path length(=$MAX_CHAR_FOR_IAR_DEEPEST_PATH)" 
        exit 1
    fi
    
    if [[ "$(basename $SHOULD_NOT_BE_LLD_VALIDATION_FOLDER)" == "LLD_validation" ]]; then
        print_error "DO NOT use this script in this folder, create a workspace folder, and launch the script that inits the folder (check in the README.md)" 
        exit 1
    fi
}


#################################################
##########            MAIN            ###########
#################################################
SHOULD_NOT_BE_LLD_VALIDATION_FOLDER=$(realpath  $(pwd)/../..)

#we are in ${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/02_Scripts/
WORKSPACE_ROOT_PATH=$(realpath  $(pwd)/../../..)
COMMON_PATHS=$(realpath  ${WORKSPACE_ROOT_PATH}/00_Tools_and_config/00_Common/02_Scripts/Common.paths)

source $COMMON_PATHS
source $COMMON_LIB
source $COMMON_CFG

mkdir -p $M0_TOP_DIR
mkdir -p $M4_TOP_DIR

check_parameter $@
echo

print_cfg
echo

parse_update_options
echo

git_work
echo

exit 0
