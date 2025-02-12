"""
EXTRACTING VARIOUS STATISTICAL PROPERTIES OF IMD DATA
"""
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

# No. of days in each of the 1 to 12 seasons in the year
def annual_days_in_season(no_of_seasons: int, current_year: int):
    # Documenting all the number of days each month has in a year
    days_of_month = {
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
    months_of_year = list(days_of_month.keys())
    season_days_array = np.empty(1 if no_of_seasons == 0 else no_of_seasons, int)

    if no_of_seasons == 0 or no_of_seasons == 1:
        season_days_array[0] = sum(days_of_month.values())
    elif no_of_seasons == 12:
        for season_no in range(no_of_seasons):
            season_days_array[season_no] = days_of_month[months_of_year[season_no]]
    else:
        retype_season_months = True
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
                        elif start_month not in days_of_month:
                            print("Invalid month entered. Please try again.")
                            continue  # Retry this iteration

                        end_month = input(
                            f"Ending month of season {season_no + 1} (type 'retry' to retype season boundaries): "
                        ).lower()
                        if end_month.lower() == 'retry':
                            print("\nRe-enter season boundaries...")
                            retype_season_months = True
                            break
                        elif end_month not in days_of_month:
                            print("Invalid month entered. Please try again.")
                            continue  # Retry this iteration

                        if months_of_year.index(end_month) < months_of_year.index(start_month):  # Check for season
                            print(
                                f"\nEnding month must be after the starting month.\n"
                                f"Please re-enter for season {season_no + 1}..."
                            )
                            continue  # Retry this iteration

                        season_months = months_of_year[
                                        months_of_year.index(start_month): months_of_year.index(end_month) + 1
                        ]
                        season_days = sum(days_of_month[month] for month in season_months)

                        season_days_array[season_no] = season_days
                        break  # In case of valid month inputs, break the retry 'while' loop

                    except Exception as e:
                        print(f"An error occurred: \n{e}\n Please try again.")
                        sys.exit()

                if retype_season_months:
                    break

            if sum(season_days_array) != sum(days_of_month.values()) and not retype_season_months:  # Check for total days
                print("\nThe demarcation of seasons are not strict and have overlaps or gaps.\n"
                      "Please re-enter the season boundaries ensuring no overlap...")
                retype_season_months = True

    return season_days_array

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

# Seasonal stats are extracted from multiple files for the defined time-period scale

# Input number of seasons considered in a year
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

for period, years in time_periods.items():
    for year in years:
        season_array = annual_days_in_season(no_of_seasons=total_seasons, current_year=year)


