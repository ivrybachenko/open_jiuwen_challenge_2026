```bash
python3 -c "
# We need to find integer side lengths a, b, c of a non-degenerate triangle
# such that:
# 1. a + b + c = 12 (perimeter)
# 2. max(a, b, c) = 6 (longest side is 6)
# 3. Triangle inequality: a + b > c, a + c > b, b + c > a
# 4. Non-degenerate means strict inequality holds

# Since the longest side is 6, let's say c = 6 (or one of the sides is 6 and it's the max)
# Then a + b = 12 - 6 = 6
# And we need a, b to be positive integers with a <= 6, b <= 6, and at least one of them could be 6 but the max is 6.
# Also triangle inequality: a + b > 6 => 6 > 6 which is FALSE.

# Wait, let me reconsider. If the longest side is 6, then c = 6 and a, b <= 6.
# a + b = 6
# For non-degenerate triangle: a + b > c => 6 > 6 which is false.
# So no such triangle exists?

# Let me check if there's another interpretation. Maybe the longest side is 6 but it's not unique?
# If two sides are 6: a=6, b=6, c=0? No, c must be positive.
# a=6, b=6, c=0 is degenerate and c=0 is not positive.

# Let's try a=6, b=5, c=1: perimeter=12, longest=6. Check: 5+1=6 which is not > 6. Degenerate.
# a=6, b=4, c=2: 4+2=6 not > 6. Degenerate.
# a=6, b=3, c=3: 3+3=6 not > 6. Degenerate.

# Hmm, it seems like no non-degenerate triangle exists with perimeter 12 and longest side 6.

# Wait, let me re-read. 'longest side is 6'. This means the maximum side length is 6.
# For a non-degenerate triangle with integer sides and perimeter 12:
# Possible triangles (sorted a <= b <= c):
# a + b + c = 12, a <= b <= c, a + b > c

# Let's enumerate:
# c can be at most 5 (since if c=6, a+b=6, need a+b>6, impossible)
# If c=5: a+b=7, a<=b<=5. Pairs: (2,5), (3,4)
#   (2,5,5): 2+5>5=7>5 yes. Non-degenerate. Longest=5, not 6.
#   (3,4,5): 3+4>5=7>5 yes. Non-degenerate. Longest=5, not 6.

# If c=4: a+b=8, a<=b<=4. Pairs: (4,4)
#   (4,4,4): equilateral. Longest=4.

# So no triangle with longest side 6 exists that is non-degenerate.

# But wait, the problem says 'A non-degenerate triangle has integer side lengths. Its perimeter is 12 and its longest side is 6.'
# This seems contradictory. Let me double-check.

# Actually, I think the issue is that with perimeter 12 and longest side 6, we get a degenerate triangle.
# The problem might be testing if we recognize this, or there might be an error.

# Let me re-read: 'What is the product of the lengths of the other two sides?'
# If we consider the degenerate case a=3, b=3, c=6: product = 9.
# But it says non-degenerate.

# Hmm, let me check if I'm missing something. What if the sides are not ordered?
# The longest side is 6. So one side is 6, and the other two sum to 6.
# For non-degenerate: sum of other two > 6, but they sum to 6. Contradiction.

# I'll write IMPOSSIBLE.
print('IMPOSS