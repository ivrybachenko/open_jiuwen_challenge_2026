python3 -c "
import math
# Number of paths from (0,0) to (15,15) moving only right or up
# is C(30, 15) = 30! / (15! * 15!)
result = math.comb(30, 15)
print(result)
with open('answer.txt', 'w') as f:
    f.write(str(result) + '\n')
"