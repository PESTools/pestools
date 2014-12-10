REM This part of batch file added by SVDAPREP
REM
REM Delete model input files.
del points3.dat
del points4.dat
del points5.dat
del points6.dat
del par2par.in
del Columbia.sfr
del Columbia.drn
REM
REM Run PARCALC to compute base parameters from super parameters.
parcalc
REM
REM Run PICALC to compute base parameter prior information.
picalc
REM
REM The following is copied directly from file Columbia.bat
REM
del Columbia.hds
del Columbia.ddn
del Columbia.cbb
del Columbia_streamflow.dat
del Columbia_SFR.out
del HobData.txt
del *._kx*
del *._kz*
del Columbia_Rch.dat
del parameters.in

:: run par2par to convert anisotropy to vertical K
par2par par2par.in

:: Setup K-fields using Pilot Points
fac2real <fac2real3.in
fac2real <fac2real4.in
fac2real <fac2real5.in
fac2real <fac2real6.in
fac2real <fac2realz3.in
fac2real <fac2realz4.in
fac2real <fac2realz5.in
fac2real <fac2realz6.in

:: Setup K zones in Layers 1 and 2;
:: copy K values in layers 3 and 5 for areas where TC/EC absent from layers below
..\Python27\python Columbia_calibration_utilities.py

MODFLOW-NWT_64.exe Columbia.nam

:: extract model results at flux observation locations
..\Python27\python SFRreader.py

:: calculate vertical head differences for Arlington and Rio
..\Python27\python obs2obs.py
