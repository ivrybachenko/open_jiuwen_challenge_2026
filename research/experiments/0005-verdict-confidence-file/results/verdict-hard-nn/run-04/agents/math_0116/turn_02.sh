python3 -c "
# A non-degenerate triangle has integer side lengths.
# Perimeter = 12, longest side = 6.
# Find all integer triples (a, b, c) with a <= b <= c, c = 6, a + b + c = 12.
# So a + b = 6, and c = 6 is the longest side, so b <= 6 and a <= 6.
# Also non-degenerate means strict triangle inequality: a + b > c.
# But a + b = 6 and c = 6, so a + b = c, which means degenerate.
# 
# Wait - let me re-read the problem. Maybe 'longest side is 6' doesn't mean c=6 uniquely.
# Let me check if there's any interpretation.
# 
# Actually, for a non-degenerate triangle with perimeter 12:
# The longest side must be less than half the perimeter (strictly less for non-degenerate).
# Half of 12 is 6, so the longest side must be < 6 for a non-degenerate triangle.
# But the problem says the longest side IS 6.
# 
# This seems impossible for a non-degenerate triangle. Let me verify by checking all possible triangles.

solutions = []
for a in range(1, 13):
    for b in range(a, 13):
        for c in range(b, 13):
            if a + b + c == 12:
                # Check non-degenerate triangle inequality
                if a + b > c and a + c > b and b + c > a:
                    solutions.append((a, b, c))

print('All non-degenerate integer triangles with perimeter 12:')
for sol in solutions:
    print(f'  Sides: {sol}, Longest: {sol[2]}')

# Now filter those where longest side is 6
filtered = [s for s in solutions if s[2] == 6]
print(f'Filtered (longest side = 6): {filtered}')

if not filtered:
    print('No non-degenerate triangle with perimeter 12 has longest side 6.')
    print('This is because for non-degenerate triangle, longest side < perimeter/2 = 6.')
    print('So longest side must be at most 5.')
else:
    for sol in filtered:
        product = sol[0] * sol[1]
        print(f'Product of other two sides: {product}')
"