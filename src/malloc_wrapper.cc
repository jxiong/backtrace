#include <stdlib.h> /* added */
#include <stdio.h>
#include <execinfo.h>
#include <unistd.h>

#include <spdlog/spdlog.h>

#define UNW_LOCAL_ONLY
#include <libunwind.h>
#include <cxxabi.h>

#include "absl/debugging/stacktrace.h"

extern "C" {
extern void *__real_malloc (size_t);
extern void __real_free(void *);
void *__wrap_malloc(size_t size);
void __wrap_free(void *ptr);
}

constexpr size_t BT_BUFSZ = 100;

void absl_backtrace()
{
	void* result[BT_BUFSZ];

	/* will add backtrace soon */
	auto rc = absl::GetStackTrace(result, BT_BUFSZ, 0);
	spdlog::info("======== absl: {} frames returned\n", rc);
}

void gnu_backtrace()
{
	int j, nptrs;
	void *buffer[BT_BUFSZ];
	char **strings;

	spdlog::info("======== gnu: backtrace() returned {} addresses\n", nptrs);

	nptrs = backtrace(buffer, BT_BUFSZ);

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

	spdlog::info("======== unwind: backtrace()\n");

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

		if ( name != symbol ) {
			extern void __real_free(void *);
			__real_free(name);
		}
	}
}

/* This function wraps the real malloc */
void *__wrap_malloc(size_t size)
{
	void *lptr = __real_malloc(size);

	spdlog::info("Malloc: {} bytes @{:p}\n", size, lptr);
	mybacktrace();

	return lptr;
}

void __wrap_free(void *ptr)
{
	spdlog::info("Free: @{:p} is freed\n", ptr);
	__real_free(ptr);
}
