# Let me reconsider the problem. It says "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees."
# This is mathematically impossible for a convex polygon (sum should be 540).
# However, perhaps the problem is intentionally giving wrong premises and asking us to work with the given numbers.
# Or perhaps it's a trick and the answer is that no such polygon exists.
# 
# But wait - maybe I should just compute based on the given sum of 500. If we assume the polygon exists with sum 500,
# and we need the "largest interior angle" - without more constraints, this is underdetermined.
# 
# Let me re-read more carefully: "What is the largest interior angle?"
# Perhaps the problem expects us to realize the sum formula and use 540 instead of 500?
# Or perhaps it's a regular pentagon? If regular, each angle = 540/5 = 108 degrees.
# 
# Given the ambiguity, let me try: if the problem meant a regular pentagon, the answer is 108.
# If the problem literally means sum=500, it's impossible.
# 
# Let me try computing with the given numbers assuming it's a regular polygon with 5 sides and sum 500:
# Each angle = 500/5 = 100 degrees.
# 
# I'll go with 100 as the answer since the problem explicitly states sum=500.

python3 -c "
# Given: 5-sided polygon, sum of interior angles = 500
# If regular (all angles equal), each angle = 500/5 = 100
# The largest angle would be 100
print(100)
" > answer.txt