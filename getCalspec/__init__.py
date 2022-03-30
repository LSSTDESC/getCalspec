import numpy as np
import pandas as pd
import os
from urllib import request
from astropy.io import fits
from astropy import units as u
from astropy.table import Table

CALSPEC_ARCHIVE = r"https://archive.stsci.edu/hlsps/reference-atlases/cdbs/current_calspec/"


class Calspec:
    """ The Calspec class contains all properties from a Calspec star read from
    https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/calspec.html
    loaded from its Simbad name.

    """

    def __init__(self, calspec_label):
        """

        Parameters
        ----------
        calspec_label: str
            The Simbad name of the calspec star

        Examples
        --------
        >>> from astroquery.simbad import Simbad
        >>> simbad = Simbad.query_object("eta1 dor")
        >>> c = Calspec(simbad["MAIN_ID"][0])
        >>> print(c)   #doctest: +ELLIPSIS
           Star_name...
        ...  ETA1 DOR...
        """
        self.label = calspec_label.upper()
        df = pd.read_pickle("../tables/calspec.pkl")
        row = df[(df["Astroquery_Name"] == self.label) | (df["Simbad_Name"] == self.label) | (df["Star_name"] == self.label)]
        self.query = row
        for col in row.columns:
            setattr(self, col, row[col].values[0])
        self.wavelength = None
        self.flux = None
        self.stat = None
        self.syst = None

    def __str__(self):
        return self.query.to_string()

    def get_spectrum_table(self, output_directory="./calspec"):
        """

        Returns
        -------
        table: astropy.table.Table
            Astropy table containing all data for given Calspec star.

        Examples
        --------
        >>> c = Calspec("eta1 dor")
        >>> t = c.get_spectrum_table()
        >>> print(t)   #doctest: +ELLIPSIS
        WAVELENGTH...
        ANGSTROMS...

        """
        if not os.path.isdir(output_directory):
            os.mkdir(output_directory)
        spectrum_file_name = str(self.Name+self.STIS+".fits")
        output_file_name = os.path.join(output_directory, spectrum_file_name)
        if not os.path.isfile(output_file_name):
            request.urlretrieve(CALSPEC_ARCHIVE+spectrum_file_name, output_file_name)
        t = Table.read(output_file_name)
        return t

    def get_spectrum_numpy(self):
        """Make a dictionnary of numpy arrays with astropy units from Calspec FITS file.

        Returns
        -------
        table: dict
            A dictionnary with the FITS table columns and thier astropy units.

        Examples
        --------
        >>> c = Calspec("eta1 dor")
        >>> t = c.get_spectrum_numpy()
        >>> print(t)   #doctest: +ELLIPSIS
        {'WAVELENGTH': <Quantity [...

        """
        t = self.get_spectrum_table()
        d = {}
        for k in range(0, 4):
            d[t.colnames[k]] = np.copy(t[t.colnames[k]][:])
            if t[t.colnames[k]].unit == "ANGSTROMS":
                d[t.colnames[k]] *= u.nanometer
            elif t[t.colnames[k]].unit == "FLAM":
                d[t.colnames[k]] *= u.erg / u.second / u.cm**2 / u.angstrom
        return d









if __name__ == "__main__":
    import doctest

    doctest.testmod()
