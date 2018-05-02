#!/usr/bin/env python3

import doctest, declinator

doctest.testmod(declinator, verbose=True)

def gendoctest(name):
    print('{' + ', '.join('%r: %r' % t
                    for t in sorted(declinator.declmod(name).items(),
                                    key=lambda x: 'ngdailv'.index(x[0][0]))
                    ) + '}')
