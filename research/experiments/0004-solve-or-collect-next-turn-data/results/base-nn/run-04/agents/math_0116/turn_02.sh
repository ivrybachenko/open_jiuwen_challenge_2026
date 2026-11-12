python3 -c "
# Let's carefully enumerate all integer triangles with perimeter 12
# and check which have longest side = 6

count = 0
results = []
for a in range(1, 13):
    for b in range(1, 13):
        for c in range(1, 13):
            if a + b + c == 12:
                # Non-degenerate: strict triangle inequality
                if a + b > c and a + c > b and b + c > a:
                    if max(a, b, c) == 6:
                        count += 1
                        results.append((a, b, c))

print(f'Found {count} triangles: {results}')
if count == 0:
    print('No such triangle exists')
else:
    for a, b, c in results:
        sides = sorted([a, b, c])
        product = sides[0] * sides[1]
        print(f'Sides: {a}, {b}, {c} -> product of other two: {product}')
"