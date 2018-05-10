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
