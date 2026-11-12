python3 -c "
import math
# Robot moves from (0,0) to (15,15)
# Total steps: 15 right + 15 up = 30 steps
# Number of paths = C(30, 15) = 30! / (15! * 15!)
result = math.comb(30, 15)
print(result)
with open('answer.txt', 'w') as f:
    f.write(str(result) + '\n')
"
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Computed C(30,15) for robot path problem" >> verdict.txt