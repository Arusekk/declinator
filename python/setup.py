
import glob
import subprocess
import sys
import traceback

from setuptools import setup

# Convert README.md to reStructuredText for PyPI
long_description = ''
try:
    long_description = subprocess.check_output(['pandoc', 'README.md', '--to=rst'])
except (FileNotFoundError, subprocess.CalledProcessError):
    print("Failed to convert README.md through pandoc, proceeding anyway", file=sys.stderr)
    traceback.print_exc()

setup(
    name                 = 'declinator',
    python_requires      = '>=3',
    version              = '1.0.1',
    description          = "Declinator automatised declension of names.",
    long_description     = long_description,
    author               = "Arusekk",
    author_email         = "arek_koz@o2.pl",
    url                  = 'https://github.com/Arusekk/declinator',
    download_url         = "https://github.com/Arusekk/declinator/releases",
    data_files           = [('declinator', glob.glob('rules/*/*.*'))],
    license              = 'AGPL-3.0+',
    keywords             = 'declinator declination declension localization names',
    packages             = ['declinator'],
    classifiers          = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License version 3+',
        'Natural Language :: English',
        'Natural Language :: Polish',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Declension',
        'Topic :: Declination',
        'Topic :: Localization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
