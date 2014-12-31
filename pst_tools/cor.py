# -*- coding: utf-8 -*-

from pst import Pest
import numpy as np
import pandas as pd
import plots
import warnings

class Cor(Pest):

    def __init__(self, basename, res_file=None, jco_df=None):
        Pest.__init__(self, basename)

        ''' Create ParSen class

        Parameters
        ----------
        basename : str
            basename for PEST control file, if pull path not provided the 
            current working directory is assumed.
            
        jco_df : DataFrame, optional,
            Pandas DataFrame of the jacobian. If not provided then it will be
            read in based on base name of PEST control file. Providing a
            jco_df offers some efficiencies if working interactively.
            Otherwise the jco is read in every time Cor class is initialized.
            Jco_df is an attribute of the Jco class
            
        res_file : str, optional
            Path to a .res  or .rei file to use to define the weights used to 
            calculate the parameter sensitivity.  If not provided it will look
            for basename+'.res'.  Weights are not taken from PEST control file
            (.pst) because regularization weights in PEST conrtrol file do
            not reflect the current weights.



        Attributes
        ----------

        Methods
        -------

        Notes
        ------


        '''
        
        # Check if reularization is used and warn the user
        # Note: Might want to come up with some better warning
        if 'regularisation' in open(self.pstfile).read():
            warnings.warn('Regularization used, statistical matrices may not applicable')
            
        if jco_df is None:
            jco_df = self._load_jco()
        self._read_par_data()
        self._read_obs_data()
      
        if res_file is None:
            res_file = self.pstfile.rstrip('pst')+'res'
        # Check if .res or .rei
        try:
            check = open(res_file, 'r')
        except:           
            raise IOError('Not able to open .res or .rei file: %s (res_file)')            
        line_num = 0
        while True:
            current_line = check.readline()
            if "name" in current_line.lower() and "residual" in current_line.lower():
                break
            else:
                line_num += 1
        res_df = pd.read_csv(res_file, skiprows=line_num, delim_whitespace=True)
        res_df.index = [n.lower() for n in res_df['Name']]
        
        pars = jco_df.columns.values
        phi = sum(res_df['Weight*Residual']**2)
        weights = res_df['Weight'].values
        q = np.diag(np.diag(np.tile(weights**2, (len(weights), 1))))
        
        # Calc Covarience Matrix
        # See eq. 2.17 in PEST Manual
        # Note: Number of observations are number of non-zero weighted observations
        cov = np.dot((phi/(np.count_nonzero(weights)-len(pars))),
                     (np.linalg.inv(np.dot(np.dot(jco_df.values.T, q),jco_df.values))))
        
        # Put into dataframe
        cov_df = pd.DataFrame(cov, index = pars, columns = pars)
        
        # Calc correlation matrix   
        d = np.diag(cov)
        cor = cov/np.sqrt(np.multiply.outer(d,d))
        # Put into dataframe
        cor_df = pd.DataFrame(cor, index = pars, columns = pars)
        
        # Calc eigenvalues, eigenvectors
        eig_values, eig_vectors = np.linalg.eigh(cov)
        #Put eig_vectors into dataframe
        eig_vectors_df = pd.DataFrame(eig_vectors, index = pars)
        
        
        self.df = cor_df
        self.array = cor
        self.eig_vectors = eig_vectors_df
        self.eig_values = eig_values
        self.cov_df = cov_df
#        
if __name__ == '__main__':
    cor = Cor(r'C:\Users\egc\pest_tools-1\cc\Columbia.pst')