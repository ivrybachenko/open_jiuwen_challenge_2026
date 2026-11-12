python3 -c "
# Find all non-degenerate triangles with integer sides, perimeter 12, longest side 6
# Let sides be a, b, c where c=6 is the longest side
# a + b + 6 = 12 => a + b = 6
# Non-degenerate triangle: a + b > c, a + c > b, b + c > a
# Since c=6 is longest: a <= 6, b <= 6
# a + b = 6, so a + b > 6 is false... wait, a + b = 6 and c = 6, so a + b = c which is degenerate!
# Let me re-read: non-degenerate means strict triangle inequality
# a + b > c => 6 > 6 is false. So no solution?
# Wait, let me check if c=6 is truly the longest. If a=6, b=6, c=0... no, sides must be positive integers.
# a + b = 6, with a, b >= 1 and a <= 6, b <= 6
# Possible pairs (a,b): (1,5), (2,4), (3,3), (4,2), (5,1)
# For non-degenerate: a + b > c => 6 > 6 is FALSE. So all are degenerate.
# Hmm, but the problem says non-degenerate. Let me re-check.
# Actually, triangle inequality: a + b > c, a + c > b, b + c > a
# With a+b=6 and c=6: a+b=c, so a+b > c fails. These are degenerate (collinear).
# So there are NO non-degenerate triangles with perimeter 12 and longest side 6.
# But the problem asks for the product, implying there is one.
# Let me re-read: 'longest side is 6'. Maybe the longest side is 6 but not necessarily unique?
# Still, a+b=6, c=6, so a+b=c, degenerate.
# Unless... I'm misunderstanding. Let me check if perimeter 12 with longest side 6 can work.
# If sides are 5, 5, 2: perimeter=12, longest=5, not 6.
# If sides are 6, 5, 1: 1+5=6, degenerate.
# If sides are 6, 4, 2: 2+4=6, degenerate.
# If sides are 6, 3, 3: 3+3=6, degenerate.
# All cases with a longest side of 6 and perimeter 12 give degenerate triangles.
# The problem might have an error, or I need to output something. Let me just compute for the 'least degenerate' or check if the problem means something else.
# Actually, wait - maybe 'longest side is 6' means at least one side is 6 and it's the maximum.
# All my cases above have max side 6. And all are degenerate.
# The problem says non-degenerate. This seems impossible.
# Let me just output the product for the case that's closest, or state IMPOSSIBLE.
# But let me double-check: is there any interpretation where this works?
# No, mathematically a+b=c means degenerate.
# I'll write IMPOSSIBLE.
print('IMPOSSIBLE')
" > answer.txt