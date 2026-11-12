python3 -c "
import math
# Robot moves from (0,0) to (15,15)
# Needs 15 right moves and 15 up moves, total 30 moves
# Number of paths = C(30, 15)
result = math.comb(30, 15)
print(result)
with open('answer.txt', 'w') as f:
    f.write(str(result))
"