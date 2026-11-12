python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3; keep if 4, 5, or 6.
# Expected value of a single roll = 3.5
# If we keep (4,5,6), expected value = (4+5+6)/3 = 5
# If we reroll (1,2,3), expected value = 3.5
# Overall expected value = (3/6)*5 + (3/6)*3.5 = 2.5 + 1.75 = 4.25 = 17/4

from fractions import Fraction

# Strategy: reroll if roll <= 3, keep if roll >= 4
# P(keep) = 3/6, E[keep | keep] = (4+5+6)/3 = 5
# P(reroll) = 3/6, E[reroll] = 3.5 = 7/2

ev_keep = Fraction(4+5+6, 3)  # 5
ev_reroll = Fraction(7, 2)   # 3.5

# Total EV = P(keep)*ev_keep + P(reroll)*ev_reroll
ev = Fraction(3, 6) * ev_keep + Fraction(3, 6) * ev_reroll

print(ev)
print(f'{ev.numerator}/{ev.denominator}')
" > answer.txt

cat answer.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Optimal expected value is 17/4" >> verdict.txt