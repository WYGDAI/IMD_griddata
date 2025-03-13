# IMD_griddata
## For dealing with gridded archive and realtime data provided by Indian Meteorological Depratment (IMD).

This is a set of codes dealing with various tasks that maybe required before proper usage of data as provided by Indian Meteorological Department. For smooth operation, it is recommended to use all of these codes in unison and sequence.

The numbers preceeding the file name of each code is the expected running order of each of the codes. A brief description of each of them is given below:

1. 0_downloadIMD
   - for downloading archive and realtime data at resolutions mentioned within the description of the code
     
2. 1_GRD_nc_conv
   - convert .GRD and .grd files to .nc files to open them up for geospatial functions. This is necessary for succeeding codes to work.

3. 2_regrid
   - interpolate and regrid a particular .nc dataset in accordance to the grid structure of another .nc dataset
   - bilinear interpolation is used primarily
   - where bilinear is not applicable, nearest neighbour is used to ensure edge values are not lost
  
4. 3_ncClip
   - clip a .nc dataset with a shapefile given by the user
  
5. 4_rename
   - if any mixing of datasets of a particular variable is done
      - like mixing of archive data for a period and realtime for another
   - standardizes the name of each file in a folder in accordance to the year of each data
  
6. 5_nc2excel
   - gives an excel file for the final .nc file
   - rows: grid points, columns: days of the year
   - 3 index columns with headers: " ", "Lat", "Lon"
  
7. 6_statistical_extractions
   - for computation of various statistical measures from the generated excel files
   - gives an excel file
  
Further information on each of the individual codes are provided in the description section within each code.
