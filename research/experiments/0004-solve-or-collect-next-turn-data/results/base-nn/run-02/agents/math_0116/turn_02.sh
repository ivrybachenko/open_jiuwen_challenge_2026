python3 -c "
# Re-examine: non-degenerate triangle, integer sides, perimeter 12, longest side 6.
# Let sides be a, b, c with c = 6 being the longest side.
# a + b + c = 12 => a + b = 6
# Non-degenerate triangle requires strict triangle inequalities:
#   a + b > c  => 6 > 6 => FALSE
#   a + c > b  => a + 6 > b
#   b + c > a  => b + 6 > a
# Since a + b = 6, we have b = 6 - a.
# a + 6 > 6 - a => 2a > 0 => a > 0 (true for positive integers)
# 6 - a + 6 > a => 12 > 2a => a < 6
# So a can be 1, 2, 3, 4, 5.
# But a + b > c is required for non-degenerate, and a + b = 6 = c, so a + b > c fails.
# All such triangles are degenerate (the three points are collinear).
# Therefore, no non-degenerate triangle exists with these constraints.
# However, the problem asks for a product, suggesting a valid answer exists.
# Let me reconsider: perhaps 'longest side is 6' doesn't mean c=6 is strictly the longest,
# but that the maximum side length is 6. Same analysis applies.
# Or perhaps I should check if the problem allows degenerate triangles despite saying non-degenerate.
# If degenerate were allowed, possible (a,b,c) with max=6, a+b=6:
# (1,5,6): product of other two = 1*5 = 5
# (2,4,6): product = 2*4 = 8
# (3,3,6): product = 3*3 = 9
# (4,2,6): product = 4*2 = 8
# (5,1,6): product = 5*1 = 5
# But the problem explicitly says non-degenerate.
# Let me check if there's a different interpretation. What if the longest side is NOT 6,
# but the problem says it is? No, the problem is clear.
# 
# Wait - let me re-read: 'Its perimeter is 12 and its longest side is 6.'
# What if there are multiple sides of length 6? e.g., (6, 6, 0) - no, 0 is not positive.
# (6, 5, 1): degenerate as shown.
# (6, 4, 2): degenerate.
# (6, 3, 3): degenerate.
# 
# I'll go with IMPOSSIBLE as the mathematical answer.
print('IMPOSSIBLE')
" > answer.txt