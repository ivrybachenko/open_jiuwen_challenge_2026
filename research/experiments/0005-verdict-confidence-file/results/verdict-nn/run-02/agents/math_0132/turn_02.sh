# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# For a convex polygon with n sides, the sum of interior angles is (n-2)*180.
# For n=5, sum = (5-2)*180 = 540 degrees.
# The problem states the sum is 500 degrees, which is a contradiction for a convex pentagon.
# However, if we assume the problem is asking for the largest angle in a convex pentagon with sum 540 (ignoring the 500 as a typo),
# and if it's regular, each angle is 108.
# If it's not regular, the largest angle can be anything from 108 (regular) up to just under 180.
# But the problem gives a specific sum of 500. This is impossible for a convex pentagon.
# Let's consider if the problem is a trick. Maybe it's not a simple polygon? No, "convex polygon".
# Maybe the number of sides is different? If sum is 500, (n-2)*180 = 500 => n-2 = 500/180 = 2.777 => n = 4.777, not an integer.
# So no convex polygon has interior angle sum of 500.
# Therefore, the task is impossible as stated.
echo "IMPOSSIBLE" > answer.txt
echo "The sum of interior angles for a convex pentagon is 540 degrees, not 500. No convex polygon has an interior angle sum of 500 degrees." >> answer.txt
echo "impossible" > verdict.txt
echo "0.00" >> verdict.txt
echo "The problem statement contains a mathematical contradiction." >> verdict.txt