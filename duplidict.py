'''
This file provides an implementation of a dict that allows dynamic duplications
linked via "#include" special key (DupliDict).
'''

__all__ = ['DupliDict', 'FSDict']

import collections
import json
import os.path

json.__dict__.setdefault('JSONDecodeError', ValueError)

class DupliDict(collections.UserDict):
	def __init__(self, *a, **kw):
		self._par = par = kw.pop('_par', None)
		super().__init__(*a, **kw)
		if '#include' in self:
			inc = self.pop('#include')
			while par is not None:
				try:
					_fixx(self, par[inc])
					break
				except KeyError:
					par = par._par
			else:
				raise KeyError(inc)
		for key, val in list(self.items()):
			self[key] = self._fixup(val)
	def _fixup(self, val):
		if isinstance(val, collections.MutableMapping):
			return DupliDict(val, _par=self)
		elif isinstance(val, collections.MutableSequence):
			for i, v in list(enumerate(val)):
				val[i] = self._fixup(v)
			return val
		return val

def _fixx(cont, ins):
	for k, v in ins.items():
		if k not in cont:
			cont[k] = v
			continue
		if isinstance(cont[k], collections.MutableMapping):
			_fixx(cont[k], v)

class FSDict(DupliDict):
	def __init__(self, path):
		self._path = path
		super().__init__()
	def __getitem__(self, key):
		try:
			return super().__getitem__(key)
		except KeyError:
			if '.' not in key:
				key += '.json'
			try:
				with open(os.path.join(self._path, key), 'rt') as fp:
					try:
						val = json.load(fp)
					except json.JSONDecodeError:
						fp.seek(0)
						val = fp.read()
					val = self._fixup(val)
				self[key] = val
				return val
			except FileNotFoundError:
				pass
			raise
