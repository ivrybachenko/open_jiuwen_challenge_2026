python3 -c "
# Find integer side lengths a, b, c such that:
# 1. a + b + c = 12
# 2. c = 6 (longest side)
# 3. a, b, c are positive integers
# 4. Triangle inequality: a + b > c, a + c > b, b + c > a
# 5. c is the longest side, so c >= a and c >= b

# Since c = 6 and a + b + c = 12, we have a + b = 6
# Triangle inequality: a + b > c => 6 > 6 is false!
# Wait, let me re-check.

# For a non-degenerate triangle, the triangle inequality must be strict:
# a + b > c
# a + c > b
# b + c > a

# If c = 6 (longest side), and a + b = 6, then a + b = c, which means the triangle is degenerate (all three points are collinear).
# But the problem says 'non-degenerate triangle'.

# Let me re-read: 'Its perimeter is 12 and its longest side is 6.'
# If the longest side is 6, and perimeter is 12, then the other two sides sum to 6.
# For a non-degenerate triangle, we need a + b > c, i.e., 6 > 6, which is false.

# Hmm, let me check if there's any interpretation where this works.
# Maybe the longest side is not unique? Even so, if one side is 6 and it's the longest, 
# the other two sum to 6, and the triangle inequality fails.

# Wait, let me reconsider. Perhaps I should check all possible integer triples.

solutions = []
for a in range(1, 13):
    for b in range(1, 13):
        for c in range(1, 13):
            if a + b + c == 12:
                # Check triangle inequality (non-degenerate)
                if a + b > c and a + c > b and b + c > a:
                    # Check that the longest side is 6
                    sides = sorted([a, b, c])
                    if sides[2] == 6:
                        solutions.append((a, b, c))

print('Solutions:', solutions)
if solutions:
    # Get the product of the other two sides (not the longest one, or if tied, pick appropriately)
    for sol in solutions:
        sides = sorted(sol)
        # Longest side is sides[2] = 6
        # The other two are sides[0] and sides[1]
        product = sides[0] * sides[1]
        print(f'Sides: {sol}, Product: {product}')
else:
    print('No valid non-degenerate triangle found!')
" > /dev/null 2>&1

# Let me actually run it and capture output
python3 -c "
solutions = []
for a in range(1, 13):
    for b in range(1, 13):
        for c in range(1, 13):
            if a + b + c == 12:
                if a + b > c and a + c > b and b + c > a:
                    sides = sorted([a, b, c])
                    if sides[2] == 6:
                        solutions.append((a, b, c))

print('Solutions:', solutions)
if solutions:
    for sol in solutions:
        sides = sorted(sol)
        product = sides[0] * sides[1]
        print(f'Sides: {sol}, Product: {product}')
else:
    print('No valid non-degenerate triangle found!')
"