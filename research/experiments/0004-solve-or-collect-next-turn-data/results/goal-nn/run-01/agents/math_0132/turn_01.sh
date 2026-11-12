# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# Wait, let me verify: For a convex polygon with n sides, the sum of interior angles is (n-2)*180.
# For n=5: (5-2)*180 = 3*180 = 540 degrees.
# But the problem says the sum is 500 degrees. This is contradictory for a standard convex polygon.
# However, the problem explicitly states "The sum of its interior angles is 500 degrees."
# This is a math problem that might be testing if we notice the contradiction, or it might be a non-standard polygon.
# But it says "convex polygon" which by definition has sum = (n-2)*180.
# For n=5, sum must be 540, not 500.
# 
# Let me re-read: "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees. What is the largest interior angle?"
# 
# This is impossible as stated because a convex pentagon must have interior angle sum of 540 degrees.
# If the sum is 500, it cannot be a convex pentagon.
# 
# However, perhaps the problem is poorly stated and we should just work with the given numbers.
# If we have 5 angles that sum to 500, and we want the largest one... but we don't have enough info.
# 
# Actually, let me reconsider. Maybe the problem is a trick question. A convex polygon with 5 sides MUST have sum 540.
# Since 500 ≠ 540, such a polygon cannot exist. So the answer might be IMPOSSIBLE.
# 
# But wait - let me check if there's another interpretation. Perhaps it's not a simple polygon? No, "convex polygon" implies simple.
# 
# Let me just compute what the problem seems to ask: if we have 5 angles summing to 500, what's the largest?
# Without additional constraints, the largest could be anything from 500/5 = 100 (if all equal) up to nearly 500 (if others are nearly 0).
# But for a convex polygon, each angle must be < 180 degrees.
# 
# Given the contradiction, I'll write IMPOSSIBLE.

echo "IMPOSSIBLE" > answer.txt
echo "A convex polygon with 5 sides must have an interior angle sum of (5-2)*180 = 540 degrees, not 500. Such a polygon cannot exist." >> answer.txt