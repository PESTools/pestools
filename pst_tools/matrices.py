# -*- coding: utf-8 -*-

from pst import Pest
import numpy as np
import pandas as pd
import plots
import os
import warnings

class Matrices(Pest):

    def __init__(self, basename, res_file=None, jco_df=None):
        Pest.__init__(self, basename)

        ''' Create Matrices class

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
            (.pst)

        Attributes
        ----------
        cov : array
            array of the parameter covariance matrix
        cov_df : DataFrame
            DataFrame of the parameter covariance matrix
        cor : array
            array of the correlation coefficient matrix
        cor_df : DataFrame
            DataFrame of the correlation coefficient matrix
        eig_values : array
            array of the eigenvalues
        eig_vectors : array
            array of the eigenvectors matrix
        eig_vectors_df : DataFrame
            DataFrame of the eigenvectors matrix

        Methods
        -------

        Notes
        ------
        As noted in Section 5.3.6 of the PEST manual, there may be slight
        differences between matrixes recorded to the final matrix file (.mtt) 
        from PEST and those listed in the run record file at the end of a PEST 
        run. The same issue applies here.  "Reference variance" used to record 
        values in the PEST matrix (.mtt) file is conputed using the objective 
        function computed from the previous iteration.  The covariance matrices
        recorded in the run record uses the best objective function value.
        Covariance calculated with pestools uses the final .res file and .jco,
        or any alternative jco, .rei, or .res if provided.  
        The .mtt and .rec files are not used by  pestools.
        


        '''
        
        # Check if reularization is used and warn the user
        # Note: Might want to come up with some better warning
#        if 'regularisation' in open(self.pstfile).read():
#            warnings.warn('Regularization used, statistical matrices may not applicable')
            
        if jco_df is None:
            jco_df = self._load_jco()
      
        if res_file is None:
            res_file = os.path.splitext(self.pstfile)[0]+'.res'
            #res_file = self.pstfile.rstrip('pst')+'res'
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
        self.cov = np.dot((phi/(np.count_nonzero(weights)-len(pars))),
                     (np.linalg.inv(np.dot(np.dot(jco_df.values.T, q),jco_df.values))))        
        # Put into dataframe
        self.cov_df = pd.DataFrame(self.cov, index = pars, columns = pars)
        
        # Calc correlation matrix   
        d = np.diag(self.cov)
        self.cor = self.cov/np.sqrt(np.multiply.outer(d,d))
        # Put into dataframe
        self.cor_df = pd.DataFrame(self.cor, index = pars, columns = pars)
        
        # Calc eigenvalues, eigenvectors
        self.eig_values, self.eig_vectors = np.linalg.eigh(self.cov, UPLO = 'U')
        #Put eig_vectors into dataframe
        self.eig_vectors_df = pd.DataFrame(self.eig_vectors, index = pars)
        


#        
if __name__ == '__main__':
    #mtt = Matrices(r'C:\Users\egc\pest_tools-1\cc\Columbia.pst')
    #mtt = Matrices(r'H:\Pest_Tools_Archive\pest_tools\Examples\cor_testing')
    mtt = Matrices (r'C:\PEST\pest13\ppestex\test.pst')