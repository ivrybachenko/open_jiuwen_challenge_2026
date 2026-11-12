python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3; keep if 4, 5, or 6.
# Expected value of a single roll = 3.5
# If we keep (4,5,6), expected value = (4+5+6)/3 = 5
# If we reroll (1,2,3), expected value = 3.5
# Overall expected value = (3/6)*5 + (3/6)*3.5 = 2.5 + 1.75 = 4.25 = 17/4

from fractions import Fraction

# Probability of keeping: 3/6 = 1/2, expected value when keeping: 5
# Probability of rerolling: 3/6 = 1/2, expected value when rerolling: 7/2

ev_keep = Fraction(4+5+6, 3)  # 5
ev_reroll = Fraction(7, 2)    # 3.5
prob_keep = Fraction(3, 6)    # 1/2
prob_reroll = Fraction(3, 6)  # 1/2

total_ev = prob_keep * ev_keep + prob_reroll * ev_reroll

print(total_ev)
print(f'{total_ev.numerator}/{total_ev.denominator}')
" > /dev/null

python3 -c "
from fractions import Fraction
ev_keep = Fraction(4+5+6, 3)
ev_reroll = Fraction(7, 2)
prob_keep = Fraction(3, 6)
prob_reroll = Fraction(3, 6)
total_ev = prob_keep * ev_keep + prob_reroll * ev_reroll
with open('answer.txt', 'w') as f:
    f.write(f'{total_ev.numerator}/{total_ev.denominator}\n')
"

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Optimal expected value is 17/4" >> verdict.txt