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

def getsuf(word, dic, gender):
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

def decld(name, case, gender = 'auto'):
  newsuf, i = getsuf(name, case, gender)
  #print(name, '->', name[:i] + newsuf)
  return name[:i] + newsuf

def declmodd(name, cases, gender = 'auto'):
  if gender == 'auto':
    gender = findgender(name)
  cases.setdefault('nominative', {'f':{'':''}})
  return {x: decld(name, cases[x], gender) for x in cases}

def declmod(name, gender='auto'):
  match = detector.match(name)
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
      defs = settings[k][0]
      wordds = []
      for met in settings[k][1:]:
        try:
          wordds.append(declmodd(word, met, gender))
        except DeclensionPatternError:
          pass
      if not wordds:
        raise DeclensionPatternError('Possibilities exhausted: %s'%word)
      #print(word, ':', wordds)
      wordd = wordds[getsuf(word, defs, gender)[0]] ## maybe return whole list?
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
