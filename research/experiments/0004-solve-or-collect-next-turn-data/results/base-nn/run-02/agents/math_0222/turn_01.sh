python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3; keep if 4, 5, or 6.
# Expected value of a single roll = 3.5
# If we keep, we get the value. If we reroll, we get 3.5.
# So we keep if value > 3.5, i.e., 4, 5, 6.
# P(keep) = 3/6 = 1/2, expected value when keeping = (4+5+6)/3 = 5
# P(reroll) = 3/6 = 1/2, expected value when rerolling = 3.5 = 7/2
# Total expected value = (1/2)*5 + (1/2)*(7/2) = 5/2 + 7/4 = 10/4 + 7/4 = 17/4

from fractions import Fraction

# Strategy: reroll if roll <= 3
# EV = sum over first roll of P(first roll) * max(first roll, EV_of_reroll)
# EV_of_reroll = 3.5 = 7/2

ev_reroll = Fraction(7, 2)
total_ev = Fraction(0, 1)
for i in range(1, 7):
    total_ev += Fraction(1, 6) * max(Fraction(i, 1), ev_reroll)

print(total_ev)
print(total_ev.numerator, total_ev.denominator)
" > /dev/null

python3 -c "
from fractions import Fraction
ev_reroll = Fraction(7, 2)
total_ev = Fraction(0, 1)
for i in range(1, 7):
    total_ev += Fraction(1, 6) * max(Fraction(i, 1), ev_reroll)
with open('answer.txt', 'w') as f:
    f.write(str(total_ev))
"