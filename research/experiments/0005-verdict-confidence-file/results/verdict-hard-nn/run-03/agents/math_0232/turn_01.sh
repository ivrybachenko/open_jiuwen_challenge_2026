python3 -c "
s = '1'
for i in range(19):  # We already have term 1, need to generate up to term 20
    new_s = ''
    count = 1
    for j in range(1, len(s)):
        if s[j] == s[j-1]:
            count += 1
        else:
            new_s += str(count) + s[j-1]
            count = 1
    new_s += str(count) + s[-1]
    s = new_s
print(len(s))
" > answer.txt
cat answer.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Computed look-and-say sequence 20th term length" >> verdict.txt