# getCalspec
Python package to load Calspec spectra.

The main function query the Calspec table located in `tables/calspec.pkl` 
to download spectrum FITS files from STSC archive https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/calspec.html

Example
```
c = Calspec("eta1 dor")
c.get_spectrum_fits()  # download the fits file
c.get_spectrum_table()  # download and return an Astropy table
c.get_spectrum_numpy()  # download and return a dictionnary of numpy arrays with units
c.plot_spectrum()  # download and plot the spectrum
```

The script `tables/extract_calspec_tables_from_web.py` update the calspec tables, reading the STSC webpage.