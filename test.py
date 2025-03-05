import numpy as np

# Define dimensions for the test data:
Y = 2   # Number of years in a period
S = 3   # Number of seasons per year
n = 4   # Number of grid points
d = 5   # Number of days per season (for 'daily' subkey)
m = 2   # Number of months per season (for 'monthly' subkey)

# Assume raw_stat_list and count_list as defined in BASIS:
raw_stat_list = ["sum", "max", "min"]
count_list = ["days", "wetdays"]

# Build a dummy final_data_dictList4d with the expected structure.

# For raw statistics keys, we generate random float data.
final_data_dictList4d = {}
for key in raw_stat_list:
    final_data_dictList4d[key] = {
        "daily": np.random.rand(Y, S, n, d).tolist(),        # Shape: [Y, S, n, d]
        "monthly": np.random.rand(Y, S, n, m).tolist(),          # Shape: [Y, S, n, m]
        "seasonal": np.random.rand(Y, S, n).tolist()             # Shape: [Y, S, n]
    }

# For count keys ('days' and 'wetdays'):
final_data_dictList4d["days"] = {
    "daily": np.ones((Y, S, n, d), dtype=int).tolist(),          # All ones for 'days'
    "monthly": np.ones((Y, S, n, m), dtype=int).tolist(),          # All ones for 'days'
    "seasonal": np.ones((Y, S, n), dtype=int).tolist()             # All ones for 'days'
}
# For 'wetdays', we simulate binary values (0 or 1)
final_data_dictList4d["wetdays"] = {
    "daily": np.random.randint(0, 2, size=(Y, S, n, d)).tolist(),   # Binary data for 'wetdays'
    "monthly": np.random.randint(0, 2, size=(Y, S, n, m)).tolist(),   # Binary data for 'wetdays'
    "seasonal": np.random.randint(0, 2, size=(Y, S, n)).tolist()       # Binary data for 'wetdays'
}

# Now define your mean() function (as provided) – for convenience, I'll assume it's defined as follows:
def mean(f_final_data_dictList4d: dict[str, dict[str, list]],
         stat_list: list = None,
         zeroes=True):
    import numpy as np
    if stat_list is None:
        stat_list = raw_stat_list

    f_mean_dict2List2d = {f_key: {'daily': [], 'monthly': [], 'seasonal': []} for f_key in stat_list}
    for f_key in stat_list:
        for f_subkey in ['daily', 'monthly', 'seasonal']:
            days_data = np.array(f_final_data_dictList4d['days'][f_subkey])
            wetdays_data = np.array(f_final_data_dictList4d['wetdays'][f_subkey])

            # Sum the count data over years and the last axis (d or m)
            if days_data.ndim == 4 and wetdays_data.ndim == 4:
                total_days = np.sum(days_data, axis=(0, -1))
                total_wetdays = np.sum(wetdays_data, axis=(0, -1))
            elif days_data.ndim == 3 and wetdays_data.ndim == 3:
                total_days = np.sum(days_data, axis=0)
                total_wetdays = np.sum(wetdays_data, axis=0)
            else:
                total_days = total_wetdays = 1  # Fallback

            # Sum the raw data over the corresponding dimensions.
            f_data = np.array(f_final_data_dictList4d[f_key][f_subkey])
            if f_data.ndim == 4:
                f_data_sum = np.sum(f_data, axis=(0, -1))
            elif f_data.ndim == 3:
                f_data_sum = np.sum(f_data, axis=0)
            else:
                f_data_sum = f_data

            # Compute the mean (handling division errors)
            with np.errstate(divide='ignore', invalid='ignore'):
                if zeroes:
                    f_mean_data = np.true_divide(f_data_sum, total_days)
                else:
                    f_mean_data = np.true_divide(f_data_sum, total_wetdays)
                f_mean_data[np.isnan(f_mean_data)] = 0

            # Append the computed mean array (shape should be [S, n]) to the corresponding list.
            f_mean_dict2List2d[f_key][f_subkey].append(f_mean_data)
    return f_mean_dict2List2d

# Now, call the mean() function using the dummy data.
mean_result = mean(final_data_dictList4d, stat_list=raw_stat_list, zeroes=True)

# Print the structure of the mean_result.
print("Mean Result Structure:")
for key in mean_result:
    print(f"Key: {key}")
    for subkey in mean_result[key]:
        # Each subkey is a list of arrays. We'll print the shape of the first array in each list.
        array_shape = np.array(mean_result[key][subkey][0]).shape
        print(f"  {subkey}: shape {array_shape}")

print('okay')