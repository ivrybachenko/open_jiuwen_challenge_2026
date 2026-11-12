python3 -c "
# Find all integer triangles with perimeter 12 and longest side 6
# Let sides be a, b, c where a <= b <= c and c = 6
# a + b + c = 12 => a + b = 6
# Triangle inequality: a + b > c => 6 > 6 is false!
# Wait, let me re-check.
# For a non-degenerate triangle, we need strict inequality: a + b > c
# If c = 6 and a + b = 6, then a + b = c, which means degenerate triangle.
# Let me check if there are any valid triangles.

# Actually, let me reconsider. The problem says longest side is 6.
# So c = 6, and a <= b <= 6, and a + b + 6 = 12, so a + b = 6.
# Triangle inequality requires a + b > c, i.e., 6 > 6, which is false.
# So no non-degenerate triangle exists with perimeter 12 and longest side 6.

# Wait, let me double-check by enumerating all possibilities.
count = 0
results = []
for a in range(1, 7):
    for b in range(a, 7):
        c = 6  # longest side is 6
        if a + b + c == 12 and a <= b <= c:
            if a + b > c and a + c > b and b + c > a:
                count += 1
                results.append((a, b, c))

if count == 0:
    print('No non-degenerate triangle exists')
    print('IMPOSSIBLE')
else:
    for a, b, c in results:
        print(f'Sides: {a}, {b}, {c}, Product of other two: {a * b}')
" > /dev/null 2>&1

# Let me actually run it properly
python3 -c "
count = 0
results = []
for a in range(1, 7):
    for b in range(a, 7):
        c = 6
        if a + b + c == 12 and a <= b <= c:
            if a + b > c and a + c > b and b + c > a:
                count += 1
                results.append((a, b, c))

if count == 0:
    print('IMPOSSIBLE')
else:
    for a, b, c in results:
        print(f'Sides: {a}, {b}, {c}, Product: {a * b}')
"