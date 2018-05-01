#!/usr/bin/python3

# wizja: wyrażenie regularne, które tworzy słownik tytułu, imienia, przedrostka, nazwiska, numeru
# Taki słownik potem odmieniamy zgodnie z plikami w odpowiednim lokalu.
# Po polsku możnaby zrobić słownik podstawowy i uzupełnienia. [DONE]

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
  found = False
  for i in range(len(name),-1,-1):
    suf = name[i:]
    if suf in case:
      name = name[:i] + case[suf]
      found = True
  if not found:
    raise DeclensionPatternError('case does not decline such a form:\n%s\n%s'%(json.dumps(case, indent='\t'), name))
  return name

def declmodd(name, cases, gender = 'auto'):
  if gender == 'auto':
    gender = findgender(name)
  #print(json.dumps(cases, indent='\t'))
  cases.setdefault('nominative', {'f':{'':''}})
  return {x: decld(name, cases[x], gender) for x in cases}

def declmod(name, gender='auto'):
  match = detector.match(name).groupdict()
  ans = collections.defaultdict(str)
  for k, v in match.items():
    if not v:
      continue
    ansv = collections.defaultdict(lambda: v)
    for w in letters.finditer(v):
      word = w.group()
      print(word)
      for met in settings[k]:
        try:
          wordd = declmodd(word, met, gender)
          break
        except DeclensionPatternError:
          pass
      else:
        raise DeclensionPatternError('Possibilities exhausted: %s'%word)
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
  par.add_argument("word", help="the word to roll", default='Julia')
  arg = par.parse_args()
  for speechpart in obj:
    try:
      m = declmod(arg.word, speechpart, arg.gender)
    except DeclensionPatternError:
      continue
    print("\n=== speechpart! ===")
    print("Idę sobie z %(instrumental)s, przyglądam się %(dative)s, pytam"
          " %(accusative)s, a %(nominative)s odpowiada. %(vocative)s! Odpowiedź"
          " %(genitive)s jest o %(locative)s." % declmod(arg.word, speechpart, arg.gender))

if __name__ == "__main__":
  test()
