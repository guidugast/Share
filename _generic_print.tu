#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>
#include <stdlib.h>

//////////////////////////////////////////////////////////////
///////////////          IMPORTED LIB         ////////////////
//////////////////////////////////////////////////////////////
#define GEN_ID_DEFAULT_ 0
#define GEN_ID_POINTER_ 1
#define GEN_ID_INTEGER_ 2
#define GEN_ID_STRING_ 3
#define GEN_ID_ARRAY_ 4

#define IS_ARRAY_(arg,type)                       _Generic((&arg), \
                                                  type (*)[]: 1, \
                                                  default: 0)
                                                  
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
//////////////////////////////////////////////////////////////
///////////////          TO BE TESTED         ////////////////
//////////////////////////////////////////////////////////////
                                               
#define INTEGER_PRINT_(data,type)    do{ type fdata = *((type*)&data); RLV_LOG_LINE("(integer) of type "#type": %u",fdata); }while(0)
#define STRING_PRINT_(data)          RLV_LOG_LINE("string : %s\n",(char*)&data)
#define ARRAY_PRINT_(data,type)      do{ \
                                        type gen_buf_[sizeof(data)]; \
                                        memcpy(gen_buf_,(type*)&data,sizeof(data)); \
                                        RLV_LOG_APPEND("(array) of type "#type": "); \
                                        for(uint32_t _igen_ = 0; _igen_<sizeof(data)/sizeof(type);_igen_++) \
                                        {  \
                                            RLV_LOG_LINE("%d,",gen_buf_[_igen_]); \
                                        } \
                                    }while(0)

#define GENERIC_PRINT(data,type)    do { switch(_Generic( \
                                        (&data)+0, \
                                        default: GEN_ID_DEFAULT_, \
                                        type *: GEN_ID_INTEGER_, \
                                        type **: GEN_ID_POINTER_, \
                                        char *: GEN_ID_STRING_, \
                                        type (*)[]: GEN_ID_ARRAY_ \
                                        )){ \
                                        case GEN_ID_POINTER_ :  \
                                        case GEN_ID_INTEGER_ : INTEGER_PRINT_(data,type); break; \
                                        case GEN_ID_STRING_ : STRING_PRINT_(data); break; \
                                        case GEN_ID_ARRAY_ : ARRAY_PRINT_(data,type); break; \
                                        default: RLV_LOG_ERROR("Print cannot be applied to the type of "#data". "); break; \
                                        } \
                                    }while(0)
//////////////////////////////////////////////////////////////
///////////////          VALIDATION           ////////////////
//////////////////////////////////////////////////////////////
#define VALID_GEN_PRINT(data,type)   do{ \
                                        printf(#data", ");  \
                                        GENERIC_PRINT(data,type); \
                                        printf("\n"); \
                                     }while(0)
#define RLV_LOG_LINE printf
#define RLV_LOG_DEBUG printf
#define RLV_LOG_ERROR printf
#define RLV_LOG_APPEND printf

int main()
{
    uint32_t foo32         = 15;
    uint32_t foo32_bis     = 15;
    uint32_t not_foo32     = 13;
    uint16_t foo16         = 15;
    uint16_t foo16_bis     = 15;
    uint16_t not_foo16     = 13;
    uint8_t  foo8          = 15;
    uint8_t  foo8_bis      = 15;
    uint8_t  not_foo8      = 13;
    uint32_t bar32[]       = {42,43,44,15};
    uint32_t bar32_bis[]   = {42,43,44,15};
    uint32_t not_bar32[]   = {42,43,0,15};
    uint16_t bar16[]       = {42,43,44,15};
    uint16_t bar16_bis[]   = {42,43,44,15};
    uint16_t not_bar16[]   = {42,43,0,15};
    uint8_t  bar8[]         = {42,43,44,15};
    uint8_t  bar8_bis[]     = {42,43,44,15};
    uint8_t  not_bar8[]     = {42,43,0,15};
    
    
    printf("----------integers-------------\n");
    VALID_GEN_PRINT(foo32         ,uint32_t    );                                                                                              
    VALID_GEN_PRINT(foo32_bis     ,uint32_t    );
    VALID_GEN_PRINT(not_foo32     ,uint32_t    );
    VALID_GEN_PRINT(foo16         ,uint16_t    );                                                                                              
    VALID_GEN_PRINT(foo16_bis     ,uint16_t    );
    VALID_GEN_PRINT(not_foo16     ,uint16_t    );
    VALID_GEN_PRINT(foo8          ,uint8_t     );                                                                                              
    VALID_GEN_PRINT(foo8_bis      ,uint8_t     );
    VALID_GEN_PRINT(not_foo8      ,uint8_t     );
    VALID_GEN_PRINT(foo16         ,uint32_t    );
    VALID_GEN_PRINT(foo8          ,uint32_t    );
    VALID_GEN_PRINT(foo16         ,uint16_t    );
    VALID_GEN_PRINT(foo8          ,uint8_t     );
    printf("----------arrays-------------\n");
    VALID_GEN_PRINT(bar32         ,uint32_t    );                                                                                        
    VALID_GEN_PRINT(bar32_bis     ,uint32_t    );
    VALID_GEN_PRINT(not_bar32     ,uint32_t    );
    VALID_GEN_PRINT(bar16         ,uint16_t    );                                                                                        
    VALID_GEN_PRINT(bar16_bis     ,uint16_t    );
    VALID_GEN_PRINT(not_bar16     ,uint16_t    );
    VALID_GEN_PRINT(bar8          ,uint8_t     );                                                                                        
    VALID_GEN_PRINT(bar8_bis      ,uint8_t     );
    VALID_GEN_PRINT(not_bar8      ,uint8_t     );
    VALID_GEN_PRINT(bar16         ,uint32_t    );
    VALID_GEN_PRINT(bar8          ,uint32_t    );
    VALID_GEN_PRINT(bar16         ,uint16_t    );
    VALID_GEN_PRINT(bar8          ,uint8_t     );
 
    return 0;
}


/*
warnings (only for wrong use of API):
>> no warning                                                                                

output:
----------integers-------------                                                                                                                                                      
foo32, (integer) of type uint32_t: 15                                                                                                                                                
foo32_bis, (integer) of type uint32_t: 15                                                                                                                                            
not_foo32, (integer) of type uint32_t: 13                                                                                                                                            
foo16, (integer) of type uint16_t: 15                                                                                                                                                
foo16_bis, (integer) of type uint16_t: 15                                                                                                                                            
not_foo16, (integer) of type uint16_t: 13                                                                                                                                            
foo8, (integer) of type uint8_t: 15                                                                                                                                                  
foo8_bis, (integer) of type uint8_t: 15                                                                                                                                              
not_foo8, (integer) of type uint8_t: 13                                                                                                                                              
foo16, Print cannot be applied to the type of foo16.                                                                                                                                 
foo8, Print cannot be applied to the type of foo8.                                                                                                                                   
foo16, (integer) of type uint16_t: 15                                                                                                                                                
foo8, (integer) of type uint8_t: 15                                                                                                                                                  
----------arrays-------------                                                                                                                                                        
bar32, (array) of type uint32_t: 42,43,44,15,                                                                                                                                        
bar32_bis, (array) of type uint32_t: 42,43,44,15,                                                                                                                                    
not_bar32, (array) of type uint32_t: 42,43,0,15,                                                                                                                                     
bar16, (array) of type uint16_t: 42,43,44,15,                                                                                                                                        
bar16_bis, (array) of type uint16_t: 42,43,44,15,                                                                                                                                    
not_bar16, (array) of type uint16_t: 42,43,0,15,                                                                                                                                     
bar8, (array) of type uint8_t: 42,43,44,15,                                                                                                                                          
bar8_bis, (array) of type uint8_t: 42,43,44,15,                                                                                                                                      
not_bar8, (array) of type uint8_t: 42,43,0,15,                                                                                                                                       
bar16, Print cannot be applied to the type of bar16.                                                                                                                                 
bar8, Print cannot be applied to the type of bar8.                                                                                                                                   
bar16, (array) of type uint16_t: 42,43,44,15,                                                                                                                                        
bar8, (array) of type uint8_t: 42,43,44,15,                
*/