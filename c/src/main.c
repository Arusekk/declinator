/* main.c
 * Copyright (C) 2018 Arusekk
 * This file is part of Declinator.
 *
 * Declinator is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Declinator is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Declinator.  If not, see <http://www.gnu.org/licenses/>.
 */

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
