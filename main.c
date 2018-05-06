#include <stdio.h>
#include <string.h>
#include "declinator.h"

int main(int argc, char *argv[]) {
	enum gender gen = gender_auto;
	if (argc == 4 && strcmp(argv[1], "-g") == 0) {
		gen = (enum gender)argv[2][0];
		argc = 2;
		argv[1] = argv[3];
	}
	if (argc != 2) {
		fprintf(stderr, "Usage: %s [-g {f[emale],m[ale],a[uto]}] '<name>'\n", argv[0]);
		return 1;
	}
	declinator_init();
	json_object_to_file_ext("/dev/stdout", declmod(argv[1], gen), JSON_C_TO_STRING_PRETTY);
	puts("");
	return 0;
}
