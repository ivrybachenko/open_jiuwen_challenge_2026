# The problem is to find the number of paths from (0,0) to (15,15) moving only right or up.
# This is a combinatorics problem: we need to make 15 right moves and 15 up moves, for a total of 30 moves.
# The number of paths is C(30, 15) = 30! / (15! * 15!)

python3 -c "
import math
result = math.comb(30, 15)
print(result)
" > answer.txt

cat answer.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Computed C(30,15) for grid paths" >> verdict.txt