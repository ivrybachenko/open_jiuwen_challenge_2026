cat > program.py << 'EOF'
import sys

def levenshtein(s1, s2):
    m = len(s1)
    n = len(s2)
    
    # Create a matrix to store distances
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill in the rest of the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # deletion
                    dp[i][j-1],    # insertion
                    dp[i-1][j-1]   # substitution
                )
    
    return dp[m][n]

def main():
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        s1 = lines[0]
        s2 = lines[1]
    else:
        # Handle case where there might be fewer lines
        if len(lines) == 1:
            s1 = lines[0]
            s2 = ""
        else:
            s1 = ""
            s2 = ""
    
    distance = levenshtein(s1, s2)
    print(distance)

if __name__ == "__main__":
    main()
EOF

echo "DONE" > answer.txt