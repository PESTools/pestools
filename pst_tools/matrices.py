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
        if 'regularisation' in open(self.pstfile).read():
            warnings.warn('Regularization used, statistical matrices may not applicable')           
        if jco_df is None:
            self._jco_df = self._load_jco()

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
        self._res_df = pd.read_csv(res_file, skiprows=line_num, delim_whitespace=True)
        self._res_df.index = [n.lower() for n in self._res_df['Name']]

        # Define _pars, _phi, and _weights in Matrices class.  Plan to allow
        # for additional filtering etc here later
        self._pars = self._jco_df.columns.values
        self._phi = sum(self._res_df['Weight*Residual']**2)
        self._weights = self._res_df['Weight'].values
    
    def _cov(self):
        # Calc Covarience Matrix
        # See eq. 2.17 in PEST Manual
        # Note: Number of observations are number of non-zero weighted observations
        q = np.diag(np.diag(np.tile(self._weights**2, (len(self._weights), 1))))
        cov = np.dot((self._phi/(np.count_nonzero(self._weights)-len(self._pars))),
                     (np.linalg.inv(np.dot(np.dot(self._jco_df.values.T, q),self._jco_df.values))))
        cov_df = pd.DataFrame(cov, index=self._pars, columns=self._pars)
        return cov_df
            
    def _cor(self):
        # Calc correlation matrix
        cov = self._cov().values
        d = np.diag(cov)
        cor = cov/np.sqrt(np.multiply.outer(d, d))
        # Put into dataframe
        cor_df = pd.DataFrame(cor, index=self._pars, columns=self._pars)
        return cor_df
        
    def _eig(self):
        # Calc eigenvalues, eigenvectors
        # Use UPLO='U' (upper triangular part) to be consistent with PEST
        eig_values, eig_vectors = np.linalg.eigh(self._cov().values, UPLO='U')
        eig_vectors_df = pd.DataFrame(eig_vectors, index=self._pars)
        return eig_vectors_df, eig_values


class Cov(Matrices):
    def __init__(self, basename):
        Matrices.__init__(self, basename, res_file=None, jco_df=None)
        
        self.df = self._cov()
        


class Cor(Matrices):
    def __init__(self, basename):
        Matrices.__init__(self, basename, res_file=None, jco_df=None)
        
        self.df = self._cor()
        
    def plot_heatmap(self, label_rows=True, label_cols=True, **kwds):
        plot_obj = plots.HeatMap(self.df, label_rows=label_rows, label_cols=label_cols, **kwds)
        plot_obj.generate()
        plot_obj.draw()
        return plot_obj.fig, plot_obj.ax
        
class Eig(Matrices):
    def __init__(self, basename):
        Matrices.__init__(self, basename, res_file=None, jco_df=None)
        
        self.df, self.values = self._eig()
        # .df may not be clear what it is compared to .values
        # make a .vectors attribute also that is the same is
        self.vectors = self.df


if __name__ == '__main__':
    #mtt = Matrices(r'C:\Users\egc\pest_tools-1\cc\Columbia.pst')
    #mtt = Matrices(r'H:\Pest_Tools_Archive\pest_tools\Examples\cor_testing')
    #mtt = Matrices(r'C:\PEST\pest13\ppestex\test.pst')
    #cov = Cov(r'C:\PEST\pest13\ppestex\test.pst')
    cor = Cor(r'C:\PEST\pest13\ppestex\test.pst')
    #eig = Eig(r'C:\PEST\pest13\ppestex\test.pst')
    cor.plot_heatmap(label_rows = True, label_cols = True, cmap = 'PuOr')
    
    #cor2 = Cor(r'C:\Users\egc\pest_tools-1\cc\Columbia.pst')
    #cor2.plot_heatmap()