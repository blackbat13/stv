# DEPRECATED

import math

file = open("results.txt")
file2 = open("parsed_results.txt", "w")

for _ in range(0,30):
    line = file.readline()
    values = line.split(";")
    new_values = []
    for i in range(0, len(values)):
        values[i] = int(values[i])
        if i % 3 != 1:
            new_values.append(values[i])

    for i in range(2, len(new_values)):
        new_values[i] = 100-((100*new_values[i])/new_values[i%2])
        new_values[i] = math.ceil(new_values[i])

    for i in range(0, len(new_values) - 1):
        file2.write(str(new_values[i]))
        file2.write(" &")
    file2.write(str(new_values[len(new_values)-1]))
    file2.write(" \\\\\\hline\n")
    print(new_values)

file.close()
file2.close()