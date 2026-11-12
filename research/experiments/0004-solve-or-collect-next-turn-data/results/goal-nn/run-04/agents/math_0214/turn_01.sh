python3 -c "
import math
# Robot moves from (0,0) to (15,15), only right or up
# Total steps: 15 right + 15 up = 30 steps
# Choose 15 positions for right moves (or up moves)
result = math.comb(30, 15)
print(result)
with open('answer.txt', 'w') as f:
    f.write(str(result) + '\n')
"