```bash
python3 -c "
# Find all integer triangles with perimeter 12 and longest side 6
# Let sides be a, b, c where a <= b <= c and c = 6
# a + b + c = 12 => a + b = 6
# Triangle inequality: a + b > c => 6 > 6 is false!
# Wait, let me reconsider.

# For a non-degenerate triangle, we need strict triangle inequality.
# If c = 6 is the longest side, then a + b > c must hold.
# a + b = 12 - 6 = 6
# So we need a + b > 6, but a + b = 6. This means 6 > 6, which is false.

# Hmm, let me re-read the problem. 'longest side is 6'. 
# This means the maximum side length is 6, not that one side is exactly 6 and it's the longest.
# Actually, 'its longest side is 6' means the maximum of the three sides is 6.

# So we need: a, b, c are positive integers, a + b + c = 12, max(a,b,c) = 6, and triangle inequality holds.

# Let's enumerate all possibilities where the longest side is 6.
# Without loss of generality, let c = 6 be the longest side.
# Then a + b = 6, with a <= b <= 6.
# Also need a + b > c for non-degenerate: 6 > 6? No, that's degenerate.

# Wait, maybe the longest side being 6 doesn't mean one side is exactly 6?
# 'its longest side is 6' - this means the maximum side length equals 6.
# So at least one side is 6, and no side exceeds 6.

# If c = 6, a + b = 6, a <= b <= 6.
# For non-degenerate: a + b > c => 6 > 6, impossible.
# So there are NO non-degenerate triangles with perimeter 12 and longest side 6?

# Let me double-check by enumerating all integer triangles with perimeter 12.
count = 0
results = []
for a in range(1, 13):
    for b in range(a, 13):
        c = 12 - a - b
        if c < b:
            continue
        if c < 1:
            continue
        # Check triangle inequality: a + b > c, a + c > b, b + c > a
        if a + b > c and a + c > b and b + c > a:
            max_side = max(a, b, c)
            if max_side == 6:
                count += 1
                results.append((a, b, c))
                print(f'Triangle: {a}, {b}, {c}, product of other two: {a*b if c==6 else (a*c if b==6 else b*c)}')

if count == 0:
    print('No such triangles found')
else:
    print(f'Found {count} triangle(s)')
" > /dev/null 2>&1

# Let me actually run this properly
python3 -c "
results = []
for a in range(1, 13):
    for b in range(a, 13):
        c = 12 - a - b
        if c < b:
            continue
        if c < 1:
            continue
        if a + b > c and a + c > b and b + c > a:
            max_side = max(a, b, c)
            if max_side == 6:
                results.append((a, b, c))

if len(results) == 0:
    print('IMPOSSIBLE: No non-degenerate triangle with perimeter 12 and longest side 6 exists')
    print('Because if longest side is 6, other two sum to 6, and 6 > 6 is false')
else:
    for (a, b, c) in results:
        if c == 6:
            prod = a * b
        elif b == 6:
            prod = a * c
        else:
            prod = b * c
        print(f'Triangle: {a}, {b}, {c}, product: {prod}')