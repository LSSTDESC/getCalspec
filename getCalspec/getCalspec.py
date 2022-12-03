import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import warnings
from urllib.error import URLError
from astropy import units as u
from astropy.table import Table
from astropy.utils.data import download_file


__all__ = ['get_calspec_keys',
           'is_calspec',
           'Calspec',
           ]


CALSPEC_ARCHIVE = r"https://archive.stsci.edu/hlsps/reference-atlases/cdbs/current_calspec/"


def getCalspecDataFrame():
    dirname = _getPackageDir()
    filename = os.path.join(dirname, "../calspec_data/calspec.csv")
    df = pd.read_csv(filename)
    return df


def _getPackageDir():
    """This method must live in the top level of this package, so if this
    moves to a utils file then the returned path will need to account for that.
    """
    dirname = os.path.dirname(__file__)
    return dirname


def get_calspec_keys(star_label):
    """Return the DataFrame keys if a star name corresponds to a Calspec entry
    in the tables.

    Parameters
    ----------
    star_label: str
        The star name.

    Returns
    -------
    keys: array_like
        The DataFrame keys corresponding to the star name.

    Examples
    --------
    >>> get_calspec_keys("eta1 dor")   #doctest: +ELLIPSIS
    0      False
    1      False
    ...
    """
    label = star_label.upper()
    df = getCalspecDataFrame()
    return (df["Astroquery_Name"] == label) | (df["Simbad_Name"] == label) | (df["Star_name"] == label) \
        | (df["Alternate_Simbad_Name"] == label) | (df["Alt_Star_name"] == label)


def is_calspec(star_label):
    """Test if a star name corresponds to a Calspec entry in the tables.

    Parameters
    ----------
    star_label: str
        The star name.

    Returns
    -------
    is_calspec: bool
        True is star name is in Calspec table.

    Examples
    --------
    >>> is_calspec("eta1 dor")
    True
    >>> is_calspec("eta dor")
    True
    """
    return np.any(get_calspec_keys(star_label.upper()))


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
        >>> c = Calspec("* eta01 Dor")
        >>> print(c)   #doctest: +ELLIPSIS
        eta1dor
        >>> c = Calspec("etta dor")   #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        KeyError: 'ETTA DOR not found in Calspec tables.'
        >>> c = Calspec("mu col")
        >>> c = Calspec("* mu. Col")
        >>> print(c)   #doctest: +ELLIPSIS
        mucol
        """
        self.label = calspec_label.upper()
        test = is_calspec(self.label)
        if not test:
            raise KeyError(f"{self.label} not found in Calspec tables.")
        df = getCalspecDataFrame()
        row = df[get_calspec_keys(self.label)]
        self.query = row
        for col in row.columns:  # sets .STIS and .Name attributes
            setattr(self, col, row[col].values[0])
        self.wavelength = None
        self.flux = None
        self.stat = None
        self.syst = None

    def __str__(self):
        return self.Name

    def _santiseName(self, name):
        """Special casing for cleaning up names in the table for use in
        downloading.
        """
        name = name.lower()
        if name == 'sdss151421':
            name = 'sdssj151421'
        return name

    def get_spectrum_fits_filename(self):
        """Downloads the data or pulls it from the cache if available.

        Examples
        --------
        >>> c = Calspec("eta1 dor")
        >>> c.get_spectrum_fits_filename()  #doctest: +ELLIPSIS
        '...astropy/cache/download/url/...'

        """
        spectrum_file_name = self._santiseName(self.Name) + self.STIS.replace('*', '') + ".fits"
        url = CALSPEC_ARCHIVE + spectrum_file_name
        try:
            output_file_name = download_file(url, cache=True)
        except URLError as e:
            raise RuntimeError(f"Failed to get data for {self.Name} from {url}") from e
        return output_file_name

    def get_spectrum_table(self):
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
        output_file_name = self.get_spectrum_fits_filename()
        with warnings.catch_warnings():  # calspec fits files use non-astropy units everywhere
            warnings.filterwarnings("ignore", message='.*did not parse as fits unit')
            t = Table.read(output_file_name)
        return t

    def get_spectrum_numpy(self):
        """Make a dictionary of numpy arrays with astropy units from Calspec
        FITS file.

        Returns
        -------
        table: dict
            A dictionary with the FITS table columns and their astropy units.

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
                d[t.colnames[k]] *= u.angstrom
            elif t[t.colnames[k]].unit == "NANOMETERS":
                d[t.colnames[k]] *= u.nanometer
            elif t[t.colnames[k]].unit == "FLAM":
                d[t.colnames[k]] *= u.erg / u.second / u.cm**2 / u.angstrom
        return d

    def plot_spectrum(self, xscale="log", yscale="log"):
        """Plot Calspec spectrum.

        Examples
        --------
        >>> c = Calspec("eta1 dor")
        >>> c.plot_spectrum()

        """
        t = self.get_spectrum_numpy()
        _ = plt.figure()
        plt.errorbar(t["WAVELENGTH"].value, t["FLUX"].value, yerr=t["STATERROR"].value)
        plt.grid()
        plt.yscale(yscale)
        plt.xscale(xscale)
        plt.title(self.label)
        plt.xlabel(rf"$\lambda$ [{t['WAVELENGTH'].unit}]")
        plt.ylabel(rf"Flux [{t['FLUX'].unit}]")
        plt.show()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
