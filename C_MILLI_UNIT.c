#include <stdio.h>


typedef void (*callback_t)(int a, int b);

typedef struct 
{
    char * name;    
    callback_t callback;
}command_t;


#define COMMAND_LIST(X) \
        X(toto) \
        X(help) \
        //end of list
        
#define CALLBACK_DEC(COMMAND_NAME)  void _##COMMAND_NAME(int a, int b);
COMMAND_LIST(CALLBACK_DEC);
#undef CALLBACK_DEC

#define COMMAND_DEF(COMMAND_NAME)  (command_t){ #COMMAND_NAME, & _##COMMAND_NAME },
static command_t commands[] =
{
  COMMAND_LIST(COMMAND_DEF)
};
#undef COMMAND_DEF



#define INIT_LOG(X) static char messageBuffer[1024]
#define APPEND_LOG(X) do{ char temp_buf[1024]; sprintf(temp_buf, "%s %s",messageBuffer, X); sprintf(messageBuffer,"%s",temp_buf);}while(0)
#define LOG_LINE(...)  do{APPEND_LOG("M0@ : "); char va_args_buf[256]; sprintf(va_args_buf,__VA_ARGS__); APPEND_LOG(va_args_buf); APPEND_LOG("\n");}while(0)
#define PRINT_LOG()  do{ printf ("%s\n",messageBuffer); }while(0)


#define EXPECT_EQ(name,observed,expected) do{if(expected==observed){LOG_LINE(#name" : SUCCESS");}else{LOG_LINE(#name" : FAILURE - expected %d / observed %d",expected,observed);}}while(0)
#define STEP(STEP_NAME,CODE) void _##STEP_NAME(int a, int b) { LOG_LINE(#STEP_NAME" - setup"); CODE LOG_LINE(#STEP_NAME" - teardown\n"); }


INIT_LOG();

int add(int x, int y)
{
    return x+y;
}

STEP(help,
    LOG("this is help");
)

STEP(toto,
    EXPECT_EQ(add_nominal,add(1,1),2);
    EXPECT_EQ(add_degraded,add(1,2),2);
)

int main()
{
    
    commands[0].callback(1,2);
    commands[1].callback(1,2);
    PRINT_LOG();
    return 0;
}
