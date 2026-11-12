# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# However, for a convex polygon with n sides, the sum of interior angles is (n-2)*180.
# For n=5: (5-2)*180 = 3*180 = 540 degrees.
# The problem states the sum is 500 degrees, which contradicts the formula for a convex polygon.
# But let's re-read: "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees."
# This is mathematically impossible for a convex polygon. A convex pentagon must have interior angle sum of 540.
# If the sum is 500, it cannot be a convex polygon.
# However, the problem asks "What is the largest interior angle?" given these conditions.
# Since the conditions are contradictory (convex + 5 sides => sum=540, but sum=500), this is impossible.
# Let me reconsider: perhaps the problem is testing if I notice the contradiction, or perhaps it's a trick.
# Actually, wait - maybe I should just compute based on the given numbers? But "convex" is a constraint.
# For a convex polygon, all interior angles must be < 180 degrees.
# If sum = 500 and n = 5, average = 100. The largest could be anything from just above 100 to just below 180.
# But without more constraints, the largest interior angle is not uniquely determined.
# The problem is ill-posed/contradictory. Let me write IMPOSSIBLE.

echo "IMPOSSIBLE" > answer.txt
echo "A convex polygon with 5 sides must have an interior angle sum of (5-2)*180 = 540 degrees, not 500. The given conditions are contradictory." >> answer.txt