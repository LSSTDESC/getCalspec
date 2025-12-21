[![PyPI version](https://badge.fury.io/py/getCalspec.svg)](https://badge.fury.io/py/getCalspec)
[![Documentation Status](https://readthedocs.org/projects/getcalspec/badge/?version=latest)](https://getcalspec.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# getCalspec
Python package to download Calspec spectra.

The main function query the Calspec table located in `calspec_data/calspec.csv`
to download spectrum FITS files from [STSC archive](https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/calspec.html).

Example:
```
from getCalspec.getCalspec import *

test = is_calspec("eta1 dor")
c = Calspec("eta1 dor")
print("Gaia source id:", c.source_id)
c.get_spectrum_table(type="stis", date="latest")  # download and return an Astropy table
c.get_spectrum_numpy(type="mod", date="2010-12-11")  # download and return a dictionnary of numpy arrays with units
c.plot_spectrum()  # download and plot the spectrum
```

To get Calspec table and the list of available Calspec names:
```
from getCalspec.getCalspec import getCalspecDataFrame

df = getCalspecDataFrame()
print(df.Name.values)
# Gaia IDs
print(df.source_id.values)
```


To get all Calspec data in one time in cache, write:
```
from getCalspec.rebuild import rebuild_cache
rebuild_cache()
```

When the [STSC webpage](https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/calspec) is updated,
it might be necessary to rebuild the `calspec_data/calspec.csv` table and the cache:
```
from getCalspec.rebuild import rebuild_tables, rebuild_cache
rebuild_tables()
rebuild_cache()
```
