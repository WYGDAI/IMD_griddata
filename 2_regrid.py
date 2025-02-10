"""
INTERPOLATING ONE FILE ACCORDING TO ALIGN TO THE GRID STRUCTURE OF ANOTHER FILE
    - code runs bilinear interpolation primarily
    - at regions where bilinear interpolation is not applicable, nearest neighbour is used

A few prerequisites required:
    + use 'ncinfo.py' on the following to find out the applicable dimensions to be adjusted into the code
        - any one of the files in the input folder that need to be interpolated
        - the file that is going to be the basis of interpolation

* Variables that need to be edited are given from lines 41 to 56 *
    + folder where the to-be-interpolated files are present: "input_folder"
    + folder where the interpolated files are to be saved: "output_folder"
    + file that will be the basis of interpolation: "file_used_for_interpolation"
    + Variable of the dataset to be interpolated: "var"
        - rain
        - temp_max
        - temp_min
            can be any other variable - check from the information of the .nc file using "ncinfo.py"
    + Dimensions to be adjusted
        - for input files that are to be interpolated
            input_latitude_variable_name
            input_longitude_variable_name
            input_time_variable_name
        - for basis file used for interpolation
            interpolation_latitude_name
            interpolation_longitude_name

                                            - k.r.bro_05
"""

import os
import xarray as xr
import re
import sys
import numpy as np
import pyinterp
import netCDF4 as nc
from scipy.interpolate import griddata

# Variables that need adjusting
input_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\1_IMD_GRDncConv\temp_min-realtime_nc"
output_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\2_IMDinterpolated"

file_used_for_interpolation = xr.open_dataset(
    r"C:\Users\koust\Desktop\PhD\IMD_grid\0_IMDraw\rainNC-archive\RF25_ind2023_rfp25.nc"
)

var = 'temp_min'

# Dimensions need adjusting according to the information on .nc file
input_latitude_variable_name = 'LATITUDE'
input_longitude_variable_name = 'LONGITUDE'
input_time_variable_name = 'TIME'
interpolation_latitude_name = 'LATITUDE'
interpolation_longitude_name = 'LONGITUDE'

# Making a new folder for the particular set of files to be interpolated
new_folder_name = os.path.basename(input_folder.rstrip(os.sep)) + 'Interpolated'
new_folder_path = os.path.join(output_folder, new_folder_name)
os.makedirs(new_folder_path, exist_ok=True)


# Looping the interpolation
for nc_file in os.listdir(input_folder):
    if nc_file.endswith('.nc'):
        file_to_be_interpolated = xr.open_dataset(os.path.join(input_folder, nc_file))

        # Extracting the year of data
        match = re.search(r"\d{4}", nc_file)
        if match:
            year = int(match.group())
        else:
            print(f"Ensure that {nc_file} is a valid .nc file")
            sys.exit()

        # Extract variables and dimensions from the file to be interpolated
        initial_lat = file_to_be_interpolated[input_latitude_variable_name].values
        initial_lon = file_to_be_interpolated[input_longitude_variable_name].values
        days_of_year = file_to_be_interpolated[input_time_variable_name].values
        data_to_be_interpolated = file_to_be_interpolated[var].values # needs a string input inside [] brackets

        # Extract variables and dimensions from the file used for interpolation
        final_lat = file_used_for_interpolation[interpolation_latitude_name].values
        final_lon = file_used_for_interpolation[interpolation_longitude_name].values

        # Mesh data for final grids
        final_lat_grid, final_lon_grid = np.meshgrid(final_lat, final_lon)

        # Array for interpolated data
        final_data = np.empty((len(days_of_year), len(final_lat), len(final_lon)))

        # Loop for each day to interpolate
        for day in range(len(days_of_year)):
            # Create a 2D data array for the current day's data
            grid = pyinterp.Grid2D(
                pyinterp.Axis(initial_lat, is_circle=False), # Latitude axis
                pyinterp.Axis(initial_lon, is_circle=False),  # Longitude axis
                data_to_be_interpolated[day, :, :] # 2D data for the particular day
            )

            # Bilinear interpolation
            interpolated_data = pyinterp.bivariate(
                grid,
                final_lat_grid.ravel("F"),  # Latitude mesh grid converted to 1D
                final_lon_grid.ravel("F"),  # Longitude mesh grid converted to 1D
                bounds_error=False, # Does not remove edges
            )
            final_grid_shape = np.empty((len(final_lat), len(final_lon)))
            reshaped_data = interpolated_data.reshape(final_grid_shape.shape) # Interpolated 1D data converted to 2D

            # Nearest neighbour interpolation for grids where bilinear interpolation is not applicable
            nan_mask = np.isnan(reshaped_data)
            if np.any(nan_mask):
                coarse_points = np.array([(lat, lon) for lat in initial_lat for lon in initial_lon])
                coarse_values = data_to_be_interpolated[day, :, :].ravel()
                # Points where interpolation is needed
                nan_points = np.array([(final_lat[i], final_lon[j]) for i, j in zip(*np.where(nan_mask))])
                # Interpolation
                nn_interpolated_values = griddata(
                    coarse_points, coarse_values, nan_points, method='nearest'
                )
                # Assign nearest values to the NaN positions in reshaped_data
                reshaped_data[nan_mask] = nn_interpolated_values

            # Interpolated data for the day
            final_data[day, :, :] = reshaped_data # Shape: (TIME, LATITUDE, LONGITUDE)

        # Create a NetCDF file with netCDF4
        output_file = os.path.join(new_folder_path, os.path.splitext(nc_file)[0]) + '-interpolated.nc'
        with nc.Dataset(output_file, "w", format="NETCDF4") as dataset:
            # Create dimensions
            dataset.createDimension("TIME", len(days_of_year))
            dataset.createDimension("LATITUDE", len(final_lat))
            dataset.createDimension("LONGITUDE", len(final_lon))

            # Create variables
            time_var = dataset.createVariable("TIME", "f4", ("TIME",))
            lat_var = dataset.createVariable("LATITUDE", "f4", ("LATITUDE",))
            lon_var = dataset.createVariable("LONGITUDE", "f4", ("LONGITUDE",))
            interpolated_var = dataset.createVariable(
                str(var), np.float32,("TIME", "LATITUDE", "LONGITUDE")
            )

            # Add attributes and metadata
            dataset.description = f"Daily {str(var)} data for {year}"
            dataset.history = "Created " + str(np.datetime64('now'))

            time_var.units = f"days since {year}-01-01"
            lat_var.units = "degrees_north"
            lon_var.units = "degrees_east"

            # Assign values to variables
            time_var[:] = np.arange(len(days_of_year))
            lat_var[:] = final_lat
            lon_var[:] = final_lon
            interpolated_var[:, :, :] = final_data
            interpolated_var.units = "mm" if var == 'rain' else "Celsius"

            print(f"Interpolated netCDF file of '{var}' created for year {year}: {output_file}")