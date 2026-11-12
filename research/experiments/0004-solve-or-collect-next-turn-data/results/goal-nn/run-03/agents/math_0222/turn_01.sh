python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3 (i.e., <= 3)
# Expected value of a single die roll is 3.5
# If first roll > 3 (i.e., 4, 5, 6), keep it
# If first roll <= 3, reroll and take expected value 3.5

# P(keep) = 3/6 = 1/2, average of kept values = (4+5+6)/3 = 5
# P(reroll) = 3/6 = 1/2, expected value of reroll = 3.5

# E = (1/2)*5 + (1/2)*3.5 = 2.5 + 1.75 = 4.25 = 17/4

from fractions import Fraction

# Compute exactly
ev = Fraction(0)
for first in range(1, 7):
    p_first = Fraction(1, 6)
    if first > 3:
        # Keep first roll
        ev += p_first * first
    else:
        # Reroll, expected value of reroll is 3.5 = 7/2
        ev += p_first * Fraction(7, 2)

print(ev)
print(f'{ev.numerator}/{ev.denominator}')
" > answer.txt