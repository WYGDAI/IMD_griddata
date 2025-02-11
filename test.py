import pandas as pd
import numpy as np

days_in_seasons = np.array([59, 92, 153, 61], int)

input_file = r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\rain-excel\2023-rain-IMD.xlsx"

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

print("Debug line")