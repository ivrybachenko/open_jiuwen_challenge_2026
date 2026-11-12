python3 -c "
# Find all integer triangles with perimeter 12 and longest side 6
# Let sides be a, b, c where a <= b <= c and c = 6
# a + b + c = 12 => a + b = 6
# Triangle inequality: a + b > c => 6 > 6 is false!
# Wait, let me re-check.
# For a non-degenerate triangle, we need strict inequality: a + b > c
# If c = 6 and a + b = 6, then a + b = c, which means degenerate triangle.
# So there are no non-degenerate triangles with perimeter 12 and longest side 6?
# Let me verify by checking all possibilities.

solutions = []
for a in range(1, 13):
    for b in range(a, 13):
        for c in range(b, 13):
            if a + b + c == 12 and c == 6:
                # Check triangle inequality: a + b > c, a + c > b, b + c > a
                if a + b > c and a + c > b and b + c > a:
                    solutions.append((a, b, c))

if solutions:
    for s in solutions:
        print(f'Found: {s}, product of other two sides: {s[0]*s[1]}')
    # Take the first one (should be unique)
    print(solutions[0][0] * solutions[0][1])
else:
    print('No non-degenerate triangle found')
    print('IMPOSSIBLE')
" > answer.txt 2>&1
cat answer.txt