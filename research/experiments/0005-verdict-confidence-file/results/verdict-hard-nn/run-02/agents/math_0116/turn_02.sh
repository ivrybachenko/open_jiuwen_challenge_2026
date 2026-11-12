python3 -c "
# Find integer sides a, b, c of a non-degenerate triangle
# Perimeter = 12, longest side = 6
# a + b + c = 12, max(a,b,c) = 6, a,b,c >= 1 integers
# Non-degenerate: triangle inequality strict

# Since longest side is 6, let c = 6 (WLOG, c is the max)
# Then a + b = 6, with 1 <= a <= b <= 6
# Triangle inequality: a + b > c => 6 > 6 => FALSE
# So no non-degenerate triangle exists with these constraints.

# But wait - let me check if the problem might allow the longest side to be 6
# but not necessarily unique. Even if two sides are 6:
# a=6, b=6, c=0: c=0 not positive, invalid.
# a=6, b=5, c=1: 5+1=6 not > 6, degenerate.
# a=6, b=4, c=2: 4+2=6 not > 6, degenerate.
# a=6, b=3, c=3: 3+3=6 not > 6, degenerate.

# All cases with longest side 6 and perimeter 12 are degenerate.
# The problem states 'non-degenerate', so this is impossible.

print('IMPOSSIBLE')
" > answer.txt

echo "IMPOSSIBLE" > answer.txt
echo "impossible" > verdict.txt
echo "0.95" >> verdict.txt
echo "No non-degenerate triangle exists with perimeter 12 and longest side 6" >> verdict.txt