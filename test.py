import os
import re
import sys
import numpy as np
import pandas as pd

input_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\rain-excel"
period_length = 10

# Taking out dictionary of analysis periods and list of years for which input files
def time_period(folder):
    year_list = []
    for file in os.listdir(folder):
        if file.endswith('.xlsx'):
            # Only files with the year in the file name are considered
            match = re.search(r"\d{4}", file)
            if match:
                year = int(match.group())
            else:
                print(
                    f"{file} skipped as no year is detected. Please ensure that year is included in the name of the file"
                )
                continue
            year_list.append(year)
    year_list.sort()

    # Checking whether dataset is complete
    unavailable_years = []
    for i in range(len(year_list) - 1):
        if year_list[i] + 1 != year_list[i + 1]:
            unavailable_years.append(year_list[i] + 1)
    if unavailable_years:
        print(f"Data for the following years are not present:\n"
              f"{unavailable_years}\n"
              f"Please complete the database before proceeding forward")
        sys.exit()

    time_period_dict = {i: year_list[i:i + period_length] for i in
                        range(len(year_list) - (period_length - 1))}

    return time_period_dict

days_in_seasons = np.array([59, 92, 153, 61], int)

# Relevant seasonal stats are extracted for year of the current input file
def stats_annual(excel_file: str, season_days_list: np.ndarray):
    df = pd.read_excel(excel_file)
    # Iterate over days in each season
    season_index = 1
    seasonal_data = {}
    non_zero_counts = {}
    for season_days in season_days_list:
        # Summation of seasonal rainfall
        season_col_name = f"Season_{season_index}"
        df[season_col_name] = df.apply(
            lambda row: row.iloc[3:3 + season_days].sum(), axis=1
        )
        seasonal_data[season_col_name] = df[season_col_name]

        # Non-zero counts
        non_zero_col_name = f"NonZero_{season_index}"
        df[non_zero_col_name] = df.apply(
            lambda row: np.count_nonzero(row.iloc[3:3 + season_days].values), axis=1
        )
        non_zero_counts[non_zero_col_name] = df[non_zero_col_name]

        season_index += 1

    yearly_seasonal_sum = pd.concat([df.iloc[:, :3], pd.DataFrame(seasonal_data)], axis=1)
    yearly_seasonal_wetdays = pd.concat([df.iloc[:, :3], pd.DataFrame(non_zero_counts)], axis=1)

    return yearly_seasonal_sum, yearly_seasonal_wetdays

time_periods = pd.DataFrame(time_period(input_folder))

print("Debug_point")