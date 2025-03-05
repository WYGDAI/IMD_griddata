# Summing the second given list of numbers
numbers = [
    68, 97, 21, 98, 64, 11, 61, 65, 2, 72, 86, 8, 13, 61, 37, 62, 23, 10, 14, 23, 11, 45, 71, 79, 40, 17, 30, 85, 19, 62, 91, 85, 1, 15, 83, 30, 27, 71, 38, 16, 23, 80, 85, 84, 2, 71, 21, 0, 6, 38, 40, 69, 55, 25, 89, 20, 6, 45, 91, 58, 9, 26, 74, 16, 27, 7, 77, 25, 47, 92, 96, 89, 55, 1, 96, 6, 45, 62, 44, 52, 50, 88, 99, 88, 8, 24, 89, 22, 31, 72, 38, 56
]

total_sum_2 = sum(numbers)

# Slicing the list and calculating sums for the specified groups
sum_first_31 = sum(numbers[:31])
sum_next_28 = sum(numbers[31:62])
sum_last_30 = sum(numbers[62:])

print(sum_first_31, sum_next_28, sum_last_30)

print(total_sum_2)
