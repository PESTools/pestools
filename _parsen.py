# -*- coding: utf-8 -*-
"""
Created on Fri Nov 28 09:31:15 2014

@author: egc
"""
from _pst import Pst
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class ParSen(Pst):
    def __init__(self, pst_path, jco_df = None, drop_regul = False, drop_groups = None, keep_groups = None, keep_obs = None, remove_obs = None):
        super(ParSen, self).__init__(pst_path)


        ''' Create ParSen class
            
        Parameters
        ---------- 
        jco_df : DataFrame, optional,
            Pandas DataFrame of the jacobian. If not provided then it will be
            read in based on base name of pest file provided. Providing a jco_df
            offers some efficiencies if working interactively. Otherwise the jco
            is read in every time ParSen class is initialized.  Jco_df is an
            attribute of the Jco class

        drop_regul: {False, True}, optional
            Flag to drop regularization information in calculating parameter
            sensitivity.  Will set weight to zero for all observations with
            'regul' in the observation group name
        
        drop_groups: list, optional
            List of observation groups to drop when calculating parameter 
            sensitivity.  If all groups are part of regularization it may
            be easier to use the drop_regul flag
            
        keep_groups: list, optional
            List of observation groups to include in calculating parameter
            sensitivity.  Sometimes easier to use when looking at sensitivity
            to a single, or small number, or observation groups
        
        keep_obs: list, optional
            List of obervations to include in calculating parameter
            sensitivity.  If keep_obs != None then weights for all observations
            not in keep_obs will be set to zero.
            
        remove_obs: list, optional
            List of obervations to remove in calculating parameter
            sensitivity.  If remove_obs != None then weights for all observations
            in remove_obs will be set to zero.       
            
        Attributes
        ----------
        par_sen_df : Pandas DataFrame 
            DataFrame of parameter sensitivity.  Index entries of the DataFrame
            are the parameter names.  The DataFrame has two columns: 
            1) Parameter Group and 2) Sensitivity
            
        Methods
        -------
        plot()
        tail()
        head()
        par()
        group()
        sum_group()
        plot_sum_group()
        plot_mean_group()



        Notes
        ------
        For drop_regul = True could alternatively remove regularization info 
        from jco_df but haven't found easy way to do so, particularly 
        with large jco
        
        ''' 
        if jco_df == None:              
            jco_df = self._load_jco()

        # Build weights array
        weights = []
        ob_groups = []
        for ob in jco_df.index:
            weight = float(self._obs_dict[ob][1])
            ob_group = self._obs_dict[ob][2]
            
            # Set weights for regularization info to zero if drop_regul == True
            if drop_regul == True and 'regul' in ob_group.lower():
                weight = 0.0
            
            # Set weights for obs in drop_groups to zero
            if drop_groups != None:
                # set all groups in drop_groups to lower case
                drop_groups = [item.lower() for item in drop_groups]
                if ob_group.lower() in drop_groups:
                    weight = 0.0
            
            # Set weights for obs not in keep_group to zero
            if keep_groups != None:
                # set all groups in keep_groups to lower case
                keep_groups = [item.lower() for item in keep_groups]
                if ob_group.lower() not in keep_groups:
                    weight = 0.0
                    
            # Set weights for obs not in keep_obs to zero
            if keep_obs != None:
                # set all obs in keep_obs to lower case
                keep_obs = [item.lower() for item in keep_obs]
                if ob.lower() not in keep_obs:
                    weight = 0.0
            # Set weights for obs in remove_obs to zero
            if remove_obs != None:
                # set all obs in keep_obs to lower case
                remove_obs = [item.lower() for item in remove_obs]
                if ob.lower() in remove_obs:
                    weight = 0.0                
                
            weights.append(weight)
            ob_groups.append(ob_group)
        
        # Get count of non-zero weights    
        n_nonzero_weights = np.count_nonzero(weights)
        
        # Calculate sensitivities
        sensitivities = []
        for col in jco_df:
            sen = np.linalg.norm(np.asarray(jco_df[col])*weights)/n_nonzero_weights
            sensitivities.append(sen)    
        
        # Build Group Array
        par_groups = []
        for par in jco_df.columns:
            par_group = self._pars_dict[par][5]
            par_groups.append(par_group)
        
        # Build pandas data frame of parameter sensitivities    
        sen_data = {'Sensitivity' : sensitivities, 'Parameter Group' : par_groups}
        par_sen_df = pd.DataFrame(sen_data, index = jco_df.columns)
        self.par_sen_df = par_sen_df


    def plot(self, n = None, group = None):
        ''' Generate plot of parameter sensitivity
        
        Paramters
        ----------
        n: {None, int}, optional
            If None then plot all parameters, else n is the number to plot.
            If n is less than 0 then plot least sensitive parameters
            If n is greater than 0 then plot most sensitive parameters
        group: {None, str}, optional
            Parameter group to plot           
            If None plot all parameter groups
                      
        Returns
        -------
        Matplotlib plot
            Bar plot of parameter sensitivity
        '''
        plt.figure() ### Make New figure
        if group == None:    
            if n == None:
                n_head = len(self.par_sen_df.index)
            else:
                n_head = n
            if n_head > 0:                        
                pars = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).head(n=n_head)['Sensitivity'].index
                sensitivity = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).head(n=n_head)['Sensitivity'].values
                par_groups = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).head(n=n_head)['Parameter Group'].values
            if n_head < 0:
                n_head = abs(n_head)
                pars = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).tail(n=n_head)['Sensitivity'].index
                sensitivity = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).tail(n=n_head)['Sensitivity'].values
                par_groups = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).tail(n=n_head)['Parameter Group'].values            
    
            # Assign colors for each group
            color_map = plt.get_cmap('Spectral')
            color_dict = dict()
            unique_par_groups = np.asarray(self.par_sen_df.drop_duplicates(cols = 'Parameter Group')['Parameter Group'])
            for i in range(len(unique_par_groups)):
                color = color_map(1.*i/len(unique_par_groups))
                color_dict[unique_par_groups[i]] = color
            colors = []
            for par_group in par_groups:            
                colors.append(color_dict[par_group])
            
            plt.barh(np.arange(len(pars)), sensitivity, color = colors, align = 'center')
            plt.yticks(np.arange(len(pars)), pars)
            plt.ylim(-1, len(pars))
            plt.xlabel('Parameter Sensitivity')
            plt.ylabel('Parameter') 
            plt.grid(True, axis = 'x')
            plt.tight_layout()
            
        if group != None:
            group = group.lower()
            if n == None:
                n_head = len(self.par_sen_df.index)
            else:
                n_head = n
            
            if n_head > 0:            
                pars = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).ix[self.par_sen_df['Parameter Group'] == group, 'Sensitivity'].head(n=n_head).index
                sensitivity = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).ix[self.par_sen_df['Parameter Group'] == group, 'Sensitivity'].head(n=n_head).values          
            if n_head < 0:
                n_head = abs(n_head)            
                pars = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).ix[self.par_sen_df['Parameter Group'] == group, 'Sensitivity'].tail(n=n_head).index
                sensitivity = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).ix[self.par_sen_df['Parameter Group'] == group, 'Sensitivity'].tail(n=n_head).values                      
            
            plt.barh(np.arange(len(pars)), sensitivity, align = 'center')
            plt.yticks(np.arange(len(pars)), pars)
            plt.ylim(-1, len(pars))
            plt.xlabel('Parameter Sensitivity')
            plt.ylabel('Parameter')        
            plt.tight_layout() 
            
    def tail(self, n_tail):
        ''' Get the lest sensitive parameters
        Parameters
        ----------
        n_tail: int
            Number of parameters to get
                
        Returns
        ---------
        pandas Series
            Series of n_tail least sensitive parameters
                
        '''
        return self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).tail(n=n_tail)['Sensitivity']
        
    def head(self, n_head):
        ''' Get the most sensitive parameters
        Parameters
        ----------
        n_head: int
            Number of parameters to get
                
        Returns
        -------
        pandas Series
            Series of n_head most sensitive parameters
        '''
        return self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).head(n=n_head)['Sensitivity']

    def par(self, parameter):
        '''Return the sensitivity of a single parameter
        
        Parameters
        ----------
        parameter: string
        
        Returns
        ---------
        float
            sensitivity of parameter
        
        '''
        return self.par_sen_df.xs(parameter)['Sensitivity']
        
    def group(self, group, n = None):
        '''Return the sensitivites of a parameter group
        
        Parameters
        ----------
        group: string
        
        n: {None, int}, optional
            If None then return all parmeters from group, else n is the number
            of paremeters to return.
            If n is less than 0 then return the least sensitive parameters 
            If n is greater than 0 then retrun the most sensitive parameters
            
        Returns
        -------
        Pandas DataFrame
        
        '''
        group = group.lower()
        if n == None:
            n_head = len(self.par_sen_df.index)
        else:
            n_head = n
        
        if n_head > 0:            
            sensitivity = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).ix[self.par_sen_df['Parameter Group'] == group].head(n=n_head)
        if n_head < 0:
            n_head = abs(n_head)            
            sensitivity = self.par_sen_df.sort(columns = 'Sensitivity', ascending = False).ix[self.par_sen_df['Parameter Group'] == group].tail(n=n_head)
            
        sensitivity.index.name = 'Parameter'
        return sensitivity
        
    def sum_group (self):
        ''' Return sum of all parameters sensitivity by group
        
        Returns
        -------
        Pandas DataFrame
        '''
        sen_grouped = self.par_sen_df.groupby(['Parameter Group']).aggregate(np.sum).sort(columns = 'Sensitivity', ascending = False)
        return sen_grouped
        
    def plot_sum_group (self):
        ''' Plot sum of all parameters sensitivity by group
        
        Returns
        -------
        Matplotlib plot
            Bar plot of sum of sensitivity by parameter group
        '''
        plt.figure() ## Make New Figure
        sen_grouped = self.par_sen_df.groupby(['Parameter Group']).aggregate(np.sum).sort(columns = 'Sensitivity', ascending = False)
        pars = sen_grouped.index
        sensitivity = sen_grouped.values
        plt.barh(np.arange(len(pars)), sensitivity, align = 'center')
        plt.yticks(np.arange(len(pars)), pars)
        plt.ylim(-1, len(pars))
        plt.xlabel('Sum of Parameter Sensitivity')
        plt.ylabel('Parameter Group')
        plt.grid(True, axis = 'x')        
        plt.tight_layout() 
        
    def plot_mean_group (self):
        ''' Plot mean of all parameters sensitivity by group
        
        Returns
        -------
        Matplotlib plot
            Bar plot of mean of sensitivity by parameter group
        '''
        plt.figure() ## Make New Figure
        sen_grouped = self.par_sen_df.groupby(['Parameter Group']).aggregate(np.mean).sort(columns = 'Sensitivity', ascending = False)
        pars = sen_grouped.index
        sensitivity = sen_grouped.values
        plt.barh(np.arange(len(pars)), sensitivity, align = 'center')
        plt.yticks(np.arange(len(pars)), pars)
        plt.ylim(-1, len(pars))
        plt.xlabel('Mean of Parameter Sensitivity')
        plt.ylabel('Parameter Group')
        plt.grid(True, axis = 'x')        
        plt.tight_layout()
        
if __name__ == '__main__':
    par_sen = ParSen('C:\Anaconda\Lib\site-packages\pest_tools\Examples\example.pst')