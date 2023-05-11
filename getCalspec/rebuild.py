from astroquery.simbad import Simbad
import os
import glob
import pandas as pd
import warnings
import logging
from bs4 import BeautifulSoup
import urllib.request

from .getCalspec import _getPackageDir, getCalspecDataFrame, Calspec

__all__ = ["rebuild_tables",
           "rebuild_cache",
           "download_all_data",
           ]

# the address of the page which contains the tables listing the most recent
# versions for each star's data
CALSPEC_TABLE_URL = (
    "https://www.stsci.edu/hst/instrumentation/"
    "reference-data-for-calibration-and-tools/"
    "astronomical-catalogs/calspec.html"
)


def add_astroquery_id(df):
    names = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i, row in df.iterrows():
            simbad = Simbad.query_object(row["Star name"], wildcard=False)
            if simbad is None:
                simbad = Simbad.query_object(row["Star name"].lower(), wildcard=False)
            if simbad is None and row["Simbad Name"] != "":
                simbad = Simbad.query_object(row["Simbad Name"])
            if simbad is None and row["Name"] != "":
                simbad = Simbad.query_object(row["Name"])
            if simbad is None and "NGC6681" in row["Star name"]:
                simbad = Simbad.query_object("NGC6681")
            if simbad is not None:
                names.append(simbad["MAIN_ID"][0].upper())
            else:
                names.append('')
    df["Astroquery Name"] = names


def add_alt_star_name(df):
    name_columns = [name for name in df.columns if "name" in name.lower()]
    print(name_columns)
    for i, row in df.iterrows():
        if row["Star name"] == "ETA1 DOR":
            df.at[i, "Alt Star name"] = "ETA DOR"
        else:
            all_names = None
            for name in name_columns:
                all_names = Simbad.query_objectids(row[name])
                if all_names is not None and len(all_names) > 0:
                    break
            if all_names is not None:
                for name in list(all_names['ID']):
                    if "HD" in name:
                        df.at[i, "Alt Star name"] = name.replace(' ','')
            else:
                continue



def clean_table(df):
    for col in df.columns:
        if "*" in col:
            df.rename(columns={col: col.replace("*", "")}, inplace=True)
    for col in df.columns:
        if "mas/yr" in col:
            df.rename(columns={col: col.replace(" (mas/yr)", "")}, inplace=True)
    for col in df.columns:
        if "." in col:
            df.rename(columns={col: col.replace(".", "")}, inplace=True)
    for col in df.columns:
        if "-" in col:
            df.rename(columns={col: col.replace("-", "_")}, inplace=True)
    for col in df.columns:
        if " " in col:
            df.rename(columns={col: col.replace(" ", "_")}, inplace=True)
    df.set_index("Star_name", inplace=True)
    df.drop(index="[1]", inplace=True)
    df.reset_index(drop=False, inplace=True)
    # remove _stis from Model column and put it in STIS column
    for index, row in df.iterrows():
        if type(row["Model"]) is str and "stis" in row["Model"]:
            df.at[index, "STIS"] = row["Model"]
            df.at[index, "Model"] = ""


def rebuild_tables():
    logger = logging.getLogger()
    logger.warning("Calling this function rebuilds the csv file,"
                   " which supplies which the fits file versions used to get the CALSPEC"
                   " spectra. It should be called when you would like to pull in new spectra,"
                   " though preferably this would be done by the package maintainers as part of"
                   " a new release, such that the versions of the spectra remain tied to the"
                   " package version.")

    webpage = urllib.request.urlopen(CALSPEC_TABLE_URL).read()
    soup = BeautifulSoup(webpage, 'html.parser')
    # clean superscripts in table
    for x in soup.find_all('sup'):
        x.extract()
    # find tables
    web_tables = soup.find_all("table")
    tables = []
    # convert to pd.DataFrame
    for web_table in web_tables:
        tables.append(pd.read_html(str(web_table))[0])
    # format tables
    for table in tables:
        if isinstance(table.columns, pd.MultiIndex):
            table.columns = table.columns.droplevel(1)  # drop multiindex columns
        table.rename(columns={"Star Name": "Star name"}, inplace=True)
        # table.set_index("Star name", inplace=True)
        if r"[1]" in table.index:
            table = table.drop(index=r"[1]")

    df = tables[0]
    if len(tables) > 1:
        df = pd.concat([df, tables[1]])
        df = pd.merge(df, tables[2], on="Star name", how='left')

    add_astroquery_id(df)
    add_alt_star_name(df)
    clean_table(df)

    packageDir = _getPackageDir()
    csvFilename = os.path.join(packageDir, '../calspec_data', 'calspec.csv')
    csvFilename = os.path.abspath(csvFilename)
    df.to_csv(csvFilename)
    print(f'Successfully wrote new .csv file to {csvFilename}')


def _deleteCache():
    dataPath = os.path.join(_getPackageDir(), "../calspec_data")
    dataPath = os.path.abspath(dataPath)
    # *stis* included for extra safety in case other fits files are present
    files = glob.glob(os.path.join(dataPath, '*stis*.fits'))
    for file in files:
        os.remove(file)


def download_all_data():
    df = getCalspecDataFrame()
    for row in df["Star_name"]:
        print(f"Downloading data for {row}...")
        c = Calspec(row)
        _ = c.get_spectrum_numpy()  # triggers the download
    print('Finished downloading all data.')


def rebuild_cache():
    _deleteCache()
    download_all_data()
