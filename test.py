"""
EXTRACTING VARIOUS STATISTICAL PROPERTIES OF IMD DATA
"""
import os
import re
import sys
import numpy as np
import pandas as pd

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
    season_month_counter = 0
    for season_days in f_season_days_array1d:
        start_column = 3 + day_counter
        end_column = start_column + season_days

        # Extract daily data for the season
        season_data = df.iloc[:, start_column:end_column].values

        for f_key in raw_stat_list:
            # DAILY VALUES
            daily_stat = season_data.tolist()
            f_annual_data_dict2List3d[f_key]['daily'].append(daily_stat)

            # MONTHLY SUMS
            monthly_stat = []
            current_day = day_counter
            local_month_counter = season_month_counter
            while current_day < day_counter + season_days:
                month = f_months_of_year_list[local_month_counter]
                month_days = f_days_of_month_dict[month]

                month_start = max(current_day, day_counter)  # Start from the beginning of the month or season
                month_end = min(current_day + month_days,
                                day_counter + season_days)  # End at month or season boundary

                # Dynamically call the method on the slice of season_data.
                current_month_stat = getattr(season_data[:, (month_start - day_counter):(month_end - day_counter)],
                                             f_key)(axis=1)
                monthly_stat.append(current_month_stat.tolist())

                current_day += month_days

                # Increment month_counter to the next month
                local_month_counter = (local_month_counter + 1) % len(f_months_of_year_list)

            f_annual_data_dict2List3d[f_key]['monthly'].append(monthly_stat)

            # SEASONAL SUM
            seasonal_stat = getattr(np, f_key)(np.array(monthly_stat), axis=0)
            f_annual_data_dict2List3d[f_key]['seasonal'].append(seasonal_stat)

        # Update the day_counter to the next season's start
        day_counter += season_days
        season_month_counter = local_month_counter
    return f_annual_data_dict2List3d

# --- Create Sample Data ---

# Number of grid points (rows)
num_grid_points = 5

# Create coordinate data (for example, latitude, longitude, elevation)
lat = np.linspace(10, 20, num_grid_points)
lon = np.linspace(50, 60, num_grid_points)
elev = np.linspace(100, 200, num_grid_points)

# Number of daily data columns (for a non-leap year, 365 days)
num_daily = 365
# Create random daily data (e.g., rainfall amounts, temperature, etc.)
daily_data = np.random.randint(0, 100, size=(num_grid_points, num_daily))

# Build a DataFrame with 3 coordinate columns and 365 daily columns.
columns = ["lat", "lon", "elev"] + [f"day{i+1}" for i in range(num_daily)]
data = np.column_stack((lat, lon, elev, daily_data))
df_sample = pd.DataFrame(data, columns=columns)

# Save to an Excel file for testing purposes
g_excel_file = "test_data.xlsx"
df_sample.to_excel(g_excel_file, index=False)
print(f"Sample data written to {g_excel_file}")

# --- Define Parameters for stats_annual ---

# For this test, we'll use a non-leap year
g_days_of_month_dict = {
    "jan": 31,
    "feb": 28,
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
g_months_of_year_list = list(g_days_of_month_dict.keys())

# Partition the 365-day year into 4 seasons:
# For example: Season 1 = 90 days, Season 2 = 91 days, Season 3 = 92 days, Season 4 = 92 days
season_days_array1d = np.array([90, 91, 92, 92])

# --- Call the stats_annual Function ---

# (Assuming your stats_annual function is defined as in your BASIS code.)
result = stats_annual(g_excel_file, g_days_of_month_dict, g_months_of_year_list, season_days_array1d)

# Print the result to verify
print("Computed seasonal statistics:")
print(result)
