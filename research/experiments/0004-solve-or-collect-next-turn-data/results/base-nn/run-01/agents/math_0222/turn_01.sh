python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3 (i.e., <= 3)
# because the expected value of a single die roll is 3.5.
# If first roll is 4, 5, or 6, keep it.

# Expected value calculation:
# P(keep) = 3/6 = 1/2, and the kept values are 4, 5, 6 with equal prob
# P(reroll) = 3/6 = 1/2, and the reroll gives expected value 3.5

# EV = (1/6)*4 + (1/6)*5 + (1/6)*6 + (1/6)*3.5 + (1/6)*3.5 + (1/6)*3.5
# EV = (4+5+6)/6 + 3*(3.5)/6
# EV = 15/6 + 10.5/6
# EV = 25.5/6 = 51/12 = 17/4

from fractions import Fraction

ev = Fraction(0)
for first in range(1, 7):
    if first >= 4:
        ev += Fraction(first) / 6
    else:
        ev += Fraction(3, 2) / 6  # expected value of reroll is 7/2, but we divide by 6 for the first roll prob

print(ev)
print(ev.numerator, ev.denominator)
" > /dev/null

python3 -c "
from fractions import Fraction
ev = Fraction(0)
for first in range(1, 7):
    if first >= 4:
        ev += Fraction(first) / 6
    else:
        ev += Fraction(7, 2) / 6
print(ev)
" > answer.txt