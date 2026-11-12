python3 -c "
# Optimal strategy: reroll if first roll <= 3, keep if first roll >= 4
# Expected value = P(keep) * E[keep | keep] + P(reroll) * E[reroll]
# P(keep) = 3/6 = 1/2, E[keep | keep] = (4+5+6)/3 = 5
# P(reroll) = 3/6 = 1/2, E[reroll] = 3.5 = 7/2
# EV = (1/2)*5 + (1/2)*(7/2) = 5/2 + 7/4 = 10/4 + 7/4 = 17/4

from fractions import Fraction

# Strategy: reroll if roll <= 3
ev = Fraction(0)
for roll in range(1, 7):
    if roll >= 4:
        ev += Fraction(roll, 6)
    else:
        ev += Fraction(3.5, 6)  # expected value of reroll

print(ev)
print(ev.numerator, ev.denominator)
" > /dev/null

python3 -c "
from fractions import Fraction
ev = Fraction(17, 4)
print(ev)
with open('answer.txt', 'w') as f:
    f.write(str(ev))
"