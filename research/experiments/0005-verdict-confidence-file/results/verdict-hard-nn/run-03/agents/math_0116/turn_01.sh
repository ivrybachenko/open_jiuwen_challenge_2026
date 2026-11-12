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
                if a + b > c and a + c > b and b + c > a:
                    solutions.append((a, b, c))

if solutions:
    for sol in solutions:
        print(f'Solution: {sol}, product of other two sides: {sol[0] * sol[1]}')
else:
    print('No non-degenerate triangle found with perimeter 12 and longest side 6')
    print('This is because a + b = 6 = c, so a + b = c, which is degenerate')
" > answer.txt 2>&1
cat answer.txt
echo "not_solved" > verdict.txt
echo "0.00" >> verdict.txt
echo "No non-degenerate triangle exists with perimeter 12 and longest side 6" >> verdict.txt