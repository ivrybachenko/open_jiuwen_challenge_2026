python3 -c "
# A non-degenerate triangle has integer side lengths.
# Perimeter = 12, longest side = 6.
# Let sides be a, b, c with a <= b <= c = 6.
# a + b + 6 = 12 => a + b = 6.
# For non-degenerate triangle: a + b > c => 6 > 6, which is FALSE.
# So no non-degenerate triangle exists with these constraints.
# But wait - let me double-check by enumerating all possible integer triangles with perimeter 12.

solutions = []
for a in range(1, 13):
    for b in range(a, 13):
        c = 12 - a - b
        if c < b:
            continue
        if c < 1:
            continue
        # Check triangle inequality: a + b > c, a + c > b, b + c > a
        if a + b > c and a + c > b and b + c > a:
            solutions.append((a, b, c))

print('All non-degenerate integer triangles with perimeter 12:')
for a, b, c in solutions:
    print(f'  ({a}, {b}, {c}), longest={max(a,b,c)}, product of other two={a*b if c==max(a,b,c) else (a*c if b==max(a,b,c) else b*c)}')

# Check if any have longest side = 6
found = False
for a, b, c in solutions:
    if max(a, b, c) == 6:
        print(f'Found: ({a}, {b}, {c})')
        found = True

if not found:
    print('No triangle with perimeter 12 has longest side exactly 6.')
    print('IMPOSSIBLE')
" > /dev/null 2>&1

python3 -c "
solutions = []
for a in range(1, 13):
    for b in range(a, 13):
        c = 12 - a - b
        if c < b:
            continue
        if c < 1:
            continue
        if a + b > c and a + c > b and b + c > a:
            solutions.append((a, b, c))

print('All non-degenerate integer triangles with perimeter 12:')
for a, b, c in solutions:
    print(f'  ({a}, {b}, {c}), longest={max(a,b,c)}')

found = False
for a, b, c in solutions:
    if max(a, b, c) == 6:
        print(f'Found: ({a}, {b}, {c})')
        found = True

if not found:
    print('No triangle with perimeter 12 has longest side exactly 6.')
"