```bash
python3 -c "
# Triangle with integer sides, perimeter 12, longest side 6
# Let sides be a, b, c where c=6 is the longest side
# a + b + c = 12 => a + b = 6
# Triangle inequality: a + b > c => 6 > 6 is false!
# Wait, let me reconsider.

# For a non-degenerate triangle, we need strict triangle inequality.
# If longest side is 6, and perimeter is 12, then a + b = 6.
# Triangle inequality requires a + b > 6 (since c=6 is the longest).
# But a + b = 6, so a + b > 6 is false.
# This means no such non-degenerate triangle exists?

# Let me re-read: 'longest side is 6'. This means max(a,b,c) = 6.
# a + b + c = 12, c = 6 (wlog, c is longest)
# a + b = 6
# Triangle inequality: a + b > c => 6 > 6 => False

# Hmm, but wait - maybe I should check all possibilities more carefully.
# Let's enumerate all integer triples with perimeter 12 and max side 6.

solutions = []
for a in range(1, 13):
    for b in range(1, 13):
        for c in range(1, 13):
            if a + b + c == 12 and max(a, b, c) == 6:
                # Check triangle inequality
                if a + b > c and a + c > b and b + c > a:
                    solutions.append((a, b, c))

print('Solutions:', solutions)
if solutions:
    for s in solutions:
        # Find the two sides that are not the longest (6)
        sides = sorted(s)
        other_two = [sides[0], sides[1]]  # These are the non-longest if longest is unique
        # Actually, we need the product of the other two sides (not the longest one)
        # The longest side is 6, so the other two are the remaining ones
        product = 1
        for side in s:
            if side != 6:
                product *= side
            else:
                # If there are multiple 6s, we only exclude one 6
                # But we need to be careful
                pass
        # Better: sort and take first two
        print(f'Sides: {s}, other two: {sides[0]}, {sides[1]}, product: {sides[0] * sides[1]}')
else:
    print('No valid triangle found')
" > /dev/null 2>&1

# Let me think again more carefully
# If perimeter = 12 and longest side = 6:
# a + b + 6 = 12, so a + b = 6
# For non-degenerate triangle: a + b > 6, but a + b = 6, so this fails.
# UNLESS... the problem allows degenerate? No, it says "non-degenerate".

# Wait, let me re-check. Maybe I'm misunderstanding "longest side is 6".
# Perhaps it means the longest side has length 6, but there could be ties.
# E.g., (6, 6, 0) - but 0 is not a valid side length.
# (6, 5, 1): 6+5+1=12, max=6. Triangle: 5+1=6, not > 6. Degenerate.
# (6, 4, 2): 4+2=6, not > 6. Degenerate.
# (6, 3, 3): 3+3=6, not > 6. Degenerate.

# So indeed, no non-degenerate triangle exists with these constraints.
# But the problem asks for a product, implying a solution exists.

# Let me re-read: "Its perimeter is 12 and its longest side is 6"
# Maybe I should consider that the triangle inequality is a + b >= c for degenerate,
# but non-degenerate means strict inequality.

# Actually wait - let me reconsider. What if the sides are (5, 5, 2)?
# Perimeter = 12, longest side = 5, not