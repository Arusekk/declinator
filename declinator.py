#!/usr/bin/python3

import duplidict

import collections
import os.path
import re
import sys

locale = 'pl_PL'

settings = duplidict.FSDict(os.path.join(os.path.dirname(__file__),"rules",locale))

detector = re.compile(settings['detection.pcre'])

letters = re.compile(r'[^\W\d_]+')

def findgender(word):
  return 'f' if word[-1:] in 'aeis' else 'm'

class DeclensionPatternError(Exception): pass

def decld(name, case, gender = 'auto'):
  if gender == 'auto':
    gender = findgender(name)
  case = case.get(gender, next(iter(case.values())))
  print(case)
  found = False
  suf = ''
  for i in range(len(name),-1,-1):
    suf = name[i:i+1] + suf
    if suf in case:
      name = name[:i] + case[suf]
      found = True
  if not found:
    raise DeclensionPatternError('Case does not decline: %s'%(name,))
  return name

def declmodd(name, cases, gender = 'auto'):
  if gender == 'auto':
    gender = findgender(name)
  #print(json.dumps(cases, indent='\t'))
  cases.setdefault('nominative', {'f':{'':''}})
  return {x: decld(name, cases[x], gender) for x in cases}

def declmod(name, gender='auto'):
  match = detector.match(name)
  ans = collections.defaultdict(str)
  for k, v in sorted(
      match.groupdict(default='').items(),
      key=lambda x: match.groups().index(x[1])):
    if not v:
      continue
    ansv = collections.defaultdict(lambda: v)
    for w in letters.finditer(v):
      word = w.group()
      for met in settings[k]:
        try:
          wordd = declmodd(word, met, gender)
          break
        except DeclensionPatternError:
          pass
      else:
        raise DeclensionPatternError('Possibilities exhausted: %s'%word)
      print(word, ':', wordd)
      for case, dec in wordd.items():
        ansv[case] = ansv[case].replace(word, dec)
    for case, dec in ansv.items():
      ans[case] += dec
  return dict(ans)

def test():
  #json.dump(obj, sys.stderr, indent='\t')
  import argparse
  par = argparse.ArgumentParser()
  par.add_argument("-g", "--gender", help="the word's gender", choices=['f','m','n','auto'], default='auto')
  par.add_argument("word", help="the word to roll", default='Julia Kwiatkowska')
  arg = par.parse_args()
  m = declmod(arg.word, arg.gender)
  print("\n=== speechpart! ===")
  print("Idę sobie z %(instrumental)s, przyglądam się %(dative)s, pytam"
        " %(accusative)s, a %(nominative)s odpowiada. %(vocative)s! Odpowiedź"
        " %(genitive)s jest o %(locative)s." % m)

if __name__ == "__main__":
  test()
