#ifndef DUPLIDICT_H
#define DUPLIDICT_H

#include <json-c/json.h>
#include <pcre.h>

#define CF (PCRE_UCP|0)
#define EF (PCRE_UCP&0)

#if 0
class DupliDict {
	dict_t m_dict;

public:
	DupliDict();
	DupliDict(const dict_t& x, DupliDict& par);

	value_t& operator[](const key_t& key);
	void _fixup(const dict_t& val);
};

class FSDict : public DupliDict {
	std::string m_path;
public:
	FSDict(const std::string& path);

	value_t& operator[](const key_t& key);
};
#endif

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
