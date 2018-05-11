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
"use strict";

function DupliDict(obj, par) {
	this._fixup = function(val) {
		if (typeof val.length !== "undefined") {
			for (var i = 0; i < val.length; i ++) {
				val[i] = this._fixup(val[i]);
			}
			return val;
		}
		else if (typeof val === "object") {
			return new DupliDict(val, this);
		}
		return val;
	};

	this._fixx = function(cont, ins) {
		for (var k in ins) {
			if (!(k in cont)) {
				cont[k] = ins[k];
				continue;
			}
			if (typeof cont[k] === "object") {
				this._fixx(cont[k], ins[k]);
			}
		}
	};

	var inc, k;
	for (k in obj) {
		if (k === "#include") {
			inc = obj[k];
		}
		else {
			this[k] = obj[k];
		}
	}
	this._par = par;

	if (typeof inc !== "undefined") {
		while (typeof par !== "undefined") {
			if (inc in par) {
				this._fixx(this, par[inc]);
				break;
			}
			par = par._par;
		}
	}

	for (k in this) {
		this[k] = this._fixup(this[k]);
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
					cb1(xhr.responseText);
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

function regExpEscape(literal_string) {
	return literal_string.replace(/[-[\]{}()*+!<=:?.\/\\^$|#\s,]/g, "\\$&");
}

function FSDict(path, suf, text) {
	this.path = path;
	this.ensure = function(key) {
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
		FS.testDir(newpath, function(text) {
			this[key] = new FSDict(newpath, suf+"/"+key, text);
		}, function(pot) {
			if (key.lastIndefOf(".") === -1) {
				newpath += ".json";
			}
			FS.getFile(newpath, function(contents) {
				var ext = newpath.slice(newpath.lastIndefOf(".")+1);
				if (ext === "json") {
					this[key] = this[key+".json"] = new DupliDict(JSON.parse(contents), this);
				}
				else if (ext === "pcre") {
					this[key] = new RegExp(
						"(?u)" + contents.slice(contents.indexOf("(?"))
					);
				}
				else {
					console.log("unknown file extension:", ext, "in", path,
					            "[", key, "]");
				}
			}, function(){}, pot);
		});
	}

	FS.getFile(function(txt) {
		var m, re = new RegExp("/"+regExpEscape(suf)+"/([^\"]+)", "g");
		while (m=re.exec(txt)) {
			this.ensure(m[1]);
		}
	}, function(){}, text);
}

function Declinator(URL1, URL2) {
	this.DETECTOR_NAME = "detector.pcre";

	this.settingsAll = new FSDict(URL1+URL2, URL2);

	this.settings = this.settingsAll[this.defaultLocale];
	this.detector = this.settings[this.DETECTOR_NAME];

	this.declmod = function(name, gen, locale) {
		if (typeof locale === "undefined") {
			locale = this.defaultLocale;
		}
		var settings_ = this.settings;
		var detector_ = this.detector;
		if (locale !== this.defaultLocale) {
			settings_ = this.settingsAll[locale];
			detector_ = settings_[this.DETECTOR_NAME];
		}
		var match = detector_.exec(name);
		var ans = {};
		if (gen === "auto") {
			gen = this.findGender(letters.exec(match[detector_.namedGroups["first"]])[0]);
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
			while (w = letters.exec(val)) {
				var word = w[0];
				var wordds = [];
				for (var i = 1; i < sets.length; i ++) {
					var x = this._declmodd(word, sets[i], gen);
					if (x) {
						wordds.push(x);
					}
				}
				if (wordds.length === 0)
					return; // TODO: throw
				wordd = wordds[this._getSuf(word, defs, gen)[0]]; // ### maybe?
				for (var cas in wordd) {
					if (typeof ansv[cas] === "undefined")
						ansv[cas] = val;
					ansv[cas] = ansv[cas].replace(word, wordd[cas]);
				}
			}
			for (var ca in ansv) {
				if (typeof ans[ca] === "undefined")
					ans[ca] = "";
				ans[ca] += ansv[ca];
			}
		}
		return ans;
	}

	this._declmodd = function(word, dic, gen) {
		var ret = {};
		for (var k in dic) {
			var v = this._decld(word, dic[k], gen);
			if (typeof v === "undefined") {
				return;
			}
			ret[k] = v;
		}
		return ret;
	}

	this._decld = function(word, dic, gen) {
		var s = this._getSuf(word, gen);
		if (s[1] !== -1) {
			return s.slice(0, s[1]) + s[0];
		}
	}

	this._getSuf = function(word, dic0, gen) {
		if (gen === "auto") {
			gen = this.findGender(word);
		}
		var dic = dic0[gen];
		if (typeof dic === "undefined") {
			for (var k in dic0) {
				dic = dic0[k];
				break;
			}
		}
		for (var i=0; i<word.length; i++) {
			var t = word.slice(i);
			if (typeof dic[t] !== "undefined") {
				return [dic[t], i];
			}
		}
		return ["", -1];
	}

	this.findGender = function(w) {
		return "aeis".indexOf(w.slice(-1)) !== -1 ? "f" : "m";
	}
}

window.declinator = new Declinator(
	"https://github.com/Arusekk/declinator/raw/",
	"v1.0.0/rules"
);
