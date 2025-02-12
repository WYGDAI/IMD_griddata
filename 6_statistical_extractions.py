"""
EXTRACTING VARIOUS STATISTICAL PROPERTIES OF IMD DATA
"""
import os
import re
import sys
import numpy as np
import pandas as pd

input_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\test"
period_length = 2

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

    time_period_dict = {i: year_list[i:i + period_length] for i in
                        range(len(year_list) - (period_length - 1))}

    return time_period_dict

# No. of days in each of the 1 to 12 seasons in the year
def annual_days_in_season(no_of_seasons: int, current_year: int, seasons_defined = None):
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
    season_days_array = np.zeros(1 if no_of_seasons == 0 else no_of_seasons, int)

    # Use predefined seasons if provided
    if seasons_defined is not None:
        for season_no, (start_month, end_month) in enumerate(seasons_defined):
            season_months = months_of_year[
                            months_of_year.index(start_month): months_of_year.index(end_month) + 1
                            ]
            season_days_array[season_no] = sum(days_of_month[month] for month in season_months)
        return season_days_array, seasons_defined

    # If predefined seasons are not provided
    if no_of_seasons == 0 or no_of_seasons == 1:
        season_days_array[0] = sum(days_of_month.values())
        return season_days_array, None
    elif no_of_seasons == 12:
        for season_no in range(no_of_seasons):
            season_days_array[season_no] = days_of_month[months_of_year[season_no]]
        return season_days_array, None
    else:
        retype_season_months = True
        user_defined_seasons = []
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
                        user_defined_seasons.append((start_month, end_month))
                        print(f"User input for season {len(user_defined_seasons)} added")
                        break  # In case of valid month inputs, break the retry 'while' loop

                    except Exception as e:
                        print(f"An error occurred: \n{e}\n Please try again.")
                        sys.exit()

                if retype_season_months:
                    user_defined_seasons = []
                    break

            if sum(season_days_array) != sum(days_of_month.values()) and not retype_season_months:  # Check for total days
                print("\nThe demarcation of seasons are not strict and have overlaps or gaps.\n"
                      "Please re-enter the season boundaries ensuring no overlap...")
                user_defined_seasons = []
                retype_season_months = True

    return season_days_array, user_defined_seasons

# Relevant seasonal stats are extracted for year of the current input file
def stats_annual(excel_file: str, season_days_list: np.ndarray):
    df = pd.read_excel(excel_file)
    # Extract the first three columns for index, lat and lon
    base_array = df.iloc[: , :3].to_numpy()
    # Iterate over days in each season
    season_index = 1
    seasonal_data = np.empty((df.shape[0],0))
    non_zero_counts = np.empty((df.shape[0],0))
    for season_days in season_days_list:
        # Summation of seasonal rainfall
        season_col_name = f"Season_{season_index}"
        df[season_col_name] = df.apply(
            lambda row: row.iloc[3:3 + season_days].sum(), axis=1
        )
        seasonal_data = np.hstack((seasonal_data, df[season_col_name].to_numpy().reshape(-1,1)))

        # Non-zero counts
        non_zero_col_name = f"NonZero_{season_index}"
        df[non_zero_col_name] = df.apply(
            lambda row: np.count_nonzero(row.iloc[3:3 + season_days].values), axis=1
        )
        non_zero_counts = np.hstack((non_zero_counts, df[non_zero_col_name].to_numpy().reshape(-1,1)))

        season_index += 1

    yearly_seasonal_sum = np.hstack((base_array, seasonal_data))
    yearly_seasonal_wetdays = np.hstack((base_array, non_zero_counts))

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

final_season_cum_list = []
final_season_wetdays_list = []
season_boundaries = None
for period, years in time_periods.items():
    period_season_cum = []
    period_season_wetdays = []
    for year in years:
        # Defining season boundaries
        if season_boundaries is None:
            season_array, season_boundaries = annual_days_in_season(
                no_of_seasons=total_seasons, current_year=year
            )
            print("User input of seasonal boundaries registered\n")
        else:
            season_array, _ = annual_days_in_season(
                no_of_seasons=total_seasons, current_year=year, seasons_defined=season_boundaries
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
                    annual_season_cum, annual_season_wetdays = stats_annual(
                            excel_file=input_file_path, season_days_list=season_array
                        )

                    period_season_cum.append(annual_season_cum)
                    period_season_wetdays.append(annual_season_wetdays)
                    print(f"Year {year} ({input_file}) for period {period+1} read...")
    period_season_cum = np.stack(period_season_cum, axis=0)
    period_season_wetdays = np.stack(period_season_wetdays, axis=0)

    final_season_cum_list.append(period_season_cum)
    final_season_wetdays_list.append(period_season_wetdays)

    print(f"\nPeriod {period + 1} out of {len(time_periods)} added\n")

array_base = np.array((annual_season_cum[:, :3]))

print("Generating base data...")
cumulative_list = []
for array in final_season_cum_list:
    cum_result_array = np.hstack((np.empty((array_base.shape[0], 0)), array_base))
    cum_result = np.sum(array[:,:, 3:], axis=0)
    cum_result_array = np.hstack((cum_result_array, cum_result))
    cumulative_list.append(cum_result_array)

wetdays_list = []
for array in final_season_wetdays_list:
    wetdays_result_array = np.hstack((np.empty((array_base.shape[0], 0)), array_base))
    wetdays_result = np.sum(array[:,:, 3:], axis=0)
    wetdays_result_array = np.hstack((wetdays_result_array, wetdays_result))
    wetdays_list.append(wetdays_result)

cumulative_list = pd.DataFrame(cum_result_array)
wetdays_list = pd.DataFrame(wetdays_result_array)

cumulative_list.to_excel(r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\test\cum.xlsx")
wetdays_list.to_excel(r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\test\wet.xlsx")