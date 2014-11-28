# -*- coding: utf-8 -*-
"""
Created on Fri Nov 28 10:27:13 2014

@author: egc
"""

from _pst import Pst
#import numpy as np
#import pandas as pd

class Jco(Pst):
    '''
        Attributes
    ----------
    jco_df : Pandas Data Frame

    '''
    def __init__(self, pst_path):
        super(Jco, self).__init__(pst_path)
        self.jco_df = self._load_jco()
        

if __name__ == '__main__':
    jco = Jco(r'C:\Anaconda\Lib\site-packages\pest_tools\Examples\example.pst')
        