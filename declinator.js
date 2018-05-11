/* declinator.js
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
/* eslint "security/detect-object-injection": "off" */
"use strict";

/*
 * minimal support for verbose PCRE
 */
function PCRE(pattern) {
	var namedGroups = {};
	var opts = "";
	var pattern = pattern.replace(/\(\?([a-z]+)\)/g, function(mat, g1) { opts += g1; return ""; });
	if (opts.indexOf("x") !== -1)
		pattern = pattern.replace(/\s/g, "");
	opts = opts.replace(/[x]/,"");
	var groupp = /\((?:\?P<([^>]*)>|([^\?]))/g;
	var m, idx = 0;
	while ((m = groupp.exec(pattern))) {
		if (m[1]) {
			namedGroups[m[1]] = ++idx;
		}
	}
	pattern = pattern.replace(groupp, "($2").replace(/([^\\](?:\\\\)*)\{,/g, "$1{0,");
	// eslint-disable-next-line security/detect-non-literal-regexp
	var code = new RegExp(pattern, opts);
	code.namedGroups = namedGroups;
	return code;
}

function DupliDict(obj, par) {
	this._fixup = function(val) {
		if (typeof val === "object") {
			if (typeof val.length !== "undefined") {
				for (var i = 0; i < val.length; i ++) {
					val[i] = this._fixup(val[i]);
				}
				return val;
			}
			if (!("_commitInclusion" in val)) {
				val = new DupliDict(val, this);
			}
			val._commitInclusion(val._par);
			return val;
		}
		return val;
	};

	this._fixx = function(cont, ins) {
		for (var k in ins) {
			if (k.slice(0,1) !== "_") {
				if (!(k in cont)) {
					cont[k] = ins[k];
					continue;
				}
				if (typeof cont[k] === "object") {
					this._fixx(cont[k], ins[k]);
				}
			}
		}
	};

	var inc, k;
	for (k in obj) {
		if (({}).hasOwnProperty.call(obj, k)) {
			if (k === "#include") {
				inc = obj[k];
			}
			else {
				this[k] = obj[k];
			}
		}
	}
	this._par = par;
	this._commitInclusion = function(par) {
		this._success = true;
		if (typeof inc !== "undefined") {
			while (typeof par !== "undefined") {
				if (inc in par) {
					this._fixx(this, par[inc]);
					break;
				}
				par = par._par;
			}
			if (typeof par === "undefined") {
				if (typeof this._par !== "undefined") {
					this._par._success = false;
				}
				return;
			}
		}

		for (k in this) {
			if (({}).hasOwnProperty.call(this, k) && k != "_par") {
				this[k] = this._fixup(this[k]);
			}
		}
		if (this._success) {
			this._par = void(0);
		}
		else if (typeof this._par !== "undefined") {
			this._par._success = false;
		}
	}
}

var FS = {
	testDir: function(path, cb1, cb2) {
		FS.getFile(path+"/", cb1, cb2);
	},
	getFile: function(path, cb1, cb2, pot) {
		if (typeof pot !== "undefined") {
			return cb1(pot);
		}
		var xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			if (xhr.readyState === 4) {
				if (xhr.status === 200) {
					if (xhr.status === 400) {
						cb1();
					}
					else {
						cb1(xhr.responseText);
					}
				}
				else {
					cb2();
				}
			}
		};
		xhr.open("GET", path);
		xhr.send();
	}
};

function regExpEscape(literal) {
	return literal.replace(/[-[\]{}()*+!<=:?.\/\\^$|#\s,]/g, "\\$&");
}

function FSDict(path, suf, text) {
	DupliDict.call(this, {});

	this._path = path;
	this._ensure = function(key, cb) {
		if (key.slice(-5) === ".json") {
			key = key.slice(0, -5);
		}
		else if (key.slice(-1) === "/") {
			key = key.slice(0, -1);
		}
		if (key in this) {
			return;
		}
		var newpath = path + "/" + key;
		var ref = this;
		FS.testDir(newpath, function(text) {
			ref[key] = new FSDict(newpath, suf+"/"+key, text);
		}, function(pot) {
			if (key.lastIndexOf(".") === -1) {
				newpath += ".json";
			}
			FS.getFile(newpath, function(contents) {
				var ext = newpath.slice(newpath.lastIndexOf(".")+1);
				if (ext === "json") {
					ref[key] = ref[key+".json"] = ref._fixup(JSON.parse(contents));
					ref._commitInclusion(ref._par);
				}
				else if (ext === "pcre") {
					var nv = PCRE(
						contents.replace("(*UTF8)", "(?u)")
					);
					nv._commitInclusion = function(){};
					ref[key] = nv;
				}
				else {
					console.log("unknown file extension:", ext, "in", path,
					            "[", key, "]");
				}
				if (typeof cb !== "undefined") {
					cb(ref[key]);
				}
			}, function() {
				ref[key] = new FSDict(newpath, suf+"/"+key);
			}, pot);
		});
	};

	var ref = this;
	FS.getFile(path+"/", function(txt) {
		// eslint-disable-next-line security/detect-non-literal-regexp
		var m, re = new RegExp("href=\".*/"+regExpEscape(suf)+"/([^\"]+)\"", "g");
		var count = 0;
		while ((m = re.exec(txt))) {
			ref._ensure(m[1]);
			count ++;
		}
		re = /href="([^"]+)"/g;
		while ((m = re.exec(txt))) {
			ref._ensure(m[1]);
			count ++;
		}
		
	}, function() {
		ref._ensure("_listdir", function(l) {
			for (var i = 0; i < l.length; i ++) {
				ref._ensure(l[i]);
			}
		});
	}, text);
}

function Declinator(URL1, URL2) {
	this.DETECTOR_NAME = "detection.pcre";

	this.settingsAll = new FSDict(URL1+URL2, URL2);

	this.langJsToIso = function(l) {
		if (l.length === 2)
			return l + "_" + l.toUpperCase();
		return l.replace("-", "_");
	}

	this.getDefaultLocale = function() {
		for (var i = 0; i < navigator.languages.length; i ++) {
			var guess = this.langJsToIso(navigator.languages[i]);
			if (guess in this.settingsAll)
				return guess;
		}
	}

	this.declmod = function(name, gen, locale) {
		if (typeof locale === "undefined") {
			locale = this.getDefaultLocale();
		}
		if (typeof gen === "undefined") {
			gen = "auto";
		}
		var settings_ = this.settingsAll[locale];
		var detector_ = settings_[this.DETECTOR_NAME];
		var match = detector_.exec(name);
		var ans = {};
		if (gen === "auto") {
			gen = this.findGender(/[^\W\d_]+/u.exec(
					match[detector_.namedGroups["first"]]
			)[0]);
		}
		for (var key in detector_.namedGroups) {
			var val = match[detector_.namedGroups[key]];
			if (!val) {
				continue;
			}
			var ansv = {};
			var sets = settings_[key];
			var defs = sets[0];
			var w;
			var letters = /[^\W\d_]+/gu;
			while ((w = letters.exec(val))) {
				var word = w[0];
				var wordds = [];
				for (var i = 1; i < sets.length; i ++) {
					var x = this._declmodd(word, sets[i], gen);
					if (x) {
						wordds.push(x);
					}
				}
				if (wordds.length === 0) {
					return; // TODO: throw
				}
				var wordd = wordds[this._getSuf(word, defs, gen)[0]]; // ### maybe?
				for (var cas in wordd) {
					if (!(cas in ansv)) {
						ansv[cas] = val;
					}
					ansv[cas] = ansv[cas].replace(word, wordd[cas]);
				}
			}
			for (var ca in ansv) {
				if (!(ca in ans)) {
					ans[ca] = "";
				}
				ans[ca] += ansv[ca];
			}
		}
		return ans;
	};

	this._declmodd = function(word, dic, gen) {
		var ret = {};
		if (!("nominative" in dic)) {
			dic.nominative = {f:{"":""}};
		}
		for (var k in dic) {
			if (k.slice(0,1) !== "_") {
				var v = this._decld(word, dic[k], gen);
				if (typeof v === "undefined") {
					return;
				}
				ret[k] = v;
			}
		}
		return ret;
	};

	this._decld = function(word, dic, gen) {
		var s = this._getSuf(word, dic, gen);
		if (s[1] !== -1) {
			return word.slice(0, s[1]) + s[0];
		}
	};

	this._getSuf = function(word, dic0, gen) {
		if (gen === "auto") {
			gen = this.findGender(word);
		}
		var dic = dic0[gen];
		if (typeof dic === "undefined") {
			for (var k in dic0) {
				if (k.slice(0,1) !== "_") {
					dic = dic0[k];
					break;
				}
			}
		}
		for (var i = 0; i <= word.length; i ++) {
			var t = word.slice(i);
			if (t in dic) {
				return [dic[t], i];
			}
		}
		return ["", -1];
	};

	this.findGender = function(w) {
		return "aeis".indexOf(w.slice(-1)) !== -1 ? "f" : "m";
	};
}

window.declinator = new Declinator(
// 	"https://github.com/Arusekk/declinator/raw/",
	"https://raw.githubusercontent.com/Arusekk/declinator/",
	"javascript/rules"
);
