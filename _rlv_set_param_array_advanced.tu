#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#define RLV_APPEND_LOG printf
#define RLV_LOG_ERROR printf
#define RLV_LOG_LINE printf


//SIZES
#define RLV_MAX_ARR_BUF_SIZE                                1000
#define RLV_MAX_DISPLAYABLE_ARR_SIZE                        30//{"0x1234,0xFFFF,0xFF,0,0x1000,..."}
#define RLV_MAX_INPUTABLE_ARRAY_LENGHT_CHAR_SIZE            5//["12345"]{content[0],...}
#define RLV_MAX_INPUTABLE_ARRAY_CHAR_SIZE                   800//[length]{"0x1234,0xFFFF,0xFF,0,0x1000,..."}
#define RLV_MAX_NUMBER_OF_STORED_DATA                       10

////////////////////////////////////////////////////////////////////////////////
//////////////////                  Macros                    //////////////////
////////////////////////////////////////////////////////////////////////////////
#define DEF_enum_val(enum_val) \
enum_val,
#define DEF_x_e(enum_type) \
typedef enum \
{ \
  LIST_##enum_type(DEF_enum_val) \
}enum_type

#define DEF_x_st(enum_type) \
typedef union \
{ \
    enum_type value;\
}enum_type##_t

#define DEF_array_x_t(type) \
typedef struct \
{ \
    type content[RLV_MAX_ARR_BUF_SIZE]; \
    uint16_t length; \
}array_##type

////////////////////////////////////////////////////////////////////////////////
//////////////////                  Types                     //////////////////
////////////////////////////////////////////////////////////////////////////////
DEF_array_x_t(uint32_t);
DEF_array_x_t(uint16_t);
DEF_array_x_t(uint8_t);


static inline uint16_t strpos(char *haystack, char *needle)
{
   char *p = strstr(haystack, needle);
   return (p ? p - haystack : (uint16_t)-1);
}

static inline bool IsComposedOfAtLeastOneOfCharInList(char *str, char* list)
{
    return (str[strcspn(str,list)] != '\0');
}

static inline bool DoesContainOnlySomeOrAllCharInList(char *str, char* list)
{
    return (str[strspn(str,list)] == '\0');
}

static inline bool DoesContainAllCharInList(char *str, char* list)
{
    bool retVal = true;
    for(uint8_t index = 0; index < strlen(list); index++)
    {
        retVal = retVal && strchr(str,list[index]);
        if (!retVal) break;
    }
    return retVal;
}

bool DoesContainString(char *str, char* strInStr)
{
    return (strstr(str,strInStr) != NULL);
}

#define add_from_arg_arr_x_(param,gen_current_cli_arg_,type)  \
do{ \
    bool isInError = true; \
    bool isFilled = false; \
    type bufArray[RLV_MAX_ARR_BUF_SIZE] = {0}; \
    printf("s:'%s'",gen_current_cli_arg_); \
    if(DoesContainOnlySomeOrAllCharInList(gen_current_cli_arg_, "[]{}x0123456789abcdefABCDEF*,") && \
    DoesContainAllCharInList(gen_current_cli_arg_, "[]{}") && \
    DoesContainString(gen_current_cli_arg_, "]{") && \
    (gen_current_cli_arg_[0]=='[') && \
    (gen_current_cli_arg_[strlen(gen_current_cli_arg_)-1] == '}'))  \
    {  \
        printf("test"); \
        char clen[RLV_MAX_INPUTABLE_ARRAY_LENGHT_CHAR_SIZE]; \
        uint16_t ulen=0; \
        char * gen_array_arg; \
        char current_arg[RLV_MAX_INPUTABLE_ARRAY_CHAR_SIZE] ; \
        char * current_arg_ptr = current_arg; \
        strcpy(current_arg_ptr,gen_current_cli_arg_); \
        gen_array_arg = strtok(strpbrk (current_arg_ptr, "{")+1, ","); \
        uint32_t ulen_pos =(uint32_t)(strpos(current_arg_ptr, "]")-1); \
        bool isAutoFilled = (ulen_pos == 0); \
        strxfrm(clen, (char*)(current_arg_ptr+1), (uint32_t)((size_t)current_arg_ptr+1U+(size_t)ulen_pos)); \
        do \
        {  \
            if((gen_array_arg[0]=='0') && (gen_array_arg[1]=='x')) \
            { \
                if(DoesContainOnlySomeOrAllCharInList(gen_array_arg, "x0123456789abcdefABCDEF}*")) \
                { \
                    if(DoesContainAllCharInList(gen_array_arg, "0x}*") && \
                        (ulen == 0) && \
                        (isAutoFilled == false)) \
                    { \
                        memset(bufArray, (type)strtol (gen_array_arg, NULL, 16), strtol (clen, NULL, 10)); \
                        isInError = false; \
                    } \
                    else if(DoesContainAllCharInList(gen_array_arg, "*") == false) \
                    { \
                        bufArray[ulen++] = (type)strtol (gen_array_arg, NULL, 16); \
                        isInError = !DoesContainAllCharInList(gen_array_arg, "x0}"); \
                    } \
                    else \
                    { \
                        isInError = true; \
                    } \
                } \
                else \
                { \
                    isInError = true; \
                } \
            } \
            else \
            { \
                isInError = true; \
            } \
            gen_array_arg = strtok(NULL, ","); \
        }while(gen_array_arg != NULL); \
        if (false == isInError) \
        { \
            param->length = isAutoFilled ? ulen : strtol (clen, NULL, 10); \
            memcpy(param->content, bufArray, RLV_MAX_ARR_BUF_SIZE-1); \
        } \
        else \
        { \
            RLV_LOG_ERROR("wrong format for array element (%u), use hexa, for instance '[]{0xA,0x10,0x0,0xA1FC}'\n",ulen-1); \
            RLV_LOG_ERROR("or wrong format for auto filled array, use this '[3]{0xAA*}' to get '[3]{0xAA,0xAA,0xAA}'\n"); \
        } \
    } \
    else \
    { \
        RLV_LOG_ERROR("wrong format for array, use for instance '[8]{0xA,0x0,0xA1FC}', '[0]{}', or '[]{0xFF}'\n"); \
    } \
}while(0)    

    
#define DEF_add_from_arg_arr_x_(type) \
static inline void add_from_arg_array_##type(array_##type* param, char* gen_current_cli_arg_) \
{ \
    add_from_arg_arr_x_(param,gen_current_cli_arg_,type); \
} 
DEF_add_from_arg_arr_x_(uint8_t)
DEF_add_from_arg_arr_x_(uint16_t)
DEF_add_from_arg_arr_x_(uint32_t)

#define DEF_print_array_x_t(type) \
static inline void print_array_##type(array_##type* val, char * dummy) \
{ \
    (void)dummy; \
    RLV_APPEND_LOG("[%u] = {",val->length); \
    for(uint16_t i = 0; (i < RLV_MAX_DISPLAYABLE_ARR_SIZE)&&(i < val->length); i++) \
    { \
        RLV_APPEND_LOG(dummy,val->content[i],val->content[i]); \
        if((i +1 < RLV_MAX_DISPLAYABLE_ARR_SIZE) && (i + 1 < val->length)) {RLV_APPEND_LOG(",");} \
    } \
    RLV_APPEND_LOG("}\n"); \
} 
DEF_print_array_x_t(uint32_t)
DEF_print_array_x_t(uint16_t)
DEF_print_array_x_t(uint8_t)


#define DEF_TEST_array_x_t(type) \
static inline void TEST_##type(array_##type* val, char * args) \
{ \
    add_from_arg_array_##type(val,args); \
    print_array_##type(val,"0x%02x"); \
} 
DEF_TEST_array_x_t(uint32_t)
DEF_TEST_array_x_t(uint16_t)
DEF_TEST_array_x_t(uint8_t)

int main()
{
    array_uint8_t myParam = {0};
    TEST_uint8_t(&myParam,"[]0x1,0x2,0x3}");             //E : wrong format                   O: OK V
    TEST_uint8_t(&myParam,"[0x1,]{0x2,0x3}");            //E : wrong format                   O: KO 
    TEST_uint8_t(&myParam,"[]0x1,{0x2,0x3}");            //E : wrong format                   O: OK V 
    TEST_uint8_t(&myParam,"[]{0x1,0x2,0x3");             //E : wrong format                   O: OK V
    TEST_uint8_t(&myParam,"[]{0x1,0x2,0x3}");            //E : [3]{0x01,0x02,0x03}            O: OK V
    TEST_uint8_t(&myParam,"[2]{0x1,0x2,0x3,0x4}");       //E : [2]{0x01,0x02}                 O: OK V
    TEST_uint8_t(&myParam,"[4]{0x1,0x2}");               //E : [4]{0x01,0x02,0x00,0x00}       O: OK V
    TEST_uint8_t(&myParam,"[]{0xFF,0xFF,0xFF,0xFF}");    //E : [2]{0xFF,0xFF,0xFF,0xFF}       O: OK V
    TEST_uint8_t(&myParam,"[]{0x1,0x2,0x3,Z}");          //E : wrong format + OxFF*4          O: OK V
    TEST_uint8_t(&myParam,"[4]{0x1,0x2}");               //E : [4]{0x01,0x02,0x00,0x00}       O: OK
    TEST_uint8_t(&myParam,"[]{0x1}");                    //E : [1]{0x01}                      O: OK
    TEST_uint8_t(&myParam,"[]{0x1*}");                   //E : wrong format                   O: OK
    TEST_uint8_t(&myParam,"[3]{*0x1}");                  //E : wrong format                   O: OK
    TEST_uint8_t(&myParam,"[3]{0x1*}");                  //E : [3]{0x01,0x01,0x01}            O: OK



    

    return 0;
}
