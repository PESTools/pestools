#####<center>Pestools - A Python toolkit for processing PEST-related information
<center>Evan G. Christianson<sup>1</sup>, Andrew T. Leaf<sup>2</sup></center>
<center><sup>1</sup>Barr Engineering, echristianson@barr.com, Minneapolis, MN, USA</center>
<center><sup>2</sup>USGS – Wisconsin Water Science Center, aleaf@usgs.gov, Madison, WI, USA</center>  

  
#####<center>ABSTRACT</center>
PESTools is an open-source Python package for processing and visualizing information associated 
with the parameter estimation software PEST.  While PEST output can be reformatted for post- 
processing in spreadsheets or other menu-driven software packages, this approach can be error-prone 
and time-consuming. Managing information from highly parameterized models with thousands of 
parameters and observations presents additional challenges. PESTools consists of a set of Python 
object classes to facilitate efficient processing and visualization of PEST-related information. 
Processing and visualization of observation residuals, objective function contributions, parameter and 
observation sensitivities, parameter correlation and identifiability, and other common PEST outputs 
have been implemented. The use of dataframe objects (pandas Python package) facilitates rapid 
slicing and querying of large datasets, as well as the incorporation of ancillary information such as 
observation locations and times and measurement types. PESTools’ object methods can be easily be 
scripted with concise code, or alternatively, the use of IPython notebooks allows for live interaction 
with the information. PESTools is designed to not only streamline workflows, but also provide deeper 
insight into model behavior, enhance troubleshooting, and improve transparency in the calibration
process.

#####<center>INTRODUCTION
In recent years the PEST software suite has become the industry standard for calibrating groundwater flow models and evaluating uncertainty in their predictions. PEST has many advantages, including the ability to robustly handle highly parameterized models with thousands of observations and parameters, as well as numerous  utility programs to perform ancillary analyses and facilitate use with popular modeling software such as MODFLOW. The use of PEST presents many challenges, however, especially in the highly parameterized context. Calibration of a highly parameterized model typically requires managing large volumes of information spread across numerous input and output files. This information can provide valuable insight to the modeler, but can be difficult or impossible to effectively visualize without custom programming. PESTools aims to provide a central platform for managing and visualizing this information, which minimizes the number of intermediate files and custom code required for parameter estimation workflows.

#####<center>DEMONSTRATION
PESTools consists of a set of Python object classes to facilitate efficient processing and visualization of PEST-related information. Some of the cababilities of PESTools are presented below.
<table border="1" class="dataframe">  <thead>    <tr style="text-align: right;">      <th></th>      <th>Group summary</th>    </tr>  </thead>  <tbody>    <tr>      <th>Mean</th>      <td>-2.704151</td>    </tr>    <tr>      <th>MAE</th>      <td> 15.54417</td>    </tr>    <tr>      <th>RMSE</th>      <td> 24.49298</td>    </tr>  </tbody></table>
**Table 1. with some stuff**  
some more stuff  
![a graph](examples/hexbin.pdf)  
**Figure 1. showing some stuff** 
#####<center>SUMMARY
PESTools is an open-source package aimed at leveraging the data analysis and visualization capabilities of Python to streamline parameter estimation workflows, allowing for deeper insight into model behavior, enhanced troubleshooting, and improved transparency in the calibration process. PESTtools is a work in progress. It can be downloaded at https://github.com/PESTools. We encourage contributions of code and examples, as well as feedback in the form of GitHub Issues.

#####<center>REFERENCES
Doherty, J., 2010a, PEST, Model-independent parameter estimation—User manual (5th ed., with slight additions): Brisbane, Australia, Watermark Numerical Computing, accessed November 13, 2014 at http://www.pesthomepage.org/.  Doherty, J., 2010b, PEST, Model Independent Parameter Estimation. Addendum to User Manual (5th Edition): Brisbane, Australia, Watermark Numerical Computing, accessed November 13, 2014 at http://www.pesthomepage.org/.