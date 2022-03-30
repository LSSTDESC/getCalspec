"""
This script read an incomplete table (simbad_names.org) that contains
the simbad identifiers of the calspec stars, gets the star coordinates
from the simbad web site and dumps an index.

This index is the file that will be used by the saunerie interface to
CALSPEC.
"""

import numpy as np
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy import units as u
import pandas as pd
import urllib


CALSPEC_LINK_LATEST = "https://archive.stsci.edu/hlsps/reference-atlases/cdbs/current_calspec/"
lines = str(urllib.request.urlopen(CALSPEC_LINK_LATEST).read()).split(r'\n')
filenames = []
for line in lines:
    if ".fits" not in line:
        continue
    filenames.append(line.split('"')[1])

print(urllib.request.urlopen("https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/calspec.html").read())

# we need the spectral type and proper motion information
try:
    Simbad.add_votable_fields('pm')
    Simbad.add_votable_fields('sp')
except:
    pass

# read the initial index 
calspec = pd.read_csv('simbad_names.org', sep=r'\s*\|\s*', engine="python").iloc[:, 1:-1]

for i, row in calspec.iterrows():
    nm = row["SIMBAD_NAME"]
    print(f' {i} {nm} processing ')
    r = Simbad.query_object(nm.strip())
    if r is None:
        print(f" {nm} not found in SIMBAD")
        continue

    c = SkyCoord(r['RA'][0] + ' ' + r['DEC'][0], unit=(u.hourangle, u.deg))
    calspec.at[i, 'RA'] = c.ra.deg
    calspec.at[i, 'DEC'] = c.dec.deg
    for key in ['PMRA', 'PMDEC']:
        if np.isnan(r[key][0]) or np.ma.is_masked(r[key][0]):
            calspec.at[i, key] = 0
        else:
            calspec.at[i, key] = float(r[key][0])
    calspec.at[i, 'SP_TYPE'] = r['SP_TYPE'][0]
    pattern = '*' + '*'.join(calspec.at[i, 'CALSPEC_NAME'].lower().split()) + '*'
    pattern = pattern.replace(' ', 'd').replace('+', '_').replace('-', '_')
    if calspec.at[i, 'FILENAME'] == 'nan':
        for filename in filenames:
            if pattern in filename:
                calspec.at[i, 'FILENAME'] = filename
                break

calspec.to_pickle('calspec.pkl')

