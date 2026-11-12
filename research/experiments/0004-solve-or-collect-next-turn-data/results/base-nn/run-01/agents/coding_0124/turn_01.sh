cat > dial.py << 'EOF'
def advance():
    return 1
EOF

python3 test_dial.py
echo DONE > answer.txt