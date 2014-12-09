__author__ = 'aleaf'

import sys
sys.path.append('../pst_tools')
from pst import *
from res import *
from matplotlib.backends.backend_pdf import PdfPages


class Rei(Pest):
    """
    Class for working with set of REI files from a PEST run

    Parameters
    ----------
    basename : string
        Base name for PEST run.


    Attributes
    ----------
    reifiles : dict
        Dictionary of rei files (strings) produced from PEST run
        with residuals information saved every iteration (REISAVEITN).
        Integer keys represent iteration number.

    Methods
    -------
    one2one_plots()


    Notes
    ------
    
    """

    def __init__(self, basename):

        Pest.__init__(self, basename)

        reifiles = [f for f in os.listdir(self.run_folder) if self.basename + '.rei' in f]

        # sort by iteration number (may not be the most elegant approach)
        self.reifiles = {}
        for f in reifiles:
            try:
                i = int(f.split('.')[-1])
                self.reifiles[i] = os.path.join(self.run_folder, f)
            except:
                continue


    def one2one_plots(self, groupinfo, outpdf='', **kwds):

        if len(outpdf) == 0:
            outpdf = self.basename + '_reis.pdf'

        print 'plotting...'
        pdf = PdfPages(outpdf)
        for i in self.reifiles.iterkeys():
            print '{}'.format(self.reifiles[i])
            r = Res(self.reifiles[i])
            fig, ax = r.one2one_plot(groupinfo, **kwds)

            pdf.savefig(fig, **kwds)
        print '\nsaved to {}'.format(outpdf)
        pdf.close()