python3 -c "
# A non-degenerate triangle has integer side lengths.
# Perimeter = 12, longest side = 6.
# Let sides be a, b, c with a <= b <= c and c = 6.
# a + b + c = 12 => a + b = 6.
# Triangle inequality requires a + b > c for non-degenerate.
# But a + b = 6 and c = 6, so a + b = c, which is degenerate.
# Therefore, no non-degenerate triangle exists with these constraints.
print('IMPOSSIBLE')
" > answer.txt

cat answer.txt