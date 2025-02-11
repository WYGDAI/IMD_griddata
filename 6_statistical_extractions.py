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

days_of_month = {
    "Jan": 31,
    "Feb": 29 if is_leap_year(year) else 28,
    "Mar": 31,
    "Apr": 30,
    "May": 31,
    "Jun": 30,
    "Jul": 31,
    "Aug": 31,
    "Sep": 30,
    "Oct": 31,
    "Nov": 30,
    "Dec": 31
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

# Iterations for 1 to 12 numbers of seasons in a year
if no_of_seasons == 0 or no_of_seasons == 1:
    season_days_array[0] = sum(days_of_month.values())
elif no_of_seasons == 12:
    for season_no in range(no_of_seasons):
        season_days_array[season_no] = days_of_month[months_of_year[season_no]]
else:
    for season_no in range(no_of_seasons):
        while True: # Retry until valid input is provided
            try:
                start_month = str(input(f"Starting month of season {season_no+1}: "))
                end_month = str(input(f"Ending month of season {season_no+1}: "))

                # Validate months
                if start_month not in days_of_month or end_month not in days_of_month:
                    print("Invalid month entered. Please try again.")
                    continue # Retry this iteration

                season_months = months_of_year[months_of_year.index(start_month) : months_of_year.index(end_month)+1]
                season_days = sum(days_of_month[months_of_year] for month in season_months)
                season_days_array[season_no] = season_days
                break # In case of valid month inputs, break the retry 'while' loop
            except Exception as e:
                print(f"An error occurred: \n{e}\n Please try again.")
                sys.exit()

print("Debug Tester")