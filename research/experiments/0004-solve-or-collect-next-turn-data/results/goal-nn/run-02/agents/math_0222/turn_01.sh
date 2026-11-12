python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3 (since expected value of a die roll is 3.5)
# If first roll is 4, 5, or 6, keep it.
# E = (1/6)*(E[second roll] + E[second roll] + E[second roll] + 4 + 5 + 6)
# E[second roll] = 3.5 = 7/2
# E = (1/6)*(3*3.5 + 4 + 5 + 6) = (1/6)*(10.5 + 15) = (1/6)*25.5 = 25.5/6 = 51/12 = 17/4

from fractions import Fraction

# Expected value of one die roll
e_one_roll = Fraction(21, 6)  # 3.5

# Strategy: reroll if roll <= 3, keep if roll >= 4
# E = (1/6) * [E[reroll] for 1,2,3] + (1/6)*[4,5,6]
# E = (3/6)*e_one_roll + (1/6)*(4+5+6)
# E = (1/2)*e_one_roll + (1/6)*15
# E = (1/2)*(7/2) + 15/6
# E = 7/4 + 5/2 = 7/4 + 10/4 = 17/4

e_optimal = Fraction(3, 6) * e_one_roll + Fraction(1, 6) * (4 + 5 + 6)
print(e_optimal)
print(f'{e_optimal.numerator}/{e_optimal.denominator}')
" > answer.txt