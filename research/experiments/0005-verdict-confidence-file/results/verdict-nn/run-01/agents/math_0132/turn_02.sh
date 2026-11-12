# Re-reading the problem: "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees. What is the largest interior angle?"
# 
# The sum of interior angles of a convex polygon with n sides is (n-2)*180.
# For n=5: (5-2)*180 = 540 degrees.
# The problem states the sum is 500 degrees, which contradicts geometry.
#
# However, perhaps the problem is poorly worded and we should just compute based on the given sum of 500.
# If we assume the sum is 500 (even though it's geometrically impossible for a convex pentagon),
# and we want the "largest interior angle", we need more information.
#
# Wait - maybe the problem is asking: given a convex polygon with 5 sides where the sum is somehow 500,
# what's the maximum possible value for one angle? In a convex polygon, each angle must be < 180.
# If 4 angles are as small as possible (approaching 0), the 5th could approach 500, but that violates convexity (< 180).
# 
# Actually, for a convex polygon, each interior angle must be strictly less than 180 degrees.
# If the sum is 500 and there are 5 angles, and each < 180, the maximum one angle can be is:
# 500 - 4*(minimum angle). The minimum angle in a convex polygon approaches 0.
# So the max approaches 500, but must be < 180. So max < 180.
#
# But this doesn't give a unique answer. Let me reconsider.
#
# Perhaps the problem has a typo and meant 540 degrees. If sum = 540 and it's a regular pentagon,
# each angle = 540/5 = 108 degrees. The largest would be 108.
#
# Or perhaps the problem is just wrong and we should answer based on the stated sum of 500.
# If we assume equal angles: 500/5 = 100 degrees each. Largest = 100.
#
# Given the ambiguity, let me try computing with the stated sum of 500, assuming equal angles:
python3 -c "print(500 // 5)" > answer.txt

cat > verdict.txt << 'EOF'
solved
0.50
Assumed equal angles with sum 500, giving 100 degrees each. Problem statement is geometrically inconsistent.
EOF