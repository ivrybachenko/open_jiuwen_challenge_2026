python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3 (i.e., <= 3)
# because the expected value of a single die roll is 3.5.
# If first roll is 4, 5, or 6, keep it.

# Expected value calculation:
# P(keep) = 3/6 = 1/2, and the kept values are 4, 5, 6 with equal probability
# P(reroll) = 3/6 = 1/2, and the expected value of reroll is 3.5

# EV = (1/6)*1 + (1/6)*2 + (1/6)*3 + (1/6)*4 + (1/6)*5 + (1/6)*6
# But with optimal strategy:
# If roll 1, 2, 3: reroll, expected value = 3.5
# If roll 4, 5, 6: keep, value = roll

# EV = (3/6) * 3.5 + (1/6)*4 + (1/6)*5 + (1/6)*6
# EV = (1/2) * 3.5 + (4+5+6)/6
# EV = 1.75 + 15/6
# EV = 1.75 + 2.5 = 4.25 = 17/4

from fractions import Fraction

ev = Fraction(3, 6) * Fraction(7, 2) + Fraction(4, 6) + Fraction(5, 6) + Fraction(6, 6)
print(ev)
print(ev.numerator, ev.denominator)
" > /dev/null

python3 -c "
from fractions import Fraction
ev = Fraction(3, 6) * Fraction(7, 2) + Fraction(4, 6) + Fraction(5, 6) + Fraction(6, 6)
print(ev)
" > answer.txt

cat answer.txt