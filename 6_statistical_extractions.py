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

raw_stat_list = ['sum', 'max', 'min']
count_list = ['days', 'wetdays']
# Taking out dictionary of analysis periods and list of years for which input files
def time_period(folder, f_period_length=period_length, check_complete=True):
    """
       Extracts time periods from file names containing years.

       Args:
           folder (str): Path to the folder containing files.
           f_period_length (int): Length of the time period to group years.
           check_complete (bool): Whether to check for missing years (default: True).

       Returns:
           dict: A dictionary with indices as keys and lists of years as values.

       """
    if f_period_length <= 0:
        print("Period length must be greater than 0.")
        sys.exit(1)

    year_list = []
    for file in os.listdir(folder):
        if file.endswith('.xlsx'):
            # Only files with the year in the file name are considered
            fn_match = re.search(r"\d{4}", file)
            if fn_match:
                current_year = int(fn_match.group())
            else:
                print(
                    f"Warning: File {file} skipped as no year is detected."
                )
                continue
            year_list.append(current_year)
    year_list.sort()

    # Checking whether dataset is complete if required
    if check_complete:
        unavailable_years = [
            year_list[i] + 1
            for i in range(len(year_list) - 1)
            if year_list[i] + 1 != year_list[i + 1]
        ]
        if unavailable_years:
            print(f"Error: Data for the following years are not present: {unavailable_years}\n"
                  f"Please complete the dataset before proceeding.")
            sys.exit(1)

    time_period_dictList = {i: year_list[i:i + f_period_length] for i in
                        range(len(year_list) - (f_period_length - 1))}

    return time_period_dictList

# No. of days in each of the 1 to 12 seasons in the year
def annual_season_boundaries(no_of_seasons: int, current_year: int, seasons_defined = None):
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
def stats_annual(excel_file: str,
                 f_days_of_month_dict: dict[str, int],
                 f_months_of_year_list: list[str],
                 f_season_days_array1d: np.ndarray):
    """
    Compute annual statistics from the provided Excel file for each season, divided into 'daily', 'monthly', and 'seasonal' keys.

    Args:
        excel_file (str): Path to the Excel file containing the data.
        f_days_of_month_dict (dict): Dictionary with month names as keys and number of days in each month as values.
        f_months_of_year_list (list): List of month names in order.
        f_season_days_array1d (np.ndarray): Array of season lengths in days.

    Returns:
        dict: A dictionary with calculated statistics for each season, including 'daily', 'monthly', and 'seasonal' keys.
    """

    df = pd.read_excel(excel_file)
    f_annual_data_dict2List3d = {f_key: {'daily': [], 'monthly': [], 'seasonal': []} for f_key in
                                 raw_stat_list + count_list}

    day_counter = 0  # Tracks the day of the year
    month_counter = 0  # Tracks the day of the year

    for season_days in f_season_days_array1d:
        start_column = 3 + day_counter
        end_column = start_column + season_days

        # Extract daily data for the season
        season_data = df.iloc[:, start_column:end_column].values

        for f_key in raw_stat_list:
            if f_key == 'sum':
                # DAILY VALUES
                daily_stat = season_data.tolist()
                f_annual_data_dict2List3d[f_key]['daily'].append(daily_stat)

                # MONTHLY SUMS
                monthly_stat = []
                current_day = day_counter
                while current_day < day_counter + season_days:
                    month = f_months_of_year_list[month_counter]
                    month_days = f_days_of_month_dict[month]

                    month_start = max(current_day, day_counter)  # Start from the beginning of the month or season
                    month_end = min(current_day + month_days,
                                    day_counter + season_days)  # End at month or season boundary

                    # Sum columns for this month (grid points)
                    current_month_stat = season_data[:, (month_start - day_counter):(month_end - day_counter)].sum(axis=1)
                    monthly_stat.append(current_month_stat.tolist())

                    current_day += month_days  # Move to the next month

                    # Increment month_counter to the next month
                    month_counter = (month_counter + 1) % len(f_months_of_year_list)

                f_annual_data_dict2List3d[f_key]['monthly'].append(monthly_stat)

                # SEASONAL SUM
                seasonal_stat = np.sum(monthly_stat, axis=0)
                f_annual_data_dict2List3d[f_key]['seasonal'].append(seasonal_stat)

                # Update the day_counter to the next season's start
                day_counter += season_days

            elif f_key == 'max':
                # DAILY VALUES
                daily_stat = season_data.tolist()
                f_annual_data_dict2List3d[f_key]['daily'].append(daily_stat)

                # MONTHLY SUMS
                monthly_stat = []
                current_day = day_counter
                while current_day < day_counter + season_days:
                    month = f_months_of_year_list[month_counter]
                    month_days = f_days_of_month_dict[month]

                    month_start = max(current_day, day_counter)  # Start from the beginning of the month or season
                    month_end = min(current_day + month_days,
                                    day_counter + season_days)  # End at month or season boundary

                    # Sum columns for this month (grid points)
                    current_month_stat = season_data[:, (month_start - day_counter):(month_end - day_counter)].max(axis=1)
                    monthly_stat.append(current_month_stat.tolist())

                    current_day += month_days  # Move to the next month

                    # Increment month_counter to the next month
                    month_counter = (month_counter + 1) % len(f_months_of_year_list)

                f_annual_data_dict2List3d[f_key]['monthly'].append(monthly_stat)

                # SEASONAL SUM
                seasonal_stat = np.max(monthly_stat, axis=0)
                f_annual_data_dict2List3d[f_key]['seasonal'].append(seasonal_stat)

                # Update the day_counter to the next season's start
                day_counter += season_days

            elif f_key == 'min':
                # DAILY VALUES
                daily_stat = season_data.tolist()
                f_annual_data_dict2List3d[f_key]['daily'].append(daily_stat)

                # MONTHLY SUMS
                monthly_stat = []
                current_day = day_counter
                while current_day < day_counter + season_days:
                    month = f_months_of_year_list[month_counter]
                    month_days = f_days_of_month_dict[month]

                    month_start = max(current_day, day_counter)  # Start from the beginning of the month or season
                    month_end = min(current_day + month_days,
                                    day_counter + season_days)  # End at month or season boundary

                    # Sum columns for this month (grid points)
                    current_month_stat = season_data[:, (month_start - day_counter):(month_end - day_counter)].min(axis=1)
                    monthly_stat.append(current_month_stat.tolist())

                    current_day += month_days  # Move to the next month

                    # Increment month_counter to the next month
                    month_counter = (month_counter + 1) % len(f_months_of_year_list)

                f_annual_data_dict2List3d[f_key]['monthly'].append(monthly_stat)

                # SEASONAL SUM
                seasonal_stat = np.min(monthly_stat, axis=0)
                f_annual_data_dict2List3d[f_key]['seasonal'].append(seasonal_stat)

                # Update the day_counter to the next season's start
                day_counter += season_days

            elif f_key == 'days':


    return f_annual_data_dict2List3d

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
                season_days_array1d, season_boundaries_listTuple = annual_season_boundaries(
                    no_of_seasons=total_seasons, current_year=year
                )
                print("User input of seasonal boundaries registered\n")
            else:
                season_days_array1d, _ = annual_season_boundaries(
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
def mean(f_result_dictList3d: dict[str, list[list[list]]],
         stat_list: list = None,
         zeroes=True):
    if stat_list is None:
        stat_list = raw_stat_list

    f_mean_dictList3d = {f_key: [] for f_key in stat_list}
    for var in stat_list:
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

def stdDev(f_final_data_dictList4d: dict[str, list[list[list[list]]]],
           f_result_dictList3d: dict[str, list[list[list]]],
           stat_list: list = None,
           zeroes=True):
    if stat_list is None:
        stat_list = raw_stat_list
    f_mean_dictList3d = mean(f_result_dictList3d, zeroes=zeroes)

    f_stdDev_dictList3d = {f_key: [] for f_key in stat_list}
    for var in stat_list:
        for mean_2d, data_3d in zip(f_mean_dictList3d[var], f_final_data_dictList4d[var]):
            stdDev_2d = []
            for mean_row, data_matrix in zip(mean_2d, data_3d):
                stdDev_row = []
                # Handle zero-exclusion logic
                for mean_val, height_val in zip(mean_row, zip(*data_matrix)):
                    filtered_values = height_val if zeroes else [val for val in height_val if val != 0]
                    if filtered_values:  # Check for non-empty list
                        variance = sum((val - mean_val) ** 2 for val in filtered_values) / len(filtered_values)
                        f_stdDev = variance ** 0.5
                    else:
                        f_stdDev = 0  # No valid values, set to 0
                    stdDev_row.append(f_stdDev)

                stdDev_2d.append(stdDev_row)
            f_stdDev_dictList3d[var].append(stdDev_2d)
        return f_stdDev_dictList3d

def skewness(f_final_data_dictList4d: dict[str, list[list[list[list]]]],
             f_result_dictList3d: dict[str, list[list[list]]],
             stat_list: list = None,
             bias=False, zeroes=True):
    if stat_list is None:
        stat_list = raw_stat_list
    f_mean_dictList3d = mean(f_result_dictList3d, zeroes=zeroes)
    f_stdDev_dictList3d = stdDev(f_final_data_dictList4d, f_result_dictList3d, zeroes=zeroes)

    f_skew_dictList3d = {f_key: [] for f_key in stat_list}
    for var in stat_list:
        for mean_2d, stdDev_2d, data_3d in zip(
                f_mean_dictList3d[var], f_stdDev_dictList3d[var], f_final_data_dictList4d[var]
        ):
            skew_2d = []
            for mean_row, stdDev_row, data_matrix in zip(mean_2d, stdDev_2d, data_3d):
                skew_row = []
                # Apply zero-exclusion logic
                for mean_val, stdDev_val, height_val in zip(mean_row, stdDev_row, zip(*data_matrix)):
                    filtered_values = height_val if zeroes else [val for val in height_val if val != 0]
                    if filtered_values and stdDev_val != 0:  # Check for non-empty list
                        skew = sum((val-mean_val)**3 for val in filtered_values)/(len(filtered_values)*stdDev_val**3)
                        if not bias and len(filtered_values) > 2:
                            n = len(filtered_values)
                            skew *= ((n*(n-1))**0.5)/(n-2)
                    else:
                        skew = 0  # No valid values, set to 0
                    skew_row.append(skew)
                skew_2d.append(skew_row)
            f_skew_dictList3d[var].append(skew_2d)
    return f_skew_dictList3d

def kurtosis(f_final_data_dictList4d: dict[str, list[list[list[list]]]],
             f_result_dictList3d: dict[str, list[list[list]]],
             stat_list: list = None,
             bias=False, zeroes=True):
    if stat_list is None:
        stat_list = raw_stat_list
    f_mean_dictList3d = mean(f_result_dictList3d, zeroes=zeroes)
    f_stdDev_dictList3d = stdDev(f_final_data_dictList4d, f_result_dictList3d, zeroes=zeroes)

    f_kurt_dictList3d = {f_key: [] for f_key in stat_list}
    for var in stat_list:
        for mean_2d, stdDev_2d, data_3d in zip(
                f_mean_dictList3d[var], f_stdDev_dictList3d[var], f_final_data_dictList4d[var]
        ):
            kurt_2d = []
            for mean_row, stdDev_row, data_matrix in zip(mean_2d, stdDev_2d, data_3d):
                kurt_row = []
                # Apply zero-exclusion logic
                for mean_val, stdDev_val, height_val in zip(mean_row, stdDev_row, zip(*data_matrix)):
                    filtered_values = height_val if zeroes else [val for val in height_val if val != 0]
                    if filtered_values and stdDev_val != 0:  # Check for non-empty list
                        kurt = sum((val - mean_val) ** 4 for val in filtered_values) / \
                               (len(filtered_values) * stdDev_val ** 4)
                        # Adjust for excess kurtosis
                        kurt -= 3
                        if not bias and len(filtered_values) > 3:
                            n = len(filtered_values)
                            kurt = ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * kurt - \
                                   (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
                    else:
                        kurt = 0  # No valid values, set to 0
                    kurt_row.append(kurt)
                kurt_2d.append(kurt_row)
            f_kurt_dictList3d[var].append(kurt_2d)
    return f_kurt_dictList3d

# Excel extractions
