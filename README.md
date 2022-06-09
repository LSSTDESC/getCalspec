# getCalspec
Python package to download Calspec spectra.

The main function query the Calspec table located in `calspec_data/calspec.csv` 
to download spectrum FITS files from [STSC archive](https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/calspec.html).

Example:
```
test = is_calspec("eta1 dor")
c = Calspec("eta1 dor")
c.get_spectrum_fits()  # download the fits file
c.get_spectrum_table()  # download and return an Astropy table
c.get_spectrum_numpy()  # download and return a dictionnary of numpy arrays with units
c.plot_spectrum()  # download and plot the spectrum
```

When the [STSC webpage](https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/calspec) is updated, 
it might be necessary to rebuild the `calspec_data/calspec.csv` table and the cache:
```
from getCalspec.rebuild import rebuild_tables, rebuild_cache
rebuild_tables()
rebuild_cache()
```