Let me first look at the test file and the dial.py file to understand what needs to be implemented.

$ cat test_dial.py
class T(unittest.TestCase):
    def test_is_integer(self):
        self.assertIs(type(advance()), int)

    def test_one_step_ahead(self):
        value = advance()
        value2 = advance()
        self.assertEqual(value2, value + 1)

if __name__ == '__main__':
    unittest.main()

$ cat dial.py
def advance():
    raise NotImplementedError("advance is not implemented yet")

Now I understand. The `advance()` function needs to:
1. Return an integer
2. Each call should return a value that is 1 greater than the previous call

This is essentially a counter. I need to implement `advance()` so that it returns incrementing integers starting from some value.

Let me implement this:

$ cat > dial.py << 'EOF'
_counter = 0

def advance():
    global _counter
    _counter += 1
    return _counter
EOF

$ python3 test_dial.py

DONE