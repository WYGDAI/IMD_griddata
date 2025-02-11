"""
RENAMING ALL FILES IN A FOLDER ACCORDING TO VARIABLE AND YEAR

This code will help in organizing the folder which contains the data that are required for further analyses
    - a variety of datasets with varying names will be renamed to a standardized form as:
                            "2016-rain-IMD" or "1981-temp_min-IMD"

* The variables that need to be adjusted are given from lines 21 and 22 *
    + folder in which the files are present: "input_folder"
    + variable of the files: "var"
        - rain = Rainfall
        - temp_max = Maximum Temperature
        - temp_min = Minimum Temperature

                                                - k.r.bro_05
"""
import os
import re
import time

input_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\4_IMD_grid_main\temp_min"
var = 'temp_min'

for file in os.listdir(input_folder):
    if file.endswith(".nc"):
        # Extracting year
        match = re.search(r"\d{4}", file)
        if match:
            year = int(match.group())
        else:
            print(f"{file} is not a valid file to rename")
            break

        old_name_path = os.path.join(input_folder, file)
        new_name = f"{year}-{var}-IMD.nc"
        new_name_path = os.path.join(input_folder, new_name)

        # Only rename the files that have old names
        if not os.path.exists(new_name_path):
            os.rename(old_name_path, new_name_path)
        while not os.path.exists(new_name_path):
            print(f"Waiting for file to be renamed to: {new_name}")
            time.sleep(1)
