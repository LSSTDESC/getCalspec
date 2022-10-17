from setuptools import setup
import os
import re


# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


version_file = os.path.join('getCalspec', '_version.py')
verstrline = open(version_file, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    current_version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (version_file,))
print(f'getCalspec version is {current_version}')

setup(
    name='getCalspec',
    version=current_version,
    packages=['getCalspec'],
    install_requires=['numpy>1.15', 'matplotlib>3.1', 'pandas', 'astropy', 'astroquery'],
    test_suite='nose.collector',
    tests_require=['nose'],
    package_dir={'getCalspec': './getCalspec'},
    package_data={'getCalspec': ['../calspec_data/calspec.csv', '../calspec_data/calspec.pkl']},
    url='https://github.com/LSSTDESC/getCalspec',
    license='BSD',
    python_requires='>=3.7',
    author='J. Neveu',
    author_email='jeremy.neveu@universite-paris-saclay.fr',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
