# -*- coding: utf-8 -*-

from _pst import Pst
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Res(Pst):
    '''
    Attributes
    ----------
    res_df : Pandas Data Frame

       
    Methods
    -------
    plot_measure_vs_model()
    plot_measured_vs_residual()
    plot_objective_contrib
    objective_contrib()
    
    
    '''
    def __init__(self, pst_path, extension = '.res'):
        super(Res, self).__init__(pst_path)
        res_file = self._fname_base+extension
        check = open(res_file, 'r')
        line_num = 0
        while True:
            current_line = check.readline()
            if "Name" in current_line and "Residual" in current_line:
                break
            else:
                line_num += 1             
        self.res_df = pd.read_csv(res_file, sep = '\s*', index_col = 0, header = line_num)
        # Apply weighted residual
        self.res_df['Weighted Residual'] = self.res_df['Residual'] * self.res_df['Weight']
        self.res_df['Absolute Residual'] = abs(self.res_df['Residual'])
        self.res_df['Weighted Absolute Residual'] = self.res_df['Absolute Residual'] * self.res_df['Weight']
        
        
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
            measured = self.res_df['Measured'].values
            modeled = self.res_df['Modelled'].values
        if groups != None:
            measured = self.res_df[self.res_df['Group'].isin(groups)]['Measured'].values
            modeled = self.res_df[self.res_df['Group'].isin(groups)]['Modelled'].values
        
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
            measured = self.res_df['Measured'].values
            if weighted == False:
                residual = self.res_df['Residual'].values
            if weighted == True:
                residual = self.res_df['Weighted Residual'].values
        if groups != None:
            measured = self.res_df[self.res_df['Group'].isin(groups)]['Measured'].values
            if weighted == False:
                residual = self.res_df[self.res_df['Group'].isin(groups)]['Residual'].values
            if weighted == True:
                residual = self.res_df[self.res_df['Group'].isin(groups)]['Weighted Residual'].values
        
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

    def objective_contrib(self, return_data = False):
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
        contributions = []
        groups = []
        grouped = self.res_df.groupby('Group')
        group_keys = grouped.groups.keys()
        for key in group_keys:
            contributions.append((grouped.get_group(key)['Weighted Residual']**2).sum())
            groups.append(key)
        percents = (contributions / sum(contributions))*100
        groups = np.array(groups)
        data = np.rec.fromarrays([percents, groups])
        data.dtype.names = ('Percent', 'Group')
        data.sort()
        for item in data:
            print '%.2f%%   %s' % (item[0], item[1])
        if return_data == True:
            return data
        else:
            return None
            
    def plot_objective_contrib(self):
        ''' Plot the contribution of each group to the objective function 
        as a pie chart.
        
        Returns
        -------
        metplotlib pie chart
        
        Notes
        -----
        Does not plot observation group is contribution is less than 1%.  This
        is to make the plot easier to read.
        '''       
        data = self.objective_contrib(return_data = True)        
        
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
    
    
if __name__ == '__main__':
    res = Res(r'C:\Anaconda\Lib\site-packages\pest_tools\notebooks\example.pst')
    res.plot_measure_vs_model(groups=['syn08'])