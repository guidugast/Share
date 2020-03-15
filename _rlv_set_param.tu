#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>
#include <stdlib.h>
    

//////////////////////////////////////////////////////////////
///////////////         VALIDATION TOOLS      ////////////////
//////////////////////////////////////////////////////////////
#define VALID_GEN_EQUAL(expected,observed)                      do{ \
                                                                    printf("Is "#observed"(%s) equal to "#expected"? ",(GEN_AUTOTYPE_(GET_TYPE_DIM_,expected) == GEN_TYPE_DIM_ARRAY_)?"array":"integer"); \
                                                                    if(IS_EQUAL_(expected,observed)) {printf("true\n");} else {printf("false\n");}\
                                                                }while(0)
                                                            
                                                 
#define VALID_GEN_TRUE(observed)                                do{ \
                                                                    printf("Is "#observed" equal to true? "); \
                                                                    if(IS_TRUE_(observed)) {printf("true\n");} else {printf("false\n");}\
                                                                }while(0)
                                                    
#define VALID_GEN_PRINT(data)                                   do{ \
                                                                    printf(#data", ");  \
                                                                    GENERIC_PRINT(data); \
                                                                    printf("\n"); \
                                                                }while(0)
                                                    
#define VALID_RLV_SET_PARAM_AUTOTYPE(paramName)                 do{ \
                                                                    RLV_SET_PARAM_TO_CMD_ARG(paramName, argListIndex_); \
                                                                    argListIndex_++; \
                                                                    GENERIC_PRINT(RLV_BLE_Parameters.paramName); \
                                                                }while(0)
                                                                //GEN_AUTOTYPE_
                                                                               
//////////////////////////////////////////////////////////////
///////////////            GEN API            ////////////////
//////////////////////////////////////////////////////////////

#define MAX_ARR_BUF_SIZE 256  

#define GEN_TYPE_DIM_DEFAULT_ 0
#define GEN_TYPE_DIM_POINTER_ 1
#define GEN_TYPE_DIM_INTEGER_ 2
#define GEN_TYPE_DIM_ARRAY_   4

#define GEN_TYPE_DEFAULT_ 0
#define GEN_TYPE_U32_ 1 
#define GEN_TYPE_U16_ 2
#define GEN_TYPE_U8_ 4
#define GEN_TYPE_BOOL_ 8

#define GET_TYPE_DIM_(type,arg)                     _Generic((&arg)+0, \
                                                        default: GEN_TYPE_DIM_DEFAULT_, \
                                                        type *: GEN_TYPE_DIM_INTEGER_, \
                                                        type **: GEN_TYPE_DIM_POINTER_, \
                                                        type (*)[]: GEN_TYPE_DIM_ARRAY_ \
                                                    )
                                                           
#define GEN_AUTOTYPE_PN(function,paramName,...)     //GEN_AUTOTYPE_(function,RLV_BLE_Parameters.paramName,__VA_ARGS__) 
#define GEN_AUTOTYPE_(function,arg,...)            do{switch(_Generic((&arg), \
                                                        _Bool * : GEN_TYPE_BOOL_, \
                                                        uint8_t* : GEN_TYPE_U8_, \
                                                        uint8_t **: GEN_TYPE_U8_, \
                                                        uint8_t(*)[] : GEN_TYPE_U8_, \
                                                        uint16_t* : GEN_TYPE_U16_, \
                                                        uint16_t **: GEN_TYPE_U16_, \
                                                        uint16_t(*)[] : GEN_TYPE_U16_, \
                                                        uint32_t* : GEN_TYPE_U32_, \
                                                        uint32_t **: GEN_TYPE_U32_, \
                                                        uint32_t(*)[] : GEN_TYPE_U32_ , \
                                                        default: GEN_TYPE_DEFAULT_ \
                                                    )){ \
                                                        case GEN_TYPE_U32_ : function(uint32_t,arg,__VA_ARGS__); break; \
                                                        case GEN_TYPE_U16_ : function(uint16_t,arg,__VA_ARGS__); break; \
                                                        case GEN_TYPE_U8_ : function(uint8_t,arg,__VA_ARGS__); break; \
                                                        case GEN_TYPE_BOOL_ :  function(_Bool,arg,__VA_ARGS__); break; \
                                                        default: RLV_LOG_ERROR("Type of "#arg" not supported yet, please add the type in GEN_AUTOTYPE_ in the code"); break; \
                                                    }}while(0)
                                                    
#define INTEGER_EQUAL_(type,expected,observed)      (observed == expected)
#define ARRAY_EQUAL_(type,expected,observed)        (memcmp((type (*)[])&observed, (type (*)[])&expected, sizeof(expected)) == 0)
#define IS_EQUAL_(type,expected,observed)           _Generic((&observed)+0, \
                                                        default: RLV_LOG_ERROR("Equality cannot be applied to the type of "#observed". ") & 0, \
                                                        type **: INTEGER_EQUAL_(type,expected,observed), \
                                                        type *:  INTEGER_EQUAL_(type,expected,observed), \
                                                        type (*)[]: ARRAY_EQUAL_(type,expected,observed) \
                                                    )
                                                                                                 
#define DEFAULT_PRINT_(data)                        do{ uint32_t gen_int_buf_ = *((uint32_t*)&data); RLV_LOG_LINE("Unknwon_type "#data" = 0x%08x",gen_int_buf_); }while(0)
#define INTEGER_PRINT_(type,data)                   do{ type gen_int_buf_ = *((type*)&data); RLV_LOG_LINE(#type" "#data" = %u",gen_int_buf_); }while(0)
#define ARRAY_PRINT_(type,data)                     do{ \
                                                        type gen_arr_buf_[sizeof(data)]; \
                                                        memcpy(gen_arr_buf_,(type*)&data,sizeof(data)); \
                                                        RLV_LOG_APPEND(#type" "#data"[] = {"); \
                                                        for(uint32_t igen_ = 0; igen_<sizeof(data)/sizeof(type);igen_++) \
                                                        {  \
                                                            RLV_LOG_LINE("0x%x",gen_arr_buf_[igen_]); \
                                                            (igen_+1<sizeof(data)/sizeof(type)) && RLV_LOG_LINE(","); \
                                                        } \
                                                        RLV_LOG_APPEND("}"); \
                                                    }while(0)
#define PRINT_TYPE_(type,data,...)                  do { switch(GET_TYPE_DIM_(type,data)){ \
                                                        case GEN_TYPE_DIM_INTEGER_ : INTEGER_PRINT_(type,data); break; \
                                                        case GEN_TYPE_DIM_ARRAY_ : ARRAY_PRINT_(type,data); break; \
                                                        case GEN_TYPE_DIM_POINTER_ :  \
                                                        case GEN_TYPE_DIM_DEFAULT_ :  \
                                                        default: DEFAULT_PRINT_(data); break; \
                                                    }}while(0)
#define GENERIC_PRINT(data)                         GEN_AUTOTYPE_(PRINT_TYPE_,data)
                                                  
//////////////////////////////////////////////////////////////
///////////////          TO BE TESTED         ////////////////
//////////////////////////////////////////////////////////////
 

#define SET_PARAM_ARRAY_(type, argListIndex, arrayMaxSize)           do{ \
                                                                          if(argList[argListIndex][0]=='#')   \
                                                                          {    \
                                                                              if(arrayMaxSize)  \
                                                                              {     \
                                                                                  paramArrayBufLength_ = 0; \
                                                                                  char arrayBuf_[strlen(argList[argListIndex])]; \
                                                                                  strcpy(arrayBuf_,argList[argListIndex]); \
                                                                                  char * argArray_; \
                                                                                  char * argData_; \
                                                                                  if((argList[argListIndex][0] == '#') && (argList[argListIndex][strlen(argList[argListIndex])-1] == '#')) \
                                                                                  {  \
                                                                                    argArray_ = strtok(arrayBuf_, "#"); \
                                                                                    if(argArray_ != NULL) \
                                                                                    { \
                                                                                      argData_ = strtok(argArray_, ","); \
                                                                                      while ((argData_ != NULL) && (paramArrayBufLength_ < arrayMaxSize)) \
                                                                                      { \
                                                                                        paramArrayBuf_[paramArrayBufLength_++]=(uint32_t)strtol(argData_, NULL, 16); \
                                                                                        argData_ = strtok(NULL, ","); \
                                                                                      } \
                                                                                    } \
                                                                                  } \
                                                                                  else \
                                                                                  { \
                                                                                    RLV_LOG_ERROR("wrong format for array, use for instance '#A,10,0,A1FC#', '##', or '#FF#' (max size %d)\n",arrayMaxSize); \
                                                                                  } \
                                                                              }  \
                                                                          } \
                                                                      }while(0)
#define SET_PARAM_NOT_ARRAY_(type, argListIndex)                     do{ \
                                                                          if((argList[argListIndex][0]=='T') || (argList[argListIndex][0]=='F'))  \
                                                                          {     \
                                                                              paramBuf_ = (type)((argList[argListIndex][0]=='T')?1:0);   \
                                                                          } \
                                                                          else if((argList[argListIndex][0]=='x') || (argList[argListIndex][1]=='x') || (argList[argListIndex][0]=='X') || (argList[argListIndex][1]=='X'))   \
                                                                          {     \
                                                                              paramBuf_ = (type)strtol(argList[argListIndex],NULL,16);   \
                                                                          }   \
                                                                          else   \
                                                                          {   \
                                                                              paramBuf_ = (type)strtol(argList[argListIndex],NULL,10);   \
                                                                          } \
                                                                      }while(0)

                                
#define SET_ARG_PARAM_(type,arg,argListIndex)                        do { \
                                                                        type paramBuf_ = 0; \
                                                                        type paramArrayBuf_[MAX_ARR_BUF_SIZE] =  {0}; \
                                                                        uint32_t paramArrayBufLength_ = 0;  \
                                                                        if(GET_TYPE_DIM_(type,arg) == GEN_TYPE_DIM_ARRAY_) \
                                                                        { \
                                                                           SET_PARAM_ARRAY_(type,argListIndex, MAX_ARR_BUF_SIZE); \
                                                                           memcpy(&(arg),&paramArrayBuf_,sizeof(type) * paramArrayBufLength_);  \
                                                                        } \
                                                                        else \
                                                                        { \
                                                                           SET_PARAM_NOT_ARRAY_(type,argListIndex); \
                                                                           memcpy(&(arg),&paramBuf_,sizeof(type)); \
                                                                        } \
                                                                     }while(0)
                                                                     
            
#define RLV_SET_PARAM_TO_CMD_ARG(paramName, argListIndex)               do { \
                                                                           if(!strcmp(argList[argListIndex],"D"))   \
                                                                           {   \
                                                                               memcpy(&RLV_BLE_Parameters.paramName,&RLV_BLE_DefaultParameters.paramName,sizeof(RLV_BLE_DefaultParameters.paramName)); \
                                                                           }   \
                                                                           else if(!strcmp(argList[argListIndex],"P"))   \
                                                                           {   \
                                                                           }   \
                                                                           else   \
                                                                           {   \
                                                                               GEN_AUTOTYPE_(SET_ARG_PARAM_,RLV_BLE_Parameters.paramName,argListIndex); \
                                                                           } \
                                                                     }while(0)
                                                                        
                                                                       
//////////////////////////////////////////////////////////////
///////////////          VALIDATION           ////////////////
//////////////////////////////////////////////////////////////                   
                                                                       

    typedef enum
    {
        E_TRUE,
        E_FALSE,
    }enum_e;
    
    typedef struct
    {
      uint16_t foo;
      bool blah;
      uint16_t bar[5];
    }mystruct_t;

    mystruct_t MyStruct1 = 
    {
        .foo = 15,
        .blah = true,
        .bar = {1,2,3}
    };
    mystruct_t const MyStruct2 = 
    {
        .foo = 888,
        .blah = false,
        .bar = {8,8,8}
    };       

    char * argList[] = {"0xFF" , "#A,B,C,D,E#" , "T", //valid --> new values
                        "D"    , "D"           , "D", //default --> back to default values 
                        "15"   , "#2,4,6,8#"   , "T", //valid --> new values 
                        "P"    , "P"           , "P", //preset --> keep last values
                        "TEST" , "ABCDE"       , "Z", //wrong values --> keep last values
                       };

    #define RLV_LOG_DEBUG                     printf
    #define RLV_LOG_APPEND                    printf
    #define RLV_LOG_LINE                      printf
    #define RLV_LOG_ERROR                     printf
    
    #define RLV_BLE_Parameters            MyStruct1
    #define RLV_BLE_DefaultParameters     MyStruct2
    
    #define TEST(TEST_NAME,code) void test_##TEST_NAME (void) { uint8_t argListIndex_= 0; code }          
    
TEST(toto,

    VALID_RLV_SET_PARAM_AUTOTYPE(foo);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(bar);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(blah);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(foo);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(bar);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(blah);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(foo);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(bar);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(blah);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(foo);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(bar);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(blah);printf("\n------\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(foo);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(bar);printf("\n");
    VALID_RLV_SET_PARAM_AUTOTYPE(blah);printf("\n------\n");
)

int main()
{
    printf("----------------command implementation--------------\n");
    test_toto();
    
    return 0;
}

/*
----------------command implementation--------------
uint16_t MyStruct1.foo = 255
uint16_t MyStruct1.bar[] = {0xa,0xb,0xc,0xd,0xe}
_Bool MyStruct1.blah = 1
------
uint16_t MyStruct1.foo = 888
uint16_t MyStruct1.bar[] = {0x8,0x8,0x8,0x0,0x0}
_Bool MyStruct1.blah = 0
------
uint16_t MyStruct1.foo = 15
uint16_t MyStruct1.bar[] = {0x2,0x4,0x6,0x8,0x0}
_Bool MyStruct1.blah = 1
------
uint16_t MyStruct1.foo = 15
uint16_t MyStruct1.bar[] = {0x2,0x4,0x6,0x8,0x0}
_Bool MyStruct1.blah = 1
------
uint16_t MyStruct1.foo = 1
uint16_t MyStruct1.bar[] = {0x2,0x4,0x6,0x8,0x0}
_Bool MyStruct1.blah = 0
------


*/