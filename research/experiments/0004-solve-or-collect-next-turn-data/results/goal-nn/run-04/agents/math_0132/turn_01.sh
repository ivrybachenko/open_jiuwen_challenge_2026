# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# Wait, let me verify: For a convex polygon with n sides, the sum of interior angles is (n-2)*180.
# For n=5: (5-2)*180 = 3*180 = 540 degrees.
# But the problem says the sum is 500 degrees. This is contradictory for a standard convex polygon.
# However, the problem explicitly states "The sum of its interior angles is 500 degrees."
# This might be a trick question or the polygon might not be regular.
# The question asks for "the largest interior angle."
# Without additional constraints (like the polygon being regular, or having specific angle relationships),
# the largest interior angle could be anything from just above 0 (if other angles are close to 180) 
# up to just below 180 (since it's convex, each angle < 180).
# 
# Let me re-read: "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees."
# This is mathematically impossible for a simple convex polygon in Euclidean geometry.
# Sum = (n-2)*180 = 540 for n=5.
# 
# However, perhaps the problem is testing if I notice this, or perhaps it's a non-Euclidean context,
# or perhaps it's simply a poorly constructed problem where I should just answer based on the given sum.
# 
# If we assume the problem is valid as stated (perhaps in a different geometry), and we need the LARGEST interior angle,
# without more information, we cannot determine a unique answer.
# 
# But wait - maybe the problem expects me to compute something specific. Let me think about what "largest interior angle" 
# could mean in a context where the sum is 500.
# 
# Actually, re-reading more carefully: the problem might be a trick. The sum of interior angles of a 5-sided convex polygon
# MUST be 540 degrees. If the problem states 500, it's contradictory. 
# 
# However, in many such puzzle contexts, if given contradictory premises, one might need to just compute based on the given numbers.
# If we assume the polygon is "as regular as possible" given the sum is 500, each angle would be 500/5 = 100 degrees.
# In that case, the largest angle would be 100.
# 
# Alternatively, if the problem is simply wrong and expects the standard answer for a regular pentagon:
# Each angle = 540/5 = 108 degrees.
# 
# Let me just compute both and see. The problem says "Compute it with the bash tool". 
# Given the ambiguity, I'll go with the interpretation that the sum is 500 and we want the largest angle in a scenario where
# angles are as equal as possible (regular-like), which gives 500/5 = 100.
# 
# But actually, the most likely intended answer is that the problem has a typo and should be 540, giving 108.
# Or the problem wants 500/5 = 100.
# 
# Let me just compute 500/5 = 100 as that's what the problem explicitly states.

python3 -c "print(500 // 5)" > answer.txt
cat answer.txt