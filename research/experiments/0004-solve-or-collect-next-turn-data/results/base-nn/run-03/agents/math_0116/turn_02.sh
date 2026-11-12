python3 -c "
# Let's carefully enumerate all integer triangles with perimeter 12
# and longest side exactly 6.
# Sides a, b, c with a <= b <= c, c = 6, a + b + c = 12 => a + b = 6
# Non-degenerate: a + b > c => 6 > 6 => FALSE
# So no non-degenerate triangle exists.

# But wait - let me also check if the problem might allow c to be <= 6
# and just say the longest side IS 6 (meaning at least one side is 6 and it's the max).
# With c=6 as the max, we need a+b=6, a<=b<=6.
# Possible (a,b): (1,5), (2,4), (3,3)
# Check triangle inequality for each:
# (1,5,6): 1+5=6, not > 6 => degenerate
# (2,4,6): 2+4=6, not > 6 => degenerate  
# (3,3,6): 3+3=6, not > 6 => degenerate

# All are degenerate. So the answer is IMPOSSIBLE.
print('IMPOSSIBLE')
" > answer.txt