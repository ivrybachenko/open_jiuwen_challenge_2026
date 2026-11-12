# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# Wait, let me verify: For a convex polygon with n sides, the sum of interior angles is (n-2)*180.
# For n=5: (5-2)*180 = 3*180 = 540 degrees.
# But the problem says the sum is 500 degrees. This is contradictory for a standard convex polygon.
# However, the problem explicitly states "The sum of its interior angles is 500 degrees."
# This might be a trick question or the polygon might not be regular.
# 
# Actually, re-reading: "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees."
# This is mathematically impossible for a simple convex polygon in Euclidean geometry.
# (5-2)*180 = 540, not 500.
# 
# But wait - maybe the problem is asking us to just work with the given numbers?
# If the sum is 500 and there are 5 angles, and we want the "largest" interior angle...
# Without additional constraints, the largest angle could be anything from just above 0 to just below 500-0-0-0=500 (but must be < 180 for convex).
# 
# Actually, for a convex polygon, each interior angle must be less than 180 degrees.
# If the sum is 500 with 5 angles, and each angle < 180, the maximum possible largest angle would be...
# If 4 angles are as small as possible (approaching 0), the 5th could approach 500, but it must be < 180.
# So the largest angle is bounded by 180 (exclusive) for convexity.
# 
# Hmm, but this seems like a poorly posed problem. Let me re-read more carefully.
# 
# Perhaps the problem is simply wrong about the sum, and we should use the correct sum of 540?
# Or perhaps it's a regular pentagon? For a regular pentagon, each angle = 540/5 = 108 degrees.
# 
# Let me just compute with the given information. If the sum is 500 and it's convex with 5 sides,
# the problem might expect us to find the maximum possible value of the largest angle.
# 
# For a convex pentagon with angle sum 500:
# Each angle < 180
# To maximize one angle, minimize the other four. The minimum interior angle approaches 0.
# So the largest angle approaches 500 - 0 - 0 - 0 - 0 = 500, but must be < 180.
# So the supremum is 180, but it can't reach 180.
# 
# This doesn't give a clean answer. Let me reconsider - maybe the problem has a typo and means
# a regular pentagon? Then each angle = 108.
# 
# Or maybe the problem is just asking: given 5 angles summing to 500, what's the max possible?
# With convexity constraint (each < 180), the answer would be "approaches 180" which isn't a number.
# 
# I think the most reasonable interpretation is that this is a regular pentagon and the sum
# should be 540, giving 108. But the problem says 500...
# 
# Let me just go with: the problem states sum=500, 5 sides, convex. The largest angle in a 
# regular pentagon would be 540/5=108. If we assume regularity despite the wrong sum, 
# 500/5 = 100.
# 
# I'll compute 500/5 = 100 as the answer, assuming the problem wants us to divide the given sum by the number of angles.

python3 -c "print(500 / 5)" > /tmp/result.txt
cat /tmp/result.txt