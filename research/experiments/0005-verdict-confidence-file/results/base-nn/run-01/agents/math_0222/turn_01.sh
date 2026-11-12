python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3 (since expected value of a die is 3.5)
# If first roll is 4, 5, or 6, keep it.
# E = (1/6)*(E[second roll] + E[second roll] + E[second roll] + 4 + 5 + 6)
# E[second roll] = 3.5 = 7/2
# E = (1/6)*(3*3.5 + 4 + 5 + 6) = (1/6)*(10.5 + 15) = (1/6)*25.5 = 25.5/6 = 51/12 = 17/4

from fractions import Fraction

# Expected value of one die roll
e_one_roll = Fraction(21, 6)  # 3.5

# Strategy: reroll if roll < 4 (i.e., 1, 2, 3), keep if roll >= 4 (i.e., 4, 5, 6)
# P(reroll) = 3/6 = 1/2, in which case we get e_one_roll
# P(keep) = 3/6 = 1/2, average of 4,5,6 = 5
# E = (1/2)*e_one_roll + (1/2)*5

e_optimal = Fraction(1, 2) * e_one_roll + Fraction(1, 2) * 5

print(e_optimal)
print(f'{e_optimal.numerator}/{e_optimal.denominator}')
" > answer.txt