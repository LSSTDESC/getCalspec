from astroquery.simbad import Simbad
import os
import glob
import pandas as pd
import warnings
import logging
from io import StringIO
from astropy.utils.data import download_file
from astropy.io import fits
from bs4 import BeautifulSoup
import urllib.request


from getCalspec import _getPackageDir, getCalspecDataFrame, Calspec, CALSPEC_ARCHIVE

__all__ = [
    "rebuild_tables",
    "rebuild_cache",
    "update_history_table",
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
            simbad = Simbad.query_object(row["Star_name"], wildcard=False)
            if simbad is None or len(simbad) == 0:
                simbad = Simbad.query_object(row["Star_name"].lower(), wildcard=False)
            if (
                (simbad is None or len(simbad) == 0)
                and pd.notna(row["Simbad_Name"])
                and row["Simbad_Name"] != ""
            ):
                simbad = Simbad.query_object(row["Simbad_Name"])
            if (simbad is None or len(simbad) == 0) and pd.notna(row["Name"]) and row["Name"] != "":
                simbad = Simbad.query_object(row["Name"])
            if (simbad is None or len(simbad) == 0) and "NGC6681" in row["Star_name"]:
                simbad = Simbad.query_object("NGC6681")
            id_key = "MAIN_ID"
            if "main_id" in simbad.colnames:
                id_key = "main_id"
            if simbad is not None and len(simbad) > 0:
                names.append(simbad[id_key][0].upper())
            else:
                names.append("")
    df["Astroquery_Name"] = names


def add_alt_star_name(df):
    """Operates on the dataframe in-place, adding the alternate names
    for each star (row), and removes spaces from HD stars."""
    name_columns = [name for name in df.columns if "name" in name.lower()]
    for i, row in df.iterrows():
        if row["Star_name"] == "ETA1 DOR":
            df.at[i, "Alt_Star_name"] = "ETA DOR"
        if row["Star_name"] == "ETA UMA":
            df.at[i, "Alt_Star_name"] = "Alkaid"
    for i, row in df.iterrows():
        all_names = None
        for name in name_columns:
            if pd.isna(row[name]) or row[name] == "":
                continue
            all_names = Simbad.query_objectids(row[name])
            if all_names is not None and len(all_names) > 0:
                break
        if all_names is not None:
            id_key = "ID"
            if "id" in all_names.colnames:
                id_key = "id"
            for name in list(all_names[id_key]):
                if name.startswith("HD"):
                    df.at[i, "HD_name"] = name.replace(" ", "")
                if name.startswith("Gaia DR2"):
                    df.at[i, "source_id"] = str(name.split(" ")[-1])
                if name.startswith("Gaia DR3"):
                    df.at[i, "source_id"] = str(name.split(" ")[-1])


def clean_table(df):
    # Build a mapping of all column renames
    rename_map = {}
    for col in df.columns:
        new_col = col
        if "*" in new_col:
            new_col = new_col.replace("*", "")
        if "mas/yr" in new_col:
            new_col = new_col.replace("_(mas/yr)", "")
        if "2000" in new_col:
            new_col = new_col.replace("_(2000)", "_J2000")
        if "." in new_col:
            new_col = new_col.replace(".", "")
        if "-" in new_col:
            new_col = new_col.replace("-", "_")
        # Replace both regular space and non-breaking space (\\xa0)
        if " " in new_col or "\xa0" in new_col:
            new_col = new_col.replace(" ", "_").replace("\xa0", "_")
        if new_col != col:
            rename_map[col] = new_col

    # Apply all renames at once
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    df.set_index("Star_name", inplace=True)
    if "[1]" in df.index:
        df.drop(index="[1]", inplace=True)
    df.reset_index(drop=False, inplace=True)
    # remove _stis from Model column and put it in STIS column
    for index, row in df.iterrows():
        if isinstance(row["Model"], str) and "stis" in row["Model"]:
            df.at[index, "STIS"] = row["Model"]
            df.at[index, "Model"] = ""
        if isinstance(row["Model"], str) and "*" in row["Model"]:
            df.at[index, "Model"] = df.at[index, "Model"].replace("*", "")
        if isinstance(row["STIS"], str) and "*" in row["STIS"]:
            df.at[index, "STIS"] = df.at[index, "STIS"].replace("*", "")
        if isinstance(row["Name"], str):
            df.at[index, "Name"] = df.at[index, "Name"].lower()


def rebuild_tables(gaia_data_release="DR3"):
    """Rebuild calspec.csv table.

    Examples
    --------
    >>> rebuild_tables()
    """
    logger = logging.getLogger()
    logger.warning(
        "Calling this function rebuilds the csv file,"
        " which supplies which the fits file versions used to get the CALSPEC"
        " spectra. It should be called when you would like to pull in new spectra,"
        " though preferably this would be done by the package maintainers as part of"
        " a new release, such that the versions of the spectra remain tied to the"
        " package version."
    )

    webpage = urllib.request.urlopen(CALSPEC_TABLE_URL).read()
    soup = BeautifulSoup(webpage, "html.parser")
    # clean superscripts in table
    for x in soup.find_all("sup"):
        x.extract()
    # find tables
    web_tables = soup.find_all("table")
    tables = []
    # convert to pd.DataFrame
    for web_table in web_tables:
        tables.append(pd.read_html(StringIO(str(web_table)))[0])
    # format tables
    clean_tables = []
    for table in tables:
        if isinstance(table.columns, pd.MultiIndex):
            table.columns = [
                col[0] if "Unnamed" in col[1] else "_".join(col).strip("_") for col in table.columns.values
            ]
        table.columns = [col.replace("*", "").replace(" ", "_").replace("\xa0", "_") for col in table.columns]
        table.rename(columns={"Star_Name": "Star_name"}, inplace=True)
        # table.set_index("Star name", inplace=True)
        if r"[1]" in table.index:
            table = table.drop(index=r"[1]")
        if r"[1]" in table["Star_name"].values:
            table = table[table["Star_name"] != r"[1]"]
        clean_tables.append(table)

    df = clean_tables[0]
    if len(clean_tables) > 1:
        df = pd.concat([df, clean_tables[1]])
        df = pd.merge(df, clean_tables[2], on="Star_name", how="left")

    add_astroquery_id(df)
    add_alt_star_name(df)
    clean_table(df)

    packageDir = _getPackageDir()
    csvFilename = os.path.join(packageDir, "../calspec_data", "calspec.csv")
    csvFilename = os.path.abspath(csvFilename)
    df.to_csv(csvFilename)
    logger.warning(f"Successfully wrote new .csv file to {csvFilename}")


def update_history_table(force=False):
    """Update history.csv table.

    Examples
    --------
    >>> update_history_table(force=False)
    """
    packageDir = _getPackageDir()
    csvFilename = os.path.abspath(os.path.join(packageDir, "../calspec_data", "history.csv"))

    if os.path.isfile(csvFilename) and not force:
        df = pd.read_csv(csvFilename)
    else:
        df = pd.DataFrame(data={"Filename": [], "Name": [], "Extension": [], "Date": []})
    df.set_index("Filename", inplace=True)

    urls = _getFileListFromURL(CALSPEC_ARCHIVE, ext=".fits")
    for url in urls:
        filename = os.path.basename(url)
        if not force and filename in df.index:
            continue
        output_file_name = download_file(url, cache=True)
        header = fits.getheader(output_file_name)
        date = None
        if "HISTORY" in header:
            for line in header["HISTORY"]:
                if "written by" in line.lower():
                    words = line.split(" ")
                    for w in words:
                        if w.count("-") == 2:
                            date = w
        elif "DATE" in header:
            date = header["DATE"]
        else:
            raise KeyError(
                f"HISTORY and DATE keys are absent from header of {filename=}. Cannot get file creation date."
            )
        is_key = False
        for key in ["mod", "stis", "fos", "nic"]:
            if key in filename:
                words = filename.split("_")
                for k, w in enumerate(words):
                    if key in w:
                        calspec_name = filename.split("_" + words[k])[0]
                        is_key = True
                        break
                break
        if not is_key:
            # just a suffix with _00X.fits
            calspec_name = "_".join(filename.split("_")[:-1])
        ext = filename.split(calspec_name)[-1]
        ext = ext.split(".")[0]
        row = {"Filename": filename, "Name": calspec_name, "Extension": ext, "Date": date}
        tmp_df = pd.DataFrame([row])
        tmp_df.set_index("Filename", inplace=True)
        df = pd.concat([df, tmp_df])
    df.to_csv(csvFilename)


def _getFileListFromURL(url, ext=".fits"):
    page = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(page, "html.parser")
    return [
        os.path.join(url, node.get("href")) for node in soup.find_all("a") if node.get("href").endswith(ext)
    ]


def _deleteCache():
    dataPath = os.path.join(_getPackageDir(), "../calspec_data")
    dataPath = os.path.abspath(dataPath)
    # *stis* included for extra safety in case other fits files are present
    files = glob.glob(os.path.join(dataPath, "*stis*.fits"))
    for file in files:
        os.remove(file)


def download_all_data():
    df = getCalspecDataFrame()
    for row in df["Star_name"]:
        print(f"Downloading data for {row}...")
        c = Calspec(row)
        _ = c.get_spectrum_numpy()  # triggers the download
    print("Finished downloading all data.")


def rebuild_cache():
    _deleteCache()
    download_all_data()
