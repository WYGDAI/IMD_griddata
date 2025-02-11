"""
This code will give all the information regarding the netCDF file given in "Dataset" variable (line 9)

                                        -k.r.bro_05
"""

from netCDF4 import Dataset

data = Dataset(
    r"C:\Users\koust\Desktop\PhD\IMD_grid\1_IMD_GRDncConv\temp_min-archive_nc\Mintemp_MinT_1951.nc",
    'r'
)


print(data)

input("Check the variables in the run statement, adjust the variables below accordingly and RERUN the code. \n"
      "Smooth run of the code means that the variables are input correctly. \n"
      "Otherwise check the variables again. \n"
      "Press any key to continue")

lat = data.variables['LATITUDE'] if 'LATITUDE' in data.variables else data.variables['lat']
lon = data.variables['LONGITUDE'] if 'LONGITUDE' in data.variables else data.variables['lon']
time = data.variables['TIME']
variable = data.variables['temp_min']

lat_values = lat[:]
lon_values = lon[:]
time_values = time[:]
variable_values = variable[:]

print("Information about latitude dimension:")
print(lat)
print("\n\n")
print("Information about longitude dimension:")
print(lon)
print("\n\n")
print("Information about time dimension:")
print(time)
print("\n\n")
print("Information about variable:")
print(variable)
print("\n\n\n\n")

print("Latitude values:")
print(lat_values)
print("\n\n")
print("Longitude values:")
print(lon_values)
print("\n\n")
print("Time values:")
print(time_values)
print("\n\n")
print("Variable values:")
print(variable_values)
print("\n\n\n\n")
