python3 -c "
# Look-and-say sequence
# Term 1: 1
# Term 2: 11 (one 1)
# Term 3: 21 (two 1s)
# Term 4: 1211 (one 2, one 1)
# Term 5: 111221 (one 1, one 2, two 1s)
# etc.

def look_and_say(s):
    result = []
    i = 0
    while i < len(s):
        count = 1
        while i + 1 < len(s) and s[i+1] == s[i]:
            count += 1
            i += 1
        result.append(str(count))
        result.append(s[i])
        i += 1
    return ''.join(result)

# Start with term 1
current = '1'
for i in range(1, 20):  # We already have term 1, need to generate up to term 20
    current = look_and_say(current)

print(f'Term 20 has {len(current)} digits')
print(f'Term 20: {current}')

with open('answer.txt', 'w') as f:
    f.write(str(len(current)) + '\n')
"