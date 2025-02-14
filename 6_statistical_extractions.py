"""
EXTRACTING VARIOUS STATISTICAL PROPERTIES OF IMD DATA
"""
import os
import re
import sys
import numpy as np
import pandas as pd
from datetime import datetime
import h5py

input_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\test"
preprocessed = False
period_length = 2

raw_stat_list = ['cum', 'max', 'min']
count_list = ['days', 'wetdays']
# Taking out dictionary of analysis periods and list of years for which input files
def time_period(folder):
    year_list = []
    for file in os.listdir(folder):
        if file.endswith('.xlsx'):
            # Only files with the year in the file name are considered
            fn_match = re.search(r"\d{4}", file)
            if fn_match:
                current_year = int(fn_match.group())
            else:
                print(
                    f"{file} skipped as no year is detected. Please ensure that year is included in the name of the file"
                )
                continue
            year_list.append(current_year)
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

    time_period_dictList = {i: year_list[i:i + period_length] for i in
                        range(len(year_list) - (period_length - 1))}

    return time_period_dictList

# No. of days in each of the 1 to 12 seasons in the year
def annual_days_in_season(no_of_seasons: int, current_year: int, seasons_defined = None):
    # Documenting all the number of days each month has in a year
    days_of_month_dict = {
        "jan": 31,
        "feb": 29 if ((current_year % 4 == 0 and current_year % 100 != 0) or (current_year % 400 == 0)) else 28,
        "mar": 31,
        "apr": 30,
        "may": 31,
        "jun": 30,
        "jul": 31,
        "aug": 31,
        "sep": 30,
        "oct": 31,
        "nov": 30,
        "dec": 31
    }
    months_of_year_list = list(days_of_month_dict.keys())

    f_season_days_array1d = np.zeros(1 if no_of_seasons == 0 else no_of_seasons, int)

    # Use predefined seasons if provided
    if seasons_defined is not None:
        for season_no, (start_month, end_month) in enumerate(seasons_defined):
            season_months = months_of_year_list[
                            months_of_year_list.index(start_month): months_of_year_list.index(end_month) + 1
                            ]
            f_season_days_array1d[season_no] = sum(days_of_month_dict[month] for month in season_months)
        return f_season_days_array1d, seasons_defined

    # If predefined seasons are not provided
    if no_of_seasons == 0 or no_of_seasons == 1:
        f_season_days_array1d[0] = sum(days_of_month_dict.values())
        return f_season_days_array1d, None
    elif no_of_seasons == 12:
        for season_no in range(no_of_seasons):
            f_season_days_array1d[season_no] = days_of_month_dict[months_of_year_list[season_no]]
        return f_season_days_array1d, None
    else:
        retype_season_months = True
        user_defined_seasons_listTuple = []
        while retype_season_months:
            retype_season_months = False  # Reset retype flag
            for season_no in range(no_of_seasons):
                while True:  # Retry until valid input is provided
                    try:
                        start_month = input(
                            f"\nStarting month of season {season_no + 1} (type 'retry' to retype season boundaries): "
                        ).lower()
                        if start_month.lower() == 'retry':
                            print("\nRe-enter season boundaries...")
                            retype_season_months = True
                            break
                        elif start_month not in days_of_month_dict:
                            print("Invalid month entered. Please try again.")
                            continue  # Retry this iteration

                        end_month = input(
                            f"Ending month of season {season_no + 1} (type 'retry' to retype season boundaries): "
                        ).lower()
                        if end_month.lower() == 'retry':
                            print("\nRe-enter season boundaries...")
                            retype_season_months = True
                            break
                        elif end_month not in days_of_month_dict:
                            print("Invalid month entered. Please try again.")
                            continue  # Retry this iteration

                        if months_of_year_list.index(end_month) < months_of_year_list.index(start_month):  # Check for season
                            print(
                                f"\nEnding month must be after the starting month.\n"
                                f"Please re-enter for season {season_no + 1}..."
                            )
                            continue  # Retry this iteration

                        season_months = months_of_year_list[
                                        months_of_year_list.index(start_month): months_of_year_list.index(end_month) + 1
                        ]
                        season_days = sum(days_of_month_dict[month] for month in season_months)

                        f_season_days_array1d[season_no] = season_days
                        user_defined_seasons_listTuple.append((start_month, end_month))
                        print(f"User input for season {len(user_defined_seasons_listTuple)} added")
                        break  # In case of valid month inputs, break the retry 'while' loop

                    except Exception as fn_e:
                        print(f"An error occurred: \n{fn_e}\n Please try again.")
                        sys.exit()

                if retype_season_months:
                    user_defined_seasons_listTuple = []
                    break

            if sum(f_season_days_array1d) != sum(days_of_month_dict.values()) and not retype_season_months:  # Check for total days
                print("\nThe demarcation of seasons are not strict and have overlaps or gaps.\n"
                      "Please re-enter the season boundaries ensuring no overlap...")
                user_defined_seasons_listTuple = []
                retype_season_months = True

    return f_season_days_array1d, user_defined_seasons_listTuple

# Relevant seasonal stats are extracted for year of the current input file
def stats_annual(excel_file: str, f_season_days_array1d: np.ndarray):
    df = pd.read_excel(excel_file)
    f_annual_data_dictList2d = {f_key: [] for f_key in raw_stat_list + count_list}

    for season_days in f_season_days_array1d:
        start_column = 3
        end_column = season_days + 3

        # Calculate raw statistics
        for f_key in raw_stat_list:
            if f_key == 'cum':
                f_annual_data_dictList2d[f_key].append(df.iloc[:, start_column:end_column].sum(axis=1).to_list())
            elif f_key == 'max':
                f_annual_data_dictList2d[f_key].append(df.iloc[:, start_column:end_column].max(axis=1).to_list())
            elif f_key == 'min':
                f_annual_data_dictList2d[f_key].append(df.iloc[:, start_column:end_column].min(axis=1).to_list())

        # Calculate counts
        for f_key in count_list:
            if f_key == 'days':
                f_annual_data_dictList2d[f_key].append([season_days] * len(df))
            elif f_key == 'wetdays':
                f_annual_data_dictList2d[f_key].append((df.iloc[:, start_column:end_column] > 0).sum(axis=1).to_list())

    return f_annual_data_dictList2d

# Saving nested dictionary as h5 dataset
def save_nested_dict_to_h5(group, data_dict):
    for f_key, value in data_dict.items():
        if isinstance(value, list):  # If value is a list
            try:
                group.create_dataset(
                    f_key,
                    data=np.array(value, dtype=object),
                    dtype=h5py.special_dtype(vlen=np.dtype('O')),
                    compression="gzip",
                    compression_opts=9,
                )
            except TypeError:
                # Handle cases where the list contains objects not convertible to a NumPy array
                subgroup = group.create_group(f_key)
                for i, item in enumerate(value):
                    subgroup.create_dataset(
                        str(i),
                        data=np.array(item, dtype=object),
                        dtype=h5py.special_dtype(vlen=np.dtype('O')),
                        compression="gzip",
                        compression_opts=9,
                    )
        elif isinstance(value, dict):  # If value is a dictionary
            subgroup = group.create_group(f_key)
            save_nested_dict_to_h5(subgroup, value)

# Loading nested h5 file to its original form
def load_nested_dict_from_h5(group):
    data_dict = {}
    for f_key in group.keys():
        item = group[f_key]
        if isinstance(item, h5py.Group):  # If it's a group, recurse
            data_dict[f_key] = load_nested_dict_from_h5(item)
        elif isinstance(item, h5py.Dataset):  # If it's a dataset, load the data
            data = item[()]  # Extract the dataset
            if isinstance(data, np.ndarray) and data.dtype == 'object':
                # If the dataset contains objects, convert back to lists
                data = data.tolist()
            data_dict[f_key] = data
    return data_dict

# Data preprocessing
if not preprocessed:
    while True:
        try:
            total_seasons = int(input("Enter the number of seasons the year is divided into: "))
            if total_seasons > 12:
                print("There cannot be more than 12 seasons")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    time_periods = time_period(input_folder)

    final_data_dictList4d = {f_key: [] for f_key in raw_stat_list + count_list}

    season_boundaries_listTuple = None
    for period, years in time_periods.items():
        period_data_dictList3d = {f_key: [] for f_key in raw_stat_list + count_list}
        for year in years:
            # Defining season boundaries
            if season_boundaries_listTuple is None:
                season_days_array1d, season_boundaries_listTuple = annual_days_in_season(
                    no_of_seasons=total_seasons, current_year=year
                )
                print("User input of seasonal boundaries registered\n")
            else:
                season_days_array1d, _ = annual_days_in_season(
                    no_of_seasons=total_seasons, current_year=year, seasons_defined=season_boundaries_listTuple
                )

            # Matching files with years
            for input_file in os.listdir(input_folder):
                input_file_path = os.path.join(input_folder, input_file)
                match = re.search(r"\d{4}", input_file)
                if not match:
                    continue
                else:
                    if match.group() != str(year):
                        continue
                    else:
                        annual_data_dictList2d = stats_annual(
                                excel_file=input_file_path, f_season_days_array1d=season_days_array1d
                            )
                        stat_key_list = annual_data_dictList2d.keys()
                        for key in stat_key_list:
                            period_data_dictList3d[key].append(annual_data_dictList2d[key])

                        print(f"Year {year} ({input_file}) for period {period+1} analysed.")

        stat_key_list = period_data_dictList3d.keys()
        for key in stat_key_list:
            final_data_dictList4d[key].append(period_data_dictList3d[key])

        print(f"\nPeriod {period + 1} out of {len(time_periods)} added\n")

    # Result dict
    result_dictList3d = {key: [] for key in final_data_dictList4d}

    # Define aggregation operations for each key
    aggregation_functions = {
        'cum': sum,
        'max': max,
        'min': min,
        'days': sum,
        'wetdays': sum
    }

    # Process each key in final_data_dictList4d to generate result_dictList3d
    for key, func in aggregation_functions.items():
        for array3d in final_data_dictList4d[key]:
            array2d = [
                [func(row) for row in zip(*height)]
                for height in zip(*array3d)
            ]
            result_dictList3d[key].append(array2d)
    print("The preprocessing steps are complete.")

    while True:
        try:
            save = input("Do you want to save progress upto this point? [y/n]: ")
            if save.lower() == 'y':
                while True:
                    try:
                        save_path = input("Please enter the directory path for saving progress file: ")
                        if os.path.exists(save_path):
                            # Dynamic naming according to time of saving
                            current_time = datetime.now().strftime('%d-%m-%Y_%H.%M')
                            save_file_name = f"StatExtractSave_{current_time}.h5"
                            save_file_path = os.path.join(save_path, save_file_name)
                            # Main saving mechanism
                            with h5py.File(save_file_path, 'w') as h5f:
                                save_nested_dict_to_h5("final_data", final_data_dictList4d)
                                save_nested_dict_to_h5("result_data", result_dictList3d)
                            print(f"Progress saved as '{save_file_name}' in '{save_path}'\n"
                                  f"To run the code from this point, switch the 'preprocessed' variable to 'True'")
                            break
                        else:
                            print(f'Please enter valid directory path')
                    except ValueError:
                        print(f'Invalid input. Please try again.')
                break
            elif save.lower() == 'n':
                print("Continuing without saving progress...")
                break
            else:
                print('Please provide a valid input...')
        except ValueError:
            print('Please provide a valid input...')
elif preprocessed:
    while True:
        try:
            load_save = input("Path to save file: ")
            if not os.path.exists(load_save):
                print("Please enter valid path to save file.")
                continue
            break
        except Exception as e:
            print(f'An error occurred: {e}\n'
                  f'Please try again...')

    with h5py.File(load_save, "r") as h5f:
        final_data_dictList4d = load_nested_dict_from_h5(h5f["final_data"])
        result_dictList3d = load_nested_dict_from_h5(h5f['result_data'])
    print("Data loaded successfully.")

# Functions for statistical extractions
def mean(f_result_dictList3d: dict[str, list[list[list]]], zeroes=True):
    f_mean_dictList3d = {fn_key: [] for fn_key in f_result_dictList3d.keys()}
    for var in raw_stat_list:
        if zeroes:
            for var_2d, days_2d in zip(f_result_dictList3d[var], f_result_dictList3d['days']):
                mean_2d = []
                for var_row, days_row in zip(var_2d, days_2d):
                    mean_row = [
                        var_val / days_val if days_val != 0 else 0
                        for var_val, days_val in zip(var_row, days_row)
                    ]
                    mean_2d.append(mean_row)
                f_mean_dictList3d[var].append(mean_2d)
            return f_mean_dictList3d

        else:
            for var_2d, wetdays_2d in zip(f_result_dictList3d[var], f_result_dictList3d['wetdays']):
                mean_2d = []
                for var_row, wetdays_row in zip(var_2d, wetdays_2d):
                    mean_row = [
                        var_val / wetdays_val if wetdays_val != 0 else 0
                        for var_val, wetdays_val in zip(var_row, wetdays_row)
                    ]

                    mean_2d.append(mean_row)
                f_mean_dictList3d[var].append(mean_2d)
            return f_mean_dictList3d
def std_dev(f_final_data_dictList4d: dict[str, list[list[list[list]]]],
            f_result_dictList3d: dict[str, list[list[list]]],
            zeroes=True):
    f_mean_dictList3d = mean(f_result_dictList3d, zeroes=zeroes)
    stdDev_dictList3d = {f_key: [] for f_key in f_mean_dictList3d.keys()}

    for var in raw_stat_list:
        for mean_2d, data_3d in zip(f_mean_dictList3d[var], f_final_data_dictList4d[var]):
            stdDev_2d = []
            for mean_row, data_matrix in zip(mean_2d, data_3d):
                data_array = np.array(data_matrix)  # Convert to NumPy array
                mean_array = np.array(mean_row)

                # Handle zero-exclusion logic
                stdDev_row = []
                for mean_val, height_val in zip(mean_array, zip(*data_array)):
                    filtered_values = height_val if zeroes else [val for val in height_val if val != 0]
                    if filtered_values:  # Check for non-empty list
                        variance = sum((val - mean_val) ** 2 for val in filtered_values) / len(filtered_values)
                        stdDev = variance ** 0.5
                    else:
                        stdDev = 0  # No valid values, set to 0
                    stdDev_row.append(stdDev)

                stdDev_2d.append(stdDev_row)
            stdDev_dictList3d[var].append(stdDev_2d)
        return stdDev_dictList3d

