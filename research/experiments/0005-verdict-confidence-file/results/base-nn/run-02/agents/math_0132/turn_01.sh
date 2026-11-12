```bash
# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# Wait, let's verify: For a polygon with n sides, the sum of interior angles is (n-2)*180.
# For n=5: (5-2)*180 = 3*180 = 540 degrees.
# The problem states the sum is 500 degrees, which contradicts the formula for a simple polygon.
# However, the problem says "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees."
# This is mathematically impossible for a simple convex polygon.
# Let me re-read carefully: "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees. What is the largest interior angle?"
# 
# If the sum is given as 500, and it's a 5-sided polygon, we need to find the largest interior angle.
# But without more information about the distribution of angles, we cannot determine the largest angle uniquely.
# 
# However, perhaps the problem is testing if I notice the contradiction, or perhaps it's a trick question.
# Let me think again. Maybe the problem is poorly stated and expects me to use the formula?
# If I use the formula, sum = 540, not 500.
# 
# Let me re-read: "The sum of its interior angles is 500 degrees."
# This is explicitly given. So we have 5 angles that sum to 500.
# For a convex polygon, each interior angle must be less than 180 degrees.
# To maximize one angle, we minimize the others. The minimum an interior angle can be in a convex polygon approaches 0 (but must be > 0).
# In practice, for a convex polygon, angles are typically > 0 and < 180.
# If we want the largest possible angle, we make the other 4 angles as small as possible.
# The smallest an interior angle can be in a convex polygon is just above 0 degrees.
# So the largest angle could approach 500 - 4*0 = 500, but it must be < 180 for convexity.
# 
# Wait, if each angle must be < 180, and we have 5 angles summing to 500:
# The maximum any single angle can be is just under 180.
# If one angle is 179.999..., the other 4 sum to 500 - 179.999... = 320.000...
# Each of the other 4 must be < 180, and 320/4 = 80, which is fine.
# So the largest angle can be at most just under 180 degrees.
# 
# But the problem asks for "the" largest interior angle, implying a unique answer.
# This suggests the problem might have a specific configuration in mind, or there's additional context.
# 
# Let me reconsider: Perhaps the problem is simply wrong, and I should use the correct sum of 540?
# Or perhaps the problem expects me to report that it's impossible?
# 
# Given the instruction "Compute it with the bash tool (python3 -c)", let me try both interpretations.
# 
# Actually, re-reading more carefully, I think the problem might be a trick. The sum of interior angles of a 5-sided polygon is ALWAYS 540 degrees. The statement "The sum of its interior angles is 500 degrees" is false. 
# 
# But the problem says to compute the largest interior angle given these conditions. If we take the conditions literally:
# - 5 angles, each < 180 (convex)
# - Sum = 500
# - Find the maximum possible value of the largest angle
# 
# The maximum value of the largest angle is bounded by 180 (exclusive). We can approach 180 arbitrarily closely.
# For example: angles = [179.999, 80, 80, 80, 80.001] sum to 500.
# 
# But this doesn't give a unique answer. Let me check if there's a standard interpretation.
# 
# Perhaps the problem meant a regular polygon? For a regular 5-g