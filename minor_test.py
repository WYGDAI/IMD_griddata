# Constants
months = ['January', 'February', 'March']
days_in_month = {'January': 31, 'February': 28, 'March': 31}

# Season 1 ends on day 90 (March 31)
season_days_array = [90, 60]  # Season 1 has 90 days, Season 2 starts at day 91

# To simulate the transition from season to season
current_day = 0  # Start from day 0 (January 1st)

# Loop over each season
for season_idx, season_days in enumerate(season_days_array):
    print(f"Season {season_idx + 1} (Total days: {season_days}):")

    # Loop through the months for the current season
    current_day_in_season = current_day
    for month in months:
        if current_day_in_season >= current_day + season_days:
            break  # If the season is over, stop processing months

        month_days = days_in_month[month]

        # Calculate the range of days for the month in the current season
        month_start = max(current_day_in_season, current_day)  # Start from the beginning of the season or month
        month_end = min(current_day_in_season + month_days,
                        current_day + season_days)  # End at the season's end or month

        # Output the month and its range in the season
        print(f"  {month}: Days {month_start + 1} to {month_end}")

        # Update current day for next month
        current_day_in_season += month_days

    # Update current_day to the start of the next season
    current_day += season_days
    print()

