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
    """
    Defines the number of days for each season in a year based on user-defined, predefined, or automated demarcations.

    Args:
        no_of_seasons (int): The number of seasons to divide the year into. Special cases:
            - 0 or 1: Treat the whole year as a single season.
            - 12: Treat each month as an individual season.
        current_year (int): The year for which the calculation is being performed (used to determine leap years).
        seasons_defined (list of tuples, optional): Predefined season boundaries in the format [(start_month, end_month), ...].

    Returns:
        tuple:
            - f_days_of_month_dict (dict): Dictionary of the number of days in each month for the given year.
            - f_months_of_year_list (list): List of month names in order.
            - f_season_days_array1d (np.ndarray): Array containing the number of days in each season.
            - user_defined_seasons_listTuple (list of tuples, optional): List of user-defined season boundaries if applicable.

    Notes:
        - Handles leap years to correctly calculate the days in February.
        - Validates season definitions to ensure no overlaps or gaps between seasons.
        - If no_of_seasons > 1 and not predefined, prompts the user to define seasons interactively.
    """

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
        return f_days_of_month_dict, f_months_of_year_list, f_season_days_array1d, seasons_defined

    # If predefined seasons are not provided
    if no_of_seasons == 0 or no_of_seasons == 1:
        f_season_days_array1d[0] = sum(f_days_of_month_dict.values())
        return f_season_days_array1d, None
    elif no_of_seasons == 12:
        for season_no in range(no_of_seasons):
            f_season_days_array1d[season_no] = f_days_of_month_dict[f_months_of_year_list[season_no]]
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

    return f_days_of_month_dict, f_months_of_year_list, f_season_days_array1d, user_defined_seasons_listTuple



