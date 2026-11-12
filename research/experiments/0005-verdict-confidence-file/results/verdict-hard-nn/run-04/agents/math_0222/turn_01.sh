python3 -c "
# Optimal strategy: reroll if first roll is 1, 2, or 3; keep if 4, 5, or 6.
# Expected value of a single roll = 3.5 = 7/2
# P(keep) = 3/6 = 1/2, expected value given keep = (4+5+6)/3 = 5
# P(reroll) = 3/6 = 1/2, expected value given reroll = 3.5 = 7/2
# Total EV = (1/2)*5 + (1/2)*(7/2) = 5/2 + 7/4 = 10/4 + 7/4 = 17/4

from fractions import Fraction

ev_single = Fraction(7, 2)  # 3.5
ev_keep = Fraction(4+5+6, 3)  # 5
p_keep = Fraction(3, 6)  # 1/2
p_reroll = Fraction(3, 6)  # 1/2

optimal_ev = p_keep * ev_keep + p_reroll * ev_single
print(optimal_ev)
print(f'{optimal_ev.numerator}/{optimal_ev.denominator}')
" > answer.txt
cat answer.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Optimal expected value is 17/4" >> verdict.txt