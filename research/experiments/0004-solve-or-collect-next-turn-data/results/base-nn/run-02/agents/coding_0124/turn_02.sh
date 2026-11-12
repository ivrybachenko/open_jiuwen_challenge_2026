cat > dial.py << 'EOF'
_counter = 0

def advance():
    global _counter
    _counter += 1
    return _counter
EOF

python3 test_dial.py
echo DONE > answer.txt