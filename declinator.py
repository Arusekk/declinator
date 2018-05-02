#!/usr/bin/python3

import duplidict

import collections
import locale
import os.path
import re

default_locale, _ = locale.getlocale()
settings_all = duplidict.FSDict(os.path.join(os.path.dirname(__file__),"rules"))
settings = settings_all[default_locale]

DETECTOR_NAME = 'detection.pcre'

detector = re.compile(settings[DETECTOR_NAME])

letters = re.compile(r'[^\W\d_]+')

def findgender(word):
  '''
      Try to guess the gender of a name.

  Examples:

      >>> findgender('Julia')
      'f'
      >>> findgender('Antonio')
      'm'
  '''
  return 'f' if word[-1:] in 'aeis' else 'm'

class DeclensionPatternError(Exception):
  pass

def _getsuf(word, dic, gender):
  '''
      Helper function to get the longest applying suffix and its position.

  Examples:

      >>> d = {'f': {'s': 'F', 'is': 'G', 'exis': 'O', 'his': 'Q'},
      ...      'm': {'r': 'T', '': 'X'}}
      >>> _getsuf('Alexis', d, 'auto')
      ('O', 2)
      >>> _getsuf('Alexis', d, 'm')
      ('X', 6)
  '''
  if gender == 'auto':
    gender = findgender(word)
  dic = dic.get(gender, next(iter(dic.values())))
  #print(dic)
  ans = None
  for i in range(len(word),-1,-1):
    suf = word[i:]
    if suf in dic:
      ans = dic[suf]
      l = i
  if ans is None:
    raise DeclensionPatternError('Case does not decline: %s'%(word,))
  return ans,l

def _decld(name, case, gender):
  newsuf, i = _getsuf(name, case, gender)
  return name[:i] + newsuf

def _declmodd(name, cases, gender):
  cases.setdefault('nominative', {'f':{'':''}})
  return {x: _decld(name, cases[x], gender) for x in cases}

def declmod(name, gender='auto', locale=default_locale):
  r'''
      Declension of a name.

  Examples:

      >>> declmod('Róża Maria Barbara Gräfin von Thun und Hohenstein',
      ... locale='pl_PL') == \
      ... {'nominative': 'Róża Maria Barbara Gräfin von Thun und Hohenstein',
      ... 'genitive': 'Róży Marii Barbary Gräfin von Thun und Hohenstein',
      ... 'dative': 'Róży Marii Barbarze Gräfin von Thun und Hohenstein',
      ... 'accusative': 'Różę Marię Barbarę Gräfin von Thun und Hohenstein',
      ... 'instrumental': 'Różą Marią Barbarą Gräfin von Thun und Hohenstein',
      ... 'locative': 'Róży Marii Barbarze Gräfin von Thun und Hohenstein',
      ... 'vocative': 'Różo Mario Barbaro Gräfin von Thun und Hohenstein'}
      True

      >>> declmod('Janusz Korwin-Mikke', locale='pl_PL') == \
      ... {'nominative': 'Janusz Korwin-Mikke', 'genitive':
      ... 'Janusza Korwina-Mikkego', 'dative': 'Januszowi Korwinowi-Mikkemu',
      ... 'accusative': 'Janusza Korwina-Mikkego', 'instrumental':
      ... 'Januszem Korwinem-Mikkem', 'locative': 'Januszu Korwinie-Mikkem',
      ... 'vocative': 'Januszu Korwinie-Mikke'}
      True

      >>> declmod('Iwo Kwiatkowski-Misiek', locale='pl_PL') == \
      ... {'nominative': 'Iwo Kwiatkowski-Misiek', 'genitive':
      ... 'Iwona Kwiatkowskiego-Miśka', 'dative':
      ... 'Iwonowi Kwiatkowskiemu-Miśkowi', 'accusative':
      ... 'Iwona Kwiatkowskiego-Miśka', 'instrumental':
      ... 'Iwonem Kwiatkowskim-Miśkiem', 'locative':
      ... 'Iwonie Kwiatkowskim-Miśku', 'vocative': 'Iwonie Kwiatkowski-Miśku'}
      True
  '''
  settings_ = settings
  detector_ = detector
  if locale != default_locale:
    settings_ = settings_all[locale]
    detector_ = settings_[DETECTOR_NAME]
  match = detector_.match(name)
  ans = collections.defaultdict(str)
  if gender == 'auto':
    gender = findgender(next(letters.finditer(match.group('first'))).group())
  for k, v in sorted(
      match.groupdict(default='').items(),
      key=lambda x: match.groups().index(x[1])):
    if not v:
      continue
    ansv = collections.defaultdict(lambda: v)
    for w in letters.finditer(v):
      word = w.group()
      sets = iter(settings_[k])
      defs = next(sets)
      wordds = []
      for met in sets:
        try:
          wordds.append(_declmodd(word, met, gender))
        except DeclensionPatternError:
          pass
      if not wordds:
        raise DeclensionPatternError('Possibilities exhausted: %s'%word)
      #print(word, ':', wordds)
      wordd = wordds[_getsuf(word, defs, gender)[0]] ## maybe return whole list?
      for case, dec in wordd.items():
        ansv[case] = ansv[case].replace(word, dec)
    for case, dec in ansv.items():
      ans[case] += dec
  return dict(ans)

def main():
  import argparse
  par = argparse.ArgumentParser()
  par.add_argument("-g", "--gender", help="the word's gender", choices=['f','m','n','auto'], default='auto')
  par.add_argument("word", help="the word to roll", default='Julia Kwiatkowska')
  arg = par.parse_args()
  m = declmod(arg.word, arg.gender)
  print(settings['illustration']['teststring'].format(**m))

if __name__ == "__main__":
  main()
