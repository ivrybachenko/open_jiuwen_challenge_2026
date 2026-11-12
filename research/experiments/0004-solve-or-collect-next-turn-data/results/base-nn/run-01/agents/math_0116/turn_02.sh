python3 -c "
# Find all integer triangles with perimeter 12 and longest side 6
# Let sides be a, b, c with a <= b <= c, c = 6 (longest side)
# a + b + c = 12 => a + b = 6
# Triangle inequality: a + b > c => 6 > 6, which is FALSE
# So no non-degenerate triangle exists with these constraints.

# But let me verify by brute force enumeration of all integer triangles with perimeter 12
results = []
for a in range(1, 13):
    for b in range(a, 13):
        c = 12 - a - b
        if c < b:
            continue
        if c < 1:
            continue
        # Check triangle inequality (strict for non-degenerate)
        if a + b > c and a + c > b and b + c > a:
            max_side = max(a, b, c)
            if max_side == 6:
                results.append((a, b, c))

if len(results) == 0:
    print('IMPOSSIBLE')
else:
    for (a, b, c) in results:
        if c == 6:
            prod = a * b
        elif b == 6:
            prod = a * c
        else:
            prod = b * c
        print(f'Triangle: {a}, {b}, {c}, product of other two: {prod}')
" > answer.txt