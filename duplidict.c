#include "duplidict.h"
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <pcre.h>
#include <assert.h>

#define IFDEBUG(x) x

#ifdef __WIN32
#define SEP "\\"
#else
#define SEP "/"
#endif

struct parpar {
	json_object *j;
	const struct parpar *par;
};

static void duplidict_fixx(struct json_object *dest, struct json_object *src);
static void duplidict_fixup(struct json_object *obj, const struct parpar *par);


void duplidict_object_init(struct json_object *obj, const struct parpar *par) {
	json_object *included;
	if (json_object_object_get_ex(obj, "#include", &included)) {
		json_object_get(included);
		json_object_object_del(obj, "#include");

		const char *key = json_object_get_string(included);

		while (par) {
			json_object *the_included;
			if (fsdict_object_get_ex(par->j, key, &the_included)) {
				duplidict_fixx(obj, the_included);
				break;
			}
			par = par -> par;
		}
		if (!par)
			fprintf(stderr, "#inclusion failed: %p[%s]", obj, key);

		json_object_put(included);
	}
	struct parpar par2 = {
		.j = obj,
		.par = par
	};
	json_object_object_foreach (obj, key, val) {
		(void)key;
		duplidict_fixup(val, &par2);
	}
}


void duplidict_fixup(struct json_object *obj, const struct parpar *par) {
	switch (json_object_get_type(obj)) {
		case json_type_object:
			duplidict_object_init(obj, par);
			break;
		case json_type_array:
			{
				int len = json_object_array_length(obj);
				for (int i=0; i<len; i++)
					duplidict_fixup(json_object_array_get_idx(obj, i), par);
			}
		default:
			break;
	}
}


void duplidict_fixx(struct json_object *dest, struct json_object *src) {
	json_object_object_foreach (src, key, val) {
		json_object *targ;
		if (!json_object_object_get_ex(dest, key, &targ)) {
			json_object_object_add(dest, key, json_object_get(val));
			continue;
		}
				if (json_object_is_type(targ, json_type_object))
					duplidict_fixx(targ, val);
	}
}


json_object *fsdict_object_new(const char *path) {
	json_object *ret = json_object_new_object();
	json_object_object_add_ex(ret, "path", json_object_new_string(path),
	                          JSON_C_OBJECT_ADD_KEY_IS_NEW
	                        | JSON_C_OBJECT_KEY_IS_CONSTANT);
	return ret;
}


json_object *json_object_from_fp(FILE *fp) {
		char buffer[4096];
		json_object *jobj = NULL;
		enum json_tokener_error jerr;
		struct json_tokener *tok = json_tokener_new();
		do {
			int stringlen = fread(buffer, 1, 4096, fp);
			if (!stringlen)
				break;
			jobj = json_tokener_parse_ex(tok, buffer, stringlen);
		} while ((jerr = json_tokener_get_error(tok)) == json_tokener_continue);

		if (jerr != json_tokener_success) {
			fprintf(stderr, "Error in %d: %s\n", fileno(fp), json_tokener_error_desc(jerr));
			json_tokener_free(tok);
			return (json_object*)-1;
		}
		json_tokener_free(tok);
		return jobj;
}


json_object *pcre_compile_fp(FILE *fp) {
	struct stat st;
	fstat(fileno(fp), &st);
	char *pattern = malloc(st.st_size);
	assert(pattern != NULL);
	assert(fread(pattern, 1, st.st_size, fp) == (unsigned)st.st_size);

	const char *err;
	int erroffset;
	pcre *re = pcre_compile(
		pattern,
		CF,                   /* default options */
		&err,
		&erroffset,
		NULL);                /* use default character tables */

	if (!re) {
		fprintf(stderr, "PCRE compilation failed at offset %d: %s\n", erroffset, err);
		json_object *pat = json_object_new_string_len(pattern, st.st_size);
		free(pattern);
		return pat;
	}
	free(pattern);

	/* HACK
	 * should be sizeof(*re), but since it's an incomplete type,
	 * we're accessing internals of malloc
	 */
	json_object *obj = json_object_new_string_len((char*)re, ((-4 & (size_t)((void**)re)[-1]) - sizeof(void*)));
	pcre_free(re);
	return obj;
}


json_bool fsdict_object_get_ex(struct json_object *obj, const char *key, json_object **value) {
	if (json_object_object_get_ex(obj, key, value))
		return TRUE;

	json_object *path;
	if (!json_object_object_get_ex(obj, "path", &path))
		return FALSE;

	int len = json_object_get_string_len(path);
	if (!len)
		return FALSE;

	int keylen = strlen(key);

	char newpath[len+keylen+8];
	int buflen = sprintf(newpath, "%s" SEP "%s", json_object_get_string(path), key);

	struct stat st;
	if (stat(newpath, &st)==0 && S_ISDIR(st.st_mode))
		*value = fsdict_object_new(newpath);
	else {
		char *ext = strrchr(key, '.');

		if (!ext) {
			ext = newpath+buflen;
			strcpy(ext, ".json");
		}

		FILE *fp = fopen(newpath, "r");
		if (!fp) {
			fprintf(stderr, "Key error: %s: %m: %s", key, newpath);
			return FALSE;
		}

		++ext;
		if (strcmp(ext, "json") == 0) {
			*value = json_object_from_fp(fp);
			fclose(fp);
			if (*value == (json_object*)-1)
				return FALSE;
			struct parpar par2 = {
				.j = obj,
				.par = NULL
			};
			duplidict_fixup(*value, &par2);
		}
		else if (strcmp(ext, "pcre") == 0) {
			*value = pcre_compile_fp(fp);
			fclose(fp);
			if (!*value)
				return FALSE;
		}
		else {
			fclose(fp);
			fprintf(stderr, "Key error: %s: unknown file extension: %s", key, ext);
			return FALSE;
		}
	}
	json_object_object_add(obj, key, *value);
	return TRUE;
}
