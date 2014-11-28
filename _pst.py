# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 19:47:37 2014

@author: egc
"""
import pandas as pd
import struct
import numpy as np

class Pst(object):
    def __init__(self, pst_file):
        '''
        Super Class that is used for most other classes.  Attributes are common
        attributes needed for other classes
        
        Attributes
        ---------
        ob_groups : list
           list of observation groups
           inlcudes prior information
        obs : list
           list of obervations
           includes prior information and regularisation
        obs_df : DataFrame 
           DataFrame of observation data section of PEST control file
           Also includes prior information and regularisation
        
        par_groups: list
           list of parameter groups
        
        pars : list
            list of parameters
        
        pars_df : DataFrame
            DataFrame of parameter data section of PEST control file
        
        '''
        f = open(pst_file,'r')
        # Set base name, use later for opening .jco .rec etc.
        self._fname_base = pst_file.rstrip('.pst')
        # Set _obs_dict for use by other classes
        self._obs_dict = dict()
        # Set _pars_dict for use by other classes.
        self._pars_dict = dict()
        
        # Search for parameters section
        while True:
            line = f.readline()
            if '* parameter data' in line:
                break
        while True:
            line = f.readline()
            if '*' in line:
                break
            parnme = line.strip().split()[0].lower()
            partrans = line.strip().split()[1].lower()
            parchglim = line.strip().split()[2].lower()
            parval1 = line.strip().split()[3].lower()
            parlbnd = line.strip().split()[4].lower()
            parubnd = line.strip().split()[5].lower()
            pargp = line.strip().split()[6].lower()
            scale = line.strip().split()[7].lower()
            offset = line.strip().split()[8].lower()
            dercom = line.strip().split()[9].lower()        
            
            self._pars_dict[parnme] =(partrans, parchglim, parval1, parlbnd, \
            parubnd, pargp, scale, offset, dercom)

        # Search for observation section
        while True:
            line = f.readline()
            if '* observation data' in line:
                break
        while True:
            line = f.readline()
            if '*' in line:
                break
            obsnme = line.strip().split()[0].lower()
            obsval = line.strip().split()[1].lower()
            weight = line.strip().split()[2].lower()
            obgnme = line.strip().split()[3].lower()
            self._obs_dict[obsnme] = (obsval, weight, obgnme)

        prior_flag = False
        while True:
            line = f.readline()
            if line == '':
                break
            if '* prior information' in line:
                prior_flag = True
                break
        if prior_flag == True:        
            while True:
                line = f.readline()
                if line == '':
                    break
                if '* predictive' in line or '* regularisation' in line:
                    break
                pilbl = line.strip().split()[0].lower()
                obsval = line.strip().split()[-3].lower()
                weight = line.strip().split()[-2].lower()
                obgnme = line.strip().split()[-1].lower()
        
                self._obs_dict[pilbl] = (obsval, weight, obgnme)

        # Set up DataFrame for observations        
        self.obs_df = pd.DataFrame(self._obs_dict).transpose()
        self.obs_df.columns = ['ObsVal', 'Weight', 'ObGroup']
        self.obs_df.index.name = 'ObsName'
        self.obs = self.obs_df.index.values
        self.ob_groups = self.obs_df.groupby('ObGroup').groups.keys()
        
        # Set up DataFrame for parameters
        self.pars_df = pd.DataFrame(self._pars_dict).transpose()
        self.pars_df.columns = ['partrans', 'parchglim', 'parval1', 'parlbnd',
        'parubnd', 'pargp', 'scale', 'offset', 'dercom']
        self.pars_df.index.name = 'Parname'
        self.pars = self.pars_df.index.values
        self.par_groups = self.pars_df.groupby('pargp').groups.keys()
        
    def _load_jco(self):
        '''
        Read PEST Jacobian matrix file (binary) into Pandas data frame
        
        Returns
        -------
        jco_df : Pandas DataFrame of jco
        
        Notes:
        Method is is the Pst class because it will be used for several other 
        classes; including Jco, ParSen, Cor
        '''
        f = open(self._fname_base+'.jco','rb')
        # Header info
        npar = abs(struct.unpack('i', f.read(4))[0])
        nobs = abs(struct.unpack('i', f.read(4))[0])
        nrecords = abs(struct.unpack('i', f.read(4))[0])
                                       
        x = np.zeros((nobs, npar))    
            
        for record in range(nrecords):
#            if nrecords > 1000000:
#                if record % 1000000 == 0:
#                    percent = (float(record) / nrecords) *100
#                    print '%.1f Percent; Record %s of %s \r' % (percent, record, nrecords)
            j = struct.unpack('i', f.read(4))[0]
            col = ((j-1) / nobs) + 1
            row = j - ((col - 1) * nobs)
            data = struct.unpack('d', f.read(8))[0]
            x[row-1, col-1] = data
           
        pars = []
        for i in range(npar):
            par_name = struct.unpack('12s', f.read(12))[0].strip().lower() 
            pars.append(par_name)
    
        obs = []
        for i in range(nobs):
            ob_name = struct.unpack('20s', f.read(20))[0].strip().lower()
            obs.append(ob_name)
        
        f.close()
        
        
        jco_df = pd.DataFrame(x, index = obs, columns = pars)
        #self.pars = pars #Don't think these need to be kept
        #self.obs = obs #Don't think these need to be kept
        # Clean Up
        del(x)
        
        return jco_df
    
        
if __name__ == '__main__':
    pst = Pst(r'C:\Anaconda\Lib\site-packages\pest_tools\Examples\example.pst')