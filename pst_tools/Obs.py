__author__ = 'aleaf'

import sys
sys.path.append('../pst_tools')
from pst import *
import pandas as pd

import numpy as np

class Obs(Pest):
    """
    Class for working with observations


    Attributes
    ----------

    """

    def __init__(self, basename, run_folder=None):

        Pest.__init__(self, basename)

        self._read_obs_data()

        self._new_obs_data = pd.DataFrame()


    def replace(self, filepath, sheetname='Sheet1'):
        """
        Replace observation data section of Pest control from csv or Excel spreadsheet.
        Should we require a header or add extra code to make it work with or without a header?

        Parameters
        ----------
        filepath: string
            csv file or Excel document containing new observation data section for PEST control file
        sheetname: string, optional
            name of spreadsheet in Excel document to read
        """
        if filepath.split('.')[-1][:2] == 'xls':
            self._new_obs_data = pd.read_excel(filepath, sheetname)

        else:
            self._new_obs_data = pd.read_csv(filepath)




        return


    def mikes_weighting_routine(self):
        # Not implemented yet
        return