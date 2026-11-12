```bash
# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# However, the formula for the sum of interior angles of an n-sided polygon is (n-2) * 180.
# For n=5: (5-2) * 180 = 3 * 180 = 540 degrees.
# The problem statement says the sum is 500 degrees, which contradicts the geometric fact for a simple polygon.
# Let's re-read carefully: "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees."
# This is a contradiction. A convex pentagon MUST have an interior angle sum of 540 degrees.
# If the sum is 500, it's not a valid convex polygon in Euclidean geometry.
# However, sometimes these problems are trick questions or have specific contexts.
# Let's look at the question: "What is the largest interior angle?"
# If we assume the problem implies a regular polygon, each angle would be 500/5 = 100 degrees.
# But a regular pentagon has angles of 108 degrees.
# If the polygon is not regular, the angles can vary, but their sum must be 540.
# Since the problem explicitly states the sum is 500, which is geometrically impossible for a convex pentagon,
# there might be a typo in the problem.
# Let's consider if it's a typo for 540. If sum is 540, and it's regular, largest is 108.
# If it's not regular, the largest angle can be anything from just above 0 to just below 180 (for convexity).
# Without more constraints (like "regular"), the largest angle is not uniquely determined.
# However, in many such "math" problems from datasets, if it says "convex polygon" and asks for "the" largest angle,
# it often implies a regular polygon.
# Let's check if 500 is a typo for 540. 540 is the correct sum.
# If the problem meant a regular pentagon, the answer is 108.
# If the problem insists on sum=500, it's impossible.
# Let's look at similar problems. Often, "sum of interior angles" is given to verify the number of sides.
# If sum = 500, then (n-2)*180 = 500 => n-2 = 500/180 = 2.77 => n = 4.77, not an integer.
# So a polygon with sum 500 doesn't exist.
# Given the contradiction, the most likely intended problem is a regular pentagon (sum 540).
# Let's assume the question meant a regular pentagon.
# Angle = 540 / 5 = 108.

# Let's try to interpret "largest interior angle" in a different way.
# Maybe it's not a simple polygon? No, "convex polygon" implies simple.
# Maybe the 500 is correct and it's a trick?
# If I have to answer based on the text "sum is 500", and it's not regular, the largest angle is undefined.
# If it's regular, each angle is 100.
# Let's check if there's a standard interpretation.
# In many online problem sets, if the sum is given incorrectly, it's a typo.
# Let's assume the typo is in the sum, and it should be 540.
# Then for a regular pentagon, angle is 108.
# If the polygon is not regular, the largest angle is not unique.
# The question asks "What is the largest interior angle?", implying a unique answer.
# This strongly suggests the polygon is regular.
# If it's regular, sum = 5 * angle.
# If sum = 500, angle = 100.
# If sum = 540, angle = 108.
# Which is more likely? 500 is a round number. 540 is the geometric truth.
# Let's look at the source. "023_math_0132".
# Let's compute both and see if one makes more sense.
# A regular pentagon has angles of 1