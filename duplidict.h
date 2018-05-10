/* duplidict.h
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

#ifndef DUPLIDICT_H
#define DUPLIDICT_H

#include <json-c/json.h>
#include <pcre.h>

#define CF (PCRE_UCP) /* default pcre_compile flags */
#define EF (0) /* default pcre_exec flags */

#define json_object_object_add_ex(o, k, v, x) json_object_object_add(o, k, v)

#ifdef __cplusplus
extern "C" {
#endif

json_object *fsdict_object_new(const char *path);
json_bool fsdict_object_get_ex(struct json_object *obj, const char *key, json_object **value);

#ifdef __cplusplus
}
#endif

#endif /* DUPLIDICT_H */
