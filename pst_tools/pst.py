__author__ = 'aleaf'


import os
import numpy as np
import pandas as pd


class Pest(object):
    """
    base class for PEST run
    contains run name, folder and some control data from PEST control file
    also has methods to read in parameter and observation data from PEST control file

    could also be a container for other global settings
    (a longer run name to use in plot titles, etc)

    basename : string
    pest basename or pest control file (includes path)
    """

    def __init__(self, basename):

        self.basename = os.path.split(basename)[-1].split('.')[0]
        self.run_folder = os.path.split(basename)[0]
        if len(self.run_folder) == 0:
            self.run_folder = os.getcwd()

        self.pstfile = os.path.join(self.run_folder, self.basename + '.pst')

        # basic control data
        # Don't really need this here.  Use Pst() class 
#        with open(self.pstfile) as pstfile:
#            top_control_data = [next(pstfile) for x in xrange(4)]
#        #RSTFLE and PESTMODE aren't really helpful in this class
#        self.RSTFLE, self.PESTMODE = top_control_data[2].strip().split()
#        self.NPAR, self.NOBS, self.NPARGP, self.NPRIOR, self.NOBSGP \
#        = [int(s) for s in top_control_data[3].strip().split()[0:5]]

        # parameter data
#        self._read_par_data()

        # observation data
#        self._read_obs_data()
        

    def _read_par_data(self):
        """
        convenience function to read parameter information into a dataframe
        """

        pst = open(self.pstfile).readlines()
        NPAR = int(pst[3].strip().split()[0])
        pardata_attr = ['PARNME', 'PARTRANS', 'PARCHGLIM', 'PARVAL1',
        'PARLBND', 'PARUBND', 'PARGP', 'SCALE', 'OFFSET', 'DERCOM']

        knt = 0
        for line in pst:
            knt +=1
            if 'parameter data' in line:
                break
        tmp = {}
        for i in np.arange(NPAR) + knt:

            l = pst[i].strip().split()
            pardata = [l[0], l[1], l[2], float(l[3]), float(l[4]), float(l[5]),
                       l[6], int(l[7]), int(l[8]), int(l[9])]

            tmp[pardata[0]] = dict(zip(pardata_attr, pardata))

        self.pardata = pd.DataFrame.from_dict(tmp, orient='index')
        self.pardata = self.pardata[pardata_attr] # preserve column order


    def _read_obs_data(self):
        """
        convenience function to read observation information into a dataframe
        """

        pst = open(self.pstfile).readlines()
        NOBS = int(pst[3].strip().split()[1])
        obsdata_attr = ['OBSNME', 'OBSVAL', 'WEIGHT', 'OBGNME']
        knt = 0
        for line in pst:
            knt +=1
            if 'observation data' in line:
                break
        tmp = {}
        for i in np.arange(NOBS) + knt:

            l = pst[i].strip().split()
            obsdata = [l[0], float(l[1]), float(l[2]), l[3]]

            tmp[obsdata[0]] = dict(zip(obsdata_attr, obsdata))

        self.obsdata = pd.DataFrame.from_dict(tmp, orient='index')
        self.obsdata = self.obsdata[obsdata_attr] # preserve column order
        
    def _read_prior(self):
        """
        convenience function to read prior information into a dataframe
        """
        pst = open(self.pstfile).readlines()
        NPRIOR = int(pst[3].strip().split()[3])
        priordata_attr = ['PILBL', 'equation', 'PIVAL', 'WEIGHT', 'OBGNME']
        knt = 0
        for line in pst:
            knt +=1
            if 'prior information' in line:
                break
        tmp = {}
        for i in np.arange(NPRIOR) + knt:
            l = pst[i].strip().split()
            priordata = [l[0], " ".join(l[1:-4]), float(l[-3]), float(l[-2]), l[-1]]

            tmp[priordata[0]] = dict(zip(priordata_attr, priordata))            
            
            
        self.priordata = pd.DataFrame.from_dict(tmp, orient='index')
        self.priordata = self.priordata[priordata_attr] # preserve column order

        
    def _load_jco(self):
        import struct
        '''
        Read PEST Jacobian matrix file (binary) into Pandas data frame
        
        Returns
        -------
        jco_df : Pandas DataFrame of jco
        
        Notes:
        Method is is the Pest class because it will be used for several other 
        classes; including Jco, ParSen, Cor
        '''
        f = open(self.pstfile.rstrip('.pst')+'.jco','rb')
        # Header info of .jco file
        npar = abs(struct.unpack('i', f.read(4))[0])
        nobs = abs(struct.unpack('i', f.read(4))[0])
        nrecords = abs(struct.unpack('i', f.read(4))[0])
                                       
        tmp = np.zeros((nobs, npar))    
            
        for record in range(nrecords):
            j = struct.unpack('i', f.read(4))[0]
            col = ((j-1) / nobs) + 1
            row = j - ((col - 1) * nobs)
            data = struct.unpack('d', f.read(8))[0]
            tmp[row-1, col-1] = data
           
        pars = []
        for i in range(npar):
            par_name = struct.unpack('12s', f.read(12))[0].strip().lower() 
            pars.append(par_name)
    
        obs = []
        for i in range(nobs):
            ob_name = struct.unpack('20s', f.read(20))[0].strip().lower()
            obs.append(ob_name)
        
        f.close()
        
        
        jco_df = pd.DataFrame(tmp, index = obs, columns = pars)
        # Clean Up
        del(tmp)
        
        return jco_df


class Pst(Pest):
    """
    Class for PEST control file
    * has method to read in run information from PEST control file

    * could also add write method, which would write out a new PEST control file

    """
    def __init__(self, basename):

        # example of how to initialize code from parent class, and have an __init__ method specific to the child class
        Pest.__init__(self, basename)

        # PEST variables
        # note: these could also be included before the __init__ method, in which case they would retain their values
        # in the Pst class (if it was called directly), but could be updated in instances of the Pst class. Not sure if we
        # need this, but it is an option.

        # svd assist
        # Not sure what this is for?
        self.svda = {}
        
        # Read in all the PEST variables
        self._read_pst()

    def _read_pst(self):
        """
        Read all run information from the PEST control file
        """

        print 'reading {}...'.format(self.pstfile)

        self.pst = open(self.pstfile).readlines()
        
        # initialize attributes

        # control data
        self.RSTFLE, self.PESTMODE = self.pst[2].strip().split()
        self.NPAR, self.NOBS, self.NPARGP, self.NPRIOR, self.NOBSGP \
        = [int(s) for s in self.pst[3].strip().split()[0:5]]

        self.NTPLFLE, self.NINSFLE = [int(s) for s in self.pst[4].strip().split()[0:2]]
        self.PRECIS, self.DPOINT = self.pst[4].strip().split()[2:4]

        self.RLAMBDA1, self.RLAMFAC, self.PHIRATSUF, self.PHIREDLAM = [float(s) for s in self.pst[5].strip().split()[0:4]]
        self.NUMLAM = int(self.pst[5].strip().split()[4])
        try:
            self.JACUPDATE = int(self.pst[5].strip().split()[5])
            self.LAMFORGIVE = self.pst[5].strip().split()[6]
            self.DERFORGIVE = self.pst[5].strip().split()[7]
        except:
            pass

        self.RELPARMAX, self.FACPARMAX, self.FACORIG = [float(s) for s in self.pst[6].strip().split()[0:3]]

        self.PHIREDSWH = float(self.pst[7].strip().split()[0])
        try:
            self.NOPTSWITCH = int(self.pst[7].strip().split()[1])
        except:
            pass
        try:
            self.DOAUI = [s for s in self.pst[7].strip().split() if 'aui' in s][0]
        except:
            pass

        self.NOPTMAX = int(self.pst[8].strip().split()[0])
        self.PHIREDSTP = float(self.pst[8].strip().split()[1])
        self.NPHISTP = int(self.pst[8].strip().split()[2])
        self.NPHINORED = int(self.pst[8].strip().split()[3])
        self.RELPARSTP = float(self.pst[8].strip().split()[4])
        self.NRELPAR = int(self.pst[8].strip().split()[5])

        self.ICOV, self.ICOR, self.IEIG = [int(s) for s in self.pst[9].strip().split()[0:3]]

        if not 'reisaveitn' in self.pst[9].lower():
            self.REISAVEITN = ''
        if not 'parsaveitn' in self.pst[9].lower():
            self.PARSAVEITN = ''


        # read parameter data
        self._read_par_data()

        # read observation data
        self._read_obs_data()

        # read rest of pst file
        knt = 10
        for line in self.pst[10:]:

            if 'singular value decompostion' in line:
                #print 'singular value decompostion...'
                self.SVD = True
                self.SVDMODE = int(self.pst[knt + 1].strip().split()[0])
                self.MAXSING = int(self.pst[knt + 2].strip().split()[0])
                self.EIGTHRESH = float(self.pst[knt + 2].strip().split()[1])
                self.EIGWRITE = int(self.pst[knt + 3].strip().split()[0])
            else:
                self.SVD = False

            if 'parameter groups' in line:
                #print 'parameter groups...'
                for i in np.arange(self.NPARGP) + 1:
                    self._read_par_group(self.pst[knt + i])

            if 'observation groups' in line:
                #print 'observation groups...'
                self._obsgroups_ind = knt + 1
                self._read_obs_groups()

            if 'model command line' in line:
                #print 'batch file...'
                self.batchfile = self.pst[knt+1].strip()

            if 'model input/output' in line:
                #print 'template and instruction files...'
                self._model_io_ind = knt + 1
                self._read_instpl()

            if 'prior information' in line:
                #print 'prior information...'
                #self._prior_ind = knt + 1
                self._read_prior()

            if 'regularisation' in line:
                #print 'regularisation...'
                self.PHIMLIM, self.PHIMACCEPT = [float(s) for s in self.pst[knt + 1].strip().split()[0:2]]
                try:
                    self.FRACPHIM = float(self.pst[knt + 1].strip().split()[2])
                except:
                    pass
                self.WFINIT, self.WFMIN, self.WFMAX = [float(s) for s in self.pst[knt + 2].strip().split()[0:3]]
                if 'linreg' in self.pst[knt + 2].lower():
                    self.LINREG = 'linreg'
                else:
                    self.LINREG = 'nonlinreg'
                if 'continue' in self.pst[knt + 2].lower():
                    self.REGCONTINUE = 'continue'
                else:
                    self.REGCONTINUE = 'nocontinue'
                self.WFFAC, self.WFTOL = [float(s) for s in self.pst[knt + 3].strip().split()[0:2]]
                self.IREGADJ = int(self.pst[knt + 3].strip().split()[2])

            knt += 1


    def _read_par_group(self, l):
        """
        convenience function to read par group information into a dictionary
        """
        self.pargroups = {}
        pargroups_attr = ['PARGPNME', 'INCTYP', 'DERINC', 'DERINCLB', 'FORCEN',
        'DERINCMUL', 'DERMTHD']        
        l = l.strip().split()
        pargp = [l[0], l[1], float(l[2]), float(l[3]), l[4], float(l[5]), l[6]]

        self.pargroups[pargp[0]] = dict(zip(pargroups_attr, pargp))


    def _read_obs_groups(self):
        """
        convenience function to read observation groups into a list
        """
        self.obsgroups = []
        knt = self._obsgroups_ind
        for i in np.arange(self.NOBSGP) + knt:
            self.obsgroups.append(self.pst[i].strip())


    def _read_instpl(self):
        """
        convenience function to read instruction and template file information into dictionaries
        """
        knt = self._model_io_ind
        self.ins = {}
        self.tpl = {}
        for i in np.arange(self.NTPLFLE) + knt:

            tpl, dat = self.pst[i].strip().split()

            self.tpl[tpl] = dat
            knt += 1

        for i in np.arange(self.NINSFLE) + knt:

            ins, dat = self.pst[i].strip().split()

            self.ins[ins] = dat



            
if __name__ == '__main__':
    pest = Pest(r'C:\Users\egc\pest_tools-1\cc\Columbia.pst')
    pst = Pst(pest.pstfile)
