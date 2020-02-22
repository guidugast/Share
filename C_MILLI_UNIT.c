#include <stdio.h>

static char messageBuffer[1024];


#define PRINT_LOG()  do{ printf ("%s",messageBuffer); }while(0)
#define LOG(...)  do{ sprintf(messageBuffer,"%s M0@ : ",messageBuffer); sprintf(messageBuffer,"M0@ : "__VA_ARGS__); }while(0)

#define EXPECT_EQ(name,expected,observed) do{(expected==observed)?LOG("%s : SUCCESS\n",name):LOG("%s : FAILURE - expected %d / observed %d\n",name,expected,observed);}while(0)
#define STEP(X,Y) void X(int a, int b) { LOG(#X" - setup\n"); Y LOG(#X" - teardown\n"); PRINT_LOG();}

int add(int x, int y)
{
    return x+y;
}

/*STEP(toto,
    EXPECT_EQ("add - nominal",add(1,1),2);
)*/

int main()
{

    LOG("test %d\n",1);
    PRINT_LOG();
    //toto(1,2);
    return 0;
}
