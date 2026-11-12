python3 -c "
boxes = 1669
boxes -= 36 * 3
boxes += 2 * 87
print(boxes)
" > answer.txt
cat answer.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Simple arithmetic: 1669 - 108 + 174 = 1735" >> verdict.txt