python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3 (since expected value of a die roll is 3.5)
# If first roll is 4, 5, or 6, keep it.
# Expected value = P(keep) * E[keep | keep] + P(reroll) * E[reroll]
# P(keep) = 3/6 = 1/2, E[keep | keep] = (4+5+6)/3 = 5
# P(reroll) = 3/6 = 1/2, E[reroll] = 3.5 = 7/2
# EV = (1/2)*5 + (1/2)*(7/2) = 5/2 + 7/4 = 10/4 + 7/4 = 17/4

from fractions import Fraction

ev_keep = Fraction(4+5+6, 3)  # 5
ev_reroll = Fraction(21, 6)   # 3.5 = 7/2

# Probability of keeping: 3/6 = 1/2
# Probability of rerolling: 3/6 = 1/2

ev = Fraction(1, 2) * ev_keep + Fraction(1, 2) * ev_reroll

print(ev)
print(ev.numerator, ev.denominator)
" > /dev/null

python3 -c "
from fractions import Fraction
ev = Fraction(1, 2) * Fraction(5, 1) + Fraction(1, 2) * Fraction(7, 2)
print(f'{ev.numerator}/{ev.denominator}')
" > answer.txt