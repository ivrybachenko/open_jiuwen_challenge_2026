```bash
# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# For a convex polygon with n sides, the sum of interior angles is (n-2)*180.
# For n=5: (5-2)*180 = 3*180 = 540 degrees.
# But the problem says the sum is 500 degrees, which contradicts the formula for a simple convex polygon.
# However, the problem asks "What is the largest interior angle?" given these conditions.
# 
# Wait, let me re-read. "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees."
# This is mathematically impossible for a simple convex polygon (sum should be 540).
# 
# But perhaps the problem is testing whether we notice this, or perhaps it's a trick question.
# Let me think about this more carefully.
# 
# Actually, re-reading the problem: it says "Compute it with the bash tool (python3 -c)".
# The problem might be poorly stated, but let's consider: if we have a 5-sided convex polygon,
# the sum MUST be 540 degrees. If the problem states 500, there's a contradiction.
# 
# However, perhaps the problem is asking: given a convex pentagon where we know the sum is 500
# (which is impossible), what would be the largest angle? This doesn't make sense.
# 
# Let me reconsider: maybe the problem is simply asking for the maximum possible interior angle
# of a convex pentagon. In a convex polygon, each interior angle must be less than 180 degrees.
# The largest interior angle in a convex pentagon would approach 180 degrees but never reach it.
# 
# But that's not a specific number. Let me think differently.
# 
# Perhaps the problem has a typo and the sum is 540 (which is correct for a pentagon).
# If the sum is 540 and we want the largest angle, we need more information.
# 
# Wait - maybe the problem is asking: what is the theoretical maximum interior angle of any
# convex polygon with 5 sides? In a convex polygon, each angle < 180°. So the maximum is
# just under 180°. But that's not a specific answer.
# 
# Let me re-read once more: "What is the largest interior angle?"
# 
# Hmm, perhaps the problem is simpler than I think. Maybe it's asking for the average angle?
# 540/5 = 108 degrees for a regular pentagon.
# 
# Or perhaps the problem is: given that the sum is 500 (ignoring the geometric impossibility),
# and we want to maximize one angle while keeping all angles positive and the polygon convex,
# the largest angle would be 500 - 4*epsilon ≈ 500, but that violates convexity (angle < 180).
# 
# I think the most reasonable interpretation is that there's a typo and the sum should be 540.
# For a regular pentagon, each angle is 108 degrees.
# 
# But the problem specifically says 500. Let me just compute what the problem asks literally.
# If we have 5 angles that sum to 500, and each must be < 180 (convex), and > 0:
# To maximize one angle, minimize the others. The minimum each other angle can be approaches 0.
# So the max angle approaches 500, but must be < 180. So max is just under 180.
# 
# This is ambiguous. Let me just go with the regular pentagon answer of 108, or note the issue.
# 
# Actually, I'll compute: for a regular convex pentagon, each interior angle = (5-2)*180/5 = 108.
# The problem might have a typo (500 instead of 540). Let me output 108 as the answer for a regular pentagon.
# 
# But wait - the problem says "the sum is 500" which is wrong. Let me just compute the correct
# sum and the corresponding regular angle.

python3 -c "
# For a convex polygon with n=5 sides:
# Sum of interior angles =