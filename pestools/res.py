import matplotlib.pyplot as plt
import math
from pest import *
import plots


class Res(Pest):
    """ Res Class

    Parameters
    ----------
    res_file : str
        Path to .res or .rei file from PEST

    obs_info_file : str, optional
        csv file containing observation locations and/or observation type.

    name_col : str, default 'Name'
        column in obs_info_file containing observation names

    x_col : str, default 'X'
        column in obs_info_file containing observation x locations

    y_col : str, default 'Y'
        column in obs_info_file containing observation y locations

    type_col : str, default 'Type'
        column in obs_info_file containing observation types (e.g. heads, fluxes, etc). A single
        type ('observation') is assigned in the absence of type information

    Attributes
    ----------
    df : DataFrame
        contains all of the information from the res or rei file; is used to build phi dataframe

    phi : DataFrame
        contains phi contribution by group, and also a column with observation type

    obsinfo : DataFrame
        contains information from observation information file, and also observation groups

    Notes
    ------
    Column names in the observation information file are remapped to their default values after import

    """

    def __init__(self, res_file, obs_info_file=None, name_col='Name',
                 x_col='X', y_col='Y', type_col='Type',
                 basename_col='basename', datetime_col='datetime', group_cols=[],
                 **kwds):
        Pest.__init__(self, res_file)

        #self._read_obs_groups()
        self.obsinfo = pd.DataFrame()
        self._obstypes = pd.DataFrame({'Type': ['observation'] * len(self.obs_groups)}, index=self.obs_groups)

        if obs_info_file is not None:
            self._read_obs_info_file(obs_info_file, name_col=name_col, x_col=x_col, y_col=y_col, type_col=type_col,
                                     basename_col=basename_col, datetime_col=datetime_col, group_cols=group_cols,
                                     **kwds)

        check = open(res_file, 'r')
        line_num = 0
        while True:
            current_line = check.readline()
            if "name" in current_line.lower() and "residual" in current_line.lower():
                break
            else:
                line_num += 1

        self.df = pd.read_csv(res_file, skiprows=line_num, delim_whitespace=True)
        self.df.index = [n.lower() for n in self.df['Name']]

        # Apply weighted residual and calculate phi contributions
        self.df['Weighted_Residual'] = self.df['Residual'] * self.df['Weight']
        self.df['Absolute_Residual'] = abs(self.df['Residual'])
        self.df['Weighted_Absolute_Residual'] = self.df['Absolute_Residual'] * self.df['Weight']

        # calculate phi
        self.df['Weighted_Sq_Residual'] = self.df['Weighted_Residual']**2
        self.phi = self.df[['Weighted_Sq_Residual']].join(self.obsinfo)
        self.phi_by_group = self.df.groupby('Group').agg('sum')[['Weighted_Sq_Residual']]
        self.phi_by_group = self.phi_by_group.join(self._obstypes)


    def group(self, group):
        ''' Get pandas DataFrame for a single group
        
        Parameters
        ----------
        group : str
            Observation group to get
            
        Returns
        --------
        pandas DataFrame
            DataFrame of residuals for group

        '''       
        return self.df.ix[self.df['Group'] == group]

    def describe_data(self, data, ddof=1):
        ''' Basic desription of np array

        Parameters
        ----------
        data : arr
            Numpy array

        Returns
        --------
        pandas DataFrame
            DataFrame of residuals for group

        '''
        from scipy.stats import shapiro

        data = data.ravel() # flatten to one dimmensional array
        data = data[~np.isnan(data)] # drop nans

        stats = {}
        stats['n'] = len(data)
        stats['Range'] = np.max(data) - np.min(data)
        stats['Max'] = np.max(data)
        stats['Min'] = np.min(data)
        stats['Mean'] = np.mean(data)
        stats['Standard deviation'] = np.std(data, ddof=ddof)
        stats['Varience'] = np.var(data, ddof=ddof)
        stats['25%'] = np.percentile(data, 25)
        stats['50%'] = np.percentile(data, 50)
        stats['75%'] = np.percentile(data, 75)
        stats['Max (absolute)'] = np.max(np.abs(data))
        stats['Min (absolute)'] = np.min(np.abs(data))
        stats['MAE'] = np.mean(np.abs(data))
        stats['RMSE']= np.sqrt(((data)**2).mean())
        stats['RMSE/range'] = stats['RMSE'] / stats['Range']

        # perform the Shapiro-Wilks test for normality of the residuals
        if stats['n'] > 2:
            W, p = shapiro(data)
        else:
            p = -1

        if p > 0.05:
            stats['Normally Distributed'] = False
        elif 0 <= p < 0.05:
            stats['Normally Distributed'] = True
        else:
            stats['Normally Distributed'] = np.nan

        stats['p-value'] = p

        return stats

    def describe_groups(self, groups, exclude_zero=True, ddof=1):
        """ Calculate summary statistics for residuals

        Parameters
        ----------
        groups : list
            groups to include. If no groups submitted, calculate stats for all residuals.

        ddof : int (optional)
            delta degrees of freedom argument to np.std and np.var (see numpy documentation)

        Returns
        -------
        Series of summary statistics for group
        """
        from scipy.stats import shapiro

        # index to supplied groups
        if isinstance(groups, list):
            groups = [g.lower() for g in groups]
            inds = [True if g in groups else False for g in self.df.Group]
            df = self.df.ix[inds, :]
        else:
            df = self.df.ix[self.df.Group == groups.lower(), :]

        # drop any regularisation
        obs = [True if 'regul' not in g else False for g in df.Group]
        df = df.ix[obs, :]

        # drop zero weighted observations
        if exclude_zero:
            nonzero = [True if w > 0 else False for w in df.Weight]
            df = df.ix[nonzero, :]

        stats = pd.DataFrame()
        stats = stats.append(df['Residual'].describe().copy())
        stats.index = ['Group summary']
        stats.columns = [c.capitalize() for c in stats.columns]
        stats.rename(columns={'Count': 'n'}, inplace=True)

        # range, variance, and std
        stats['Range'] = stats['Max'] - stats['Min']
        stats['Standard deviation'] = df.Residual.std(ddof=ddof)
        stats['Varience'] = df.Residual.var(ddof=ddof)

        # absolute max, min amd mean
        stats['Max (absolute)'] = df.Absolute_Residual.max()
        stats['Min (absolute)'] = df.Absolute_Residual.min()
        stats['MAE'] = df.Absolute_Residual.mean()

        # rmse
        stats['RMSE'] = np.sqrt(((df['Residual'].values)**2).mean())
        stats['RMSE/range'] = stats['RMSE'] / stats['Range']

        # perform the Shapiro-Wilks test for normality of the residuals
        if len(df.Residual) > 2:
            W, p = shapiro(df.Residual)
        else:
            p = -1

        if p > 0.05:
            stats['Normally Distributed'] = False
        elif 0 <= p < 0.05:
            stats['Normally Distributed'] = True
        else:
            stats['Normally Distributed'] = np.nan

        stats['p-value'] = p

        # clean-up the ordering
        stats = stats.T.ix[['n', 'Range', 'Max', 'Min', 'Mean', 'Standard deviation', 'Varience', '25%', '50%', '75%',
                          'Max (absolute)', 'Min (absolute)', 'MAE', 'RMSE', 'RMSE/range', 'Normally Distributed', 'p-value']]
        return stats

    @property
    def description(self, exclude_zero=False):
        """ Convenience method to summarize stats for each group
        """
        groups = [g for g in np.unique(self.df.Group) if 'regul' not in g.lower()]

        df = pd.DataFrame()
        for g in groups:

            df[g] = self.describe_groups(g, exclude_zero=exclude_zero)['Group summary']

        return df.T

    def print_stats(self, group):
        ''' Return stats for single group
        
        Parameters
        ----------
        group: str
            Observation group to get stats for
            
        Returns
        --------
        pandas DataFrame
            DataFrame of statistics
            
        '''       
        group_df = self.df.ix[self.df['Group'] == group.lower()]
        # Basic info
        count = group_df.count()['Group']
        min_measured = group_df.describe()['Measured'].loc['min']
        max_measured = group_df.describe()['Measured'].loc['max']
        range_measured = max_measured - min_measured
        min_model = group_df.describe()['Modelled'].loc['min']
        max_model = group_df.describe()['Modelled'].loc['max']
        range_model = max_model - min_model
        
        # Residual Stats
        mean_res = group_df['Residual'].values.mean()
        min_res = group_df['Residual'].values.min()
        max_res = group_df['Residual'].values.max()
        std_res = group_df['Residual'].values.std()
        range_res = max_res - min_res
            
        # Weighted Residual Stats
        mean_w_res = group_df['Weighted Residual'].values.mean()
        min_w_res = group_df['Weighted Residual'].values.min()
        max_w_res = group_df['Weighted Residual'].values.max()
        std_w_res = group_df['Weighted Residual'].values.std()
        range_w_res = max_w_res - min_w_res
        
        # Absolute Residual Stats
        mean_abs_res = group_df['Absolute Residual'].values.mean()
        min_abs_res = group_df['Absolute Residual'].values.min()
        max_abs_res = group_df['Absolute Residual'].values.max()
        std_abs_res = group_df['Absolute Residual'].values.std()
        range_abs_res = max_abs_res - min_abs_res
        
        # Root Mean Square Error
        rmse = math.sqrt(((group_df['Residual'].values)**2).mean())
        
        # RMSE/measured range
        rmse_over_range = rmse/float(range_measured)
        
        print '-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*'
        print 'Observation Group: %s' % (group)
        print '-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*'
        print 'Number of observations in group: %d' % (count)
        print '-------Measured Stats------------------'
        print 'Minimum:   %10.4e  Maximum:   %10.4e' % (min_measured, max_measured)
        print 'Range:     %10.4e' % (range_measured)
        print '-------Residual Stats------------------'
        print 'Mean:      %10.4e  Std Dev:    %10.4e' % (mean_res, std_res)
        print 'Minimum:   %10.4e  Maximum:    %10.4e' % (min_res, max_res)
        print 'RMSE:      %10.4e  RMSE/Range: %10.4e' % (rmse, rmse_over_range)
        print 'Range:     %10.4e' % (range_res)
        print '-------Absolute Residual Stats---------'
        print 'Mean:      %10.4e  Std Dev:   %10.4e' % (mean_abs_res, std_abs_res)
        print 'Minimum:   %10.4e  Maximum:   %10.4e' % (min_abs_res, max_abs_res)
        print 'Range:     %10.4e' % (range_abs_res)
        print '-------Weighted Residual Stats---------'
        print 'Mean:      %10.4e  Std Dev:   %10.4e' % (mean_w_res, std_w_res)
        print 'Minimum:   %10.4e  Maximum:   %10.4e' % (min_w_res, max_w_res)
        print 'Range:     %10.4e' % (range_w_res)
        print ' '
        

    def print_stats_all(self):
        ''' Return stats for each observation group
        
        Returns
        --------
        Stats for each group printed to screen
        
        '''
        grouped = self.df.groupby('Group')
        group_keys = grouped.groups.keys()
        for key in group_keys:
            group_df = self.df.ix[self.df['Group'] == key]
            # Basic info
            count = group_df.count()['Group']
            min_measured = group_df.describe()['Measured'].loc['min']
            max_measured = group_df.describe()['Measured'].loc['max']
            range_measured = max_measured - min_measured
            min_model = group_df.describe()['Modelled'].loc['min']
            max_model = group_df.describe()['Modelled'].loc['max']
            range_model = max_model - min_model
            
            # Residual Stats
            mean_res = group_df['Residual'].values.mean()
            min_res = group_df['Residual'].values.min()
            max_res = group_df['Residual'].values.max()
            std_res = group_df['Residual'].values.std()
            range_res = max_res - min_res
                
            # Weighted Residual Stats
            mean_w_res = group_df['Weighted Residual'].values.mean()
            min_w_res = group_df['Weighted Residual'].values.min()
            max_w_res = group_df['Weighted Residual'].values.max()
            std_w_res = group_df['Weighted Residual'].values.std()
            range_w_res = max_w_res - min_w_res
            
            # Absolute Residual Stats
            mean_abs_res = group_df['Absolute Residual'].values.mean()
            min_abs_res = group_df['Absolute Residual'].values.min()
            max_abs_res = group_df['Absolute Residual'].values.max()
            std_abs_res = group_df['Absolute Residual'].values.std()
            range_abs_res = max_abs_res - min_abs_res
            
            # Root Mean Square Error
            rmse = math.sqrt(((group_df['Residual'].values)**2).mean())
            
            # RMSE/measured range
            if range_measured > 0.0:
                rmse_over_range = rmse/float(range_measured)
            else:
                rmse_over_range = np.nan
            
            print '-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*'
            print 'Observation Group: %s' % (key)
            print '-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*'
            print 'Number of observations in group: %d' % (count)
            print '-------Measured Stats------------------'
            print 'Minimum:   %10.4e  Maximum:   %10.4e' % (min_measured, max_measured)
            print 'Range:     %10.4e' % (range_measured)
            print '-------Residual Stats------------------'
            print 'Mean:      %10.4e  Std Dev:    %10.4e' % (mean_res, std_res)
            print 'Minimum:   %10.4e  Maximum:    %10.4e' % (min_res, max_res)
            print 'RMSE:      %10.4e  RMSE/Range: %10.4e' % (rmse, rmse_over_range)
            print 'Range:     %10.4e' % (range_res)
            print '-------Absolute Residual Stats---------'
            print 'Mean:      %10.4e  Std Dev:   %10.4e' % (mean_abs_res, std_abs_res)
            print 'Minimum:   %10.4e  Maximum:   %10.4e' % (min_abs_res, max_abs_res)
            print 'Range:     %10.4e' % (range_abs_res)
            print '-------Weighted Residual Stats---------'
            print 'Mean:      %10.4e  Std Dev:   %10.4e' % (mean_w_res, std_w_res)
            print 'Minimum:   %10.4e  Maximum:   %10.4e' % (min_w_res, max_w_res)
            print 'Range:     %10.4e' % (range_w_res)
            print ' '


    def plot_objective_contrib (self, df=None, drop_regul=False):
        ''' Plot the contribution of each group to the objective function 
        as a pie chart.
        drop_regul: If True, ignores regularization groups
        Returns
        -------
        metplotlib pie chart
        
        Notes
        -----
        Does not plot observation group is contribution is less than 1%.  This
        is to make the plot easier to read.
        '''

        # Allow any residuals dataframe to be submitted as argument
        if df is None:
            df = self.df.copy()




        contributions = []
        groups = []
        grouped = df.groupby('Group')
        group_keys = grouped.groups.keys()
        for key in group_keys:
            if drop_regul:
                if key.lower().startswith('regul'):
                    pass
                else:
                    contributions.append((grouped.get_group(key)['Weighted_Residual']**2).sum())
                    groups.append(key)
            else:
                contributions.append((grouped.get_group(key)['Weighted_Residual']**2).sum())
                groups.append(key)
        percents = (contributions / sum(contributions))*100
        groups = np.array(groups)
        data = np.rec.fromarrays([percents, groups])
        data.sort()
        data.dtype.names = ('Percent', 'Group')
        # Get data where percent is greater than 1
        # Won't plot groups that fall into less than 1 percent category
        greater_1_values = []
        greater_1_groups = []
        for i in data:
            if i[0] > 1.0:
                greater_1_values.append(i[0])
                greater_1_groups.append(i[1]) 
        # Assign colors for each group
        color_map = plt.get_cmap('Set3')
        color_dict = dict()
        for i in range(len(greater_1_groups)):
            color = color_map(1.*i/len(greater_1_groups))
            color_dict[greater_1_groups[i]] = color
        colors = []
        for group in greater_1_groups:            
            colors.append(color_dict[group])
        plt.pie(greater_1_values, labels=greater_1_groups, autopct='%1.1f%%', colors = colors, startangle=90)

        
    def objective_contrib (self, df=None, return_data=False):
        '''Print out the contribution of each observation group to the 
        objective function as a percent
        
        Parameters
        ----------
        return_data : {False, True}, optional
            if True return data as a numpy structured array
            
        Returns
        -------
        None or Numpy array
        '''
        # Allow any residuals dataframe to be submitted as argument
        if df is None:
            df = self.df

        contributions = []
        groups = []
        grouped = self.df.groupby('Group')
        group_keys = grouped.groups.keys()
        for key in group_keys:
            contributions.append((grouped.get_group(key)['Weighted Residual']**2).sum())
            groups.append(key)
        percents = (contributions / sum(contributions))*100
        groups = np.array(groups)
        #it = np.nditer(percents, flags = ['multi_index'])
        #while not it.finished:
            #print percents[it.multi_index], groups[it.multi_index]
            #it.iternext()
        data = np.rec.fromarrays([percents, groups])
        data.dtype.names = ('Percent', 'Group')
        #data = np.rec.fromarrays([percents, groups], dtype = [('Percent', float), ('Group', str)])
        data.sort()
        for item in data:
            print '%.2f%%   %s' % (item[0], item[1])
        if return_data == True:
            return data
        else:
            return None

    
    def plot_measure_vs_model(self, groups = None, plot_type = 'scatter'):
        '''Plot measured vs. model
           
           Parameters
           ----------
           groups : {None, list}, optional
               list of observation groups to include
           
           plot_type : {'scatter', 'hexbin'}, optional
               Default is a scatter plot.  Hexbin is list a 2D histogram, colors
               are log flooded.  hexbin is useful when points are numerous and
               bunched together where symbols overlap significantly on a 
               scatter plot
               
            Returns
            -------
            matplotlib plot

        '''          
        if groups == None:
            measured = self.df['Measured'].values
            modeled = self.df['Modelled'].values
        if groups != None:
            measured = self.df[self.df['Group'].isin(groups)]['Measured'].values
            modeled = self.df[self.df['Group'].isin(groups)]['Modelled'].values
        
        # Make New Figure
        plt.figure()
        if plot_type == 'scatter':       
            plt.scatter(measured, modeled)
        if plot_type == 'hexbin':
            plt.hexbin(measured, modeled, bins = 'log', alpha = 1.0, edgecolors = 'none')
  
        # Plot 1to1 (x=y) line
        data_min = min(min(measured), min(modeled))
        data_max = max(max(measured), max(modeled))
        plt.plot([data_min,data_max], [data_min,data_max], color = 'gray')
        
        #Labels
        plt.xlabel('Measured')
        plt.ylabel('Modelled')
       
        # Print title is groups available
        if groups != None:
            plt.title(', '.join(groups))
        # Set x and Y axis equal
        #x_lim = plt.xlim()
        #plt.ylim(x_lim)
        plt.axis([data_min, data_max, data_min, data_max])
        
        plt.grid(True)
        plt.tight_layout()
    
    def plot_measured_vs_residual(self, groups = None, weighted = False, 
                                  plot_mean = True, plot_std = True, 
                                  plot_type = 'scatter'):
        ''' Plot measured vs. residual
        
            Parameters
            ----------
            groups : {None, list}, optional
                list of observation groups to include
            
            weighted : {False, True}, optional
                user weighted residuals
              
            plot_mean : {True, False}, optional
                plot line for mean residual
                
            plot_std : {True, False}, optional
                plot shaded area for std. dev. of residuals
                
            plot_type : {'scatter', 'hexbin'}, optional
               Default is a scatter plot.  Hexbin is list a 2D histogram, colors
               are log flooded.  hexbin is useful when points are numerous and
               bunched together where symbols overlap significantly on a 
               scatter plot
                
            Returns
            --------
            matplotlib plot
        
        '''
        if groups == None:
            measured = self.df['Measured'].values
            if weighted == False:
                residual = self.df['Residual'].values
            if weighted == True:
                residual = self.df['Weighted Residual'].values
        if groups != None:
            measured = self.df[self.df['Group'].isin(groups)]['Measured'].values
            if weighted == False:
                residual = self.df[self.df['Group'].isin(groups)]['Residual'].values
            if weighted == True:
                residual = self.df[self.df['Group'].isin(groups)]['Weighted Residual'].values
        
        # Make New Figure
        plt.figure()
        if plot_type == 'scatter':      
            plt.scatter(measured, residual)
            # Plot shadded area of residual std dev
            if plot_std == True:
                plt.axhspan(residual.mean()+residual.std(), residual.mean()-residual.std(), facecolor='r', alpha=0.2)
        if plot_type == 'hexbin':
            plt.hexbin(measured, residual, bins = 'log', alpha = 0.8, edgecolors = 'none')
            # Plot shadded area of residual std dev
            if plot_std == True:
                plt.axhspan(residual.mean()+residual.std(), residual.mean()-residual.std(), fc='none', ec='r', alpha=0.5)
        
        # Add thicker line at 0 residual
        plt.axhline(y=0, color = 'k')
        
        #Plot line for mean residual
        if plot_mean == True:
            plt.axhline(y=residual.mean(), color = 'r')

        
        #Labels
        plt.xlabel('Measured')
        plt.ylabel('Residual')
        
       
       # Print title is groups available
        if groups != None:
            plt.title(', '.join(groups))

        plt.grid(True)
        plt.tight_layout()


    def plot_one2one(self, groupinfo, title=None, print_stats=[], print_format='.2f',
                     exclude_zero_stats=True,
                     line_kwds={}, **kwds):
        """
        Makes one-to-one plot of two dataframe columns, using pyplot.scatter

        Parameters
        ----------
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

        Notes
        ------

        """
        plot_obj = plots.One2onePlot(self.df, 'Measured', 'Modelled', groupinfo, title=title,
                                     line_kwds=line_kwds, **kwds)

        plot_obj.generate()

        if len(print_stats) > 0:
            stats = self.describe_groups(plot_obj.groups, exclude_zero=exclude_zero_stats).ix[print_stats]
            text = ''.join(['{}: {:{fmt}}\n'.format(i, r['Group summary'], fmt=print_format) for i, r in stats.iterrows()])
            plot_obj.ax.text(0.05, 0.95, text, transform=plot_obj.ax.transAxes, va='top', ha='left')

        plot_obj.draw()

        return plot_obj.fig, plot_obj.ax


    def plot_hexbin(self, groupinfo, title=None, print_stats=[], print_format='.2f',
                    exclude_zero_stats=True, line_kwds={}, **kwds):
        """
        Makes a hexbin plot of two dataframe columns, pyplot.hexbin

        Parameters
        ----------
        groupinfo: dict, list, or string
            If string, name of group in "Group" column of df to plot. Multiple groups
            in "Group" column of df can be specified using a list. A dictionary
            can be supplied to indicate the groups to plot (as keys), with item consisting of
            a dictionary of keywork arguments to Matplotlib.pyplot to customize the plotting of each group.

        title:
            not sure if we need to specify arguments like this one if we are already using kwds. Need to look into it more.

        line_kwds: dict, optional
            Additional keyword arguments to Matplotlib.pyplot.plot, for controlling appearance of one-to-one line.
            See http://matplotlib.org/api/pyplot_api.html

        **kwds:
            Additional keyword arguments to Matplotlib.pyplot.hexbin, for controlling appearance hexbin plot.
            (need to figure out how to differentiate documentation with inheritance!)
            See http://matplotlib.org/api/pyplot_api.html

        Notes
        ------

        """
        plot_obj = plots.HexbinPlot(self.df, 'Measured', 'Modelled', groupinfo, title=title,
                                    line_kwds=line_kwds, **kwds)
        plot_obj.generate()

        if len(print_stats) > 0:
            stats = self.describe_groups(plot_obj.groups, exclude_zero=exclude_zero_stats).ix[print_stats]
            text = ''.join(['{}: {:{fmt}}\n'.format(i, r['Group summary'], fmt=print_format) for i, r in stats.iterrows()])
            plot_obj.ax.text(0.05, 0.95, text, transform=plot_obj.ax.transAxes, va='top', ha='left')

        plot_obj.draw()


        return plot_obj.fig, plot_obj.ax


    def plot_hist(self, df=None, col='Residual', by='Group', groupinfo={}, layout=None, **kwds):
        """
        Makes a histogram of a dataframe column

        Parameters
        ----------


        Notes
        ------

        """
        kwds.update({'ylabel': 'Number of Observations', 'xlabel': 'Error',
                     })
        if df is None:
            df = self.df

        plot_obj = plots.Hist(df, col, by, groupinfo, layout=None, **kwds)
        plot_obj._make_plot() # bypass the other generation methods because we're using pandas
        plot_obj.draw()


        return plot_obj.fig, plot_obj.ax
