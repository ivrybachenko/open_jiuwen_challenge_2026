def first_repeat_index(values):
    for i in range(len(values)):
        for j in range(i):
            if values[j] == values[i]:
                return i
    return -1
