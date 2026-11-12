python3 -c "
# Find all integer triangles with perimeter 12 and longest side 6
# Sides a, b, c with a <= b <= c, c = 6, a + b + c = 12
# So a + b = 6, and we need a + b > c for non-degenerate triangle
# i.e., 6 > 6 which is FALSE. So no non-degenerate triangle exists?
# 
# Wait, let me reconsider. The problem says 'longest side is 6'.
# This means max(a,b,c) = 6.
# a + b + c = 12
# 
# Let's enumerate all possible integer triples:
solutions = []
for a in range(1, 12):
    for b in range(a, 12):
        c = 12 - a - b
        if c < b:
            continue
        if c < 1:
            continue
        # Check triangle inequality: a + b > c, a + c > b, b + c > a
        if a + b > c and a + c > b and b + c > a:
            if max(a, b, c) == 6:
                solutions.append((a, b, c))

print('Valid triangles with perimeter 12 and longest side 6:', solutions)

if solutions:
    for s in solutions:
        # The longest side is 6. The other two sides are the remaining ones.
        # Since we sorted a <= b <= c and c=6, the other two are a and b.
        product = s[0] * s[1]
        print(f'Sides: {s}, product of other two: {product}')
else:
    print('No solution found')
" > /dev/null 2>&1

# Let me just compute directly
python3 << 'PYEOF'
solutions = []
for a in range(1, 12):
    for b in range(a, 12):
        c = 12 - a - b
        if c < b:
            continue
        if c < 1:
            continue
        if a + b > c and a + c > b and b + c > a:
            if max(a, b, c) == 6:
                solutions.append((a, b, c))

if solutions:
    for s in solutions:
        product = s[0] * s[1]
        print(product)
else:
    print("NO SOLUTION")
PYEOF