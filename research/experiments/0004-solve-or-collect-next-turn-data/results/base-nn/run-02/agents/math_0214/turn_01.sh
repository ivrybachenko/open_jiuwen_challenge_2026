python3 -c "
import math
# The robot needs to go from (0,0) to (15,15)
# It must make exactly 15 moves right and 15 moves up, for a total of 30 moves.
# The number of different paths is the number of ways to choose 15 right moves out of 30 total moves.
# This is C(30, 15) = 30! / (15! * 15!)
result = math.comb(30, 15)
print(result)
with open('answer.txt', 'w') as f:
    f.write(str(result))
"