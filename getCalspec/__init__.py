import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astroquery.simbad import Simbad


class Calspec:
    """ The Calspec class contains all properties from a Calspec star read from
    https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/calspec.html
    loaded from its Simbad name.

    """

    def __init__(self, simbad_id):
        """

        Parameters
        ----------
        simbad_id: str
            The Simbad name of the calspec star

        Examples
        --------
        >>> from astroquery.simbad import Simbad
        >>> simbad = Simbad.query_object("eta1 dor")
        >>> c = Calspec(simbad["MAIN_ID"][0])
        """
        df = pd.read_pickle("../tables/calspec.pkl")
        row = df[(df["Astroquery Name"] == simbad_id) | (df["Simbad Name"] == simbad_id) | (df["Star name"] == simbad_id)]
        self.query = row
        for col in row.columns:
            setattr(self, col.replace(" ", "_"), row[col].values)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
