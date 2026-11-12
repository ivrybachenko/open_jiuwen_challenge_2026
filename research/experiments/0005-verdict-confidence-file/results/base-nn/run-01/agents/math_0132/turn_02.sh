# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# This is geometrically impossible for a simple convex polygon in Euclidean geometry, where the sum must be (5-2)*180 = 540 degrees.
# However, we must follow the problem's stated premises.
# If we assume the polygon is regular (all angles equal), then each angle is 500 / 5 = 100 degrees.
# In a regular polygon, all angles are equal, so the largest is 100.
# If the polygon is not regular, the largest angle could be anything from >100 to <180, but without more info, we can't determine it.
# Given the ambiguity, the most reasonable interpretation for a "compute it" task with no other constraints is to assume regularity.
# Let's write 100 to answer.txt.

echo 100 > answer.txt