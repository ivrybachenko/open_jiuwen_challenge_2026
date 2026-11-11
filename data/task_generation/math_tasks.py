"""Generate the 34 new math tasks (``math/solvable/0007``..``0040``)."""

from __future__ import annotations

import datetime as dt
import math

from common import create_task


def _task(index: int, task_id: str, instruction: str, reward: int,
          expected, check: str = "exact_int") -> None:
    create_task(
        category="math",
        index=index,
        task_id=task_id,
        instruction=instruction,
        reward=reward,
        check=check,
        expected=str(expected),
    )


def _lcm_many(values: list[int]) -> int:
    result = 1
    for value in values:
        result = math.lcm(result, value)
    return result


def _numbers_divisible(limit: int, divisors: list[int]) -> int:
    total = 0
    for value in range(1, limit + 1):
        if any(value % divisor == 0 for divisor in divisors):
            total += 1
    return total


def _tribonacci(n: int, mod: int) -> int:
    if n < 3:
        return [0, 1, 1][n]
    a, b, c = 0, 1, 1
    for _ in range(3, n + 1):
        a, b, c = b, c, (a + b + c) % mod
    return c


def _digit_sum_count(limit: int, target: int) -> int:
    total = 0
    for value in range(1, limit + 1):
        if sum(map(int, str(value))) == target:
            total += 1
    return total


def _totient_sum(limit: int) -> int:
    phi = list(range(limit + 1))
    for value in range(2, limit + 1):
        if phi[value] == value:
            for multiple in range(value, limit + 1, value):
                phi[multiple] -= phi[multiple] // value
    return sum(phi[1:])


def _derangements(n: int) -> int:
    if n == 0:
        return 1
    if n == 1:
        return 0
    a, b = 1, 0
    for k in range(2, n + 1):
        a, b = b, (k - 1) * (a + b)
    return b


def _nim_winning_moves(heaps: list[int]) -> int:
    target = 0
    for heap in heaps:
        target ^= heap
    moves = 0
    for heap in heaps:
        wanted = heap ^ target
        if wanted < heap:
            moves += 1
    return moves


def _look_and_say(term: str) -> str:
    result = []
    index = 0
    while index < len(term):
        digit = term[index]
        end = index
        while end < len(term) and term[end] == digit:
            end += 1
        result.append(str(end - index) + digit)
        index = end
    return "".join(result)


def _base36(number: int) -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    if number == 0:
        return "0"
    parts = []
    while number:
        number, remainder = divmod(number, 36)
        parts.append(digits[remainder])
    return "".join(reversed(parts))


def _primes_below(limit: int) -> int:
    sieve = bytearray(b"\x01") * limit
    sieve[0:2] = b"\x00\x00"
    for value in range(2, int(limit ** 0.5) + 1):
        if sieve[value]:
            sieve[value * value:limit:value] = b"\x00" * len(sieve[value * value:limit:value])
    return sum(index for index, flag in enumerate(sieve) if flag)


def generate() -> None:
    _task(
        7, "math_0201",
        "A notebook costs 17 rubles and a pen costs 9 rubles. You pay with a "
        "50-ruble note and receive exact change. How many rubles is the "
        "change? Compute it with the bash tool (python3 -c). Work only inside "
        "the current directory. When you are done, write ONLY the final "
        "answer to the file answer.txt in the current directory.",
        1, 50 - 17 - 9,
    )
    _task(
        8, "math_0202",
        "A jacket is priced at 80 euros and today it is sold with a 15 percent "
        "discount. What is the final price in euros? Compute it with the bash "
        "tool (python3 -c). Work only inside the current directory. When you "
        "are done, write ONLY the final answer to answer.txt.",
        2, int(80 * 0.85),
    )
    _task(
        9, "math_0203",
        "Three gears have 84, 126 and 210 teeth. A mark on each gear starts at "
        "the same position. What is the smallest positive number of teeth that "
        "must pass before all three marks line up again? Compute it with the "
        "bash tool (python3 -c). Work only inside the current directory. When "
        "you are done, write ONLY the final answer to answer.txt.",
        3, _lcm_many([84, 126, 210]),
    )
    _task(
        10, "math_0204",
        "A cyclist rides 120 km at 60 km/h and then another 90 km at 90 km/h. "
        "What is the average speed in km/h over the whole trip, rounded to the "
        "nearest integer? Compute it with the bash tool (python3 -c). Work "
        "only inside the current directory. When you are done, write ONLY the "
        "final answer to answer.txt.",
        2, round((120 + 90) / (120 / 60 + 90 / 90)),
    )
    _task(
        11, "math_0205",
        "Positive integers x and y satisfy x + y = 11 and 3x + 5y = 47. What is "
        "the value of 2x + 3y? Compute it with the bash tool (python3 -c). "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        3, 2 * 4 + 3 * 7,
    )
    _task(
        12, "math_0206",
        "How many positive divisors does the number 2^3 * 3^4 * 5^2 have? "
        "Compute it with the bash tool (python3 -c). Work only inside the "
        "current directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        2, (3 + 1) * (4 + 1) * (2 + 1),
    )
    weekday = (dt.date(2024, 2, 29) + dt.timedelta(days=100)).strftime("%A")
    _task(
        13, "math_0207",
        "February 29, 2024 was a Thursday. What day of the week is it 100 days "
        "later? Answer with the English day name. Compute it with the bash "
        "tool (python3 -c). Work only inside the current directory. When you "
        "are done, write ONLY the final answer to answer.txt.",
        3, weekday, "exact_str",
    )
    _task(
        14, "math_0208",
        "An analog clock shows 3:40. What is the smaller angle between the hour "
        "hand and the minute hand, in degrees? Compute it with the bash tool "
        "(python3 -c). Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        2, 130,
    )
    _task(
        15, "math_0209",
        "Find the smallest positive integer x such that 17x leaves remainder 1 "
        "when divided by 100. What is x? Compute it with the bash tool "
        "(python3 -c). Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        4, pow(17, -1, 100),
    )
    _task(
        16, "math_0210",
        "A team of 3 people is chosen from a group of 12. In how many of these "
        "teams is at least one of the 5 senior members present? Compute it "
        "with the bash tool (python3 -c). Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        3, math.comb(12, 3) - math.comb(7, 3),
    )
    diophantine_x = min(
        value for value in range(1, 1000)
        if (2 - 240 * value) % 46 == 0
    )
    _task(
        17, "math_0211",
        "There exist integers x and y with 240x + 46y = 2. What is the "
        "smallest positive value of x? Compute it with the bash tool "
        "(python3 -c). Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        5, diophantine_x,
    )
    _task(
        18, "math_0212",
        "How many integers from 1 to 1000 inclusive are divisible by at least "
        "one of 3, 5 and 7? Compute it with the bash tool (python3 -c). Work "
        "only inside the current directory. When you are done, write ONLY the "
        "final answer to answer.txt.",
        4, _numbers_divisible(1000, [3, 5, 7]),
    )
    _task(
        19, "math_0213",
        "A sequence starts with 0, 1, 1 and each later term is the sum of the "
        "three preceding terms. Compute term number 50 modulo 1000000007, "
        "using non-negative remainders. Compute it with the bash tool "
        "(python3 -c). Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        6, _tribonacci(50, 1_000_000_007),
    )
    _task(
        20, "math_0214",
        "A robot starts at (0, 0) and must reach (15, 15), moving only one "
        "step right or one step up at a time. How many different paths are "
        "there? Compute it with the bash tool (python3 -c). Work only inside "
        "the current directory. When you are done, write ONLY the final answer "
        "to answer.txt.",
        4, math.comb(30, 15),
    )
    _task(
        21, "math_0215",
        "How many positive integers not exceeding 1,000,000 have decimal digit "
        "sum equal to 7? Compute it with the bash tool (python3 -c). Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        7, _digit_sum_count(1_000_000, 7),
    )
    _task(
        22, "math_0216",
        "Compute the sum of Euler's totient function phi(n) for all integers n "
        "from 1 to 1000 inclusive. Compute it with the bash tool (python3 -c). "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        7, _totient_sum(1000),
    )
    _task(
        23, "math_0217",
        "Ten letters are placed into ten addressed envelopes completely at "
        "random. How many arrangements put every letter into a wrong envelope? "
        "Compute it with the bash tool (python3 -c). Work only inside the "
        "current directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        6, _derangements(10),
    )
    _task(
        24, "math_0218",
        "How many integers x with 0 <= x < 2024 satisfy x^2 congruent to 1 "
        "modulo 2024? Compute it with the bash tool (python3 -c). Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        7, sum(1 for x in range(2024) if (x * x - 1) % 2024 == 0),
    )
    p = lambda x: 5 * x ** 6 - 3 * x ** 4 + 7 * x ** 2 - 11 * x + 13
    _task(
        25, "math_0219",
        "Evaluate p(x) = 5x^6 - 3x^4 + 7x^2 - 11x + 13 at x = 7. Compute it "
        "with the bash tool (python3 -c). Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        5, p(7),
    )
    _task(
        26, "math_0220",
        "In a normal-play Nim game there are three heaps of 3, 4 and 5 tokens. "
        "A move removes any positive number of tokens from one heap. How many "
        "distinct first moves leave the position with Nim-sum zero? Compute it "
        "with the bash tool (python3 -c). Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        6, _nim_winning_moves([3, 4, 5]),
    )
    best = max(
        3 * x + 2 * y
        for x in range(0, 12)
        for y in range(0, 12)
        if x + 2 * y <= 9 and 2 * x + y <= 9
    )
    _task(
        27, "math_0221",
        "Non-negative integers x and y satisfy x + 2y <= 9 and 2x + y <= 9. "
        "What is the largest possible value of 3x + 2y? Compute it with the "
        "bash tool (python3 -c). Work only inside the current directory. When "
        "you are done, write ONLY the final answer to answer.txt.",
        6, best,
    )
    _task(
        28, "math_0222",
        "You roll a fair six-sided die once. You may keep the result or reroll "
        "exactly once and then must keep the second result. What is the "
        "optimal expected value? Answer as a reduced fraction in the form "
        "numerator/denominator. Compute it with the bash tool (python3 -c). "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        5, "17/4", "exact_str",
    )
    rsa = pow(2790, 2753, 3233)
    _task(
        29, "math_0223",
        "An RSA public key is n = 3233 with exponent e = 17. The primes are "
        "p = 61 and q = 53. Decrypt the ciphertext 2790 to the original "
        "message m, where 0 <= m < n. What is m? Compute it with the bash tool "
        "(python3 -c). Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        7, rsa,
    )
    _task(
        30, "math_0224",
        "Write the decimal number 123456789 in base 36 using lowercase digits "
        "0-9 and a-z. What is the resulting string? Compute it with the bash "
        "tool (python3 -c). Work only inside the current directory. When you "
        "are done, write ONLY the final answer to answer.txt.",
        4, _base36(123456789), "exact_str",
    )
    det = (
        2 * (4 * 6 - 5 * 0)
        - 1 * (0 * 6 - 5 * 1)
        + 3 * (0 * 0 - 4 * 1)
    )
    _task(
        31, "math_0225",
        "Compute the determinant of the matrix with rows (2, 1, 3), (0, 4, 5) "
        "and (1, 0, 6). Compute it with the bash tool (python3 -c). Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        3, det,
    )
    _task(
        32, "math_0226",
        "Compute 1^3 + 2^3 + 3^3 + ... + 100^3. Compute it with the bash tool "
        "(python3 -c). Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        3, (100 * 101 // 2) ** 2,
    )
    _task(
        33, "math_0227",
        "A triangle has sides 13, 14 and 15. What is its area? Compute it with "
        "the bash tool (python3 -c). Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        3, 84,
    )
    arrive = (
        dt.datetime(2025, 3, 10, 22, 40)
        - dt.timedelta(hours=8)
        + dt.timedelta(hours=7, minutes=25)
        - dt.timedelta(hours=5)
    )
    _task(
        34, "math_0228",
        "A flight leaves at 2025-03-10 22:40 local time in a UTC+8 zone and "
        "lasts 7 hours 25 minutes. What is the local date and time at arrival "
        "in a UTC-5 zone? Answer in the form YYYY-MM-DD HH:MM. Compute it with "
        "the bash tool (python3 -c). Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        5, arrive.strftime("%Y-%m-%d %H:%M"), "exact_str",
    )
    _task(
        35, "math_0229",
        "Convert 5 miles, 120 yards and 2 feet into inches, using 1 mile = "
        "1760 yards, 1 yard = 3 feet and 1 foot = 12 inches. Compute it with "
        "the bash tool (python3 -c). Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        4, 5 * 63360 + 120 * 36 + 2 * 12,
    )
    ways = [0] * 31
    ways[0] = 1
    for value in range(1, 16):
        for total in range(30, value - 1, -1):
            ways[total] += ways[total - value]
    _task(
        36, "math_0230",
        "How many subsets of {1, 2, ..., 15} have sum exactly 30? The empty "
        "set counts as a subset. Compute it with the bash tool (python3 -c). "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        7, ways[30],
    )
    survivor = 0
    for size in range(2, 101):
        survivor = (survivor + 3) % size
    _task(
        37, "math_0231",
        "People numbered 1 to 100 stand in a circle. Counting starts at person "
        "1, and every third person still in the circle is removed until one "
        "person remains. Which number survives? Compute it with the bash tool "
        "(python3 -c). Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        6, survivor + 1,
    )
    term = "1"
    for _ in range(19):
        term = _look_and_say(term)
    _task(
        38, "math_0232",
        "The look-and-say sequence starts with 1. Each next term reads the "
        "previous term aloud: 1, 11, 21, 1211, 111221, ... What is the number "
        "of digits in the 20th term, counting the starting 1 as term 1? "
        "Compute it with the bash tool (python3 -c). Work only inside the "
        "current directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        8, len(term),
    )
    _task(
        39, "math_0233",
        "Compute the sum of all prime numbers strictly below 2,000,000. "
        "Compute it with the bash tool (python3 -c). Work only inside the "
        "current directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        8, _primes_below(2_000_000),
    )
    _task(
        40, "math_0234",
        "Compute 7^123456789 modulo 1000000007, using the non-negative "
        "remainder. Compute it with the bash tool (python3 -c). Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        7, pow(7, 123456789, 1_000_000_007),
    )


if __name__ == "__main__":
    generate()
