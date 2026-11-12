# The problem states a convex polygon has 5 sides and the sum of its interior angles is 500 degrees.
# However, for any convex polygon with n sides, the sum of interior angles is (n-2)*180 degrees.
# For n=5: (5-2)*180 = 3*180 = 540 degrees.
# The problem states the sum is 500 degrees, which contradicts the geometric fact.
# This is an impossible problem as stated because a convex pentagon must have interior angles summing to 540 degrees, not 500.
# Let me re-read: "A convex polygon has 5 sides. The sum of its interior angles is 500 degrees."
# This is mathematically impossible. A convex polygon with 5 sides must have interior angle sum of 540.
# Since the premise is contradictory, the task is impossible.

echo "IMPOSSIBLE" > answer.txt
echo "The sum of interior angles of a convex pentagon must be (5-2)*180 = 540 degrees, not 500. The given conditions are contradictory." >> answer.txt

cat > verdict.txt << 'EOF'
impossible
1.00
A convex pentagon must have interior angle sum of 540 degrees; 500 is geometrically impossible.
EOF