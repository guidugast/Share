#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>
#include <stdlib.h>
                                                                   
                                                                       
//////////////////////////////////////////////////////////////
///////////////          VALIDATION           ////////////////
//////////////////////////////////////////////////////////////                   
                                                                       
    #define RLV_LOG_DEBUG                     printf
    #define RLV_APPEND_LOG                    printf
    #define RLV_LOG_LINE                      printf
    #define RLV_LOG_ERROR                     printf
    
////////////////////////////////////////////////////////////////////////////////
//////////////////               Configuration                //////////////////
////////////////////////////////////////////////////////////////////////////////
#define RLV_GEN_MAX_ARR_BUF_SIZE 256  
#define RLV_MAX_DISPLAYABLE_ARR_SIZE 30  


////////////////////////////////////////////////////////////////////////////////
//////////////////                Generic Macros              //////////////////
////////////////////////////////////////////////////////////////////////////////
#define  DO_(function, type, data,arg) function##type((type)*((type*)&data),arg)
#define  DO_AUTO_(function,data,arg)   _Generic((&data)+0,  \
                                    _Bool* : DO_(function, _Bool, data,arg), \
                                    uint8_t* : DO_(function, uint8_t, data,arg), \
                                    uint16_t* : DO_(function, uint16_t, data,arg), \
                                    uint32_t* : DO_(function, uint32_t, data,arg), \
                                    array_uint32_t* : DO_(function, array_uint32_t, data,arg), \
                                    array_uint16_t* : DO_(function, array_uint16_t, data,arg), \
                                    array_uint8_t * : DO_(function, array_uint8_t, data,arg), \
                                    FunctionalState_t * : DO_(function, FunctionalState_t, data,arg), \
                                    apDataRoutine_e_t * : DO_(function, apDataRoutine_e_t, data,arg), \
                                    apCondRoutine_e_t * : DO_(function, apCondRoutine_e_t, data,arg), \
                                    actionPacket_e_t * : DO_(function, actionPacket_e_t, data,arg) \
                                    )
                                                   

////////////////////////////////////////////////////////////////////////////////
//////////////////                Type generation             //////////////////
////////////////////////////////////////////////////////////////////////////////
typedef enum 
{
    ENABLE=0,
    DISABLE=!ENABLE,
}FunctionalState;

#define LIST_apDataRoutine_e(X) \
        X(APDR_NULL) \
        X(APDR_DEFAULT)

#define LIST_apCondRoutine_e(X) \
        X(APCR_NULL) \
        X(APCR_DEFAULT)

#define LIST_actionPacket_e(X) \
        X(AP_NULL) \
        X(AP_DEFAULT)

#define DEF_enum_val(enum_val) \
enum_val,
#define DEF_x_e(enum_type) \
typedef enum \
{ \
  LIST_##enum_type(DEF_enum_val) \
}enum_type; 
DEF_x_e(apDataRoutine_e);
DEF_x_e(apCondRoutine_e);
DEF_x_e(actionPacket_e);

#define DEF_x_st(type) \
typedef union \
{ \
    type value;\
}type##_t;
DEF_x_st(FunctionalState);
DEF_x_st(apDataRoutine_e);
DEF_x_st(apCondRoutine_e);
DEF_x_st(actionPacket_e);

#define DEF_array_x_t(type) \
typedef struct \
{ \
    type content[RLV_GEN_MAX_ARR_BUF_SIZE]; \
    uint16_t length; \
}array_##type
DEF_array_x_t(uint32_t);
DEF_array_x_t(uint16_t);
DEF_array_x_t(uint8_t);


////////////////////////////////////////////////////////////////////////////////
//////////////////                Print generation            //////////////////
////////////////////////////////////////////////////////////////////////////////
#define DEF_print_x_t(int_type) \
static inline void print_##int_type(int_type val, char * dummy) \
{ \
    (void)dummy; \
    RLV_LOG_LINE(#int_type" val = %u (0x%08x)",(int_type)val,(int_type)val); \
} 
DEF_print_x_t(uint32_t);
DEF_print_x_t(uint16_t);
DEF_print_x_t(uint8_t);

#define DEF_print_array_x_t(type) \
static inline void print_array_##type(array_##type val, char * dummy) \
{ \
    (void)dummy; \
    RLV_LOG_LINE(#type" val[%u] = {",val.length); \
    for(uint16_t i = 0; (i < RLV_MAX_DISPLAYABLE_ARR_SIZE)&&(i < val.length); i++) \
    { \
        RLV_APPEND_LOG("0x%x",val.content[i]); \
        if((i +1 < RLV_MAX_DISPLAYABLE_ARR_SIZE) && (i + 1 < val.length)) {RLV_APPEND_LOG(",");} \
    } \
    RLV_APPEND_LOG("}"); \
} 
DEF_print_array_x_t(uint32_t);
DEF_print_array_x_t(uint16_t);
DEF_print_array_x_t(uint8_t);

static inline void print_FunctionalState_t(FunctionalState_t val, char * dummy)
{
    (void)dummy; \
    RLV_LOG_LINE("FunctionalState val = ");
    switch(val.value)
    {
        case ENABLE: RLV_APPEND_LOG("ENABLE"); break;
        case DISABLE: RLV_APPEND_LOG("DISABLE"); break;
        default: RLV_LOG_ERROR("unkown value for FunctionalState"); break;
    }
}

static inline void print__Bool(_Bool val, char * dummy)
{
    (void)dummy;
    RLV_LOG_LINE("bool val = %s",(val?"TRUE":"FALSE"));
}

#define DEF_print_enum(enum_val) \
case enum_val: RLV_APPEND_LOG(#enum_val); break;
#define DEF_print_x_e(enum_type) \
static inline void print_##enum_type##_t(enum_type##_t val, char * dummy) \
{ \
    (void)dummy; \
    RLV_LOG_LINE(#enum_type" val = "); \
    switch(val.value) \
    { \
         LIST_##enum_type(DEF_print_enum) \
         default: RLV_LOG_ERROR("unkown value for "#enum_type"_t"); break; \
    } \
    RLV_APPEND_LOG(";"); \
}
DEF_print_x_e(apDataRoutine_e);
DEF_print_x_e(apCondRoutine_e);
DEF_print_x_e(actionPacket_e);

#define  print_param_(param) DO_AUTO_(print_,param,"\0")

#define RLV_PRINT_VARIABLE(paramName) print_param_(RLV_BLE_TOOLS_Parameters_ptr->paramName)

////////////////////////////////////////////////////////////////////////////////
//////////////////              Set Param generation          //////////////////
////////////////////////////////////////////////////////////////////////////////

#define set_from_arg_int_x_(param,gen_current_cli_arg_) \
do{ \
    if((gen_current_cli_arg_[0]=='T')       || \
       strcmp(gen_current_cli_arg_,"TRUE")  || \
       strcmp(gen_current_cli_arg_,"true")  || \
      (gen_current_cli_arg_[0]=='F')        || \
       strcmp(gen_current_cli_arg_,"FALSE") || \
       strcmp(gen_current_cli_arg_,"false"))  \
    { \
        param = ((gen_current_cli_arg_[strspn(gen_current_cli_arg_, "Tt")] != '\0') ? 1 : 0);   \
    } \
    else if((gen_current_cli_arg_[0]=='x') || \
            (gen_current_cli_arg_[1]=='x') || \
            (gen_current_cli_arg_[0]=='X') || \
            (gen_current_cli_arg_[1]=='X'))   \
    {     \
        param = strtol(gen_current_cli_arg_,NULL,16);   \
    }   \
    else   \
    {   \
        if(gen_current_cli_arg_[strspn(gen_current_cli_arg_, "0123456789")] != '\0') \
        { \
            RLV_LOG_ERROR("wrong format for integer, use for instance 'T','F','0','33','0xFFF'\n"); \
        } \
        else \
        { \
            param = strtol(gen_current_cli_arg_,NULL,10); \
        } \
    } \
}while(0)
#define DEF_set_from_arg_int_x_(integer_type) \
static inline void set_from_arg_##integer_type(integer_type param, char* gen_current_cli_arg_) \
{ \
    set_from_arg_int_x_(param,gen_current_cli_arg_); \
} 
DEF_set_from_arg_int_x_(_Bool);
DEF_set_from_arg_int_x_(uint8_t);
DEF_set_from_arg_int_x_(uint16_t);
DEF_set_from_arg_int_x_(uint32_t);

#define set_from_arg_arr_x_(param,gen_current_cli_arg_)  \
do{ \
    if((gen_current_cli_arg_[0]=='[') && \
    (gen_current_cli_arg_[strlen(gen_current_cli_arg_)-1] == '}') && \
    (gen_current_cli_arg_[strcspn(gen_current_cli_arg_, "[]{}")] != '\0'))  \
    {  \
        char * gen_array_arg  = strtok(gen_current_cli_arg_, "]"); \
        param.length = (uint16_t)strtol(gen_array_arg, NULL, 10); \
        printf("gen_array_arg '%s'",gen_array_arg); \
    } \
    else \
    { \
        RLV_LOG_ERROR("wrong format for array, use for instance '[4]{A,10,0,A1FC}', '[0]{}', or '[3]{FF}'\n"); \
    } \
}while(0)    
/*      uint32_t array_length_index = (uint32_t)(strcspn(gen_current_cli_arg_,"]") != -1)?strcspn(gen_current_cli_arg_,"]") + 3:-1;
uint32_t array_index = (uint32_t)(strcspn(gen_current_cli_arg_,"]") != -1)?strcspn(gen_current_cli_arg_,"]") + 3:-1;
        printf("%u -- ",(uint32_t)strcspn(gen_current_cli_arg_,"]")); //index de "]"


        char * gen_array_arg strtok(gen_current_cli_arg_, "]"); \
        param.length = (uint16_t)strtol(gen_array_arg, NULL, 10); \
        printf("gen_array_arg '%s'",gen_array_arg); \
        gen_array_arg = strtok(NULL, "}"); \

        printf("param.length '%u'",param.length); \
        gen_array_arg = strtok(NULL, "]"); \
        if(gen_array_arg != NULL) \
        { \
            printf("gen_array_arg '%s'",gen_array_arg); \
            char * gen_data_arg;  \
            gen_data_arg = strtok(gen_array_arg, ","); \
            printf("gen_data_arg '%s'",gen_data_arg); \
            for(uint16_t i = 0; (gen_data_arg != NULL) && (i<RLV_GEN_MAX_ARR_BUF_SIZE);i++) \
            { \
                param.content[i] = (uint32_t)strtol(gen_data_arg, NULL, 16); \
                gen_data_arg = strtok(NULL, ","); \
            } \
        } \
        */
#define DEF_set_from_arg_arr_x_(type) \
static inline void set_from_arg_array_##type(array_##type param, char* gen_current_cli_arg_) \
{ \
    set_from_arg_arr_x_(param,gen_current_cli_arg_); \
} 
DEF_set_from_arg_arr_x_(uint8_t);
DEF_set_from_arg_arr_x_(uint16_t);
DEF_set_from_arg_arr_x_(uint32_t);

static inline void set_from_arg_FunctionalState_t(FunctionalState_t param, char * gen_current_cli_arg_)
{
    if(false){}
    else if(!strcmp(gen_current_cli_arg_,"ENABLE")) param.value = ENABLE;
    else if (!strcmp(gen_current_cli_arg_,"ENABLE")) param.value = ENABLE;
    else RLV_LOG_ERROR("unkown value for FunctionalState");
}

#define DEF_set_param(enum_val) \
else if(!strcmp(gen_current_cli_arg_,#enum_val)) param.value = enum_val;
#define DEF_set_from_arg_e_x_(enum_type) \
static inline void set_from_arg_##enum_type##_t(enum_type##_t param, char* gen_current_cli_arg_) \
{ \
    if(false){} \
    LIST_##enum_type(DEF_set_param) \
    else RLV_LOG_ERROR("unkown value for "#enum_type); \
} 
DEF_set_from_arg_e_x_(apDataRoutine_e);
DEF_set_from_arg_e_x_(apCondRoutine_e);
DEF_set_from_arg_e_x_(actionPacket_e);


#define set_from_arg_param_(param,gen_current_cli_arg_) DO_AUTO_(set_from_arg_,param,gen_current_cli_arg_)
                                                                         
#define set_param_from_arg_with_default_and_preset(param_name,gen_current_cli_arg_)  \
do { \
    if(!strcmp(gen_current_cli_arg_,"D"))   \
    {   \
         memcpy(&RLV_BLE_TOOLS_Parameters_ptr->param_name, \
                &RLV_BLE_TOOLS_DefaultParameters_ptr->param_name, \
                sizeof(RLV_BLE_TOOLS_DefaultParameters_ptr->param_name)); \
    }   \
    else if(!strcmp(gen_current_cli_arg_,"P"))   \
    {   \
    }   \
    else   \
    {   \
        set_from_arg_param_(RLV_BLE_TOOLS_Parameters_ptr->param_name,gen_current_cli_arg_); \
    } \
}while(0)


#define VALID_RLV_SET_PARAM_AUTOTYPE(param_name)               do{ \
                                                                    char * gen_current_cli_arg_ = argList[argListIndex_]; \
                                                                    set_param_from_arg_with_default_and_preset(param_name,gen_current_cli_arg_); \
                                                                    argListIndex_++; \
                                                                    RLV_PRINT_VARIABLE(param_name); \
                                                                }while(0)

                                

                                                                     




//SIZES
#define RLV_PAYLOAD_SIZE_MAX                            257
#define RLV_HOT_ANA_SIZE_MAX                            257
#define RLV_CHANNEL_MAP_SIZE_MAX                        10

//DEFAULT PARAM VALUE
#define RLV_DEFAULT_CRYSTAL_CHECK                       true
#define RLV_DEFAULT_ACK                                 false
#define RLV_DEFAULT_STARTUP_TIME                        0x001A  //(64 us)
#define RLV_DEFAULT_LOW_SPEED_OSC                       1
#define RLV_DEFAULT_WHITENING_ENABLED                   (FunctionalState_t){ENABLE}
#define RLV_DEFAULT_HOT_ANA_TABLE                       {{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},15}
#define RLV_DEFAULT_NETWORK_ID                          0x5A964129
#define RLV_DEFAULT_CHANNEL                             30
#define RLV_DEFAULT_WAKEUPTIME                          4000 
#define RLV_DEFAULT_HEADER                              0x95
#define RLV_DEFAULT_PACKET_PAYLOAD                      {{0x1C,0xB4,0x97,0xA3,0xEF,0xCF,0x5A,0x4A},8}
#define RLV_DEFAULT_DATA_ROUTINE                        (apDataRoutine_e_t){APDR_DEFAULT}
#define RLV_DEFAULT_COND_ROUTINE                        (apCondRoutine_e_t){APCR_DEFAULT}
#define RLV_DEFAULT_CHANNEL_MAP                         {{0xFF,0xFF,0xFF,0xFF,0xFF},5}
#define RLV_DEFAULT_STATE_MACHINE_ID                    0
#define RLV_DEFAULT_CHANNEL_INCREMENT                   1
#define RLV_DEFAULT_ACTION_TAG                          0//(INC_CHAN | RELATIVE | TIMER_WAKEUP | TXRX | PLL_TRIG)
#define RLV_DEFAULT_WINDOW                              9000
#define RLV_DEFAULT_AP_NEXT_TRUE                        (actionPacket_e_t){AP_DEFAULT}
#define RLV_DEFAULT_AP_NEXT_FALSE                       (actionPacket_e_t){AP_DEFAULT}

//RETURN CODES
#define RLV_ACTION_PACKET_RETURN_VALUE_SUCCESS          0
typedef struct 
{
///relative test environment validation
///------------------------------------
  uint32_t                 param1;
  uint32_t                 param2;
  uint32_t                 param3;
  
///relative to lld ble validation
///------------------------------------
  
 //Test application 
  bool                     crystalCheckEnabled;
  bool                     withAck;
  
  //Init parameters
  uint16_t                 hsStartupTime;
  uint8_t                  lowSpeedOsc;
  FunctionalState_t        whitening;
  array_uint32_t           hotAnaTable;
  
  //Connexion parameters
  uint32_t                 networkId;
  array_uint8_t            channelMap;  //40bit that defines wich channel is active
  uint8_t                  channelIncrement;
  
  //Action packet parameters
  uint8_t                  stateMachineId;
  uint8_t                  actionTag;
  uint32_t                 apReceiveWindow;
  uint8_t                  apHeader;
  array_uint8_t            apPayload;
  actionPacket_e_t         apNextTrueId;
  actionPacket_e_t         apNextFalseId;
  apCondRoutine_e_t        apCondRoutineId;
  apDataRoutine_e_t        apDataRoutineId;
  //Action packet parameters (hal)
  uint8_t                  channel;
  uint32_t                 wakeupTime;
  
  //First Packet to send (hal)
  uint8_t                  txHeader;
  array_uint8_t            txPayload;
  apDataRoutine_e_t        txDataRoutineId;
  
  //Packet to send as a reply (hal)
  uint32_t                 txAckReceiveWindow;
  uint8_t                  txAckExpectedHeader;
  array_uint8_t            txAckExpectedPayload;
  
  //First Packet to receive (hal)
  uint32_t                 rxReceiveWindow;
  uint8_t                  rxExpectedHeader;
  array_uint8_t            rxExpectedPayload;
  apDataRoutine_e_t        rxDataRoutineId;
  
  //Packet to receive as a reply (hal)
  uint8_t                  rxAckHeader;
  array_uint8_t            rxAckPayload;

}RLV_Parameters_t;

                                                          
static volatile RLV_Parameters_t          parametersPrivate        = {0};
static volatile const RLV_Parameters_t    defaultParametersPrivate =
{
    .param1                      = 8,
    .param2                      = 12,
    .param3                      = 42,
    //Test application 
    .crystalCheckEnabled         = RLV_DEFAULT_CRYSTAL_CHECK,
    .withAck                     = RLV_DEFAULT_ACK,
    //Init parameters
    .hsStartupTime               = RLV_DEFAULT_STARTUP_TIME,
    .lowSpeedOsc                 = RLV_DEFAULT_LOW_SPEED_OSC,
    .whitening                   = RLV_DEFAULT_WHITENING_ENABLED,
    .hotAnaTable                 = RLV_DEFAULT_HOT_ANA_TABLE,
    //Connexion parameters
    .networkId                   = RLV_DEFAULT_NETWORK_ID,
    .channelMap                  = RLV_DEFAULT_CHANNEL_MAP,
    .channelIncrement            = RLV_DEFAULT_CHANNEL_INCREMENT,
    //Action packet parameters
    .stateMachineId              = RLV_DEFAULT_STATE_MACHINE_ID,
    .actionTag                   = RLV_DEFAULT_ACTION_TAG,
    .apReceiveWindow             = RLV_DEFAULT_WINDOW,
    .apHeader                    = RLV_DEFAULT_HEADER,
    .apPayload                   = RLV_DEFAULT_PACKET_PAYLOAD,
    .apNextTrueId                = RLV_DEFAULT_AP_NEXT_TRUE,
    .apNextFalseId               = RLV_DEFAULT_AP_NEXT_FALSE,
    .apCondRoutineId             = RLV_DEFAULT_COND_ROUTINE,
    .apDataRoutineId             = RLV_DEFAULT_DATA_ROUTINE,
     //Action packet parameters (hal)
    .channel                     = RLV_DEFAULT_CHANNEL,
    .wakeupTime                  = RLV_DEFAULT_WAKEUPTIME,
     //First Packet to send (hal)
    .txHeader                    = RLV_DEFAULT_HEADER,
    .txPayload                   = RLV_DEFAULT_PACKET_PAYLOAD,
    .txDataRoutineId             = RLV_DEFAULT_DATA_ROUTINE,
     //Packet to send as a reply (hal)
    .txAckReceiveWindow          = RLV_DEFAULT_WINDOW,
    .txAckExpectedHeader         = RLV_DEFAULT_HEADER,
    .txAckExpectedPayload        = RLV_DEFAULT_PACKET_PAYLOAD,
     //First Packet to receive (hal)
    .rxReceiveWindow             = RLV_DEFAULT_WINDOW,
    .rxExpectedHeader            = RLV_DEFAULT_HEADER,
    .rxExpectedPayload           = RLV_DEFAULT_PACKET_PAYLOAD,
    .rxDataRoutineId             = RLV_DEFAULT_DATA_ROUTINE,
     //Packet to send as a reply (hal)
    .rxAckHeader                 = RLV_DEFAULT_HEADER,
    .rxAckPayload                = RLV_DEFAULT_PACKET_PAYLOAD,
};


RLV_Parameters_t*                RLV_BLE_TOOLS_Parameters_ptr = (RLV_Parameters_t*) &parametersPrivate;
RLV_Parameters_t*                RLV_BLE_TOOLS_DefaultParameters_ptr = (RLV_Parameters_t*) &defaultParametersPrivate;





    char * argList[] = {"0xFF" , "[5]{A,B,C,D,E}" , "T", //valid --> new values
                        "D"    , "D"           , "D", //default --> back to default values 
                        "15"   , "[3]{1,2,3}"   , "T", //valid --> new values 
                        "P"    , "P"           , "P", //preset --> keep last values
                        "TEST" , "ABCDE"       , "Z", //wrong values --> keep last values
                       };



    
#define TEST(TEST_NAME,code) void test_##TEST_NAME (void) { uint8_t argListIndex_= 0; code }          

TEST(u32,

    VALID_RLV_SET_PARAM_AUTOTYPE(apReceiveWindow);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hotAnaTable);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(apReceiveWindow);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hotAnaTable);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(apReceiveWindow);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hotAnaTable);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(apReceiveWindow);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hotAnaTable);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(apReceiveWindow);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hotAnaTable);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
)
TEST(u16,

    VALID_RLV_SET_PARAM_AUTOTYPE(hsStartupTime);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(rxAckPayload);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hsStartupTime);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(rxAckPayload);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hsStartupTime);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(rxAckPayload);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hsStartupTime);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(rxAckPayload);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hsStartupTime);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(rxAckPayload);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
)
TEST(u8,

    VALID_RLV_SET_PARAM_AUTOTYPE(txAckExpectedHeader);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hotAnaTable);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(txAckExpectedHeader);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hotAnaTable);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(txAckExpectedHeader);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hotAnaTable);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(txAckExpectedHeader);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hotAnaTable);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(txAckExpectedHeader);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(hotAnaTable);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(crystalCheckEnabled);printf("\n------\n");
)
int main()
{
    printf("----------------test u32--------------\n");
    test_u32();
    printf("----------------test u16--------------\n");
    test_u16();
    printf("----------------test u8 --------------\n");
    test_u8();
    return 0;
}