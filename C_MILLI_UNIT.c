#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/*
TODO:

- use memcpy to speed up the code exec ?



*/

#define LOG_SIZE                1024
#define LOG_LINE_SIZE           64
#define LOG_LINE_BEGIN_WITH     "M0@ : "

#define STEP_LIST(X) \
        X(toto) \
        //end of list
        
#define COMMAND_LIST(X) \
        X(toto_all) \
        X(help) \
        //end of list


typedef void (*callback_t)(int a, int b);

typedef struct 
{
    char * name;    
    callback_t callback;
}command_t;
        
#define CALLBACK_DEC(COMMAND_NAME)  void _##COMMAND_NAME(int a, int b);
COMMAND_LIST(CALLBACK_DEC);
#undef CALLBACK_DEC

#define COMMAND_DEF(COMMAND_NAME)  (command_t){ #COMMAND_NAME, & _##COMMAND_NAME },
static command_t commands[] =
{
  COMMAND_LIST(COMMAND_DEF)
};
#undef COMMAND_DEF



static inline uint16_t GetCommand(char * COMMAND_TYPED)
{ 
    bool commandFound = false;
    uint16_t commandIndex;
    for(commandIndex = 0; commandIndex < sizeof(commands)/sizeof(command_t) ; commandIndex++)
    { 
        if(!strcmp(COMMAND_TYPED,commands[commandIndex].name))
        {
            commandFound=true;
            break;
        }
    }
    return commandIndex;
}

#define RUN_CMD(COMMAND_TYPED)              commands[GetCommand(COMMAND_TYPED)].callback(1,2)
#define RUN_STEP(STEP_NAME)                 do{ LOG_LINE(#STEP_NAME" - setup"); _##STEP_NAME(1,2); LOG_LINE(#STEP_NAME" - teardown"); APPEND_LOG(LOG_LINE_BEGIN_WITH); APPEND_LOG("\n");}while(0)      

#define INIT_LOG()                          static char messageBuffer[LOG_SIZE]
#define APPEND_LOG(MSG)                     do{ char temp_buf[LOG_SIZE]; sprintf(temp_buf, "%s %s",messageBuffer, MSG); sprintf(messageBuffer,"%s",temp_buf);}while(0)
#define LOG_LINE(...)                       do{APPEND_LOG(LOG_LINE_BEGIN_WITH); char va_args_buf[LOG_LINE_SIZE]; sprintf(va_args_buf,__VA_ARGS__); APPEND_LOG(va_args_buf);  APPEND_LOG("\n");}while(0)
#define PRINT_LOG()                         do{ printf ("%s\n",messageBuffer); }while(0)


#define EXPECT_EQ(name,observed,expected)   do{if(expected==observed){LOG_LINE("- "#name" : OK");}else{LOG_LINE("- "#name" : FAILS - expected %d / observed %d",expected,observed);}}while(0)
#define STEP(STEP_NAME,CODE)                void _##STEP_NAME(int A, int B) { CODE }
#define COMMAND(COMMAND_NAME,CODE)          void _##COMMAND_NAME(int A, int B) { LOG_LINE("------------- Running command: "#COMMAND_NAME" -------------"); CODE LOG_LINE("------------- End of command: "#COMMAND_NAME" -------------"); LOG_LINE(" "); }


INIT_LOG();

short add(int x, int y)
{
    return x+y;
}

COMMAND(help,
    LOG_LINE("this is help");
)

STEP(toto_nominal,
    int a = 1;
    int b = 1;
    int ret = add(1,1);
    EXPECT_EQ(add_pass,ret,2);
    //EXPECT_EQ(add_fails,ret,3);
)

STEP(toto_degraded,
    EXPECT_EQ(add_degraded,add(1024,1024),2048);
)


COMMAND(toto_all,
    RUN_STEP(toto_nominal);
    RUN_STEP(toto_degraded);
)


int main()
{
    RUN_CMD("help");
    RUN_CMD("toto_all");
    PRINT_LOG();
    return 0;
}
