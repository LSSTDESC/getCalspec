import numpy as np
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy import units as u
import pandas as pd
import urllib

CALSPEC_URL = "https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/calspec.html"

tables = pd.read_html(CALSPEC_URL)
for table in tables:
    if isinstance(table.columns, pd.MultiIndex):
        table.columns = table.columns.droplevel(1)  # drop mulitindex columns
    table.rename(columns={"Star Name": "Star name"}, inplace=True)
    # table.set_index("Star name", inplace=True)
    if r"[1]" in table.index:
        table = table.drop(index=r"[1]")

df = tables[0]
print(df.columns)
if len(tables) > 1:
    print(tables[1])
    df = df.append(tables[1])
    df = pd.merge(df, tables[2], on="Star name", how='left')
df.to_csv('calspec.csv')
df.to_pickle('calspec.pkl')


