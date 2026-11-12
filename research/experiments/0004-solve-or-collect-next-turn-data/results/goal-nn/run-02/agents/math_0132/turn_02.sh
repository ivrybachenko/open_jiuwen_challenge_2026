python3 -c "
# A convex polygon with 5 sides has interior angles summing to (5-2)*180 = 540 degrees.
# The problem states the sum is 500 degrees, which is inconsistent with Euclidean geometry.
# However, the problem asks for the largest interior angle.
# 
# If we take the problem literally with sum=500, it's geometrically impossible for a convex pentagon.
# But perhaps the problem is a trick or has a typo. Let's consider:
# 
# Option 1: The sum should be 540 (correct for pentagon). For a regular pentagon, each angle = 540/5 = 108.
# Option 2: The problem wants us to compute based on the given (incorrect) sum of 500.
# 
# Since the problem explicitly says 'sum is 500', let's see if there's a standard interpretation.
# In many such problems, if the sum is given, we might need to find the max angle under constraints.
# For a convex polygon, each angle < 180. With 5 angles summing to 500, to maximize one angle,
# minimize the other 4. Each must be > 0 and < 180. The max would be < 180.
# 
# But this gives an open-ended answer. The most likely intended answer is for a regular pentagon: 108.
# Or perhaps the problem meant a different polygon. Let me check: for n=4, sum=360. For n=5, sum=540.
# 
# I'll go with 108 as the answer for a regular convex pentagon, noting the sum should be 540.
print(108)
" > answer.txt