python3 -c "
# Find integer side lengths a, b, c such that:
# a + b + c = 12
# c = 6 (longest side)
# a, b, c form a non-degenerate triangle
# a <= b <= c = 6
# Triangle inequality: a + b > c, a + c > b, b + c > a
# Since c=6 is longest, we need a + b > 6
# Also a + b = 12 - 6 = 6, so a + b = 6
# But we need a + b > 6 for non-degenerate triangle
# Wait, a + b = 6 and c = 6, so a + b = c, which means degenerate triangle!
# Let me re-read: perimeter is 12, longest side is 6.
# a + b + 6 = 12 => a + b = 6
# For non-degenerate triangle: a + b > 6, but a + b = 6, so this is degenerate.
# Hmm, let me check if there's any other interpretation.
# Actually, if a + b = 6 and c = 6, then a + b = c, which is degenerate.
# But the problem says non-degenerate. Let me reconsider.
# Maybe the longest side is not unique? If two sides are 6, then a + 6 + 6 = 12 => a = 0, not valid.
# So the only possibility with c=6 as longest is a+b=6.
# For non-degenerate: a + b > c => 6 > 6, which is false.
# This seems impossible. But wait, let me check all integer triples.

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
            if c == 6:
                solutions.append((a, b, c))

print('Solutions:', solutions)
if solutions:
    for a, b, c in solutions:
        print(f'Product: {a * b}')
else:
    print('No solution found')
" > /dev/null 2>&1

# Let me actually run it and see
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
            if c == 6:
                solutions.append((a, b, c))

print('Solutions:', solutions)
if solutions:
    for a, b, c in solutions:
        print(f'Product: {a * b}')
else:
    print('No solution found')
"