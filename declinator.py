
import os.path, sys, json

locale = 'pl_PL'

with open(os.path.join(os.path.split(__file__)[0],"rules","%s.json"%locale), 'rt') as fp:
  obj = json.load(fp)

def findgender(word):
  return 'f' if word[-1:] in 'aeis' else 'm'

def decl(name, case, gender = 'auto'):
  if gender == 'auto':
    gender = findgender(name[0])
  case = case.get(gender, iter(case.values()).__next__())
  name = list(name)
  for idx, word in enumerate(name):
    rw = word
    for i in range(len(word),-1,-1):
      suf = word[i:]
      if suf in case:
        rw = word[:i] + case[suf]
    name[idx] = rw
  return ' '.join(name)

def declmod(word, cases, gender = 'auto'):
  name = word.split()
  if gender == 'auto':
    gender = findgender(name[0])
  cases.setdefault('nominative', {'f':{}})
  return {x: decl(name, cases[x], gender) for x in cases}

def test():
  #json.dump(obj, sys.stderr, indent='\t')
  import argparse
  par = argparse.ArgumentParser()
  par.add_argument("-g", "--gender", help="the word's gender", choices=['f','m','n','auto'], default='auto')
  par.add_argument("word", help="the word to roll", default='Julia')
  arg = par.parse_args()
  for speechpart in obj:
    print("\n=== speechpart! ===")
    print("Idę sobie z %(instrumental)s, przyglądam się %(dative)s, pytam"
	  " %(accusative)s, a %(nominative)s odpowiada. %(vocative)s! Odpowiedź"
	  " %(genitive)s jest o %(locative)s." % declmod(arg.word, speechpart, arg.gender))

if __name__ == "__main__":
  test()
