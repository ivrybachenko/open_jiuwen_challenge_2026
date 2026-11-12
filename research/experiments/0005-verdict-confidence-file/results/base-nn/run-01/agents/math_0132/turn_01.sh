# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# However, the formula for the sum of interior angles of an n-sided polygon is (n-2)*180.
# For n=5: (5-2)*180 = 3*180 = 540 degrees.
# The problem statement says the sum is 500 degrees, which contradicts the geometric fact for a simple convex polygon.
# Let's re-read carefully: "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees."
# This is a contradiction. A convex pentagon MUST have an interior angle sum of 540 degrees.
# If the sum is 500, it's not a valid convex polygon in Euclidean geometry.
# However, sometimes these problems are trick questions or have specific contexts.
# Let's check if there's any other interpretation.
# Maybe it's not a simple polygon? But "convex polygon" implies simple.
# Maybe the question is flawed. Let's look at the "largest interior angle" part.
# If we assume the sum is 540 (correct geometric value), we can't determine the largest angle without more info.
# If we assume the sum is 500 (as stated), we still can't determine the largest angle without more info.
# Wait, let's re-read the prompt again. "Compute it with the bash tool".
# Is it possible the problem is asking for something else?
# Let's consider that the problem might be a "trick" where the answer is derived from the given numbers directly.
# But "largest interior angle" in a regular pentagon is 108 degrees.
# In an irregular convex pentagon, the largest angle can be anything from just over 108 to just under 180.
# There is no unique answer unless the polygon is regular.
# Let's assume the polygon is regular. Then each angle is 540/5 = 108.
# If the sum is 500, and it's regular, each angle is 500/5 = 100.
# Given the contradiction, the most likely intended answer is based on the regular polygon assumption with the CORRECT geometric sum.
# Sum = 540, Largest angle (regular) = 108.
# OR, the problem expects us to use the given sum of 500 and assume regularity.
# Largest angle = 500 / 5 = 100.
# Let's look at similar problems online. Often, if a problem states a false premise, you follow the premise.
# "The sum ... is 500 degrees". If we follow this, and assume regularity (since no other info is given), the answer is 100.
# If we correct the premise, the answer is 108.
# Let's try to compute both and see if one makes more sense.
# Actually, let's just use Python to calculate the regular angle for the stated sum.
python3 -c "print(500 // 5)"