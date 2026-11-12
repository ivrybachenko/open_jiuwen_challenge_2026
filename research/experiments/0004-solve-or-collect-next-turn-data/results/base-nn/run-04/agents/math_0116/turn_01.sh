python3 -c "
# Find all non-degenerate triangles with integer sides, perimeter 12, longest side 6
# Let sides be a, b, c where c=6 is the longest side
# a + b + 6 = 12 => a + b = 6
# Triangle inequality: a + b > c => 6 > 6 is false... wait
# Non-degenerate means strict inequality: a + b > c
# But a + b = 6 and c = 6, so a + b = c, which means degenerate (collinear)
# Let me re-read: longest side is 6. So c=6, and a <= 6, b <= 6
# a + b = 6
# For non-degenerate: a + b > c => 6 > 6 => false
# Hmm, let me check if there are any valid triangles.

# Actually, let me reconsider. The longest side is 6.
# So max(a,b,c) = 6 and a+b+c=12
# Without loss of generality, let c=6 be the longest.
# Then a + b = 6, with a <= 6, b <= 6, and a,b >= 1
# Triangle inequality requires: a + b > c, a + c > b, b + c > a
# a + b > 6 => 6 > 6 => FALSE

# So there are NO non-degenerate triangles with perimeter 12 and longest side 6.
# Wait, let me double check by enumerating all possibilities.

count = 0
results = []
for a in range(1, 13):
    for b in range(1, 13):
        for c in range(1, 13):
            if a + b + c == 12:
                # Check non-degenerate triangle inequality
                if a + b > c and a + c > b and b + c > a:
                    # Check longest side is 6
                    if max(a, b, c) == 6:
                        count += 1
                        results.append((a, b, c))

print(f'Found {count} triangles: {results}')
if count == 0:
    print('No such triangle exists')
else:
    for a, b, c in results:
        # Product of the other two sides (not the longest)
        sides = sorted([a, b, c])
        # Longest is sides[2] = 6
        # Other two are sides[0] and sides[1]
        product = sides[0] * sides[1]
        print(f'Sides: {a}, {b}, {c} -> product of other two: {product}')
" > /dev/null 2>&1

# Let me just run it directly
python3 -c "
count = 0
results = []
for a in range(1, 13):
    for b in range(1, 13):
        for c in range(1, 13):
            if a + b + c == 12:
                if a + b > c and a + c > b and b + c > a:
                    if max(a, b, c) == 6:
                        count += 1
                        results.append((a, b, c))

print(f'Found {count} triangles: {results}')
if count == 0:
    print('IMPOSSIBLE')
else:
    for a, b, c in results:
        sides = sorted([a, b, c])
        product = sides[0] * sides[1]
        print(f'Sides: {a}, {b}, {c} -> product: {product}')
"