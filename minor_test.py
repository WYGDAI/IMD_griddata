import numpy as np
import sys

def annual_days_in_season(no_of_seasons: int, current_year: int, seasons_defined=None):
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

    # Interactive mode for defining seasons
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
                        print(f"Input added for season {season_no}")
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

        return season_days_array, user_defined_seasons


# Example Usage:
# To use in a loop and only request user inputs once:
seasons_defined = None
for year in range(2000, 2005):  # Example loop over years
    if seasons_defined is None:
        season_days, seasons_defined = annual_days_in_season(no_of_seasons=4, current_year=year)
    else:
        season_days, _ = annual_days_in_season(no_of_seasons=4, current_year=year, seasons_defined=seasons_defined)
    print(f"Year: {year}, Season Days: {season_days}")

