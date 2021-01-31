#include <execinfo.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define UNW_LOCAL_ONLY
#include <libunwind.h>
#include <cxxabi.h>

#define BT_BUF_SIZE 100

#include "absl/debugging/stacktrace.h"

void absl_backtrace()
{
	void* result[32];

	auto rc = absl::GetStackTrace(result, 32, 0);
	printf("%d frames returned\n", rc);
}

void gnu_backtrace()
{
	int j, nptrs;
	void *buffer[BT_BUF_SIZE];
	char **strings;

	nptrs = backtrace(buffer, BT_BUF_SIZE);
	printf("backtrace() returned %d addresses\n", nptrs);

	/* The call backtrace_symbols_fd(buffer, nptrs, STDOUT_FILENO)
	   would produce similar output to the following: */

	strings = backtrace_symbols(buffer, nptrs);
	if (strings == NULL) {
		perror("backtrace_symbols");
		exit(EXIT_FAILURE);
	}

	for (j = 0; j < nptrs; j++)
		printf("%s\n", strings[j]);

	free(strings);
}

void mybacktrace()
{
	absl_backtrace();
	gnu_backtrace();

	unw_cursor_t cursor;
	unw_context_t context;

	unw_getcontext(&context);
	unw_init_local(&cursor, &context);

	int n=0;
	while ( unw_step(&cursor) ) {
		unw_word_t ip, sp, off;

		unw_get_reg(&cursor, UNW_REG_IP, &ip);
		unw_get_reg(&cursor, UNW_REG_SP, &sp);

		char symbol[256] = {"<unknown>"};
		char *name = symbol;

		if ( !unw_get_proc_name(&cursor, symbol, sizeof(symbol), &off) ) {
			int status;
			if ( (name = abi::__cxa_demangle(symbol, NULL, NULL, &status)) == 0 )
				name = symbol;
		}

		printf("#%-2d 0x%016" PRIxPTR " sp=0x%016" PRIxPTR " %s + 0x%" PRIxPTR "\n",
				++n,
				static_cast<uintptr_t>(ip),
				static_cast<uintptr_t>(sp),
				name,
				static_cast<uintptr_t>(off));

		if ( name != symbol )
			free(name);
	}
}
