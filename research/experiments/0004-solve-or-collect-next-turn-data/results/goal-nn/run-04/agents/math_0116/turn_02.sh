python3 -c "
# Find integer triangles with perimeter 12 and longest side 6
# Sides a, b, c where a <= b <= c, c = 6, a + b + c = 12
# So a + b = 6, with 1 <= a <= b <= 6
# Triangle inequality for non-degenerate: a + b > c, i.e., 6 > 6, which is FALSE
# This means no non-degenerate triangle exists with these constraints.

# However, let me double-check by enumerating all possibilities:
solutions = []
for a in range(1, 7):
    for b in range(a, 7):
        c = 6  # longest side is 6
        if a + b + c == 12 and a <= b <= c:
            # Check triangle inequality: a + b > c, a + c > b, b + c > a
            if a + b > c and a + c > b and b + c > a:
                solutions.append((a, b, c))

if solutions:
    for s in solutions:
        print(f'Found: {s}, product of other two sides = {s[0] * s[1]}')
else:
    print('No non-degenerate triangle found')
    # The problem might have an error, but let's see if there's a common interpretation
    # Perhaps they mean the longest side is at most 6? Let's check all triangles with perimeter 12
    all_triangles = []
    for a in range(1, 12):
        for b in range(a, 12):
            for c in range(b, 12):
                if a + b + c == 12 and a + b > c:
                    all_triangles.append((a, b, c))
    print(f'All non-degenerate triangles with perimeter 12: {all_triangles}')
    for t in all_triangles:
        print(f'  {t}, product of two shorter sides = {t[0] * t[1]}, longest = {t[2]}')
" > /tmp/triangle_check.txt 2>&1
cat /tmp/triangle_check.txt