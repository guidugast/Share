#!/bin/bash
FLASH_SCRIPT_VERSION=v0.23


#################################################
##########    DEFAULT CONFIGURATION    ##########
#################################################
set_user_cfg() {
    DEVICE_ID=0
    
    M0_FLASH=1
    M0_BINARY_FILE=""
    
    M4_FLASH=1
    M4_BINARY_FILE=""
}

print_cfg() {

   echo "-------------------------------------" 
   echo "-------     Config is :    ----------"
   echo "-------------------------------------"
   echo "---- ST-link utility path : $(readlink -m """$ST_LINK_UTILITY""")"   
   echo "---- Project path : $(readlink -m """$PROJECT_C_SOURCES_PATH""")"     # project files where sources are
   echo "---- Workspace path : $(readlink -m """$WORKSPACE_ROOT_PATH""")"      # jenkins workspace path where LDD scripts are
   echo "---- Log path : $(readlink -m """$LOG_PATH""")"                       # output path to put log files
   echo "---- M0 binary : $M0_BINARY_FILE"
   echo "---- M4 binary : $M4_BINARY_FILE"
   echo "---- Device Id: $DEVICE_ID"
   echo "---- Flash script version : $FLASH_SCRIPT_VERSION"
   echo "---- Flash script last update  : $(date -r ${COMMON_SCRIPTS_PATH}/flash.sh)"
   echo "-------------------------------------"
}

############################################################################
##     User Config                                                        ##
############################################################################

init_variables(){   
    ADDRESS_START_FLASH=0x08000000

    OFFSET_M0=0x80000
    ADDRESS_M0=$(($ADDRESS_START_FLASH+$OFFSET_M0))
    #echo "ADDRESS_M0 = $ADDRESS_M0"

    SBRV=0x20000
    IPCCDBA=0x0
    SRAM2_RST=1

    #For STM32WB 1MB of FLASH is available
    # -> Standard split is as follow:512k for M4 and 512k for M0
    # -> In Case M0 binary is greater than half flash, we must change SBRV Option bytes
    # 512k * 1024 = 524288
    FLASH_SIZE=$((1024*1024))
    HALF_FLASH_SIZE=$((FLASH_SIZE/2))
}

set_ob() { #This function sets following Option Bytes : IPCCDBA, SBRV and SRAM2_RST
    echo
    echo "--> Setting Option bytes : "
    echo "  -  IPCCDBA to $IPCCDBA" 
    printf '  -  SBRV = 0x%x\n' $1    
    echo "  -  SRAM2_RST to $SRAM2_RST"
    echo ""
    "$ST_LINK_UTILITY" -c ID=$DEVICE_ID UR swd -OB IPCCDBA=$IPCCDBA SBRV=$1 SRAM2_RST=$SRAM2_RST -Rst 
    parse_st_link_error_code
    
    echo ""
    echo "--> Option bytes set, reading new option bytes " 
    "$ST_LINK_UTILITY" -c ID=$DEVICE_ID UR swd -rOB
    parse_st_link_error_code
    echo "--> end of option bytes config"
}

set_memory_size() {
    FILENAME=$1
    SHORTNAME=$(basename $FILENAME)
    FILESIZE=$(stat -c %s "$FILENAME")
    echo
    echo "Size of $SHORTNAME = $(($FILESIZE / 1024)) kB."
    if [ "$FILESIZE" -gt "$HALF_FLASH_SIZE" ]; then
        echo "$SHORTNAME size is GREATER than $(($HALF_FLASH_SIZE / 1024))kB (Half Flash size)"
        diff_size=$((FILESIZE-HALF_FLASH_SIZE))
        #echo "diff size = $diff_size"
        new_offset_M0=$(($OFFSET_M0-$diff_size))
        #printf 'new_offset_M0 = 0x%x\n' $new_offset_M0
        
        #Offset must be 4k aligned (sector in FLASH is 4k), 
        #  otherwise M4 during OTA will erase part of M0 FW...
        new_offset_M0=$(($new_offset_M0&0xFF000))
        printf 'new_offset_M0 (4k aligned) = 0x%x\n' $new_offset_M0
            
        #Compute SBRV value (offset_M0 / 4)
        SBRV=$(($new_offset_M0/4))
        printf 'SBRV = 0x%x\n' $SBRV
        
        #Set Option Bytes 
        set_ob $SBRV
        
        #Modify ADDRESS_M0 in order to fit with binary size 
        ADDRESS_M0=$(($ADDRESS_START_FLASH+$new_offset_M0))
    else
        echo "$SHORTNAME size is LOWER than $(($HALF_FLASH_SIZE / 1024)) kB (Half Flash size)"
        #Set Option Bytes 
        set_ob $SBRV
    fi
}

display_help() { # TODO, update & clean this
    echo
    echo "*********************************************************************************************************************************"
    echo "*********************************************************************************************************************************"
    echo "     USAGE: $0 [option...] "                     
    echo "Options: "
    echo "    -m0 <m0_binary>                                 flash M0 binary "
    echo "    -m4 <m4_binary>                                 flash M4 binary "
    echo "    -p | --project_path <project_path>              path for project where folders M0 firmware and M4 Firmware are, $PROJECT_C_SOURCES_PATH by default"
    echo "    -id <id>                                        id of ST-LINK [0..9] to use when multiple probes are connected to the host, $DEVICE_ID by default"
    echo "    -l | --log_path <log_path>                      path where to output compilation logs, $LOG_PATH by default"
    echo "*********************************************************************************************************************************"
    echo "*********************************************************************************************************************************"
    echo
    
    exit 1
}

flash() { #binary_file , target
    local binary_file=$1
    local target=$2
    local binary_file_name="$(basename $binary_file)"

    local application_name="${binary_file_name%.*}"
    local binary_extension="${binary_file_name##*.}"
    
    echo "--> Flashing application $application_name"
    echo "--> Application built on the $(date -r $binary_file)"
    
    if [[ "$binary_extension" != "hex" ]]; then
        print_error "File extension should be in intel format (hex)"
        exit 1
    fi
    
    hex_folder_path=$(realpath  $(dirname $binary_file))
    map_folder_path=$(realpath  $hex_folder_path/../List)
    echo "hex_folder_path : $(readlink -m $hex_folder_path)"
    echo "map_folder_path : $(readlink -m $map_folder_path)"
    
    
    echo "--> Copying hex, and map in the log folder"
    built_hex_file=$(realpath  $hex_folder_path/${application_name}.hex)
    built_map_file=$(realpath  $map_folder_path/${application_name}.map)
    log_hex_file=$(realpath  $LOG_PATH/${application_name}.hex)
    log_map_file=$(realpath  $LOG_PATH/${application_name}.map)
    echo "built_hex_file : $(readlink -m $built_hex_file)"
    echo "built_map_file : $(readlink -m $built_map_file)"
    echo "log_hex_file : $(readlink -m $log_hex_file)"
    echo "log_map_file : $(readlink -m $log_map_file)"
    
    if [[ -f "$built_hex_file" ]]; then
        cp "$built_hex_file" "$log_hex_file"
    else
        print_error "File built_hex_file does not exit."
        exit 1
    fi
    if [[ -f "$built_map_file" ]]; then
        cp "$built_map_file" "$log_map_file"
    else
        print_error "File built_map_file does not exit."
        exit 1
    fi
   
    flash_this $DEVICE_ID $log_hex_file $target
    echo "--> Flashing complete"
}

check_parameter() {
    
    init_variables
    set_user_cfg
    while :
    do
        case "$1" in
        
            -h | --help)
                display_help
                exit 0
                ;;
                
            -m0)
                M0_FLASH=1
                M0_BINARY_FILE="$2"
                shift 2
                ;;

            -m4)
                M4_FLASH=1
                M4_BINARY_FILE="$2"
                shift 2
                ;;
                
            -p | --project_path)
                PROJECT_C_SOURCES_PATH="$2"
                shift 2
                ;;   
                
            -id)
                DEVICE_ID="$2"
                shift 2
                ;;   
               
            -l | --log_path)
               LOG_PATH=$(realpath  $2)
               shift 2
               ;;
               
            --) # End of all options
                shift
                break
                ;;
                
            -*)
                print_error "Unknown option: $1" 
                display_help
                exit 1 
                ;;

            *)  # No more options
            break
            ;;
        esac
    done
}

parse_flash_option() {
    
    if [[ "$M0_FLASH" = "1" ]] || [[ "$M4_FLASH" = "1" ]]; then
        M0_BINARY_FILE=$(realpath  $PROJECT_C_SOURCES_PATH/$M0_TOP_DIR/$M0_BINARY_FILE)
        M4_BINARY_FILE=$(realpath  $PROJECT_C_SOURCES_PATH/$M4_TOP_DIR/$M4_BINARY_FILE)
        

        if [[ ! -f "$M0_BINARY_FILE" ]] && [[ "$M0_FLASH" = "1" ]]; then
            print_error "Path/file $M0_BINARY_FILE does not exist"
            exit 1
        fi
        if [[ ! -f "$M4_BINARY_FILE" ]] && [[ "$M4_FLASH" = "1" ]]; then
            print_error "Path/file $M4_BINARY_FILE does not exist"  
            exit 1
        fi
    fi
    
    if [[ "$M0_FLASH" = "1" ]] && [[ "$M4_FLASH" = "1" ]]; then
        echo "--> Flashing M0 and M4."
        if [ "$(($(stat -c %s "$M0_BINARY_FILE")+$(stat -c %s "$M4_BINARY_FILE")))" -gt "$FLASH_SIZE" ]; then
            print_error "Sum of size of binaries exceeds flash size"
            exit 1
        fi
    fi
}

flash_device() {
    if [[ "$M0_FLASH" = "1" ]]; then
        echo "///////////////////////////////////"
        echo "///       Flashing M0....       ///"
        echo "///////////////////////////////////"
        set_memory_size $M0_BINARY_FILE 
        flash $M0_BINARY_FILE M0
    fi

    if [[ "$M4_FLASH" = "1" ]]; then
        echo "///////////////////////////////////"
        echo "///       Flashing M4....       ///"
        echo "///////////////////////////////////"
        set_memory_size $M4_BINARY_FILE 
        flash $M4_BINARY_FILE m4  
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

parse_flash_option 
echo 

flash_device
echo 

display_end_banner
