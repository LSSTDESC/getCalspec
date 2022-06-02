from astroquery.simbad import Simbad
import pandas as pd
import warnings

CALSPEC_URL = "https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/calspec.html"


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
    for i, row in df.iterrows():
        if row["Star name"] == "ETA1 DOR":
            df.at[i, "Alt Star name"] = "ETA DOR"


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


tables = pd.read_html(CALSPEC_URL)
for table in tables:
    if isinstance(table.columns, pd.MultiIndex):
        table.columns = table.columns.droplevel(1)  # drop mulitindex columns
    table.rename(columns={"Star Name": "Star name"}, inplace=True)
    # table.set_index("Star name", inplace=True)
    if r"[1]" in table.index:
        table = table.drop(index=r"[1]")

df = tables[0]
if len(tables) > 1:
    df = df.append(tables[1])
    df = pd.merge(df, tables[2], on="Star name", how='left')

add_astroquery_id(df)
add_alt_star_name(df)
clean_table(df)

df.to_csv('calspec.csv')
df.to_pickle('calspec.pkl')
