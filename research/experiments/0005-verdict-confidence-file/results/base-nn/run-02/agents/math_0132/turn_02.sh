cat > /tmp/solve.py << 'PYEOF'
# The problem states: A convex polygon has 5 sides. The sum of its interior angles is 500 degrees.
# 
# For any simple polygon with n sides, the sum of interior angles is (n-2)*180.
# For n=5: (5-2)*180 = 540 degrees.
# 
# The problem states the sum is 500 degrees, which contradicts the geometric fact.
# However, we must work with the given information.
# 
# If we take the problem literally: 5 angles, each < 180 (convex), summing to 500.
# We need to find "the largest interior angle."
# 
# Without additional constraints, the largest angle is not uniquely determined.
# However, perhaps the problem expects us to assume the polygon is regular?
# If regular: each angle = 500/5 = 100 degrees. All angles are equal, so the largest is 100.
# 
# Let's check: 100 < 180, so it's convex. This is a valid convex pentagon (equiangular but not necessarily equilateral).
# 
# Alternatively, if the problem has a typo and meant 540 degrees:
# Regular: 540/5 = 108 degrees.
# 
# Given the explicit statement of 500, I'll go with 500/5 = 100 as the answer, assuming regularity or equal angles.
# 
# Actually, let me reconsider. The problem says "What is the largest interior angle?" which implies a specific value.
# If the polygon is not regular, there are infinitely many solutions.
# The most reasonable interpretation is that the polygon is regular (all angles equal).
# 
# So: 500 / 5 = 100

print(100)
PYEOF
python3 /tmp/solve.py > answer.txt
cat answer.txt