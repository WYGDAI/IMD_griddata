final_data_dictList4d = {
    'cum': [
        [  # First 3D list
            [[1, 2], [3, 4]],  # Height 1
            [[5, 6], [7, 8]],  # Height 2
        ],
        [  # Second 3D list
            [[9, 10], [11, 12]],  # Height 1
            [[13, 14], [15, 16]],  # Height 2
        ]
    ]
}

for array3d in final_data_dictList4d['cum']:
    # Initialize the 2D array to store the sum across heights
    compressed_2d_array = [
        [sum(row) for row in zip(*height)]
        for height in zip(*array3d)
    ]

    # Print the compressed 2D array
    print("Compressed 2D Array:\n", compressed_2d_array)

