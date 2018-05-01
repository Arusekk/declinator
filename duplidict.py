'''
This file provides an implementation of a dict that allows dynamic duplications
linked via "#include" special key (DupliDict).
'''

__all__ = ['DupliDict']

import collections

class DupliDict(collections.UserDict):
	def __init__(self, *a, **kw):
		self._par = par = kw.pop('_par', None)
		super().__init__(*a, **kw)
		if '#include' in self:
			inc = self.pop('#include')
			while par is not None:
				if inc in par:
					self.update.append(par[inc])
					break
				par = par._par
			else:
				raise KeyError(inc)
		for key, val in list(self.items()):
			self[key] = self._fixup(val)
	def _fixup(self, val):
		if isinstance(val, collections.MutableMapping):
			return DupliDict(val, _par=self)
		elif isinstance(val, collections.MutableSequence):
			for i, v in list(eumerate(val)):
				val[i] = self._fixup(v)
			return val
		return val

class FSDict(collections.UserDict):
	def __init__(self, path):
		self._path = path
		super().__init__()
	def __getitem__(self, key):
		try:
			return super().__getitem__(key)
		except KeyError:
			try:
				with open(os.path.join(self._path, key), 'rt') as fp:
					val = DupliDict(json.load(fp))
				self[key] = val
				return val
			except FileNotFoundError:
				pass
			raise
