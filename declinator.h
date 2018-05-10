/* declinator.h
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

#ifndef DECLINATOR_H
#define DECLINATOR_H

#include <json-c/json.h>

#define FIXME fprintf(stderr, "FIXME %s:%d!\n", __FILE__, __LINE__)

enum gender {
	gender_auto = 'a',
	gender_f = 'f',
	gender_m = 'm'
};

#ifdef __cplusplus
extern "C" {
#endif

extern void declinator_init();
extern json_object *declmod(const char *name, enum gender gen);
extern json_object *declmod_locale(const char *name, enum gender gen,
                                   const char *locale);

#ifdef __cplusplus
}
#endif

#endif /* DECLINATOR_H */
