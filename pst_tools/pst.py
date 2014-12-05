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

        # list of information from PEST control file
        self.pst = []

        # control data
        self.RSTFLE = 'restart'
        self.PESTMODE = 'estimation'

        self.NPAR = 1
        self.NOBS = 1
        self.NPARGP = 1
        self.NPRIOR = 0
        self.NOBSGP = 1

        # parameter data
        self.paradata = pd.DataFrame()
        self.pardata_attr = ['PARNME', 'PARTRANS', 'PARCHGLIM', 'PARVAL1',
                             'PARLBND', 'PARUBND', 'PARGP', 'SCALE', 'OFFSET', 'DERCOM']

        # observation data
        self.obsdata = pd.DataFrame()
        self.obsdata_attr = ['OBSNME', 'OBSVAL', 'WEIGHT', 'OBGNME']


    def read_top_control_data(self):
        """
        reads basic run information from control data section of PEST control file
        """
        print 'control data...'
        self.RSTFLE, self.PESTMODE = self.pst[2].strip().split()
        self.NPAR, self.NOBS, self.NPARGP, self.NPRIOR, self.NOBSGP \
        = [int(s) for s in self.pst[3].strip().split()[0:5]]


    def read_par_data(self):
        """
        convenience function to read parameter information into a dataframe
        """
        knt = 0
        for line in self.pst:
            knt +=1
            if 'parameter data' in line:
                break

        print 'parameter data...'
        tmp = {}
        for i in np.arange(self.NPAR) + knt:

            l = self.pst[i].strip().split()
            pardata = [l[0], l[1], l[2], float(l[3]), float(l[4]), float(l[5]),
                       l[6], int(l[7]), int(l[8]), int(l[9])]

            tmp[pardata[0]] = dict(zip(self.pardata_attr, pardata))

        self.pardata = pd.DataFrame.from_dict(tmp, orient='index')
        self.pardata = self.pardata[self.pardata_attr] # preserve column order


    def read_obs_data(self):
        """
        convenience function to read observation information into a dataframe
        """
        knt = 0
        for line in self.pst:
            knt +=1
            if 'observation data' in line:
                break

        print 'observation data...'
        tmp = {}
        for i in np.arange(self.NOBS) + knt:

            l = self.pst[i].strip().split()
            obsdata = [l[0], float(l[1]), float(l[2]), l[3]]

            tmp[obsdata[0]] = dict(zip(self.obsdata_attr, obsdata))

        self.obsdata = pd.DataFrame.from_dict(tmp, orient='index')
        self.obsdata = self.obsdata[self.obsdata_attr] # preserve column order


class Pst(Pest):
    """
    Class for PEST control file
    * has method to read in run information from PEST control file

    * could also add write method, which would write out a new PEST control file

    """
    def __init__(self, basename, run_folder=None):

        # example of how to initialize code from parent class, and have an __init__ method specific to the child class
        Pest.__init__(self, basename, run_folder)

        # PEST variables
        # note: these could also be included before the __init__ method, in which case they would retain their values
        # in the Pst class (if it was called directly), but could be updated in instances of the Pst class. Not sure if we
        # need this, but it is an option.

        # control data not in base class
        self.NTPLFLE = 1
        self.NINSFLE = 1
        self.PRECIS = 'double'
        self.DPOINT = 'point'

        self.RLAMBDA1 = 20
        self.RLAMFAC = -3
        self.PHIRATSUF = 0.3
        self.PHIREDLAM = 0.01
        self.NUMLAM = -10
        self.JACUPDATE = 999
        self.LAMFORGIVE = 'lamforgive'
        self.DERFORGIVE = ''

        self.RELPARMAX = 10
        self.FACPARMAX = 10
        self.FACORIG = 0.001

        self.PHIREDSWH = 0.1
        self.NOPTSWITCH = 1
        self.DOAUI = 'noaui'

        self.NOPTMAX = 0
        self.PHIREDSTP = 0.01
        self.NPHISTP = 3
        self.NPHINORED = 3
        self.RELPARSTP = 0.01
        self.NRELPAR = 3

        self.ICOV = 0
        self.ICOR = 0
        self.IEIG = 0
        self.REISAVEITN = 'REISAVEITN'
        self.PARSAVEITN = 'PARSAVEITN'

        # singular value decomposition
        self.SVD = False
        self.SVDMODE = 1,
        self.MAXSING = 1
        self.EIGTHRESH = 5e-7
        self.EIGWRITE = 1

        # svd assist
        self.svda = {}

        # parameter groups
        self.pargroups = {}
        self.pargroups_attr = ['PARGPNME', 'INCTYP', 'DERINC', 'DERINCLB', 'FORCEN',
                               'DERINCMUL', 'DERMTHD']

        # observation groups
        self.obsgroups_ind = int()
        self.obsgroups = []

        # model command line
        self.batchfile = ''

        # model input/output
        model_io_ind = int()
        self.ins = {}
        self.tpl = {}

        # prior information
        self.prior_ind = ()
        self.prior = []

        # regularisation
        self.PHIMLIM = self.NOBS
        self.PHIMACCEPT = self.PHIMLIM * 1.05
        self.FRACPHIM = 0.10
        self.WFINIT = 1.0
        self.WFMIN = 1e-10
        self.WFMAX = 1e10
        self.REGCONTINUE = ''
        self.WFFAC = 1.3
        self.WFTOL = 0.01
        self.IREGADJ = 1


    def read_pst(self):
        """
        Read all run information from the PEST control file
        """

        print 'reading {}...'.format(self.pstfile)

        self.pst = open(self.pstfile).readlines()

        # control data
        self.read_top_control_data()

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
        self.read_par_data()

        # read observation data
        self.read_obs_data()

        # read rest of pst file
        knt = 10
        for line in self.pst[10:]:

            if 'singular value decompostion' in line:
                print 'singular value decompostion...'
                self.SVD = True
                self.SVDMODE = int(self.pst[knt + 1].strip().split()[0])
                self.MAXSING = int(self.pst[knt + 2].strip().split()[0])
                self.EIGTHRESH = float(self.pst[knt + 2].strip().split()[1])
                self.EIGWRITE = int(self.pst[knt + 3].strip().split()[0])

            if 'parameter groups' in line:
                print 'parameter groups...'
                for i in np.arange(self.NPARGP) + 1:
                    self.read_par_group(self.pst[knt + i])

            if 'observation groups' in line:
                print 'observation groups...'
                self.obsgroups_ind = knt + 1
                self.read_obs_groups()

            if 'model command line' in line:
                print 'batch file...'
                self.batchfile = self.pst[knt+1].strip()

            if 'model input/output' in line:
                print 'template and instruction files...'
                self.model_io_ind = knt + 1
                self.read_instpl()

            if 'prior information' in line:
                print 'prior information...'
                self.prior_ind = knt + 1
                self.read_prior()

            if 'regularisation' in line:
                print 'regularisation...'
                self.PHIMLIM, self.PHIMACCEPT = [float(s) for s in self.pst[knt + 1].strip().split()[0:2]]
                try:
                    self.FRACPHIM = float(self.pst[knt + 1].strip().split()[2])
                except:
                    pass
                self.WFINIT, self.WFMIN, self.WFMAX = [float(s) for s in self.pst[knt + 2].strip().split()[0:3]]
                self.WFFAC, self.WFTOL = [float(s) for s in self.pst[knt + 3].strip().split()[0:2]]
                self.IREGADJ = int(self.pst[knt + 3].strip().split()[2])

            knt += 1


    def read_par_group(self, l):
        """
        convenience function to read par group information into a dictionary
        """
        l = l.strip().split()
        pargp = [l[0], l[1], float(l[2]), float(l[3]), l[4], float(l[5]), l[6]]

        self.pargroups[pargp[0]] = dict(zip(self.pargroups_attr, pargp))


    def read_obs_groups(self):
        """
        convenience function to read observation groups into a list
        """
        knt = self.obsgroups_ind
        for i in np.arange(self.NOBSGP) + knt:
            self.obsgroups.append(self.pst[i].strip())


    def read_instpl(self):
        """
        convenience function to read instruction and template file information into dictionaries
        """
        knt = self.model_io_ind
        for i in np.arange(self.NTPLFLE) + knt:

            tpl, dat = self.pst[i].strip().split()

            self.tpl[tpl] = dat
            knt += 1

        for i in np.arange(self.NINSFLE) + knt:

            ins, dat = self.pst[i].strip().split()

            self.ins[ins] = dat


    def read_prior(self):
        """
        convenience function to read prior information into a dataframe
        for now, just read items into list
        """
        knt = self.prior_ind
        tmp = {}
        for i in np.arange(self.NOBS) + knt:

            self.prior.append(self.pst[i].strip())
