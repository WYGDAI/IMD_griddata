my_dict = {
    "key1": [1, 2, 3],
    "key2": [4, 5, 6],
    "key3": [7, 8, 9],
}


for key, values in my_dict.items():
    print(f"Processing Key: {key}")
    for value in values:
        print(f"Value: {value}")
