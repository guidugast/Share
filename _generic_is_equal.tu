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
#define IS_ARRAY_(arg,type)                       _Generic((&arg), \
                                                  type (*)[]: 1, \
                                                  default: 0)
                                                  
//////////////////////////////////////////////////////////////
///////////////          TO BE TESTED         ////////////////
//////////////////////////////////////////////////////////////
                                               
#define INTEGER_EQUAL_(expected,observed,type)           (observed == expected)
#define STRING_EQUAL_(expected,observed)                 (strcmp((char *)&observed, (char *)&expected) == 0)
#define ARRAY_EQUAL_(expected,observed,type)             (memcmp((type (*)[])&observed, (type (*)[])&expected, sizeof(expected)) == 0)
#define GENERIC_EXPECT_EQUAL(expected,observed,type)     _Generic( \
                                                         (&observed)+0, \
                                                         default: RLV_LOG_ERROR("Equality cannot be applied to the type of "#observed". ") && 0, \
                                                         char *:  STRING_EQUAL_(expected,observed), \
                                                         type **: INTEGER_EQUAL_(expected,observed,type), \
                                                         type *:  INTEGER_EQUAL_(expected,observed,type), \
                                                         type (*)[]: ARRAY_EQUAL_(expected,observed,type) \
                                                         )
#define GENERIC_EXPECT_TRUE(observed)                   _Generic( \
                                                         (&observed)+0, \
                                                         default: RLV_LOG_ERROR("Equality cannot be applied to the type of "#observed". ") && 0, \
                                                         Bool_ *:  (observed) \
                                                         )

//////////////////////////////////////////////////////////////
///////////////          VALIDATION           ////////////////
//////////////////////////////////////////////////////////////
#define VALID_GEN_EQUAL(expected,observed,type)   do{ \
                                                  printf("Is "#observed"(%s) equal to "#expected" of type "#type"? ",IS_ARRAY_(expected,type)?"array":"integer"); \
                                                  if(GENERIC_EXPECT_EQUAL(expected,observed,type)) {printf("true\n");} else {printf("false\n");}\
                                                  }while(0)
#define VALID_GEN_TRUE(observed)   do{ \
                                                  printf("Is "#observed" equal to true? "); \
                                                  if(observed) {printf("true\n");} else {printf("false\n");}\
                                                  }while(0)
#define RLV_LOG_LINE printf
#define RLV_LOG_DEBUG printf
#define RLV_LOG_ERROR printf

int main()
{
    _Bool    blah          = true;
    _Bool    not_blah       = false;
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
    
    printf("------------expect_true----------------\n");
    VALID_GEN_TRUE(foo32);
    VALID_GEN_TRUE(blah);
    VALID_GEN_TRUE(not_blah);
    printf("----------expect_equal_integers----------\n");
    VALID_GEN_EQUAL(foo32, foo32         ,uint32_t    );   
    VALID_GEN_EQUAL(foo32, foo32         ,uint32_t    );                                                                                              
    VALID_GEN_EQUAL(foo32, foo32_bis     ,uint32_t    );
    VALID_GEN_EQUAL(foo32, not_foo32     ,uint32_t    );
    VALID_GEN_EQUAL(foo16, foo16         ,uint16_t    );                                                                                              
    VALID_GEN_EQUAL(foo16, foo16_bis     ,uint16_t    );
    VALID_GEN_EQUAL(foo16, not_foo16     ,uint16_t    );
    VALID_GEN_EQUAL(foo8,  foo8          ,uint8_t     );                                                                                              
    VALID_GEN_EQUAL(foo8,  foo8_bis      ,uint8_t     );
    VALID_GEN_EQUAL(foo8,  not_foo8      ,uint8_t     );
    VALID_GEN_EQUAL(foo32, foo16         ,uint32_t    );
    VALID_GEN_EQUAL(foo32, foo8          ,uint32_t    );
    VALID_GEN_EQUAL(foo32, foo16         ,uint16_t    );
    VALID_GEN_EQUAL(foo32, foo8          ,uint8_t     );
    printf("---------expect_equal_arrays-------------\n");
    VALID_GEN_EQUAL(bar32, bar32         ,uint32_t    );                                                                                        
    VALID_GEN_EQUAL(bar32, bar32_bis     ,uint32_t    );
    VALID_GEN_EQUAL(bar32, not_bar32     ,uint32_t    );
    VALID_GEN_EQUAL(bar16, bar16         ,uint16_t    );                                                                                        
    VALID_GEN_EQUAL(bar16, bar16_bis     ,uint16_t    );
    VALID_GEN_EQUAL(bar16, not_bar16     ,uint16_t    );
    VALID_GEN_EQUAL(bar8,  bar8          ,uint8_t     );                                                                                        
    VALID_GEN_EQUAL(bar8,  bar8_bis      ,uint8_t     );
    VALID_GEN_EQUAL(bar8,  not_bar8      ,uint8_t     );
    VALID_GEN_EQUAL(bar32, bar16         ,uint32_t    );
    VALID_GEN_EQUAL(bar32, bar8          ,uint32_t    );
    VALID_GEN_EQUAL(bar32, bar16         ,uint16_t    );
    VALID_GEN_EQUAL(bar32, bar8          ,uint8_t     );
 
    return 0;
}


/*
warnings (only for wrong use of API):
main.c:20:60: warning: comparison of distinct pointer types lacks a cast                                                                                                             
main.c:28:60: note: in expansion of macro ‘INTEGER_EQUAL_’                                                                                                                           
main.c:35:58: note: in expansion of macro ‘GENERIC_EQUAL’                                                                                                                            
main.c:88:5: note: in expansion of macro ‘VALID_GEN_EQUAL’                                                                                                                           
main.c:20:60: warning: comparison of distinct pointer types lacks a cast                                                                                                             
main.c:29:60: note: in expansion of macro ‘INTEGER_EQUAL_’                                                                                                                           
main.c:35:58: note: in expansion of macro ‘GENERIC_EQUAL’                                                                                                                            
main.c:88:5: note: in expansion of macro ‘VALID_GEN_EQUAL’                                                                                                                           
main.c:20:60: warning: comparison of distinct pointer types lacks a cast                                                                                                             
main.c:28:60: note: in expansion of macro ‘INTEGER_EQUAL_’                                                                                                                           
main.c:35:58: note: in expansion of macro ‘GENERIC_EQUAL’                                                                                                                            
main.c:89:5: note: in expansion of macro ‘VALID_GEN_EQUAL’                                                                                                                           
main.c:20:60: warning: comparison of distinct pointer types lacks a cast                                                                                                             
main.c:29:60: note: in expansion of macro ‘INTEGER_EQUAL_’                                                                                                                           
main.c:35:58: note: in expansion of macro ‘GENERIC_EQUAL’                                                                                                                            
main.c:89:5: note: in expansion of macro ‘VALID_GEN_EQUAL’                                                                                                                           
main.c:20:60: warning: comparison of distinct pointer types lacks a cast                                                                                                             
main.c:28:60: note: in expansion of macro ‘INTEGER_EQUAL_’                                                                                                                           
main.c:35:58: note: in expansion of macro ‘GENERIC_EQUAL’                                                                                                                            
main.c:90:5: note: in expansion of macro ‘VALID_GEN_EQUAL’                                                                                                                           
main.c:20:60: warning: comparison of distinct pointer types lacks a cast                                                                                                             
main.c:29:60: note: in expansion of macro ‘INTEGER_EQUAL_’                                                                                                                           
main.c:35:58: note: in expansion of macro ‘GENERIC_EQUAL’                                                                                                                            
main.c:90:5: note: in expansion of macro ‘VALID_GEN_EQUAL’                                                                                                                           
main.c:20:60: warning: comparison of distinct pointer types lacks a cast                                                                                                             
main.c:28:60: note: in expansion of macro ‘INTEGER_EQUAL_’                                                                                                                           
main.c:35:58: note: in expansion of macro ‘GENERIC_EQUAL’                                                                                                                            
main.c:91:5: note: in expansion of macro ‘VALID_GEN_EQUAL’                                                                                                                           
main.c:20:60: warning: comparison of distinct pointer types lacks a cast                                                                                                             
main.c:29:60: note: in expansion of macro ‘INTEGER_EQUAL_’                                                                                                                           
main.c:35:58: note: in expansion of macro ‘GENERIC_EQUAL’                                                                                                                            
main.c:91:5: note: in expansion of macro ‘VALID_GEN_EQUAL’                                   

output:
------------expect_true----------------
Is foo32 equal to true? true
Is blah equal to true? true
Is not_blah equal to true? false
----------expect_equal_integers----------
Is foo32(integer) equal to foo32 of type uint32_t? true
Is foo32(integer) equal to foo32 of type uint32_t? true
Is foo32_bis(integer) equal to foo32 of type uint32_t? true
Is not_foo32(integer) equal to foo32 of type uint32_t? false
Is foo16(integer) equal to foo16 of type uint16_t? true
Is foo16_bis(integer) equal to foo16 of type uint16_t? true
Is not_foo16(integer) equal to foo16 of type uint16_t? false
Is foo8(integer) equal to foo8 of type uint8_t? true
Is foo8_bis(integer) equal to foo8 of type uint8_t? true
Is not_foo8(integer) equal to foo8 of type uint8_t? false
Is foo16(integer) equal to foo32 of type uint32_t? Equality cannot be applied to the type of foo16. false
Is foo8(integer) equal to foo32 of type uint32_t? Equality cannot be applied to the type of foo8. false
Is foo16(integer) equal to foo32 of type uint16_t? true
Is foo8(integer) equal to foo32 of type uint8_t? true
---------expect_equal_arrays-------------
Is bar32(array) equal to bar32 of type uint32_t? true
Is bar32_bis(array) equal to bar32 of type uint32_t? true
Is not_bar32(array) equal to bar32 of type uint32_t? false
Is bar16(array) equal to bar16 of type uint16_t? true
Is bar16_bis(array) equal to bar16 of type uint16_t? true
Is not_bar16(array) equal to bar16 of type uint16_t? false
Is bar8(array) equal to bar8 of type uint8_t? true
Is bar8_bis(array) equal to bar8 of type uint8_t? true
Is not_bar8(array) equal to bar8 of type uint8_t? false
Is bar16(array) equal to bar32 of type uint32_t? Equality cannot be applied to the type of bar16. false
Is bar8(array) equal to bar32 of type uint32_t? Equality cannot be applied to the type of bar8. false
Is bar16(integer) equal to bar32 of type uint16_t? false
Is bar8(integer) equal to bar32 of type uint8_t? false

*/
