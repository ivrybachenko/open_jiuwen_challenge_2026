python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3 (since expected value of a die roll is 3.5)
# If first roll is 4, 5, or 6, keep it.
# Expected value = P(keep) * E[keep | keep] + P(reroll) * E[reroll]
# P(keep) = 3/6 = 1/2, E[keep | keep] = (4+5+6)/3 = 5
# P(reroll) = 3/6 = 1/2, E[reroll] = 3.5 = 7/2
# EV = (1/2)*5 + (1/2)*(7/2) = 5/2 + 7/4 = 10/4 + 7/4 = 17/4

from fractions import Fraction

# First roll outcomes
ev = Fraction(0)
for i in range(1, 7):
    if i >= 4:
        # Keep the result
        ev += Fraction(i, 6)
    else:
        # Reroll, expected value of reroll is 3.5 = 7/2
        ev += Fraction(7, 2) * Fraction(1, 6)

print(ev)
print(ev.numerator, ev.denominator)
" > /dev/null

python3 -c "
from fractions import Fraction
ev = Fraction(0)
for i in range(1, 7):
    if i >= 4:
        ev += Fraction(i, 6)
    else:
        ev += Fraction(7, 2) * Fraction(1, 6)
print(ev)
" > answer.txt