__author__ = 'aleaf'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import operator
from pst import *


class Plot(object):
    """
    Base class for assembling a plot using matplotlib

    This plotting structure is loosely based on pandas (albeit greatly simplified). Some of the structure may be
    to complicated for our needs, and we may want add additional functionality and shift parts of it around
    as needed. But hopefully it will provide a starting point to work off of.

    The overall goal is to centralize plotting code for consistency and to maximize extensibility

    """
    def __init__(self, df, kind=None, by=None, subplots=False, sharex=True,
                 sharey=False, use_index=True,
                 figsize=None, grid=None, legend=True, legend_title='',
                 ax=None, fig=None, title=None, xlim=None, ylim=None,
                 xticks=None, yticks=None, xlabel=None, ylabel=None, units=None,
                 sort_columns=False, fontsize=None,
                 secondary_y=False,
                 layout=None, **kwds):

        self.df = df
        self.by = by

        self.kind = kind

        self.sort_columns = sort_columns

        self.subplots = subplots
        self.sharex = sharex
        self.sharey = sharey
        self.figsize = figsize
        self.layout = layout

        self.xticks = xticks
        self.yticks = yticks
        self.xlim = xlim
        self.ylim = ylim
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.units = units
        self.title = title
        self.use_index = use_index

        self.fontsize = fontsize


        if grid is None:
            grid = False if secondary_y else True

        self.grid = grid
        self.legend = legend
        self.legend_title = legend_title
        self.legend_handles = []
        self.legend_labels = []

        self.ax = ax
        self.fig = fig
        self.axes = None

        self.kwds = kwds


    def _adorn_subplots(self):

        self.ax.set_ylabel(self.xlabel)
        self.ax.set_xlabel(self.ylabel)
        if self.title:
            self.ax.set_title(self.title)

    def log_trans(self, x, pos):
        # Reformat tick labels out of log space
        # x : value
        # pos : position
        return '%d' % (10**x)

    def draw(self):
        plt.draw_if_interactive()

    def generate(self):

        self._initialize()
        self._make_plot()
        self._adorn_subplots()
        self._make_legend()

    def _initialize(self):
        # this will need to be extended to accommodate subplots
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)


class One2onePlot(Plot):
    """Makes one-to-one plot of two dataframe columns, using pyplot.scatter"""

    def __init__(self, df, x, y, groupinfo, line_kwds={}, **kwds):

        Plot.__init__(self, df, **kwds)
        """

        Parameters
        ----------
        df : DataFrame,
            Pandas DataFrame

        x: string or int
            Column in df containing values to plot on the x-axis

        y: string or int
            Column in df containing values to plot on the y-axis

        groupinfo: dict, list, or string
            If string, name of group in "Group" column of df to plot. Multiple groups
            in "Group" column of df can be specified using a list. A dictionary
            can be supplied to indicate the groups to plot (as keys), with item consisting of
            a dictionary of keywork arguments to Matplotlib.pyplot to customize the plotting of each group.

        line_kwds: dict, optional
            Additional keyword arguments to Matplotlib.pyplot.plot, for controlling appearance of one-to-one line.
            See http://matplotlib.org/api/pyplot_api.html

        **kwds:
            Additional keyword arguments to Matplotlib.pyplot.scatter and Matplotlib.pyplot.hexbin,
            for controlling appearance scatter or hexbin plot. Order of priority for keywords is:
                * keywords supplied in groupinfo for individual groups
                * **kwds entered for whole plot
                * default settings

            (need to figure out how to differentiate documentation with inheritance,
            and how to duplicate it in the plotting method!)
            See http://matplotlib.org/api/pyplot_api.html

        Notes
        ------

        """
        if x is None or y is None:
            raise ValueError( 'scatter requires and x and y column')
        if pd.lib.is_integer(x) and not self.df.columns.holds_integer():
            x = self.df.columns[x]
        if pd.lib.is_integer(y) and not self.df.columns.holds_integer():
            y = self.df.columns[y]

        self.x = x
        self.y = y
        self.groupinfo = groupinfo
        self.groups = np.unique(self.df.Group)
        self.line_kwds = line_kwds
        self._legend_order = {}
        self.max, self.min = -999999.9, 999999.9

        # format x and y labels
        if self.xlabel is None:
            self.xlabel = str(self.x)
        if self.ylabel is None:
            self.ylabel = str(self.y)
        if self.units is not None:
            self.xlabel += ', {}'.format(self.units)
            self.ylabel += ', {}'.format(self.units)

        # dictionary supplied for groupinfo
        if isinstance(self.groupinfo, dict):
            # only attempt to plot groups that are in Res dataframe
            self.groupinfo = dict((k.lower(), v) for k, v in self.groupinfo.iteritems())
            self.groups = list(set(self.groupinfo.keys()).intersection(set(self.groups)))

        # list of group names supplied
        elif isinstance(self.groupinfo, list):
            self.groupinfo = [g.lower() for g in self.groupinfo]
            self.groups = list(set(self.groupinfo).intersection(set(self.groups)))
            self.groupinfo = dict(zip(self.groupinfo, [{}] * len(self.groupinfo)))

        elif isinstance(self.groupinfo, str):
            self.groupinfo = self.groupinfo.lower()
            self.groups = list(set([self.groupinfo]).intersection(set(self.groups)))
            self.groupinfo = {self.groupinfo: {}}

        else:
            raise ValueError('Invalid input for groupinfo.')

        if len(self.groups) == 0:
            raise IndexError('Specified groups not found in residuals file.')

    def _make_plot(self):

        # use matplotlib's color cycle to plot each group as a different color by default
        color_cycle = self.ax._get_lines.color_cycle
        for grp in self.groups:

            # default keyword settings, which can be overriden by submitted keywords
            # order of priority is default, then keywords entered for whole plot,
            # then keywords supplied for individual group
            kwds = {'label': grp, 'c': next(color_cycle), 'linewidth': 0.25}
            kwds.update(self.kwds)
            kwds.update(self.groupinfo.get(grp, {}))
            label = kwds.get('label', grp)

            g = self.df[self.df.Group == grp]

            x, y = g[self.x], g[self.y]

            s = self.ax.scatter(x, y, **kwds)
            self._legend_order[label] = s.get_zorder()

            # keep track of min/max for one2one line
            if np.max([x, y]) > self.max:
                self.max = np.max([g.Measured, g.Modelled])
            if np.min([x, y]) < self.min:
                self.min = np.min([g.Measured, g.Modelled])

        #plot one2one line
        line_kwds = {'color': 'r', 'zorder': 0}
        line_kwds.update(self.line_kwds)
        plt.plot(np.arange(self.min, self.max+1), np.arange(self.min, self.max+1), **line_kwds)

        self.ax.set_ylim(self.min, self.max)
        self.ax.set_xlim(self.min, self.max)

    def _make_legend(self):

        if self.legend:
            handles, labels = self.ax.get_legend_handles_labels()

            # weed out duplicate legend entries (from multiple PEST groups in single category)
            # enforce drawing order in legend
            u_handles, u_labels = [], []
            legend_order = sorted(self._legend_order.items(), key=operator.itemgetter(1))
            legend_order.reverse()

            for item in legend_order:
                u_handles.append([handles[i] for i, l in enumerate(labels) if l==item[0]][0])
                u_labels.append(item[0])

            lg = plt.legend(u_handles, u_labels, title=self.legend_title, loc='lower right', fontsize=8,
                            scatterpoints=1, labelspacing=1.5, ncol=1, columnspacing=1)

            plt.setp(lg.get_title(), fontsize=9, fontweight='bold')
            lg.set_zorder(100)


class HexbinPlot(One2onePlot):
    """Makes a hexbin plot of two dataframe columns, pyplot.hexbin"""

    def _make_plot(self):

        # overrides _make_plot() method in One2onePlot; inherits everything else
        x = self.df[self.df['Group'].isin(self.groups)]['Measured'].values
        y = self.df[self.df['Group'].isin(self.groups)]['Modelled'].values
        self.min, self.max = np.min([x, y]), np.max([x, y])

        # default keyword settings, which can be overriden by submitted keywords
        kwds = {'bins': 'log', 'mincnt': 1, 'extent': (self.min, self.max, self.min, self.max),
                'alpha': 1.0, 'edgecolors': 'none'}
        kwds.update(self.kwds)
        self.kwds = kwds

        plt.hexbin(x, y, **self.kwds)

        #plot one2one line
        line_kwds = dict(color='k', alpha=0.5, zorder=1)
        line_kwds.update(self.line_kwds)
        plt.plot(np.arange(self.min, self.max+1), np.arange(self.min, self.max+1), **line_kwds)

        #self.ax.set_ylim(np.min(y), np.max(y))
        #self.ax.set_xlim(self.min, self.max)

    def _make_legend(self):

        if self.legend:
            # put this here for now, may want to restructure later
            cb = plt.colorbar()
            if self.kwds['bins'] == 'log':
                cb.formatter = mpl.ticker.FuncFormatter(self.log_trans)
                cb.update_ticks()
                cb.set_label('Bin counts')
            else:
                cb.set_label('Bin counts')


class BarPloth(Plot):
    def __init__(self, df, values_col, group_col=None, color_dict = None, alt_labels = None, **kwargs):
        Plot.__init__(self, df, **kwargs)
        '''
        Make horizontal bar graph
        Parameters
        ----------
        df : DataFrame,
            Pandas DataFrame

        values_col: string
            Column in df containing values to plot as the length of the bars
            the 'width' parameter for matplotlib.pyplot.barh
            
        group_col : string, optional
            Column in df containing group for each value.  Will be used to color
            bars based on groups
            
        color_dict : dict, optional
            Dictionary of alternate colors for groups.  Keys are groups and values
            are colors.  Can be tuple such as (0.8, 0.1, 0.1, 1.0), or other
            standard matplotlib recognized color
            
        alt_labels : dict, optional
            Dictionary of alternative labels to use. Keys are raw PEST names.
            Values are preferred lables or descriptions
        '''
        
        self.df = df
        self.values_col = values_col
        self.group_col = group_col
        self.color_dict = color_dict
        self.alt_labels = alt_labels
        
        if self.ylabel is None:
            self.ylabel = str(self.values_col)

    def _make_plot(self, ):
        
        values = self.df[self.values_col].values
        bottom = np.arange(len(values))
        
        # Assign colors for each group
        # Will be overriden by kwds if provoded for color
        if self.group_col != None:            
            # Use provided colormap or use Set1 as default
            if 'cmap' in self.kwds:
                cmap = plt.get_cmap(self.kwds['cmap'])
                del self.kwds['cmap']
            else:
                #Default of jet is ugly
                #cmap = plt.get_cmap()
                cmap = plt.get_cmap('Set2')
            _color_dict = dict()
            unique_par_groups = np.asarray(self.df.drop_duplicates(cols = self.group_col)[self.group_col])
            for i in range(len(unique_par_groups)):
                # If color is provied for paragroup in color_dict parameter than use it               
                try:
                    _color_dict[unique_par_groups[i]] = self.color_dict[unique_par_groups[i]]
                except:
                    color = cmap(1.*i/len(unique_par_groups))
                    _color_dict[unique_par_groups[i]] = color
            
            self.colors = []
            for par_group in self.df[self.group_col].values:            
                self.colors.append(_color_dict[par_group])
        else:
            self.colors = None
            
        # default keyword settings, which can be overriden by submitted keywords
        kwds = {'align' : 'center', 'color' : self.colors}
        kwds.update(self.kwds)
        self.kwds = kwds
        
        plt.barh(bottom, values, **self.kwds)
        
        plt.ylim(-1, len(bottom))

        if self.alt_labels == None:
            plt.yticks(np.arange(len(self.df.index)), self.df.index)
        else:
            # Make sure all keys are lower
            self.alt_labels = dict((k.lower(), v) for k, v in self.alt_labels.iteritems())
            labels = []
            for label in self.df.index:
                if label in self.alt_labels:
                    labels.append(self.alt_labels[label])
                else:
                    labels.append(label)
            plt.yticks(np.arange(len(labels)), labels)

        plt.xlabel(self.xlabel)
        plt.tight_layout()

    def _make_legend(self):
        # This needs work, or maybe not needed?
        None
