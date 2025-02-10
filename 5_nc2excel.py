"""
This code converts the netCDF file into readable Excel format

* The variables that need to be adjusted are given from lines 15 and 16 *
    + Folder which contains the input files: "input_nc_folder"
    + Folder where the Excel files will be saved: "output_excel_folder"
                                        -k.r.bro_05
"""

from netCDF4 import Dataset
import pandas as pd
import numpy as np
import os

input_nc_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\1_IMDclipped\rainNC-archive_clipped"
output_excel_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\2_IMDexcel"

# Making a folder according to the input data
new_folder_name = os.path.basename(input_nc_folder.rstrip(os.sep))
var_out_folder = os.path.join(output_excel_folder, new_folder_name) + r'_excel'
os.makedirs(var_out_folder, exist_ok=True)

for file in os.listdir(input_nc_folder):
    if file.endswith(".nc"):
        # Access files
        file_path = os.path.join(input_nc_folder, file)
        data = Dataset(file_path, 'r')

        # loading 1d data into variables
        date_values = np.array(data.variables['TIME'][:])
        lat_values = np.array(data.variables['LATITUDE'][:])
        long_values = np.array(data.variables['LONGITUDE'][:])
        precip =data.variables['RAINFALL']

        # creating date ranges
        date_range = range(0, len(date_values))

        # creating pandas dataframe
        df = pd.DataFrame(columns=date_range)
        df.insert(0, 'Lat', 0)
        df.insert(1, 'Long', 0)
        df.columns = [col.date() if isinstance(col, pd.Timestamp) else col for col in df.columns]


        for lat in range(0, len(lat_values)):
            for long in range(0, len(long_values)):
                yearly_data = np.array([lat_values[lat], long_values[long]])
                for day in range(0,len(date_values)):
                    yearly_data = np.append(yearly_data, precip[day, lat, long])
                df.loc[len(df)] = yearly_data

        output_path = os.path.join(var_out_folder, os.path.splitext(file)[0]) + '.xlsx'
        df.to_excel(output_path)

        print(f'{os.path.basename(output_path.rstrip(os.sep))} is generated')
