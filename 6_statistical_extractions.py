"""
EXTRACTING VARIOUS STATISTICAL PROPERTIES OF IMD DATA
"""
import os
import re
import sys
import winsound
import numpy as np
import pandas as pd
from datetime import datetime
import h5py
from scipy.stats import skew, kurtosis

# User defined
input_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\test"
output_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\test_out"
preprocessed = True
period_length = 2
raw_stat_list = ['sum', 'max', 'min']

# Hard-coded
count_list = ['days', 'wetdays']
stat_scale_list = ['daily', 'monthly', 'seasonal']

user_scale_list = []
while not user_scale_list:
    for scale in stat_scale_list:
        while True:
            scale_required = input(f"Do you want to compute {scale} statistics? [y/n]: ").strip().lower()
            if scale_required in ('y', 'n'):
                if scale_required == 'y':
                    user_scale_list.append(scale)
                break
            else:
                print("Please enter 'y' or 'n'")
    if not user_scale_list:
        print("You need to select at least one scale for the statistical measures to be computed.")

print("Statistical measures will be computed for the following scales: ", user_scale_list)

# Taking out dictionary of analysis periods and list of years for which input files
def time_period(folder, f_period_length=period_length, check_complete=True):
    """
       Extracts time periods from file names containing years.

       Args:
           folder (str): Path to the folder containing files.
           f_period_length (int): Length of the time period to group years for analysis
           check_complete (bool): Whether to check for missing years (default: True).

       Returns:
           dict: A dictionary with indices as keys and lists of years as values.

       """
    if f_period_length <= 0:
        print("Period length must be greater than 0.")
        sys.exit(1)

    year_list = []
    for f_file in os.listdir(folder):
        if f_file.endswith('.xlsx'):
            # Only files with the year in the file name are considered
            fn_match = re.search(r"\d{4}", f_file)
            if fn_match:
                current_year = int(fn_match.group())
            else:
                print(
                    f"Warning: File {f_file} skipped as no year is detected."
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
    f_days_of_month_dict = {
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
    f_months_of_year_list = list(f_days_of_month_dict.keys())

    f_season_days_array1d = np.zeros(1 if no_of_seasons == 0 else no_of_seasons, int)

    # Use predefined seasons if provided
    if seasons_defined is not None:
        for season_no, (start_month, end_month) in enumerate(seasons_defined):
            season_months = f_months_of_year_list[
                            f_months_of_year_list.index(start_month): f_months_of_year_list.index(end_month) + 1
                            ]
            f_season_days_array1d[season_no] = sum(f_days_of_month_dict[month] for month in season_months)
        return f_season_days_array1d, seasons_defined, f_days_of_month_dict, f_months_of_year_list

    # If predefined seasons are not provided
    if no_of_seasons == 0 or no_of_seasons == 1:
        f_season_days_array1d[0] = sum(f_days_of_month_dict.values())
        return f_season_days_array1d, None, f_days_of_month_dict, f_months_of_year_list
    elif no_of_seasons == 12:
        for season_no in range(no_of_seasons):
            f_season_days_array1d[season_no] = f_days_of_month_dict[f_months_of_year_list[season_no]]
        return f_season_days_array1d, None, f_days_of_month_dict, f_months_of_year_list
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
                        elif start_month not in f_days_of_month_dict:
                            print("Invalid month entered. Please try again.")
                            continue  # Retry this iteration

                        end_month = input(
                            f"Ending month of season {season_no + 1} (type 'retry' to retype season boundaries): "
                        ).lower()
                        if end_month.lower() == 'retry':
                            print("\nRe-enter season boundaries...")
                            retype_season_months = True
                            break
                        elif end_month not in f_days_of_month_dict:
                            print("Invalid month entered. Please try again.")
                            continue  # Retry this iteration

                        if f_months_of_year_list.index(end_month) < f_months_of_year_list.index(start_month):  # Check for season
                            print(
                                f"\nEnding month must be after the starting month.\n"
                                f"Please re-enter for season {season_no + 1}..."
                            )
                            continue  # Retry this iteration

                        season_months = f_months_of_year_list[
                                        f_months_of_year_list.index(start_month): f_months_of_year_list.index(end_month) + 1
                        ]
                        season_days = sum(f_days_of_month_dict[month] for month in season_months)

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

            if sum(f_season_days_array1d) != sum(f_days_of_month_dict.values()) and not retype_season_months:  # Check for total days
                print("\nThe demarcation of seasons are not strict and have overlaps or gaps.\n"
                      "Please re-enter the season boundaries ensuring no overlap...")
                user_defined_seasons_listTuple = []
                retype_season_months = True

    return f_season_days_array1d, user_defined_seasons_listTuple, f_days_of_month_dict, f_months_of_year_list

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
    f_annual_data_dict2List3d = {f_key: {f_scale: [] for f_scale in user_scale_list} for f_key in
                                 raw_stat_list + count_list}

    day_counter = 0  # Tracks the day of the year
    season_month_counter = 0
    for season_days in f_season_days_array1d:
        start_column = 3 + day_counter
        end_column = start_column + season_days

        # Extract daily data for the season
        season_data = df.iloc[:, start_column:end_column].values

        for f_key in raw_stat_list + count_list:
            # --- DAILY VALUES ---
            if 'daily' in user_scale_list:
                if f_key in raw_stat_list:
                    daily_stat = season_data.tolist()
                else:
                    if f_key == 'days':
                        daily_stat = np.ones(season_data.shape, dtype=int).tolist()
                    elif f_key == 'wetdays':
                        # For 'wetdays', 1 if the value > 0, else 0.
                        daily_stat = (season_data > 0).astype(int).tolist()
                    else:
                        print("Please remove all entries within 'count_list' except 'days' and 'wetdays'.")
                        sys.exit(1)
                f_annual_data_dict2List3d[f_key]['daily'].append(daily_stat)

            # --- MONTHLY VALUES ---
            if 'monthly' in user_scale_list:
                monthly_stat = []
                current_day = day_counter
                local_month_counter = season_month_counter
                while current_day < day_counter + season_days:
                    month = f_months_of_year_list[local_month_counter]
                    month_days = f_days_of_month_dict[month]

                    month_start = max(current_day, day_counter)  # Start from the beginning of the month or season
                    month_end = min(current_day + month_days,
                                    day_counter + season_days)  # End at month or season boundary

                    # Slice the season_data corresponding to this month.
                    data_slice = season_data[:, (month_start - day_counter):(month_end - day_counter)]

                    # Dynamically call the method on the slice of season_data.
                    if f_key in raw_stat_list:
                        current_month_stat = getattr(data_slice, f_key)(axis=1)
                    else:
                        if f_key == "days":
                            current_month_stat = 1
                        else:
                            current_month_stat = (np.any(data_slice != 0, axis=1)).astype(int)
                    monthly_stat.append(current_month_stat.tolist())

                    current_day += month_days
                    local_month_counter = (local_month_counter + 1) % len(f_months_of_year_list)
                transposed_monthly_stat = list(map(list, zip(*monthly_stat)))
                f_annual_data_dict2List3d[f_key]['monthly'].append(transposed_monthly_stat)

            # --- SEASONAL VALUES ---
            if 'seasonal' in user_scale_list:
                if f_key in raw_stat_list:
                    seasonal_stat = getattr(np, f_key)(season_data, axis=1)
                else:
                    if f_key == 'days':
                        seasonal_stat = 1
                    else:
                        seasonal_stat = (np.any(season_data != 0, axis = 1)).astype(int)
                f_annual_data_dict2List3d[f_key]['seasonal'].append(seasonal_stat)

        # Update the day_counter to the next season's start
        day_counter += season_days
        season_month_counter = local_month_counter

    return f_annual_data_dict2List3d

# Saving nested dictionary as h5 dataset
def save_nested_dict_to_h5(f_group, data_dict):
    if isinstance(data_dict, dict):
        keys_list = list(data_dict.keys())
        for f_key in keys_list:
            value = data_dict[f_key]
            if isinstance(value, dict):
                print(f"\nSaving data for: {f_key} ({keys_list.index(f_key)+1}/{len(keys_list)})")
            elif isinstance(value, list):
                print(f"Saving '{f_key}' data")
            subgroup = f_group.create_group(f_key)
            save_nested_dict_to_h5(subgroup, value)
    elif isinstance(data_dict, list):  # If value is a list
        try:
            f_group.create_dataset(
                "data",
                data=np.array(data_dict, dtype=object),
                dtype=h5py.special_dtype(vlen=np.dtype('O')),
                compression="gzip",
                compression_opts=9,
            )
        except TypeError:
            # Handle cases where the list contains objects not convertible to a NumPy array
            for i, item in enumerate(data_dict):
                if isinstance(item, (list, dict)):
                    save_nested_dict_to_h5(f_group.create_group(str(i)), item)
                else:
                    f_group.create_dataset(str(i), data=item)
    else:
        f_group.create_dataset("data", data=data_dict)

# Loading nested h5 file to its original form
def load_nested_dict_from_h5(f_group):
    keys = list(f_group.keys())
    # If the group contains only one key named "data", return that dataset's contents.
    if len(keys) == 1 and keys[0] == "data":
        data = f_group["data"][()]
        if isinstance(data, np.ndarray) and data.dtype == 'object':
            data = data.tolist()
        return data
    else:
        data_dict = {}
        for f_key in f_group.keys():
            item = f_group[f_key]
            if isinstance(item, h5py.Group):
                data_dict[f_key] = load_nested_dict_from_h5(item)
            elif isinstance(item, h5py.Dataset):
                data = item[()]  # Extract the dataset
                if isinstance(data, np.ndarray) and data.dtype == 'object':
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

    final_data_dictList4d = {key: {scale: [] for scale in user_scale_list} for key in raw_stat_list + count_list}


    season_boundaries_listTuple = None
    for period, years in time_periods.items():
        period_data_dictList3d = {key: {scale: [] for scale in user_scale_list} for key in raw_stat_list + count_list}

        for year in years:
            # Defining season boundaries
            if season_boundaries_listTuple is None:
                season_days_array1d, season_boundaries_listTuple, days_of_month_dict, months_of_year_list = annual_season_boundaries(
                    no_of_seasons=total_seasons, current_year=year
                )
                print("User input of seasonal boundaries registered\n")
            else:
                season_days_array1d, _, days_of_month_dict, months_of_year_list = annual_season_boundaries(
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
                        annual_data_dict2List3d = stats_annual(
                            excel_file=input_file_path,
                            f_days_of_month_dict=days_of_month_dict,
                            f_months_of_year_list=months_of_year_list,
                            f_season_days_array1d=season_days_array1d
                        )
                        for key in annual_data_dict2List3d.keys():
                            for subkey in user_scale_list:
                                period_data_dictList3d[key][subkey].append(annual_data_dict2List3d[key][subkey])

                        print(f"Year {year} ({input_file}) for period {period+1} analysed.")

        for key in period_data_dictList3d.keys():
            for subkey in user_scale_list:
                final_data_dictList4d[key][subkey].append(period_data_dictList3d[key][subkey])

        print(f"\nPeriod {period + 1} out of {len(time_periods)} added\n")

    print("The preprocessing steps are complete.")
    winsound.Beep(700, 3000)

    while True:
        try:
            save = input("\nProgress can be saved, but will take a very significant amount of time. \n"
                         "Do you want to save progress upto this point? [y/n]: ")
            if save.lower() == 'y':
                while True:
                    try:
                        save_path = input("Please enter the directory path for saving progress file: \n")
                        if os.path.exists(save_path):
                            # Dynamic naming according to time of saving
                            current_time = datetime.now().strftime('%d-%m-%Y_%H.%M')
                            save_file_name = f"StatExtractSave_{current_time}.h5"
                            save_file_path = os.path.join(save_path, save_file_name)
                            # Main saving mechanism
                            with h5py.File(save_file_path, 'w') as h5f:
                                group = h5f.create_group("final_data")
                                save_nested_dict_to_h5(group, final_data_dictList4d)
                            print(f"Progress saved as '{save_file_name}' in '{save_path}'\n"
                                  f"To run the code from this point, switch the 'preprocessed' variable to 'True'\n")
                            winsound.Beep(700, 7000)
                            break
                        else:
                            print(f'Please enter valid directory path')
                    except ValueError:
                        print(f'Invalid input. Please try again.')
                break
            elif save.lower() == 'n':
                print("Continuing without saving progress...\n")
                break
            else:
                print('Please provide a valid input...')
        except ValueError:
            print('Please provide a valid input...')
elif preprocessed:
    while True:
        try:
            load_save = input("Path to save file: \n")
            if not os.path.exists(load_save):
                print("Please enter valid path to save file.")
                continue
            break
        except Exception as e:
            print(f'An error occurred: {e}\n'
                  f'Please try again...')

    with h5py.File(load_save, "r") as h5f:
        final_data_dictList4d = load_nested_dict_from_h5(h5f["final_data"])
    print("Data loaded successfully.\n")
    winsound.Beep(700, 3000)

# Functions for statistical extractions
def avg(f_final_data_dictList4d: dict[str, dict[str, list[list[list]]]],
        stat_list: list = None,
        f_zeroes=True):
    """
    Compute the mean of the daily/monthly/seasonal values for each key (e.g., 'sum') for each season and grid point,
    averaging over all years in a given period and for all days.

    The structure of f_final_data_dictList4d for a given key and subkey is assumed to be:
      [Y][S][n][d/m] for all subkeys except seasonal where it is [Y][S][n]
    where Y = number of years, S = seasons per year, n = grid points, and d/m = days/months in that season.

    Args:
        f_final_data_dictList4d (dict): The nested dictionary containing the final data.
        stat_list (list): List of keys to compute the mean for. By default, this is raw_stat_list.
        f_zeroes (bool): If True, compute the normal arithmetic mean.
                       If False, ignore zero values in the computation.

    Returns:
        dict: A dictionary with the same keys and subkeys containing the mean computed for each season and grid point.
    """

    if stat_list is None:
        stat_list = raw_stat_list

    f_mean_dict2List2d = {f_key: {f_scale: [] for f_scale in user_scale_list} for f_key in stat_list}
    for f_key in stat_list:
        for f_subkey in user_scale_list:
            f_data = np.array(f_final_data_dictList4d[f_key][f_subkey])
            if not f_zeroes:
                f_data = np.ma.masked_equal(f_data, 0)

            if f_data.ndim == 4:
                f_mean_data = np.mean(f_data, axis=(0,-1)).filled(0)
            elif f_data.ndim == 3:
                f_mean_data = np.mean(f_data, axis=0).filled(0)
            else:
                print("Unexpected error: Need to check code")
                sys.exit("Statistical extractions")

            f_mean_dict2List2d[f_key][f_subkey].append(f_mean_data)
    return f_mean_dict2List2d

def std_dev(f_final_data_dictList4d: dict[str, dict[str, list[list[list]]]],
            stat_list: list = None,
            f_zeroes=True):
    """
    Compute the standard deviation of the daily/monthly/seasonal values for each key (e.g., 'sum') for each season and
    grid point, averaging over all years in a given period and for all days.

    The structure of f_final_data_dictList4d for a given key and subkey is assumed to be:
      [Y][S][n][d/m] for all subkeys except seasonal where it is [Y][S][n]
    where Y = number of years, S = seasons per year, n = grid points, and d/m = days/months in that season.

    Args:
        f_final_data_dictList4d (dict): The nested dictionary containing the final data.
        stat_list (list): List of keys to compute the standard deviation for. By default, this is raw_stat_list.
        f_zeroes (bool): If True, compute the normal standard deviation.
                       If False, ignore zero values in the computation.

    Returns:
        dict: A dictionary with the same keys and subkeys containing the standard deviation computed for each season
              and grid point.
    """
    if stat_list is None:
        stat_list = raw_stat_list

    f_stdDev_dict2List2d = {f_key: {f_scale: [] for f_scale in user_scale_list} for f_key in stat_list}
    for f_key in stat_list:
        for f_subkey in user_scale_list:
            f_data = np.array(f_final_data_dictList4d[f_key][f_subkey])
            if not f_zeroes:
                f_data = np.ma.masked_equal(f_data, 0)

            if f_data.ndim == 4:
                f_stdDev_data = np.std(f_data, axis=(0, -1)).filled(0)
            elif f_data.ndim == 3:
                f_stdDev_data = np.std(f_data, axis=0).filled(0)
            else:
                print("Unexpected error: Need to check code")
                sys.exit("Statistical extractions")

            f_stdDev_dict2List2d[f_key][f_subkey].append(f_stdDev_data)
    return f_stdDev_dict2List2d

def skewness(f_final_data_dictList4d: dict[str, dict[str, list[list[list]]]],
             stat_list: list = None,
             f_zeroes=True):
    """
    Compute the skewness of the daily/monthly/seasonal values for each key (e.g., 'sum') for each season and grid point,
    averaging over all years in a given period and for all days.

    The structure of f_final_data_dictList4d for a given key and subkey is assumed to be:
      [Y][S][n][d/m] for all subkeys except seasonal where it is [Y][S][n]
    where Y = number of years, S = seasons per year, n = grid points, and d/m = days/months in that season.

    Args:
        f_final_data_dictList4d (dict): The nested dictionary containing the final data.
        stat_list (list): List of keys to compute the skewness for. By default, this is raw_stat_list.
        f_zeroes (bool): If True, compute the normal skew.
                       If False, ignore zero values in the computation.

    Returns:
        dict: A dictionary with the same keys and subkeys containing the skew computed for each season and grid point.
    """
    if stat_list is None:
        stat_list = raw_stat_list

    f_skew_dict2List2d = {f_key: {f_scale: [] for f_scale in user_scale_list} for f_key in stat_list}
    for f_key in stat_list:
        for f_subkey in user_scale_list:
            f_data = np.array(f_final_data_dictList4d[f_key][f_subkey])
            if not f_zeroes:
                f_data = np.ma.masked_equal(f_data, 0).filled(np.nan)
            if f_data.ndim == 4:
                # f_data shape: [Y, S, n, d] (or d replaced by m for monthly)
                # Reshape so that we collapse year and day/month axes.
                Y, S, n, L = f_data.shape
                reshaped = f_data.transpose(1, 2, 0, 3).reshape(S, n, -1)
                # Compute skewness along the last axis
                f_skew = skew(reshaped, axis=-1, nan_policy='omit')
            elif f_data.ndim == 3:
                # For seasonal data: shape [Y, S, n] -> average over Y (axis 0)
                f_skew = skew(f_data, axis=0, nan_policy='omit')
            else:
                print("Unexpected error: Need to check code")
                sys.exit("Statistical extractions")

            f_skew_dict2List2d[f_key][f_subkey].append(f_skew)
    return f_skew_dict2List2d

def kurt(f_final_data_dictList4d: dict[str, dict[str, list[list[list]]]],
         stat_list: list = None,
         f_zeroes=True):
    """
    Compute the kurtosis of the daily/monthly/seasonal values for each key (e.g., 'sum') for each season and grid point,
    averaging over all years in a given period and for all days.

    The structure of f_final_data_dictList4d for a given key and subkey is assumed to be:
      [Y][S][n][d/m] for all subkeys except seasonal where it is [Y][S][n]
    where Y = number of years, S = seasons per year, n = grid points, and d/m = days/months in that season.

    Args:
        f_final_data_dictList4d (dict): The nested dictionary containing the final data.
        stat_list (list): List of keys to compute the kurtosis for. By default, this is raw_stat_list.
        f_zeroes (bool): If True, compute the normal kurtosis.
                       If False, ignore zero values in the computation.

    Returns:
        dict: A dictionary with the same keys and subkeys containing the kurtosis computed for each season and grid point.
    """
    if stat_list is None:
        stat_list = raw_stat_list
    f_kurtosis_dict2List2d = {f_key: {f_scale: [] for f_scale in user_scale_list} for f_key in stat_list}

    for f_key in stat_list:
        for f_subkey in user_scale_list:
            f_data = np.array(f_final_data_dictList4d[f_key][f_subkey])
            if not f_zeroes:
                f_data = np.ma.masked_equal(f_data, 0).filled(np.nan)

            if f_data.ndim == 4:
                Y, S, n, L = f_data.shape
                reshaped = f_data.transpose(1, 2, 0, 3).reshape(S, n, -1)
                f_kurt = kurtosis(reshaped, axis=-1, nan_policy='omit')
            elif f_data.ndim == 3:
                f_kurt = kurtosis(f_data, axis=0, nan_policy='omit')
            else:
                f_kurt = f_data

            f_kurtosis_dict2List2d[f_key][f_subkey].append(f_kurt)
    return f_kurtosis_dict2List2d

print("Proceeding to compute statistical measures...\n")
while True:
    zeroes_input = input("Do you want zeroes to be included in the computation? [y/n]: ").strip().lower()
    if zeroes_input in ('y', 'n'):
        zeroes = True if zeroes_input =='y' else False
        break
    else:
        print("Please enter 'y' or 'n'")

stat_dictFunc = {'mean': avg, 'standard deviation': std_dev, 'skew': skewness, 'kurtosis': kurt}

# Preparing the index columns for dataframe
for file in os.listdir(input_folder):
    if file.endswith('.xlsx'):
        if re.search(r"\d{4}", file):
            reference_file = os.path.join(input_folder, file)
            break
df_reference = pd.read_excel(reference_file, index_col=None)
reference_col = df_reference.iloc[:, :3]

for stat in stat_dictFunc.keys():
    while True:
        stat_required = input(f"Do you want to compute {stat}? [y/n]: ").strip().lower()
        if stat_required in ('y', 'n'):
            if stat_required == 'y':
                stat_dict2List2d = stat_dictFunc[stat](final_data_dictList4d, f_zeroes=zeroes)
                for key in stat_dict2List2d.keys():
                    print(f"\nProcessing {stat} data...")
                    for subkey in stat_dict2List2d[key].keys():
                        excel_file_path = os.path.join(output_folder, f"{key}-{subkey}_{stat}.xlsx")
                        with pd.ExcelWriter(excel_file_path) as writer:
                            for index, arr in enumerate(stat_dict2List2d[key][subkey]):
                                df_arr = pd.DataFrame(arr.T)
                                final_arr = pd.concat([reference_col, df_arr], axis=1)

                                final_arr.to_excel(
                                    writer,
                                    sheet_name=f"{list(time_periods.values())[index][0]}_{list(time_periods.values())[index][-1]}",
                                    index=False
                                )
                                print(f"{stat.capitalize()} of {subkey} '{key}' data for time period {list(time_periods.values())[index][0]} to {list(time_periods.values())[index][-1]} generated")
                        print(f"{stat.capitalize()} of {subkey} '{key}' data generated\n"
                              f"Saved excel file path: ", excel_file_path)
                        winsound.Beep(1000, 500)
                    print(f"\nStatistical data generation for '{key}' is completed")
                    winsound.Beep(1000, 500)
                    winsound.Beep(500, 1000)
            break
        else:
            print("Please enter 'y' or 'n'")
