#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>
#include <stdlib.h>

#define MAX_SIZE 256
#define MAX_DISPLAYABLE_SIZE 30

typedef enum
{
    ENUM1_A=0,
    ENUM1_B,
}someEnum1_e;

#define def_x_st(type) typedef union \
{ \
    type value;\
}type##_t;
def_x_st(someEnum1_e);

#define def_array_x_t(type) typedef struct \
{ \
    type content[MAX_SIZE]; \
    uint16_t length; \
}array_##type
def_array_x_t(uint32_t);
def_array_x_t(uint16_t);
def_array_x_t(uint8_t);


#define def_print_x_t(int_type) static inline void print_##int_type(int_type val) \
{ \
    printf(#int_type" val = %u;\n",(int_type)val); \
} 
def_print_x_t(uint32_t);
def_print_x_t(uint16_t);
def_print_x_t(uint8_t);

#define def_print_array_x_t(type) static inline void print_array_##type(array_##type val) \
{ \
    printf(#type" val[%u] = {",val.length); \
    for(uint16_t i = 0; (i < MAX_DISPLAYABLE_SIZE)&&(i < val.length); i++) \
    { \
        printf("%u",val.content[i]); \
        if((i +1 < MAX_DISPLAYABLE_SIZE) && (i + 1 < val.length)) {printf(",");} \
    } \
    printf("};\n"); \
} 
def_print_array_x_t(uint32_t);
def_print_array_x_t(uint16_t);
def_print_array_x_t(uint8_t);

static inline void print_someEnum1_e_t(someEnum1_e_t val)
{
    printf("someEnum1_e_t val = ");
    switch(val.value)
    {
        case ENUM1_A: printf("ENUM1_A"); break;
        case ENUM1_B: printf("ENUM1_B"); break;
        default: printf("unkown value for someEnum1_e"); break;
    }
    printf(";\n");
}

#define  DO_(function, type, data) function##type((type)*((type*)&data))
           
#define  DO_AUTO_(function,data)   _Generic((&data)+0,  \
                                    uint8_t* : DO_(function, uint8_t, data), \
                                    uint16_t* : DO_(function, uint16_t, data), \
                                    uint32_t* : DO_(function, uint32_t, data), \
                                    array_uint32_t* : DO_(function, array_uint32_t, data), \
                                    array_uint16_t* : DO_(function, array_uint16_t, data), \
                                    array_uint8_t * : DO_(function, array_uint8_t, data), \
                                    someEnum1_e_t * : DO_(function, someEnum1_e_t, data) \
                                    )
                                                         
#define  PRINT_(data) DO_AUTO_(print_,data)
           
int main (void)
{
    uint32_t            foo32 = 32;
    uint16_t            foo16 = 16;
    uint8_t             foo8 = 8;
    array_uint32_t      bar32 = {{32,33,34},3};
    array_uint16_t      bar16 = {{16,17,18},3};
    array_uint8_t       bar8 =  {{8,9,10},3};
    someEnum1_e_t       blah = {ENUM1_A};

    PRINT_( foo32    );
    PRINT_( foo16    );
    PRINT_( foo8     );
    PRINT_( bar32    );
    PRINT_( bar16    );
    PRINT_( bar8     );
    PRINT_( blah     );
}