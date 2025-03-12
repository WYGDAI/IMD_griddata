import os

import numpy as np
import pandas as pd
indices_number = 3
start_column = indices_number
end_column = start_column + 31

seasonal = []
for file in os.listdir(r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\test"):
    if file.endswith(".xlsx"):
        df = pd.read_excel(os.path.join(r"C:\Users\koust\Desktop\PhD\IMD_grid\5_IMDexcel\test", file))
        if df.shape[1] == indices_number + 365:  # to ensure dimensions match for leap and non-leap year data
            df.insert(indices_number + 59, '', np.nan)
            df.columns = list(range(df.shape[1]))

        # Extract daily data for the season
        season_data_2d = df.iloc[:, start_column:end_column].values.tolist()
        seasonal_stat = getattr(np, 'sum')(season_data_2d, axis=1)

        seasonal.append(seasonal_stat)

f_data = np.array(seasonal)
mean = np.nanmean(f_data, axis=1)
print(df.shape)


print(df)
# print(df.shape[1])
# print(season_data)
