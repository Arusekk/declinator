#include "duplidict.h"
#include "declinator.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <locale.h>

#define arrlen(x) (sizeof(x)/sizeof(*x))

static json_object *settings_all, *settings, *detector, *default_nominative;
static const char *default_locale, *letters_patt="(*UTF)[^\\W\\d]+";
static pcre *letters;


static json_object *declmod_intern(const char *part, enum gender gen,
                                   int len, json_object *cases);
static json_object *_declmodd(const char *name, json_object *cases,
                              enum gender gen);
static json_object *_decld(const char *name, json_object *dic, enum gender gen);
static int _getsuf(const char *word, json_object *dic0, enum gender gen,
                   json_object **value);
static enum gender findgender(const char *name);


void declinator_init() {
	settings_all = fsdict_object_new("rules");
	default_locale = setlocale(LC_ALL, "");
	if (!default_locale)
		default_locale = getenv("LC_ALL");
	if (!default_locale)
		default_locale = "en_US.UTF-8";
	assert(fsdict_object_get_ex(settings_all, default_locale, &settings));
	assert(fsdict_object_get_ex(settings, "detection.pcre", &detector));
	default_nominative = json_tokener_parse("{\"f\":{\"\":\"\"}}");
	const char *err;
	int erroff;
	letters = pcre_compile(letters_patt, CF, &err, &erroff, NULL);
	if (!letters)
		fprintf(stderr, "Error compiling %s at %d: %s\n", letters_patt, erroff, err);
}


json_object *declmod(const char *name, enum gender gen) {
	return declmod_locale(name, gen, default_locale);
}


json_object *declmod_locale(const char *name, enum gender gen, const char *locale) {
	json_object *settings_ = settings, *detector_ = detector;
	if (strcmp(locale, default_locale) != 0) {
		assert(fsdict_object_get_ex(settings_all, locale, &settings_));
		assert(fsdict_object_get_ex(settings_, "detection.pcre", &detector_));
	}
	pcre *re = (pcre*)json_object_get_string(detector_);
	int n;
	assert(pcre_fullinfo(re, NULL, PCRE_INFO_CAPTURECOUNT, &n) == 0);
	int ovector[3 * (n+1)];
	int count = pcre_exec(re,               /* code */
	                      NULL,             /* extra */
	                      name,             /* subject */
	                      strlen(name),     /* length */
	                      0,                /* offset */
	                      EF,               /* options */
	                      ovector,          /* ovector */
	                      3 * (n+1)         /* ovecsize */
	                     );
	if (count <= 0) {
		fprintf(stderr, "Not a valid name: %s\n", name);
		return NULL;
	}
	if (gen == gender_auto) {
		char *first;
		int flen = pcre_get_named_substring(re, name, ovector, count, "first",
		                                    (const char**)&first);
		if (flen > 0) {
			int ovec2[3];
			int fcount = pcre_exec(letters, NULL, first, flen, 0, EF, ovec2, 3);
			if (fcount > 0) {
				first[ovec2[1]] = '\0';
				gen = findgender(first+ovec2[0]);
			}
			pcre_free(first);
		}
	}

	const char *nametable;
	int entrysize, namecount;
	assert(pcre_fullinfo(re, NULL, PCRE_INFO_NAMETABLE, &nametable) == 0);
	assert(pcre_fullinfo(re, NULL, PCRE_INFO_NAMECOUNT, &namecount) == 0);
	assert(pcre_fullinfo(re, NULL, PCRE_INFO_NAMEENTRYSIZE, &entrysize) == 0);
	const char *tablename[n+1];
	for (int i=0; i<=n; i++)
		tablename[i] = NULL;
	
	for (int i=0; i<namecount; i++) {
		const char *p = nametable + i*entrysize;
		tablename[(p[0] << 8)|p[1]] = p+2;
	}
	json_object *ret = json_object_new_object();
	for (int i=1; i<=n; i++) {
		int ixfr = ovector[i<<1];
		int ixto = ovector[(i<<1)|1];
		if (ixfr == ixto || tablename[i] == NULL)
			continue;

		json_object *obj;
		assert(fsdict_object_get_ex(settings_, tablename[i], &obj));

// 		fprintf(stderr, "%s: (%d)\"%s\"\n", tablename[i], ixto-ixfr, name+ixfr);

		obj = declmod_intern(name+ixfr, gen, ixto-ixfr, obj);

		if (!obj) {
			json_object_put(ret);
			return NULL;
		}

		json_object_object_foreach(obj, key, curval) {
			json_object *prevval;
			const char *prevstr;
			int prevlen;
			if (json_object_object_get_ex(ret, key, &prevval)) {
				prevlen = json_object_get_string_len(prevval);
				if (prevlen)
					prevstr = json_object_get_string(prevval);
			}
			else
				prevlen = 0;
			const char *curstr;
			int curlen = json_object_get_string_len(curval);
			if (curlen)
				curstr = json_object_get_string(curval);
			int newlen = prevlen + curlen;
			char newstr[newlen+1];
			if (prevlen)
				memcpy(newstr, prevstr, prevlen);
			if (curlen)
				memcpy(newstr+prevlen, curstr, curlen);
			json_object *newval = json_object_new_string_len(newstr, newlen);
			json_object_object_add(ret, key, newval);
		}
	}
	return ret;
}


json_object *declmod_intern(const char *part, enum gender gen, int len, json_object *cases) {
	json_object *defaults = json_object_array_get_idx(cases, 0);
	int clen = json_object_array_length(cases), off;
	int ovec[3];
	json_object *ret = json_object_new_object();
	for (off = 0; off < len; ) {
		int nmatch = pcre_exec(letters, NULL, part, len, off, EF, ovec, 3);
		if (nmatch < 1)
			break;

		const char *word;
		int wlen = pcre_get_substring(part, ovec, nmatch, 0, &word);

		json_object *wordds = json_object_new_array();
		for (int m = 1; m < clen; m++) {
			json_object *cc = _declmodd(word, json_object_array_get_idx(cases, m), gen);
			if (cc)
				json_object_array_add(wordds, cc);
		}
		if (json_object_array_length(wordds) == 0) {
			fprintf(stderr, "Possibilities exhausted: (%d)\"%s\"\n", wlen, word);
			json_object_put(ret);
			return NULL;
		}

		json_object *suf;
		if (_getsuf(word, defaults, gen, &suf) == -1) {
			fprintf(stderr, "Impossible suffix??: (%d)\"%s\"\n", wlen, word);
			json_object_put(ret);
			return NULL;
		}
		int defsuf = json_object_get_int(suf);
		json_object *wordd = json_object_get(json_object_array_get_idx(wordds, defsuf));
// 		json_object_to_file_ext("/dev/stderr", wordds, JSON_C_TO_STRING_PRETTY);
		json_object_put(wordds);

		json_object_object_foreach (wordd, key, dec) {
			json_object *oldval;
			int oldlen;
			if (json_object_object_get_ex(ret, key, &oldval))
				oldlen = json_object_get_string_len(oldval);
			else
				oldlen = 0;
			int declen = json_object_get_string_len(dec);
			int newlen = oldlen + ovec[0] - off + declen;
			char newstr[newlen + 1];
			if (oldlen)
				memcpy(newstr, json_object_get_string(oldval), oldlen);
			if (ovec[0] - off > 0)
				memcpy(newstr+oldlen, part+off, ovec[0] - off);
			if (declen)
				memcpy(newstr+newlen-declen, json_object_get_string(dec), declen);
			json_object_object_add(ret, key,
			                       json_object_new_string_len(newstr, newlen));
		}
		json_object_put(wordd);

		off = ovec[1];
		pcre_free((char*)word);
	}
	if (len - off > 0) {
		json_object_object_foreach (ret, key, oldval) {
			int oldlen = json_object_get_string_len(oldval);
			int newlen = oldlen + len - off;
			char newstr[newlen + 1];
			if (oldlen)
				memcpy(newstr, json_object_get_string(oldval), oldlen);
			memcpy(newstr+oldlen, part+off, len - off);
			json_object_object_add(ret, key,
			                       json_object_new_string_len(newstr, newlen));
		}
	}
	return ret;
}


json_object *_declmodd(const char *name, json_object *cases, enum gender gen) {
	if (!json_object_object_get_ex(cases, "nominative", NULL)) {
		json_object_object_add_ex(cases, "nominative",
		                          json_object_get(default_nominative),
		                          JSON_C_OBJECT_ADD_KEY_IS_NEW
		                        | JSON_C_OBJECT_KEY_IS_CONSTANT);
	}
	json_object *ret = json_object_new_object();
	json_object_object_foreach (cases, key, dic) {
		json_object *val = _decld(name, dic, gen);
		if (val == NULL) {
			json_object_put(ret);
			return val;
		}
		json_object_object_add_ex(ret, key, val,
		                          JSON_C_ADD_KEY_IS_NEW);
	}
	return ret;
}


json_object *_decld(const char *name, json_object *dic, enum gender gen) {
	json_object *newsuf;
	int i = _getsuf(name, dic, gen, &newsuf);
	if (i == -1)
		return NULL;
	int suflen = json_object_get_string_len(newsuf);
	char newstr[i+suflen+1];
	memcpy(newstr, name, i);
	memcpy(newstr+i, json_object_get_string(newsuf), suflen);
	
	return json_object_new_string_len(newstr, i+suflen);
}


int _getsuf(const char *word, json_object *dic0, enum gender gen, json_object **value) {
	if (gen == gender_auto)
		gen = findgender(word);
	char gen_str[] = {gen, '\0'};
	json_object *dic;
	if (!json_object_object_get_ex(dic0, gen_str, &dic)) {
		/* HACK: we should find an arbitrary present key, but just stick to f */
		if (!json_object_object_get_ex(dic0, "f", &dic)) {
			FIXME;
			return -1;
		}
	}
		int i = 0;
		do {
			if (json_object_object_get_ex(dic, word+i, value))
				return i;
		} while (word[i++]);
		return -1;
}


enum gender findgender(const char *name) {
	switch (name[strlen(name)-1]) {
		case 'a':
		case 'e':
		case 'i':
		case 's':
			return gender_f;
	}
	return gender_m;
}
