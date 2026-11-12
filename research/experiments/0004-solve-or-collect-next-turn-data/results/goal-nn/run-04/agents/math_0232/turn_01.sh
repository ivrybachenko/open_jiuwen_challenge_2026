python3 -c "
# Look-and-say sequence: start with '1', each next term describes the previous
# Term 1: 1
# Term 2: 11 (one 1)
# Term 3: 21 (two 1s)
# Term 4: 1211 (one 2, one 1)
# Term 5: 111221 (one 1, one 2, two 1s)
# ...
# Find the number of digits in term 20

def look_and_say(s):
    result = []
    i = 0
    while i < len(s):
        count = 1
        while i + 1 < len(s) and s[i + 1] == s[i]:
            count += 1
            i += 1
        result.append(str(count))
        result.append(s[i])
        i += 1
    return ''.join(result)

current = '1'
for i in range(1, 20):
    current = look_and_say(current)

print(len(current))
" > answer.txt