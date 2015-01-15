pest_tools
==========

Development repository for PEST stuff


MODFLOW and More 2015 Abstract
===============================
Pestools - A Python toolkit for processing PEST-related information
Evan G. Christianson1, Andrew T. Leaf2

1) Barr Engineering, echristianson@barr.com, Minneapolis, MN
2) USGS – Wisconsin Water Science Center, aleaf@usgs.gov, Madison, WI

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
