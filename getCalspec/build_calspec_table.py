"""
This script read an incomplete table (simbad_names.org) that contains
the simbad identifiers of the calspec stars, gets the star coordinates
from the simbad web site and dumps an index.

This index is the file that will be used by the saunerie interface to
CALSPEC.
"""

import os
import os.path as op 
import numpy as np
import glob 

from astroquery.simbad import Simbad
from saunerie.constants import hmstodeg, dmstodeg
from croaks import NTuple 

# we need the spectral type and proper motion information
try:
    Simbad.add_votable_fields('pm')
    Simbad.add_votable_fields('sp')
except:
    pass

# read the initial index 
calspec = NTuple.fromorg('simbad_names.org')

for i,nm in enumerate(calspec['SIMBAD_NAME']):
    print ' (*) processing ', i, nm
    r = Simbad.query_object(nm.strip())
    if r is None:
        print " (-) Not found in SIMBAD: ", nm 
        continue
    
    calspec['RA'][i] = hmstodeg(*map(float, r['RA'][0].split()))
    calspec['DEC'][i] = dmstodeg(*map(float, r['DEC'][0].split()))
    calspec['PMRA'][i] = float(r['PMRA'][0])
    calspec['PMDEC'][i] = float(r['PMDEC'][0])
    calspec['SP_TYPE'][i] = r['SP_TYPE'][0]
    if calspec['FILENAME'][i] == 'nan':
        pattern = '*' + '*'.join(calspec['CALSPEC_NAME'][i].lower().split()) + '*'
        pattern = pattern.replace(' ', 'd').replace('+', '_').replace('-', '_')
        filenames = glob.glob(pattern)
        #        print calspec['FILENAME'][i], pattern, filenames 
        if len(filenames) == 1:
            #            print filenames[0]
            calspec['FILENAME'][i] = filenames[0]

# PMRA and PMDEC 
for key in ['PMRA', 'PMDEC']:
    idx = np.isnan(calspec[key])
    calspec[key][idx] = 0.
idx = calspec['FLAG'] == 'nan'
calspec['FLAG'][idx] = ''
idx = calspec['MODEL_FILENAME'] == 'nan'
calspec['MODEL_FILENAME'][idx] = ''

calspec.toorg('index.org')

