python3 -c "
# A convex polygon with 5 sides is a pentagon.
# The sum of interior angles of an n-sided polygon is (n-2)*180 degrees.
# For n=5: (5-2)*180 = 3*180 = 540 degrees.
# But the problem states the sum is 500 degrees, which is inconsistent with a standard convex pentagon.
# However, the problem says 'A convex polygon has 5 sides. The sum of its interior angles is 500 degrees.'
# This is mathematically impossible for a simple convex polygon in Euclidean geometry.
# (5-2)*180 = 540, not 500.
# 
# Let me re-read: 'A convex polygon has 5 sides. The sum of its interior angles is 500 degrees. What is the largest interior angle?'
# 
# If we take the problem at face value, it's contradictory. But perhaps it's a trick question or there's a specific interpretation.
# 
# Wait, let me reconsider. Maybe the problem is poorly stated, or maybe I should just compute based on the given sum.
# If the sum is 500 and there are 5 angles, and we want the largest, we need more constraints.
# 
# Actually, for a convex polygon, each interior angle must be less than 180 degrees.
# With 5 angles summing to 500, the average is 100 degrees.
# The largest angle could be anything from just above 100 (if all are equal) to just under 180.
# 
# But wait - the problem says the sum IS 500. For a convex pentagon, the sum MUST be 540.
# This is a contradiction. The problem as stated is impossible.
# 
# Let me check if there's another interpretation. Perhaps it's not a simple polygon?
# No, 'convex polygon' implies simple and convex.
# 
# I'll write IMPOSSIBLE since the given information contradicts Euclidean geometry.
print('IMPOSSIBLE')
" > answer.txt