cat > program.py << 'EOF'
import sys

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def main():
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        s1 = lines[0]
        s2 = lines[1]
    else:
        # Try reading from command line args if stdin is empty
        args = sys.argv[1:]
        if len(args) >= 2:
            s1 = args[0]
            s2 = args[1]
        else:
            print("Error: Need two strings", file=sys.stderr)
            sys.exit(1)
    
    distance = levenshtein(s1, s2)
    print(distance)

if __name__ == "__main__":
    main()
EOF

echo "DONE" > answer.txt