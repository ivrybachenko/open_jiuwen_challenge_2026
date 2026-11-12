python3 -c "
# Let's re-examine the problem carefully.
# Non-degenerate triangle with integer side lengths.
# Perimeter = 12.
# Longest side = 6.
# Find the product of the other two sides.

# Let sides be a, b, c with a <= b <= c.
# c = 6 (longest side).
# a + b + c = 12 => a + b = 6.
# Non-degenerate: a + b > c => 6 > 6 => FALSE.

# So with c=6 as the strict longest side, no solution.
# But what if there are multiple sides equal to 6?
# If b = 6 and c = 6, then a + 6 + 6 = 12 => a = 0. Not positive.
# If a = 6, b = 6, c = 6, then perimeter = 18. Not 12.

# Let me check: maybe the problem allows the longest side to be 6,
# meaning max(a,b,c) = 6, and we need a non-degenerate triangle.

# For a non-degenerate triangle with integer sides and perimeter 12:
# The triangle inequality requires each side < perimeter/2 = 6.
# So each side must be <= 5.
# But the problem says the longest side is 6.
# This is a contradiction for a non-degenerate triangle.

# Wait, let me re-read: 'non-degenerate' means area > 0, which means strict triangle inequality.
# For perimeter P, each side must be < P/2.
# P = 12, so each side < 6, i.e., side <= 5.
# But longest side = 6 means at least one side = 6.
# 6 is not < 6, so no non-degenerate triangle exists.

# However, let me verify by checking all integer triangles with perimeter 12.
solutions = []
for a in range(1, 13):
    for b in range(a, 13):
        c = 12 - a - b
        if c < b:
            continue
        if c < 1:
            continue
        # Check triangle inequality (non-degenerate: strict)
        if a + b > c and a + c > b and b + c > a:
            solutions.append((a, b, c))

print('All non-degenerate integer triangles with perimeter 12:')
for sol in solutions:
    print(f'  Sides: {sol}, max={max(sol)}')

if not solutions:
    print('No non-degenerate integer triangle with perimeter 12 exists.')
    print('This is because for perimeter 12, each side must be < 6,')
    print('but the problem requires the longest side to be 6.')
    print('The problem as stated has no solution.')
" > /dev/null 2>&1

# Actually, let me reconsider. Perhaps I should check if the problem
# might have a different interpretation. Let me just verify once more
# by checking all possible integer triples.

python3 -c "
# Check all integer triples (a,b,c) with a+b+c=12, a,b,c >= 1
# that form a non-degenerate triangle
found = False
for a in range(1, 12):
    for b in range(1, 12):
        c = 12 - a - b
        if c < 1:
            continue
        # Check non-degenerate triangle inequality
        if a + b > c and a + c > b and b + c > a:
            found = True
            print(f'Found: a={a}, b={b}, c={c}, max={max(a,b,c)}')
            if max(a,b,c) == 6:
                print(f'  -> This matches the condition! Product of other two: {a*b*c / max(a,b,c)}')

if not found:
    print('No non-degenerate integer triangle with perimeter 12.')
"

echo "IMPOSSIBLE" > answer.txt