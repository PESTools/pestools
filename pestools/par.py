# -*- coding: utf-8 -*-
"""
Created on Wed Sep 09 13:16:06 2015

@author: egc
"""

import numpy as np
import pandas as pd
import os


class Par(object):

    def __init__(self, basename=None, par_set=None):

        ''' Create Par class that works with data from a .par file

        Parameters
        ----------
        basename : str, optional
            basename for PEST control file, if full path not provided the 
            current working directory is assumed.
            
        par_set : Int, optional
            .par file number if multiple .par files writen with PEST.  If not
            provided then uses basename.par for the par file.  If provided uses
            basename.par.par_set as the par file
            
        Attributes
        ----------
        df : Pandas DataFrame
            DataFrame of par file.  Index entries of the DataFrame
            are the parameter names.  The DataFrame has two columns:
            1) Parameter Group and 2) Sensitivity
            
        '''
        
        if basename is not None:
            self.basename = os.path.split(basename)[-1].split('.')[0]
            self.directory = os.path.split(basename)[0]
            if len(self.directory) == 0:
                self.directory = os.getcwd() 
                
        if par_set is not None:
            self.par_file = os.path.join(self.directory, self.basename + '.par.%d' % (par_set))
        else:
            self.par_file = os.path.join(self.directory, self.basename + '.par')
         
        self.df = self.load_par_file()
        
    def load_par_file(self):        
        f = open(self.par_file, 'r')
        header = f.readline()
        df = pd.read_csv(f, header = None, names = ['PARNME', 'PARVAL', 'SCALE', 'OFFSET'],
                         sep="\s+")
        df.index = df.PARNME
        return df
    def parval(self, parnme):
        parval = self.df.ix[parnme]['PARVAL']
        return parval
        
            
            