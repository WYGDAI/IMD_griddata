"""
EXTRACTING VARIOUS STATISTICAL PROPERTIES OF IMD DATA
"""

import re
import sys
import numpy as np
import pandas as pd

input_file = r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\rain-excel\2023-rain-IMD.xlsx"
match = re.search(r"\d{4}", input_file)
year = int(match.group())

# Function to detect leap years
def is_leap_year(fn_year):
    if (fn_year % 4 == 0 and fn_year % 100 != 0) or (fn_year % 400 == 0):
        return True
    return False

# No. of days in each of the 1 to 12 seasons in the year
def annual_days_in_season(fn_no_of_seasons):
    fn_season_days_array = np.empty(1 if fn_no_of_seasons == 0 else fn_no_of_seasons, int)
    if fn_no_of_seasons == 0 or fn_no_of_seasons == 1:
        fn_season_days_array[0] = sum(days_of_month.values())
    elif fn_no_of_seasons == 12:
        for fn_season_no in range(fn_no_of_seasons):
            fn_season_days_array[fn_season_no] = days_of_month[months_of_year[fn_season_no]]
    else:
        fn_retype_season_months = True
        while fn_retype_season_months:
            fn_retype_season_months = False  # Reset retype flag
            for fn_season_no in range(fn_no_of_seasons):
                while True:  # Retry until valid input is provided
                    try:
                        fn_start_month = input(
                            f"\nStarting month of season {fn_season_no + 1} (type 'retry' to retype season boundaries): "
                        ).lower()
                        if fn_start_month.lower() == 'retry':
                            print("\nRe-enter season boundaries...")
                            fn_retype_season_months = True
                            break
                        elif fn_start_month not in days_of_month:
                            print("Invalid month entered. Please try again.")
                            continue  # Retry this iteration

                        fn_end_month = input(
                            f"Ending month of season {fn_season_no + 1} (type 'retry' to retype season boundaries): "
                        ).lower()
                        if fn_end_month.lower() == 'retry':
                            print("\nRe-enter season boundaries...")
                            fn_retype_season_months = True
                            break
                        elif fn_end_month not in days_of_month:
                            print("Invalid month entered. Please try again.")
                            continue  # Retry this iteration

                        if months_of_year.index(fn_end_month) < months_of_year.index(fn_start_month):  # Check for season
                            print(
                                f"\nEnding month must be after the starting month.\n"
                                f"Please re-enter for season {fn_season_no + 1}..."
                            )
                            continue  # Retry this iteration

                        fn_season_months = months_of_year[
                                        months_of_year.index(fn_start_month): months_of_year.index(fn_end_month) + 1
                        ]
                        fn_season_days = sum(days_of_month[fn_month] for fn_month in fn_season_months)

                        fn_season_days_array[fn_season_no] = fn_season_days
                        break  # In case of valid month inputs, break the retry 'while' loop

                    except Exception as fn_e:
                        print(f"An error occurred: \n{fn_e}\n Please try again.")
                        sys.exit()

                if fn_retype_season_months:
                    break

            if sum(fn_season_days_array) != sum(days_of_month.values()) and not fn_retype_season_months:  # Check for total days
                print("\nThe demarcation of seasons are not strict and have overlaps or gaps.\n"
                      "Please re-enter the season boundaries ensuring no overlap...")
                fn_retype_season_months = True

    return fn_season_days_array

# Documenting all the number of days each month has in a year
days_of_month = {
    "jan": 31,
    "feb": 29 if is_leap_year(year) else 28,
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

# Input number of seasons considered in a year
while True:
    try:
        no_of_seasons = int(input("Enter the number of seasons the year is divided into: "))
        if no_of_seasons > 12:
            print("There cannot be more than 12 seasons")
            continue
        break
    except ValueError:
        print("Invalid input. Please enter a valid integer.")

days_in_seasons = annual_days_in_season(no_of_seasons)
print(days_in_seasons)

df = pd.read_excel(input_file)
# Iterate over days in each season
season_index = 1
seasonal_data = {}
non_zero_counts = {}
for season_days in days_in_seasons:
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

seasonal_sum = pd.concat([df.iloc[:, :3], pd.DataFrame(seasonal_data)], axis=1)
seasonal_wet_days = pd.concat([df.iloc[:, :3], pd.DataFrame(non_zero_counts)], axis=1)
