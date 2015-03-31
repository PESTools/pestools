MODFLOW and More 2015 proceedings
===============================  

#####<center>Pestools - A Python toolkit for processing PEST-related information
<center>Evan G. Christianson<sup>1</sup>, Andrew T. Leaf<sup>2</sup>  
<center><sup>1</sup>Barr Engineering, echristianson@barr.com, Minneapolis, MN, USA  
<center><sup>2</sup>USGS – Wisconsin Water Science Center, aleaf@usgs.gov, Madison, WI, USA
  
  
#####<center>ABSTRACT
Pestools is an open-source Python package for processing and visualizing information associated 
with the parameter estimation software PEST.  While PEST output can be reformatted for post- 
processing in spreadsheets or other menu-driven software packages, this approach can be error-prone 
and time-consuming. Managing information from highly parameterized models with thousands of 
parameters and observations presents additional challenges. Pestools consists of a set of Python 
object classes to facilitate efficient processing and visualization of PEST-related information. 
Processing and visualization of observation residuals, objective function contributions, parameter and 
observation sensitivities, parameter correlation and identifiability, and other common PEST outputs 
have been implemented. The use of dataframe objects (pandas Python package) facilitates rapid 
slicing and querying of large datasets, as well as the incorporation of ancillary information such as 
observation locations and times and measurement types. Pestools’ object methods can be easily be 
scripted with concise code, or alternatively, the use of IPython notebooks allows for live interaction 
with the information. Pestools is designed to not only streamline workflows, but also provide deeper 
insight into model behavior, enhance troubleshooting, and improve transparency in the calibration 
process.  
#####<center>INTRODUCTION

#####<center>DEMONSTRATION
some stuff     
<table border="1" class="dataframe">  <thead>    <tr style="text-align: right;">      <th></th>      <th>Group summary</th>    </tr>  </thead>  <tbody>    <tr>      <th>Mean</th>      <td>-2.704151</td>    </tr>    <tr>      <th>MAE</th>      <td> 15.54417</td>    </tr>    <tr>      <th>RMSE</th>      <td> 24.49298</td>    </tr>  </tbody></table>
**Table 1. with some stuff**  
some more stuff  
![a graph](Examples/hexbin.pdf)  
**Figure 1. showing some stuff** 
#####<center>SUMMARY
#####<center>REFERENCES
