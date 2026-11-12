python3 -c "
result = (pow(3, 2026, 100000) + pow(7, 2027, 100000)) % 100000
with open('answer.txt', 'w') as f:
    f.write(str(result))
"