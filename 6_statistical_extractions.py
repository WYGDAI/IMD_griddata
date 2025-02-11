"""
EXTRACTING VARIOUS STATISTICAL PROPERTIES OF IMD DATA
"""

import re
import sys
import numpy as np

input_file = r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\rain-excel\2023-rain-IMD.xlsx"
match = re.search(r"\d{4}", input_file)
year = int(match.group())

# Function to detect leap years
def is_leap_year(fn_year):
    if (fn_year % 4 == 0 and fn_year % 100 != 0) or (fn_year % 400 == 0):
        return True
    return False

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
season_days_array = np.empty(1 if no_of_seasons == 0 else no_of_seasons, int)

# No. of days in each of the 1 to 12 seasons in the year
if no_of_seasons == 0 or no_of_seasons == 1:
    season_days_array[0] = sum(days_of_month.values())
elif no_of_seasons == 12:
    for season_no in range(no_of_seasons):
        season_days_array[season_no] = days_of_month[months_of_year[season_no]]
else:
    retype_season_months = True
    total_days_assigned = 0
    while retype_season_months:
        retype_season_months = False # Reset retype flag
        for season_no in range(no_of_seasons):
            while True: # Retry until valid input is provided
                try:
                    start_month = input(
                        f"\nStarting month of season {season_no+1} (type 'retry' to retype season boundaries): "
                    ).lower()
                    if start_month.lower() == 'retry':
                        print("\nRe-enter season boundaries...")
                        retype_season_months =True
                        break
                    elif start_month not in days_of_month:
                        print("Invalid month entered. Please try again.")
                        continue # Retry this iteration

                    end_month = input(
                        f"Ending month of season {season_no+1} (type 'retry' to retype season boundaries): "
                    ).lower()
                    if end_month.lower() == 'retry':
                        print("\nRe-enter season boundaries...")
                        retype_season_months = True
                        break
                    elif end_month not in days_of_month:
                        print("Invalid month entered. Please try again.")
                        continue # Retry this iteration

                    if months_of_year.index(end_month) < months_of_year.index(start_month): # Check for season
                        print(
                            f"\nEnding month must be after the starting month.\n"
                            f"Please re-enter for season {season_no+1}..."
                        )
                        continue # Retry this iteration

                    season_months = months_of_year[months_of_year.index(start_month) : months_of_year.index(end_month)+1]
                    season_days = sum(days_of_month[month] for month in season_months)
                    total_days_assigned += season_days

                    season_days_array[season_no] = season_days
                    break # In case of valid month inputs, break the retry 'while' loop

                except Exception as e:
                    print(f"An error occurred: \n{e}\n Please try again.")
                    sys.exit()

            if retype_season_months:
                break

        if total_days_assigned != sum(days_of_month.values()) and np.size(season_days_array) != no_of_seasons:  # Check for total days
            print("\nThe demarcation of seasons are not strict and have overlaps or gaps.\n"
                  "Please re-enter the season boundaries ensuring no overlap...")
            retype_season_months = True

print(season_days_array)