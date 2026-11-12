python3 -c "
# Find all non-degenerate integer triangles with perimeter 12 and longest side 6
# Let sides be a, b, c with a <= b <= c and c = 6 (longest side)
# a + b + c = 12 => a + b = 6
# Triangle inequality: a + b > c => 6 > 6 => FALSE
# So no non-degenerate triangle exists with these constraints.

# But let's verify by enumerating all integer triangles with perimeter 12:
results = []
for a in range(1, 13):
    for b in range(a, 13):
        c = 12 - a - b
        if c < b:
            continue
        if c < 1:
            continue
        if a + b > c:  # non-degenerate
            results.append((a, b, c))

print('All non-degenerate integer triangles with perimeter 12:', results)

# Check if any has longest side 6
found = False
for t in results:
    if max(t) == 6:
        print(f'Found: {t}')
        # Product of the other two sides (not the longest)
        other_sides = [x for x in t if x != 6]
        if len(other_sides) == 2:
            print(f'Product: {other_sides[0] * other_sides[1]}')
        else:
            # Both other sides equal 6, but that can't happen since a<=b<=c=6 and a+b=6
            pass
        found = True

if not found:
    print('No non-degenerate triangle with perimeter 12 and longest side 6 exists.')
    print('IMPOSSIBLE')
"

# Based on the math: a+b=6 and a+b>6 is required, which is impossible.
# The problem may have an error, or I need to reconsider.
# Let me check: maybe "longest side is 6" allows for multiple sides of length 6?
# If a=3, b=3, c=6: a+b=6, not >6, so degenerate.
# If a=2, b=4, c=6: a+b=6, not >6, degenerate.
# If a=1, b=5, c=6: a+b=6, not >6, degenerate.
# All cases with c=6 and a+b=6 are degenerate.

# The only non-degenerate triangles with perimeter 12 are:
# (3,4,5): longest side 5
# (4,4,4): longest side 4

# Neither has longest side 6. So the answer is IMPOSSIBLE.

echo "IMPOSSIBLE" > answer.txt