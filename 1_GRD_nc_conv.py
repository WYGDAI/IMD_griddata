"""
CONVERT IMD DATA FROM .GRD TO NETCDF

The code will convert .GRD files into .nc files based on the variable in the file.
Some points need to be noted:
    1. Gridded Data Archive can be manually downloaded, and this code can run through it for conversion
    2. Gridded Data Real Time
        - Rainfall data can be downloaded manually for this code to work
        - Temperature data needs to be downloaded through 0_downloadIMD for this code to work due to naming issues

* The variables that need to be adjusted are given in lines 37 to 41 *
    + Folder that contains the .GRD files: "input_folder" (ensure it contains only .GRD files for smooth operation)
    + Folder in which the .nc files are to be saved: "output_folder"
    + Type of variable: "var_type"
        - archive: Gridded Archive Data
        - realtime: Gridded Data Real Time
    + Variable in .GRD file: "var"
        - rainBIN = Rainfall (0.25 x 0.25 resolution)
        - temp_max = Maximum temperature
            archive - 1.0 x 1.0 resolution
            realtime - 0.5 x 0.5 resolution
        - temp_min = Minimum temperature
            archive - 1.0 x 1.0 resolution
            realtime - 0.5 x 0.5 resolution

                                                    - k.r.bro_05
"""

import sys
import numpy as np
from netCDF4 import Dataset
from collections import defaultdict
from datetime import datetime
import os
import re

# Variables that need to be adjusted
input_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\0_IMDraw\temp_min-realtime"
output_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\1_IMD_GRDncConv"
var_type = 'realtime'
var = 'temp_min'

# Make a folder in the output folder
new_folder_name = os.path.basename(input_folder.rstrip(os.sep)) + '_nc'
new_folder_path = os.path.join(output_folder, new_folder_name)
os.makedirs(new_folder_path, exist_ok=True)

data_type_size = 4  # Size of float32 in bytes (used in IMD .GRD files)

# Function for conversion of archive data
def grd_nc_conv_archive(variable, grid_size: tuple[int, int], lat_start, lon_start, resolution):
    # Generate latitude and longitude arrays
    latitudes = np.linspace(lat_start, lat_start + (grid_size[0] - 1) * resolution, grid_size[0])
    longitudes = np.linspace(lon_start, lon_start + (grid_size[1] - 1) * resolution, grid_size[1])

    for grd_file in os.listdir(input_folder):
        if grd_file.endswith(".GRD") or grd_file.endswith(".grd"):
            # Determine the number of days in the file
            input_file = os.path.join(input_folder, grd_file)
            file_size = os.path.getsize(input_file)  # File size in bytes
            num_days = file_size // (grid_size[0] * grid_size[1] * data_type_size)

            # Determine the year for which the data is for
            match = re.search(r"\d{4}", grd_file)
            if match:
                year = int(match.group())
            else:
                print(f"Ensure that {grd_file} is a valid .GRD file")
                sys.exit()

            # Initialize an empty array to hold the data (time x lat x lon)
            imd_data = np.empty((num_days, grid_size[0], grid_size[1]), dtype=np.float32)

            # Read the binary .GRD file
            with open(input_file, "rb") as fin:
                for day in range(num_days):
                    # Read binary data for one day's grid
                    data = np.fromfile(fin, dtype=np.float32, count=grid_size[0] * grid_size[1])

                    # Replace undefined values with NaN
                    if variable == 'temp':
                        data[data == 99.9] = np.nan
                    elif variable == 'rainBIN':
                        data[data == -999.0] = np.nan
                    else:
                        print('Check the if-else statements at the end')

                    # Reshape the flat data into a grid and store it
                    imd_data[day, :, :] = data.reshape(grid_size)

            # Create and save the NetCDF file
            nc_file_name = os.path.splitext(grd_file)[0]
            output_nc_path = os.path.join(new_folder_path, nc_file_name) + ".nc"
            with Dataset(output_nc_path, "w", format="NETCDF4") as nc_file:
                # Create dimensions
                nc_file.createDimension("TIME", num_days)
                nc_file.createDimension("LATITUDE", grid_size[0])
                nc_file.createDimension("LONGITUDE", grid_size[1])

                # Create variables
                time_var = nc_file.createVariable("TIME", "f4", ("TIME",))
                lat_var = nc_file.createVariable("LATITUDE", "f4", ("LATITUDE",))
                lon_var = nc_file.createVariable("LONGITUDE", "f4", ("LONGITUDE",))
                imd_var = nc_file.createVariable(
                    str(var), "f4", ("TIME", "LATITUDE", "LONGITUDE"), fill_value=np.nan
                )

                # Add metadata
                nc_file.description = f"Daily {var} date for {year}"
                time_var.units = f"days since {year}-01-01 00:00:00"
                lat_var.units = "degrees_north"
                lon_var.units = "degrees_east"
                if variable == 'rainBIN':
                    imd_var.units = "mm"
                elif variable == 'temp':
                    imd_var.units = "Celsius"

                # Write data to variables
                time_var[:] = np.arange(num_days)  # Simple time index (0, 1, 2, ...)
                lat_var[:] = latitudes
                lon_var[:] = longitudes
                imd_var[:, :, :] = imd_data

            print(f"NetCDF file created successfully at: {output_nc_path}")

# Function for conversion of real time data
def grd_nc_conv_realtime(variable, grid_size: tuple[int, int], lat_start, lon_start, resolution):
    # Generate latitude and longitude arrays
    latitudes = np.linspace(lat_start, lat_start + (grid_size[0] - 1) * resolution, grid_size[0])
    longitudes = np.linspace(lon_start, lon_start + (grid_size[1] - 1) * resolution, grid_size[1])

    data_list = []
    year_list = []
    date_list = []

    for grd_file in os.listdir(input_folder):
        if grd_file.endswith(".GRD") or grd_file.endswith(".grd"):
            # Extracting date
            match_1 = re.search(r"(\d{4})\+(\d{1,2})\+(\d{1,2})", grd_file)
            match_2 = re.search(r"_(\d{2})_(\d{2})_(\d{2})", grd_file)
            if match_1:
                year, month, day = map(int, match_1.groups())
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                year_list.append(year)
                date_list.append(date_str)
            elif match_2:
                day, month, year = map(int, match_2.groups())
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                year_list.append(year+2000)
                date_list.append(date_str)
            else:
                print(f"Invalid .GRD file name format: {grd_file}")
                sys.exit()

            # Loading the data
            input_file = os.path.join(input_folder, grd_file)
            data = np.fromfile(input_file, dtype=np.float32, count=grid_size[0] * grid_size[1])

            # Replace undefined values with NaN
            if variable == 'temp':
                data[data == 99.9] = np.nan
            elif variable == 'rainBIN':
                data[data == -999.0] = np.nan
            else:
                print('Unsupported variable type. Check your input variable.')
                sys.exit()

            # Reshape the flat data into a 2D grid
            data_2d = data.reshape(grid_size)
            data_list.append(data_2d)

    # Group all daily grids according to year
    year_date_data_list = list(zip(year_list, date_list, data_list)) # appending grids to their years
    yearly_groups = defaultdict(list)
    for year, date, data in year_date_data_list:
        yearly_groups[year].append((date, data))

    # Convert the dates into datetime objects and arrange them
    for year, date_data in yearly_groups.items():
        yearly_groups[year] = sorted(
            ((datetime.strptime(date, "%Y-%m-%d"), data) for date, data in date_data),
            key=lambda x: x[0]
        )

    # Perform checks for missing entries
    data_missing = False
    for year, date_data in yearly_groups.items():
        is_leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
        required_days = 366 if is_leap else 365
        actual_days = len(date_data)
        if actual_days != required_days:
            print(f"The year {year} has {required_days - actual_days} days of data missing")
            data_missing = True
    if data_missing:
        print("Please download the missing data before running the code")
        sys.exit()  # Exit if any year fails the check
    else:
        print("Data verification is complete")

    # Create NetCDF files for each year
    for year, date_data in yearly_groups.items():
        # Combine all 2D arrays for this year into a 3D array (time, lat, lon)
        data_3d = np.stack([data for _, data in date_data], axis=0)

        # Create time array from datetime objects
        time_array = np.array([(date - datetime(year, 1, 1)).days for date, _ in date_data], dtype="i4")

        # Define the output file name
        output_file = os.path.join(new_folder_path, f"{year}-{var}-{var_type}.nc")

        # Create the NetCDF file
        with Dataset(output_file, "w", format="NETCDF4") as nc_file:
            # Define dimensions
            nc_file.createDimension("TIME", data_3d.shape[0])
            nc_file.createDimension("LATITUDE", grid_size[0])
            nc_file.createDimension("LONGITUDE", grid_size[1])

            # Define variables
            time_var = nc_file.createVariable("TIME", "i4", ("TIME",))
            lat_var = nc_file.createVariable("LATITUDE", "f4", ("LATITUDE",))
            lon_var = nc_file.createVariable("LONGITUDE", "f4", ("LONGITUDE",))
            data_var = nc_file.createVariable(
                var, "f4", ("TIME", "LATITUDE", "LONGITUDE"), fill_value=np.nan
            )

            # Add metadata
            nc_file.description = f"Daily {var} data for {year}"
            lat_var.units = "degrees_north"
            lon_var.units = "degrees_east"
            time_var.units = f"days since {year}-01-01"
            data_var.units = "Celsius" if variable == 'temp' else "mm"

            # Write data to variables
            time_var[:] = time_array
            lat_var[:] = latitudes
            lon_var[:] = longitudes
            data_var[:, :, :] = data_3d

        print(f"NetCDF file created for year {year}: {output_file}")

if var_type == 'archive':
    if var == 'rainBIN':
        grd_nc_conv_archive('rainBIN', (129, 135), 6.5, 66.5, 0.25)
    elif var == 'temp_max' or var == 'temp_min':
        grd_nc_conv_archive('temp', (31, 31), 7.5, 67.5, 1)
    else:
        print("Please check valid IMD variables available for archive data (line 17)")
        sys.exit()
elif var_type == 'realtime':
    if var == 'rainBIN':
        grd_nc_conv_realtime('rainBIN', (129,135), 6.5, 66.5, 0.25)
    elif var == 'temp_max' or var == 'temp_min':
        grd_nc_conv_realtime('temp', (61,61), 7.5, 67.5, 0.5)
    else:
        print("Please check valid IMD variables available for real time data (line 17)")
        sys.exit()
else:
    print("Please enter valid variable type (line 14)")
    sys.exit()

print(f"All .GRD files in \n"
      f"{input_folder} \n"
      f"have been successfully converted to NetCDF format and saved in \n"
      f"{new_folder_path}.")