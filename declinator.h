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
