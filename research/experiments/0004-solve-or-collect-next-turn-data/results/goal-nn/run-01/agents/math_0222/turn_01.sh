python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3 (since expected value of a die roll is 3.5)
# If first roll is 4, 5, or 6, keep it.
# E = (1/6)*(E[second roll] + E[second roll] + E[second roll] + 4 + 5 + 6)
# E[second roll] = 3.5 = 7/2
# E = (1/6)*(3*3.5 + 4 + 5 + 6) = (1/6)*(10.5 + 15) = (1/6)*25.5 = 25.5/6 = 51/12 = 17/4

from fractions import Fraction

# Expected value of one die roll
e_one_roll = Fraction(21, 6)  # 3.5

# Strategy: reroll if roll < 4 (i.e., 1, 2, 3), keep if roll >= 4 (i.e., 4, 5, 6)
# P(reroll) = 3/6 = 1/2, in which case we get e_one_roll
# P(keep) = 3/6 = 1/2, in which case we get average of 4,5,6 = 5

# E = (1/2) * e_one_roll + (1/2) * 5
# E = (1/2) * (7/2) + (1/2) * 5 = 7/4 + 5/2 = 7/4 + 10/4 = 17/4

result = Fraction(1, 2) * e_one_roll + Fraction(1, 2) * Fraction(15, 3)  # avg of 4,5,6 is 5
# Let me recalculate more carefully

# Direct computation:
# For each first roll r:
# if r <= 3: expected value = E[second roll] = 7/2
# if r >= 4: expected value = r
# E = (1/6) * (7/2 + 7/2 + 7/2 + 4 + 5 + 6)
# E = (1/6) * (21/2 + 15) = (1/6) * (21/2 + 30/2) = (1/6) * (51/2) = 51/12 = 17/4

e = Fraction(51, 12)
print(e)
print(e.numerator, e.denominator)

with open('answer.txt', 'w') as f:
    f.write(f'{e.numerator}/{e.denominator}\n')
"