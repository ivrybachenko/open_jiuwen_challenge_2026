python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3; keep if 4, 5, or 6.
# Expected value of a single roll is 3.5.
# If we keep (prob 3/6), expected value is (4+5+6)/3 = 5.
# If we reroll (prob 3/6), expected value is 3.5.
# Total expected value = (3/6)*5 + (3/6)*3.5 = 2.5 + 1.75 = 4.25 = 17/4

from fractions import Fraction

# Strategy: reroll if roll <= 3, keep if roll >= 4
# E[keep | keep] = (4+5+6)/3 = 5
# E[reroll] = 3.5 = 7/2
# P(keep) = 3/6 = 1/2
# P(reroll) = 3/6 = 1/2

# EV = P(keep) * E[keep | keep] + P(reroll) * E[reroll]
ev = Fraction(1, 2) * 5 + Fraction(1, 2) * Fraction(7, 2)
print(ev)
print(ev.numerator, ev.denominator)

with open('answer.txt', 'w') as f:
    f.write(f'{ev.numerator}/{ev.denominator}\n')
"