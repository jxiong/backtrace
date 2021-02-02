#include <execinfo.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <spdlog/spdlog.h>

void
myfunc3(void)
{
	spdlog::info("Malloc in lib: \n");
	free(malloc(1024));
}

static void   /* "static" means don't export this symbol... */
myfunc2(void)
{
    myfunc3();
}

void
myfunc(int ncalls)
{
    if (ncalls > 1)
        myfunc(ncalls - 1);
    else
        myfunc2();
}
