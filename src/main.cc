#include <execinfo.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

extern void myfunc(int);

int
main(int argc, char *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "%s num-calls\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    printf("malloc in main\n");
    free(malloc(4096));

    myfunc(atoi(argv[1]));
    exit(EXIT_SUCCESS);
}
