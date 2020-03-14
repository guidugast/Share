#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>
#include <stdlib.h>

#include "GEN_generic_print.h"    

//////////////////////////////////////////////////////////////
///////////////         VALIDATION TOOLS      ////////////////
//////////////////////////////////////////////////////////////
#define VALID_GEN_EQUAL(expected,observed,type)   do{ \
                                                  RLV_LOG_LINE("Is "#observed"(%s) equal to "#expected" of type "#type"? ",(GET_TYPE_(expected,type) == GEN_ID_ARRAY_)?"array":"integer"); \
                                                  if(GENERIC_EQUAL(expected,observed,type)) {RLV_LOG_DEBUG("true\n");} else {RLV_LOG_DEBUG("false\n");}\
                                                  }while(0)
                                                  
#define VALID_GEN_PRINT(data,type)   do{ \
                                        printf(#data", ");  \
                                        GENERIC_PRINT(data,type); \
                                        printf("\n"); \
                                     }while(0)
//////////////////////////////////////////////////////////////
///////////////           VALIDATED           ////////////////
//////////////////////////////////////////////////////////////
#define GEN_ID_DEFAULT_ 0
#define GEN_ID_POINTER_ 1
#define GEN_ID_INTEGER_ 2
#define GEN_ID_STRING_ 3
#define GEN_ID_ARRAY_ 4

#define IS_ARRAY_(arg,type)                       _Generic((&arg), \
                                                  type (*)[]: 1, \
                                                  default: 0)
                                                  
#define GET_TYPE_(arg,type)                       _Generic((&arg)+0, \
                                                  default: GEN_ID_DEFAULT_, \
                                                  type *: GEN_ID_INTEGER_, \
                                                  type **: GEN_ID_POINTER_, \
                                                  char *: GEN_ID_STRING_, \
                                                  type (*)[]: GEN_ID_ARRAY_ \
                                                  )
#define PRINT_TYPE_(data,type)                    do { switch(GET_TYPE_(data,type)){ \
                                                      case GEN_ID_INTEGER_ : INTEGER_PRINT_(data,type); break; \
                                                      case GEN_ID_STRING_ : STRING_PRINT_(data); break; \
                                                      case GEN_ID_ARRAY_ : ARRAY_PRINT_(data,type); break; \
                                                      case GEN_ID_POINTER_ :  \
                                                      case GEN_ID_DEFAULT_ :  \
                                                      default: DEFAULT_PRINT_(data,type); break; \
                                                      } \
                                                  }while(0)
#define INTEGER_EQUAL_(expected,observed,type)    (observed == expected)
#define STRING_EQUAL_(expected,observed)          (strcmp((char *)&observed, (char *)&expected) == 0)
#define ARRAY_EQUAL_(expected,observed,type)      (memcmp((type (*)[])&observed, (type (*)[])&expected, sizeof(expected)) == 0)
#define GENERIC_EQUAL(expected,observed,type)     _Generic( \
                                                  (&observed)+0, \
                                                  default: RLV_LOG_ERROR("Equality cannot be applied to the type of "#observed". ") && 0, \
                                                  char *:  STRING_EQUAL_(expected,observed), \
                                                  type **: INTEGER_EQUAL_(expected,observed,type), \
                                                  type *:  INTEGER_EQUAL_(expected,observed,type), \
                                                  type (*)[]: ARRAY_EQUAL_(expected,observed,type) \
                                                  )
                                                                                                 
#define DEFAULT_PRINT_(data,type)    do{ type fdata_ = *((type*)&data); RLV_LOG_LINE(#type" "#data" = 0x%08x",fdata_); }while(0)
#define INTEGER_PRINT_(data,type)    do{ type fdata_ = *((type*)&data); RLV_LOG_LINE(#type" "#data" = %u",fdata_); }while(0)
#define STRING_PRINT_(data)          RLV_LOG_LINE("string : %s\n",(char*)&data)
#define ARRAY_PRINT_(data,type)      do{ \
                                        type gen_buf_[sizeof(data)]; \
                                        memcpy(gen_buf_,(type*)&data,sizeof(data)); \
                                        RLV_LOG_APPEND(#type" "#data"[] = "); \
                                        for(uint32_t igen_ = 0; igen_<sizeof(data)/sizeof(type);igen_++) \
                                        {  \
                                            RLV_LOG_LINE("0x%x,",gen_buf_[igen_]); \
                                        } \
                                    }while(0)

#define GENERIC_PRINT(data,type)    do { switch(GET_TYPE_(data,type)){ \
                                        case GEN_ID_INTEGER_ : INTEGER_PRINT_(data,type); break; \
                                        case GEN_ID_STRING_ : STRING_PRINT_(data); break; \
                                        case GEN_ID_ARRAY_ : ARRAY_PRINT_(data,type); break; \
                                        case GEN_ID_POINTER_ :  \
                                        case GEN_ID_DEFAULT_ :  \
                                        default: DEFAULT_PRINT_(data,type); break; \
                                        } \
                                    }while(0)
                                                  
//////////////////////////////////////////////////////////////
///////////////          TO BE TESTED         ////////////////
//////////////////////////////////////////////////////////////
 
#define MAX_ARR_BUF_SIZE 256  

#define SET_PARAM_ARRAY_(argListIndex, type, arrayMaxSize)           do{ \
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
#define SET_PARAM_NOT_ARRAY_(argListIndex, type)                     do{ \
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

                                
#define SET_ARG_PARAM_(arg,argListIndex,type)                        if(GET_TYPE_(arg,type) == GEN_ID_ARRAY_) \
                                                                     { \
                                                                        SET_PARAM_ARRAY_(argListIndex, type, MAX_ARR_BUF_SIZE); \
                                                                        memcpy(&(arg),&paramArrayBuf_,sizeof(type) * paramArrayBufLength_);  \
                                                                     } \
                                                                     else \
                                                                     { \
                                                                        SET_PARAM_NOT_ARRAY_(argListIndex, type); \
                                                                        memcpy(&(arg),&paramBuf_,sizeof(type)); \
                                                                     } 
            
#define RLV_SET_PARAM(type, paramName, argListIndex)                do { \
                                                                           if(!strcmp(argList[argListIndex],"D"))   \
                                                                           {   \
                                                                               memcpy(&RLV_BLE_Parameters.paramName,&RLV_BLE_DefaultParameters.paramName,sizeof(RLV_BLE_DefaultParameters.paramName)); \
                                                                           }   \
                                                                           else if(!strcmp(argList[argListIndex],"P"))   \
                                                                           {   \
                                                                           }   \
                                                                           else   \
                                                                           {   \
                                                                               type paramBuf_ = 0; \
                                                                               type paramArrayBuf_[MAX_ARR_BUF_SIZE] =  {0}; \
                                                                               uint32_t paramArrayBufLength_ = 0;  \
                                                                               SET_ARG_PARAM_(RLV_BLE_Parameters.paramName,argListIndex,type); \
                                                                           } \
                                                                       }while(0)
                                                                       
//////////////////////////////////////////////////////////////
///////////////          VALIDATION           ////////////////
//////////////////////////////////////////////////////////////                   
                                                                       
#define VALID_RLV_SET_PARAM(type, paramName, argListIndex)       do{ \
                                                                 RLV_SET_PARAM(type, paramName, argListIndex); \
                                                                 GENERIC_PRINT(RLV_BLE_Parameters.paramName,type); \
                                                                 }while(0)
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
    
    uint16_t foo = 15;
    uint16_t foo_bis = 15;
    uint16_t not_foo = 999;
    uint32_t foo_wrong_type1 = 15;
    uint8_t foo_wrong_type2 = 15;
    
    uint16_t bar[] = {1,2,3};
    uint16_t not_bar[] = {1,2,4};
    uint32_t bar_wrong_type1[] = {1,2,3};
    uint8_t bar_wrong_type2[] = {1,2,3};
    uint16_t bar_wrong_size[] = {1,2,3,4};
    
    char * argList[] = {"D","P","","15","0xFFFFFFFFFFFFFFF","T","F","0xFF","#2,4,6,8#","##","#A,B,C,D,E#","1,2,3"};
   
    #define RLV_LOG_DEBUG                     printf
    #define RLV_LOG_APPEND                    printf
    #define RLV_LOG_LINE                      printf
    #define RLV_LOG_ERROR                     printf
    
    
    #define RLV_BLE_Parameters            MyStruct1
    #define RLV_BLE_DefaultParameters     MyStruct2
    
int main()
{
    
    
    
    printf("---------------------equal interger-------------------\n");
    VALID_GEN_EQUAL(foo,     foo,                 uint16_t);
    VALID_GEN_EQUAL(foo,     foo_bis,             uint16_t);
    VALID_GEN_EQUAL(foo,     not_foo,             uint16_t);
    VALID_GEN_EQUAL(foo,     MyStruct1.foo,       uint16_t);
    printf("---------------------equal array-------------------\n");
    VALID_GEN_EQUAL(bar,     bar,                 uint16_t);
    VALID_GEN_EQUAL(bar,     MyStruct1.bar,       uint16_t);
    VALID_GEN_EQUAL(bar,     not_bar,             uint16_t);
    
  
    printf("---------------------uint16_t-------------------\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  1);  printf(" -- expect 15\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  0);  printf(" -- expect 888\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  1);  printf(" -- expect 888\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  2);  printf(" -- expect 0\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  3);  printf(" -- expect 15\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  4);  printf(" -- expect 65535\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  5);  printf(" -- expect 1\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  6);  printf(" -- expect 0\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  7);  printf(" -- expect 255\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  8);  printf(" -- expect UB\n");
    VALID_RLV_SET_PARAM(uint16_t, foo,  9);  printf(" -- expect UB\n");
    VALID_RLV_SET_PARAM(uint16_t, foo, 10);  printf(" -- expect UB\n");
    VALID_RLV_SET_PARAM(uint16_t, foo, 11);  printf(" -- expect UB\n");
    
    printf("----------------------uint32_t------------------\n");
    VALID_RLV_SET_PARAM(uint32_t, foo,  4);  printf(" -- expect UB\n");
    
    printf("--------------------uint8_t--------------------\n");
    VALID_RLV_SET_PARAM(uint8_t,  foo,  4);  printf(" -- expect UB\n");
    
    typedef enum
    {
        E_TRUE,
        E_FALSE,
    }enum_e;
    
    printf("--------------------enum_e--------------------\n");
    VALID_RLV_SET_PARAM(enum_e, foo, 5);  printf(" -- expect T(1)\n");
    VALID_RLV_SET_PARAM(enum_e, foo, 6);  printf(" -- expect F(0)\n");
    
    

    printf("---------------------ARRAY-------------------\n");
    VALID_RLV_SET_PARAM(uint16_t, bar,  1);  printf(" -- expect {1,2,3,}\n");
    VALID_RLV_SET_PARAM(uint16_t, bar,  0);  printf(" -- expect {8,8,8,}\n");
    VALID_RLV_SET_PARAM(uint16_t, bar,  1);  printf(" -- expect {8,8,8,}\n");
    VALID_RLV_SET_PARAM(uint16_t, bar,  2);  printf(" -- expect {8,8,8,}\n");
    VALID_RLV_SET_PARAM(uint16_t, bar,  3);  printf(" -- expect {8,8,8,}\n");  
    VALID_RLV_SET_PARAM(uint16_t, bar,  4);  printf(" -- expect {8,8,8,}\n");
    VALID_RLV_SET_PARAM(uint16_t, bar,  5);  printf(" -- expect {8,8,8,}\n");
    VALID_RLV_SET_PARAM(uint16_t, bar,  6);  printf(" -- expect {8,8,8,}\n");
    VALID_RLV_SET_PARAM(uint16_t, bar,  7);  printf(" -- expect {8,8,8,}\n");
    VALID_RLV_SET_PARAM(uint16_t, bar,  8);  printf(" -- expect {2,4,6,8,}\n");
    VALID_RLV_SET_PARAM(uint16_t, bar,  9);  printf(" -- expect {2,4,6,8,} or UB\n");
    VALID_RLV_SET_PARAM(uint16_t, bar, 10);  printf(" -- expect {A,B,C,D,E,}\n");
    VALID_RLV_SET_PARAM(uint16_t, bar, 11) ; printf(" -- expect {A,B,C,D,E,}\n");
    

    printf("---------------------uint32_t-------------------\n");
    VALID_RLV_SET_PARAM(uint32_t, bar, 8);  printf(" -- expect UB\n");
    
    
    printf("---------------------uint8_t-------------------\n");
    VALID_RLV_SET_PARAM(uint8_t, bar, 8);  printf(" -- expect UB\n");

    return 0;
}

/*

warnings (only for wrong use of API):
>> no warning                                                                                

output:
---------------------equal interger-------------------
Is foo(integer) equal to foo of type uint16_t? true
Is foo_bis(integer) equal to foo of type uint16_t? true
Is not_foo(integer) equal to foo of type uint16_t? false
Is MyStruct1.foo(integer) equal to foo of type uint16_t? true
---------------------equal array-------------------
Is bar(array) equal to bar of type uint16_t? true
Is MyStruct1.bar(array) equal to bar of type uint16_t? true
Is not_bar(array) equal to bar of type uint16_t? false
---------------------uint16_t-------------------
uint16_t MyStruct1.foo = 15 -- expect 15
uint16_t MyStruct1.foo = 888 -- expect 888
uint16_t MyStruct1.foo = 888 -- expect 888
uint16_t MyStruct1.foo = 0 -- expect 0
uint16_t MyStruct1.foo = 15 -- expect 15
uint16_t MyStruct1.foo = 65535 -- expect 65535
uint16_t MyStruct1.foo = 1 -- expect 1
uint16_t MyStruct1.foo = 0 -- expect 0
uint16_t MyStruct1.foo = 255 -- expect 255
uint16_t MyStruct1.foo = 0 -- expect UB
uint16_t MyStruct1.foo = 0 -- expect UB
uint16_t MyStruct1.foo = 0 -- expect UB
uint16_t MyStruct1.foo = 1 -- expect UB
----------------------uint32_t------------------
uint32_t MyStruct1.foo = 0xffffffff -- expect UB
--------------------uint8_t--------------------
uint8_t MyStruct1.foo = 0x000000ff -- expect UB
--------------------enum_e--------------------
enum_e MyStruct1.foo = 0x00000001 -- expect T(1)
enum_e MyStruct1.foo = 0x00000000 -- expect F(0)
---------------------ARRAY-------------------
uint16_t MyStruct1.bar[] = 0x1,0x2,0x3,0x0,0x0, -- expect {1,2,3,}
uint16_t MyStruct1.bar[] = 0x8,0x8,0x8,0x0,0x0, -- expect {8,8,8,}
uint16_t MyStruct1.bar[] = 0x8,0x8,0x8,0x0,0x0, -- expect {8,8,8,}
uint16_t MyStruct1.bar[] = 0x8,0x8,0x8,0x0,0x0, -- expect {8,8,8,}
uint16_t MyStruct1.bar[] = 0x8,0x8,0x8,0x0,0x0, -- expect {8,8,8,}
uint16_t MyStruct1.bar[] = 0x8,0x8,0x8,0x0,0x0, -- expect {8,8,8,}
uint16_t MyStruct1.bar[] = 0x8,0x8,0x8,0x0,0x0, -- expect {8,8,8,}
uint16_t MyStruct1.bar[] = 0x8,0x8,0x8,0x0,0x0, -- expect {8,8,8,}
uint16_t MyStruct1.bar[] = 0x8,0x8,0x8,0x0,0x0, -- expect {8,8,8,}
uint16_t MyStruct1.bar[] = 0x2,0x4,0x6,0x8,0x0, -- expect {2,4,6,8,}
uint16_t MyStruct1.bar[] = 0x2,0x4,0x6,0x8,0x0, -- expect {2,4,6,8,} or UB
uint16_t MyStruct1.bar[] = 0xa,0xb,0xc,0xd,0xe, -- expect {A,B,C,D,E,}
uint16_t MyStruct1.bar[] = 0xa,0xb,0xc,0xd,0xe, -- expect {A,B,C,D,E,}
---------------------uint32_t-------------------
uint32_t MyStruct1.bar = 0x00000000 -- expect UB
---------------------uint8_t-------------------
uint8_t MyStruct1.bar = 0x00000000 -- expect UB



*/