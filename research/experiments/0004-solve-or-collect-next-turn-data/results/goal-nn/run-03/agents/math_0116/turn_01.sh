python3 -c "
# We need to find integer side lengths a, b, c of a non-degenerate triangle
# such that:
# 1. a + b + c = 12
# 2. The longest side is 6
# 3. Triangle inequality: a + b > c, a + c > b, b + c > a
# 4. Non-degenerate means strict inequality

# Let the sides be a, b, c with c = 6 being the longest side.
# So a <= 6, b <= 6, and a + b + 6 = 12, so a + b = 6.
# Also, for c=6 to be the longest, we need a <= 6 and b <= 6 (which is satisfied since a+b=6 and a,b positive integers).
# But we also need the triangle inequality: a + b > c => 6 > 6, which is FALSE.

# Wait, let me reconsider. The longest side is 6, but there might be multiple sides equal to 6.
# Let's enumerate all possible integer triples (a, b, c) with a <= b <= c, c = 6, a + b + c = 12.
# So a + b = 6, and a <= b <= 6.

# Possible pairs (a, b) with a <= b and a + b = 6:
# (1, 5): Check triangle inequality: 1 + 5 > 6? 6 > 6? No. Degenerate.
# (2, 4): Check: 2 + 4 > 6? 6 > 6? No. Degenerate.
# (3, 3): Check: 3 + 3 > 6? 6 > 6? No. Degenerate.

# Hmm, all seem degenerate. Let me re-read the problem.
# 'non-degenerate triangle' - strict triangle inequality.
# 'longest side is 6' - at least one side is 6, and no side exceeds 6.

# Let me check if there's a case where the longest side is 6 but it's not unique.
# If two sides are 6: a + 6 + 6 = 12 => a = 0. Not valid (positive integers).

# So with perimeter 12 and longest side 6, there are no non-degenerate triangles?
# Let me double-check by trying all combinations.

solutions = []
for a in range(1, 13):
    for b in range(1, 13):
        for c in range(1, 13):
            if a + b + c == 12:
                # Check non-degenerate triangle inequality
                if a + b > c and a + c > b and b + c > a:
                    # Check that the longest side is 6
                    if max(a, b, c) == 6:
                        solutions.append((a, b, c))

print('Solutions:', solutions)
if solutions:
    for sol in solutions:
        # Sort to get consistent representation
        s = sorted(sol)
        print(f'Sides: {s[0]}, {s[1]}, {s[2]}')
        print(f'Product of other two sides (not the longest): {s[0] * s[1]}')
else:
    print('No non-degenerate triangle found with perimeter 12 and longest side 6')
" > /dev/null 2>&1

# Let me run it properly
python3 -c "
solutions = []
for a in range(1, 13):
    for b in range(1, 13):
        for c in range(1, 13):
            if a + b + c == 12:
                if a + b > c and a + c > b and b + c > a:
                    if max(a, b, c) == 6:
                        solutions.append((a, b, c))

print('Solutions:', solutions)
if solutions:
    for sol in solutions:
        s = sorted(sol)
        print(f'Sides: {s[0]}, {s[1]}, {s[2]}')
        print(f'Product of other two sides: {s[0] * s[1]}')
else:
    print('No solution found')
"