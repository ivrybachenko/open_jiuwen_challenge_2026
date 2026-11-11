"""Generate the 34 new data-analysis tasks (``data_analysis/solvable/0007``..``0040``)."""

from __future__ import annotations

import json
import math
import random
from collections import defaultdict

from common import create_task, csv_text, jsonl_text


def _task(index: int, task_id: str, instruction: str, reward: int,
          expected, files: dict[str, str], check: str = "exact_int") -> None:
    create_task(
        category="data_analysis",
        index=index,
        task_id=task_id,
        instruction=instruction,
        reward=reward,
        check=check,
        expected=str(expected),
        workspace=files,
    )


def _rows(seed: int, count: int, regions: list[str], products: list[str]):
    rng = random.Random(seed)
    rows = []
    for number in range(1, count + 1):
        rows.append([
            f"o-{number:04d}",
            rng.choice(regions),
            rng.choice(products),
            rng.randint(1, 20),
            rng.randint(3, 90),
        ])
    return rows


def _number(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def generate() -> None:
    regions = ["North", "South", "East", "West"]
    products = ["widget", "gadget", "cable", "sensor", "adapter"]

    rows7 = _rows(101, 37, regions, products)
    _task(
        7, "data_analysis_0201",
        "The file sales.csv has columns order_id,region,product,units,price. "
        "How many data rows does it contain, not counting the header? Use bash "
        "with python3 to compute it. Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        1,
        len(rows7),
        {"sales.csv": csv_text(["order_id", "region", "product", "units", "price"], rows7)},
    )

    rows8 = _rows(102, 60, regions, products)
    _task(
        8, "data_analysis_0202",
        "The file sales.csv has columns order_id,region,product,units,price. "
        "What is the total number of units across all rows? Use bash with "
        "python3 to compute it. Work only inside the current directory. When "
        "you are done, write ONLY the final answer to answer.txt.",
        2,
        sum(int(row[3]) for row in rows8),
        {"sales.csv": csv_text(["order_id", "region", "product", "units", "price"], rows8)},
    )

    rows9 = _rows(103, 50, regions, products)
    _task(
        9, "data_analysis_0203",
        "The file orders.csv has columns order_id,region,product,units,price. "
        "Revenue for a row is units multiplied by price. What is the largest "
        "single-row revenue in the file? Use bash with python3. Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        3,
        max(int(row[3]) * int(row[4]) for row in rows9),
        {"orders.csv": csv_text(["order_id", "region", "product", "units", "price"], rows9)},
    )

    rows10 = _rows(104, 30, regions, products)
    _task(
        10, "data_analysis_0204",
        "The file catalog.csv has columns item_id,category,item,units. How "
        "many distinct item names occur in the file? Use bash with python3. "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        2,
        len({row[2] for row in rows10}),
        {"catalog.csv": csv_text(["item_id", "category", "item", "units"],
                                 [[row[0], row[1], row[2], row[3]] for row in rows10])},
    )

    rng = random.Random(105)
    ratings = [rng.randint(1, 5) for _ in range(33)]
    rating_rows = [[f"r-{i:03d}", ("N/A" if i % 7 == 0 else "") if i % 9 == 0 else str(value)]
                   for i, value in enumerate(ratings, start=1)]
    valid = [int(row[1]) for row in rating_rows if row[1] not in {"", "N/A"}]
    _task(
        11, "data_analysis_0205",
        "The file ratings.csv has columns review_id,rating. Some rating cells "
        "are empty or contain N/A and must be ignored. What is the average of "
        "the remaining numeric ratings, rounded to the nearest integer? Use "
        "bash with python3. Work only inside the current directory. When you "
        "are done, write ONLY the final answer to answer.txt.",
        3,
        round(sum(valid) / len(valid)),
        {"ratings.csv": csv_text(["review_id", "rating"], rating_rows)},
    )

    rows12 = _rows(106, 55, regions, products)
    _task(
        12, "data_analysis_0206",
        "The file sales.csv has columns order_id,region,product,units,price. "
        "How many rows have region West and units greater than 10? Use bash "
        "with python3. Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        3,
        sum(1 for row in rows12 if row[1] == "West" and int(row[3]) > 10),
        {"sales.csv": csv_text(["order_id", "region", "product", "units", "price"], rows12)},
    )

    rows13 = _rows(107, 80, regions, products)
    totals13 = defaultdict(int)
    for row in rows13:
        totals13[row[1]] += int(row[3])
    _task(
        13, "data_analysis_0207",
        "The file shipments.csv has columns shipment_id,region,product,units,"
        "price. Which region has the largest total units across all its rows? "
        "Answer with the region name. Use bash with python3. Work only inside "
        "the current directory. When you are done, write ONLY the final answer "
        "to answer.txt.",
        4,
        max(totals13, key=totals13.get),
        {"shipments.csv": csv_text(["shipment_id", "region", "product", "units", "price"], rows13)},
        "exact_str",
    )

    rows14 = _rows(108, 65, regions, products)
    revenue14 = defaultdict(int)
    for row in rows14:
        revenue14[row[2]] += int(row[3]) * int(row[4])
    _task(
        14, "data_analysis_0208",
        "The file sales.csv has columns order_id,region,product,units,price. "
        "Revenue is units multiplied by price. Which product has the largest "
        "total revenue? Answer with the product name. Use bash with python3. "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        4,
        max(revenue14, key=revenue14.get),
        {"sales.csv": csv_text(["order_id", "region", "product", "units", "price"], rows14)},
        "exact_str",
    )

    customers = [[f"c-{i:03d}", f"Customer {i}", ["Leeds", "Oslo", "Lima", "Tokyo"][i % 4]]
                 for i in range(1, 16)]
    orders15 = []
    rng = random.Random(109)
    for i in range(1, 51):
        orders15.append([f"o-{i:04d}", f"c-{rng.randint(1, 15):03d}",
                         rng.randint(1, 9), rng.randint(5, 40)])
    city = {row[0]: row[2] for row in customers}
    total_leeds = sum(int(row[2]) * int(row[3]) for row in orders15 if city[row[1]] == "Leeds")
    _task(
        15, "data_analysis_0209",
        "customers.csv has columns customer_id,name,city and orders.csv has "
        "order_id,customer_id,units,price. Revenue for an order is units times "
        "price. What is the total revenue of orders placed by customers from "
        "Leeds? Use bash with python3. Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        5,
        total_leeds,
        {
            "customers.csv": csv_text(["customer_id", "name", "city"], customers),
            "orders.csv": csv_text(["order_id", "customer_id", "units", "price"], orders15),
        },
    )

    users = [f"user{i:02d}" for i in range(1, 13)]
    rng = random.Random(110)
    events16 = []
    counts16 = defaultdict(int)
    for i in range(120):
        user = rng.choice(users)
        counts16[user] += 1
        events16.append({"user": user, "action": rng.choice(["view", "edit", "share"]),
                         "ts": 1700000000 + i * 37})
    _task(
        16, "data_analysis_0210",
        "events.jsonl has one JSON object per line with fields user, action "
        "and ts. Which user has the most events? Answer with the user value. "
        "Use bash with python3. Work only inside the current directory. When "
        "you are done, write ONLY the final answer to answer.txt.",
        4,
        max(counts16, key=counts16.get),
        {"events.jsonl": jsonl_text(events16)},
        "exact_str",
    )

    monthly = [[f"2023-{month:02d}", 1000 + month * 37 % 211] for month in range(1, 13)]
    monthly += [[f"2024-{month:02d}", 1200 + month * 53 % 307] for month in range(1, 13)]
    best_month = max(monthly, key=lambda row: row[1])
    _task(
        17, "data_analysis_0211",
        "monthly.csv has columns month,revenue with month in YYYY-MM form. "
        "Which month has the highest revenue? Answer in YYYY-MM form. Use bash "
        "with python3. Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        4,
        best_month[0],
        {"monthly.csv": csv_text(["month", "revenue"], monthly)},
        "exact_str",
    )

    rng = random.Random(111)
    dedupe_rows = []
    seen = set()
    for i in range(55):
        key = f"o-{rng.randint(1, 38):03d}"
        dedupe_rows.append([key, rng.choice(regions), rng.randint(1, 20)])
        seen.add(key)
    kept = {}
    for row in dedupe_rows:
        if row[0] not in kept:
            kept[row[0]] = row
    _task(
        18, "data_analysis_0212",
        "duplicates.csv has columns order_id,region,units. When an order_id "
        "appears more than once, keep only its first occurrence. What is the "
        "total units over the remaining rows? Use bash with python3. Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        6,
        sum(int(row[2]) for row in kept.values()),
        {"duplicates.csv": csv_text(["order_id", "region", "units"], dedupe_rows)},
    )

    rng = random.Random(112)
    pivot_rows = []
    for i in range(90):
        pivot_rows.append([rng.choice(regions), rng.choice(products), rng.randint(1, 12)])
    cell = defaultdict(int)
    for region, product, units in pivot_rows:
        cell[(region, product)] += units
    _task(
        19, "data_analysis_0213",
        "pivot.csv has columns region,product,units. What is the total units "
        "for region North and product widget after grouping? Use bash with "
        "python3. Work only inside the current directory. When you are done, "
        "write ONLY the final answer to answer.txt.",
        5,
        cell[("North", "widget")],
        {"pivot.csv": csv_text(["region", "product", "units"], pivot_rows)},
    )

    rng = random.Random(113)
    series = [rng.randint(1, 30) for _ in range(40)]
    max_window = max(sum(series[i:i + 3]) for i in range(len(series) - 2))
    _task(
        20, "data_analysis_0214",
        "values.csv has columns day,value with one row per day. What is the "
        "largest sum of three consecutive daily values? Use bash with python3. "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        5,
        max_window,
        {"values.csv": csv_text(["day", "value"], [[i + 1, value] for i, value in enumerate(series)])},
    )

    xs = list(range(1, 31))
    rng = random.Random(114)
    ys = [2 * x + 3 + rng.randint(-3, 3) for x in xs]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = math.sqrt(sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys))
    correlation = numerator / denominator
    _task(
        21, "data_analysis_0215",
        "pairs.csv has columns x,y. Compute the Pearson correlation coefficient "
        "between x and y and round it to two decimal places. Use bash with "
        "python3. Work only inside the current directory. When you are done, "
        "write ONLY the final answer to answer.txt.",
        6,
        f"{correlation:.2f}",
        {"pairs.csv": csv_text(["x", "y"], list(zip(xs, ys)))},
        "exact_str",
    )

    rng = random.Random(115)
    percentile_values = sorted(rng.randint(1, 200) for _ in range(100))
    rank = math.ceil(0.9 * len(percentile_values)) - 1
    _task(
        22, "data_analysis_0216",
        "scores.csv has column score with 100 integer values. Using the "
        "nearest-rank method, what is the 90th percentile? Use bash with "
        "python3. Work only inside the current directory. When you are done, "
        "write ONLY the final answer to answer.txt.",
        6,
        percentile_values[rank],
        {"scores.csv": csv_text(["score"], [[value] for value in rng.sample(percentile_values, 100)])},
    )

    raw_names = [
        "  Ada Lovelace ", "ada lovelace", "ADA LOVELACE", "Grace Hopper",
        " grace  hopper", "Alan Turing", "alan turing ", "Edsger Dijkstra",
        "Barbara Liskov", " barbara liskov", "Margaret Hamilton",
    ]
    canonical = {" ".join(name.split()).casefold() for name in raw_names}
    _task(
        23, "data_analysis_0217",
        "names.csv has column name. Normalize each name by collapsing runs of "
        "spaces and ignoring case. How many distinct normalized names are "
        "there? Use bash with python3. Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        4,
        len(canonical),
        {"names.csv": csv_text(["name"], [[name] for name in raw_names])},
    )

    products24 = [[f"p-{i:02d}", f"Product {i}", ["DE", "FR", "NL"][i % 3], 10 + i]
                  for i in range(1, 21)]
    customer_country = {f"c-{i:03d}": ["DE", "FR", "NL"][i % 3] for i in range(1, 16)}
    orders24 = []
    rng = random.Random(116)
    for i in range(1, 70):
        orders24.append([f"o-{i:04d}", f"c-{rng.randint(1, 15):03d}",
                         f"p-{rng.randint(1, 20):02d}", rng.randint(1, 8)])
    price24 = {row[0]: row[3] for row in products24}
    de_total = sum(price24[row[2]] * row[3] for row in orders24
                   if customer_country[row[1]] == "DE")
    _task(
        24, "data_analysis_0218",
        "customers.csv has customer_id,country; products.csv has "
        "product_id,name,country,price; orders.csv has order_id,customer_id,"
        "product_id,units. What is the total revenue from customers in DE? "
        "Use bash with python3. Work only inside the current directory. When "
        "you are done, write ONLY the final answer to answer.txt.",
        7,
        de_total,
        {
            "customers.csv": csv_text(["customer_id", "country"], [[k, v] for k, v in customer_country.items()]),
            "products.csv": csv_text(["product_id", "name", "country", "price"], products24),
            "orders.csv": csv_text(["order_id", "customer_id", "product_id", "units"], orders24),
        },
    )

    dirty_amounts = [
        "$1,200.50", "1 200,50", "€940.25", "75.00", "2,345.10", "310",
        "1,099.99", "12.5", "$0.99", "4 500,00", "88.80", "1,000.00", "250.75",
        "3 200,25", "$45.10",
    ]
    cents_total = 0
    for amount in dirty_amounts:
        cleaned = amount.replace("$", "").replace("€", "").replace(" ", "")
        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(",", "")
        elif "," in cleaned:
            cleaned = cleaned.replace(",", ".")
        cents_total += round(float(cleaned) * 100)
    expected_dirty = round(cents_total / 100)
    _task(
        25, "data_analysis_0219",
        "expenses.csv has column amount with currency symbols, spaces, commas "
        "and decimal points. A comma is a decimal separator only when it is the "
        "only separator; otherwise it is a thousands separator. What is the "
        "total amount rounded to the nearest whole unit? Use bash with python3. "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        8,
        expected_dirty,
        {"expenses.csv": csv_text(["expense_id", "amount"],
                                  [[f"e-{i:03d}", value] for i, value in enumerate(dirty_amounts, start=1)])},
    )

    rng = random.Random(117)
    session_events = []
    session_counts = defaultdict(int)
    for user in ["u1", "u2", "u3"]:
        timestamp = 1000
        previous = None
        for _ in range(rng.randint(5, 10)):
            timestamp += rng.choice([120, 900, 2400])
            if previous is None or timestamp - previous > 1800:
                session_counts[user] += 1
            previous = timestamp
            session_events.append({"user": user, "ts": timestamp, "action": "open"})
    _task(
        26, "data_analysis_0220",
        "events.jsonl has fields user and ts (Unix seconds). A session starts "
        "at a user's first event and a new session starts whenever more than "
        "1800 seconds pass without an event from that user. Which user has the "
        "most sessions? Answer with the user value. Use bash with python3. Work "
        "only inside the current directory. When you are done, write ONLY the "
        "final answer to answer.txt.",
        7,
        max(session_counts, key=session_counts.get),
        {"events.jsonl": jsonl_text(session_events)},
        "exact_str",
    )

    signup = {f"u{i:02d}": f"2025-01-{i:02d}" for i in range(1, 21)}
    activity = []
    retained = 0
    for i in range(1, 21):
        if i % 2 == 0:
            activity.append({"user": f"u{i:02d}", "month": "2025-02", "action": "login"})
            retained += 1
        if i % 3 == 0:
            activity.append({"user": f"u{i:02d}", "month": "2025-03", "action": "login"})
    _task(
        27, "data_analysis_0221",
        "users.csv has columns user,signup_date. activity.jsonl has user,month,"
        "action. How many users who signed up in January 2025 were active in "
        "February 2025? Use bash with python3. Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        7,
        retained,
        {
            "users.csv": csv_text(["user", "signup_date"], [[k, v] for k, v in signup.items()]),
            "activity.jsonl": jsonl_text(activity),
        },
    )

    rng = random.Random(118)
    normal = [rng.gauss(50, 10) for _ in range(48)]
    normal += [100, 105]
    mean = sum(normal) / len(normal)
    variance = sum((value - mean) ** 2 for value in normal) / len(normal)
    std = math.sqrt(variance)
    outliers = sum(1 for value in normal if abs((value - mean) / std) > 2)
    _task(
        28, "data_analysis_0222",
        "measurements.csv has column value. Using the population mean and "
        "population standard deviation of the column, how many values have an "
        "absolute z-score greater than 2? Use bash with python3. Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        7,
        outliers,
        {"measurements.csv": csv_text(["value"], [[f"{value:.3f}"] for value in normal])},
    )

    funnels = []
    completed = 0
    for i in range(1, 61):
        user = f"u{i:03d}"
        funnels.append({"user": user, "action": "view", "ts": i})
        if i % 2 == 0:
            funnels.append({"user": user, "action": "add", "ts": i + 1})
        if i % 3 == 0:
            funnels.append({"user": user, "action": "cart", "ts": i + 2})
        if i % 6 == 0:
            funnels.append({"user": user, "action": "purchase", "ts": i + 3})
            completed += 1
    _task(
        29, "data_analysis_0223",
        "funnel.jsonl has user,action,ts with actions view, add, cart and "
        "purchase. How many users performed all four actions at least once? "
        "Use bash with python3. Work only inside the current directory. When "
        "you are done, write ONLY the final answer to answer.txt.",
        7,
        completed,
        {"funnel.jsonl": jsonl_text(funnels)},
    )

    scores = [[i, 60 + i % 21, 1 + i % 5] for i in range(1, 41)]
    weighted = sum(value * weight for _, value, weight in scores) / sum(weight for _, _, weight in scores)
    _task(
        30, "data_analysis_0224",
        "scores.csv has columns item,value,weight. Compute the weighted mean "
        "of value using weight as the weight and round it to two decimal "
        "places. Use bash with python3. Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        5,
        f"{weighted:.2f}",
        {"scores.csv": csv_text(["item", "value", "weight"], scores)},
        "exact_str",
    )

    messy_dates = [
        ["a1", "07.03.2024"], ["a2", "2023-11-05"], ["a3", "March 2, 2022"],
        ["a4", "01.01.2025"], ["a5", "2020-06-15"], ["a6", "December 31, 2021"],
    ]
    def parse_messy(text: str) -> str:
        if "-" in text:
            year, month, day = map(int, text.split("-"))
        elif "." in text:
            day, month, year = map(int, text.split("."))
        else:
            month_name, day_text, year_text = text.replace(",", "").split()
            months = {name: i for i, name in enumerate(
                ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"], start=1)}
            year, month, day = int(year_text), months[month_name], int(day_text)
        return f"{year:04d}-{month:02d}-{day:02d}"
    earliest = min(parse_messy(row[1]) for row in messy_dates)
    _task(
        31, "data_analysis_0225",
        "events.csv has columns event_id,date. Dates use YYYY-MM-DD, "
        "DD.MM.YYYY or 'Month D, YYYY'. What is the earliest date? Answer in "
        "YYYY-MM-DD form. Use bash with python3. Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        6,
        earliest,
        {"events.csv": csv_text(["event_id", "date"], messy_dates)},
        "exact_str",
    )

    emails = [
        "Ada@Example.com", "ada@example.com ", " grace@example.com",
        "grace@example.com", "alan@example.org", "ALAN@example.org",
        "bob@example.net", "carol@example.net", "carol@example.net",
        "dave@example.com",
    ]
    normalized = [email.strip().casefold() for email in emails]
    duplicates = sum(1 for email in set(normalized) if normalized.count(email) > 1)
    _task(
        32, "data_analysis_0226",
        "users.csv has column email. Normalize each email by trimming spaces "
        "and ignoring case. How many distinct normalized emails occur more "
        "than once? Use bash with python3. Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        5,
        duplicates,
        {"users.csv": csv_text(["email"], [[email] for email in emails])},
    )

    employees = [
        ["e1", "Root", "", 200], ["e2", "Anna", "e1", 120], ["e3", "Boris", "e1", 210],
        ["e4", "Chen", "e2", 90], ["e5", "Dina", "e2", 130], ["e6", "Eli", "e3", 180],
        ["e7", "Fay", "e3", 220], ["e8", "Gus", "e4", 100], ["e9", "Hana", "e4", 80],
    ]
    by_id = {row[0]: row for row in employees}
    richer = sum(1 for row in employees if row[2] and int(row[3]) > int(by_id[row[2]][3]))
    _task(
        33, "data_analysis_0227",
        "employees.csv has columns employee_id,name,manager_id,salary. Root "
        "has an empty manager_id. How many employees earn strictly more than "
        "their direct manager? Use bash with python3. Work only inside the "
        "current directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        6,
        richer,
        {"employees.csv": csv_text(["employee_id", "name", "manager_id", "salary"], employees)},
    )

    rng = random.Random(119)
    values34 = [rng.randint(1, 50) for _ in range(60)]
    max_five = max(sum(values34[i:i + 5]) for i in range(len(values34) - 4))
    _task(
        34, "data_analysis_0228",
        "values.csv has columns day,value. What is the largest sum of five "
        "consecutive values? Use bash with python3. Work only inside the "
        "current directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        5,
        max_five,
        {"values.csv": csv_text(["day", "value"], [[i + 1, value] for i, value in enumerate(values34)])},
    )

    nested = {
        "service": {"limits": {"cpu": 4, "memory": 16}, "ports": [80, 443],
                    "features": {"beta": True, "threshold": 9}},
        "metrics": {"latency": 12, "errors": 0, "nested": {"deep": 31}},
        "name": "demo",
    }
    def count_large(value) -> int:
        if isinstance(value, bool):
            return 0
        if isinstance(value, (int, float)):
            return 1 if value > 10 else 0
        if isinstance(value, dict):
            return sum(count_large(item) for item in value.values())
        if isinstance(value, list):
            return sum(count_large(item) for item in value)
        return 0
    _task(
        35, "data_analysis_0229",
        "config.json contains a nested JSON object. How many numeric leaf "
        "values are strictly greater than 10? Booleans do not count as "
        "numbers. Use bash with python3. Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        5,
        count_large(nested),
        {"config.json": json.dumps(nested, indent=2) + "\n"},
    )

    log_lines = []
    statuses = [200, 200, 301, 404, 500, 502, 200, 403, 503, 200] * 7
    for i, status in enumerate(statuses, start=1):
        log_lines.append(f'10.0.0.{i % 5} - - [10/Nov/2026:10:{i:02d}:00 +0000] "GET /item/{i} HTTP/1.1" {status} {100 + i}')
    _task(
        36, "data_analysis_0230",
        "access.log is in the common log format. How many requests returned a "
        "status code from 500 to 599 inclusive? Use bash with python3. Work "
        "only inside the current directory. When you are done, write ONLY the "
        "final answer to answer.txt.",
        5,
        sum(1 for status in statuses if 500 <= status <= 599),
        {"access.log": "\n".join(log_lines) + "\n"},
    )

    rng = random.Random(120)
    iqr_values = sorted(rng.randint(1, 100) for _ in range(60))
    iqr_values[0], iqr_values[-1] = 1, 1000
    def median(values):
        middle = len(values) // 2
        if len(values) % 2:
            return values[middle]
        return (values[middle - 1] + values[middle]) / 2

    q1 = median(iqr_values[:len(iqr_values) // 2])
    q3 = median(iqr_values[(len(iqr_values) + 1) // 2:])
    iqr = q3 - q1
    outlier_count = sum(1 for value in iqr_values if value < q1 - 1.5 * iqr or value > q3 + 1.5 * iqr)
    _task(
        37, "data_analysis_0231",
        "values.csv has column value. Using the median of the lower half as "
        "Q1 and the median of the upper half as Q3, count the values outside "
        "the interval [Q1 - 1.5*IQR, Q3 + 1.5*IQR]. Use bash with python3. Work "
        "only inside the current directory. When you are done, write ONLY the "
        "final answer to answer.txt.",
        6,
        outlier_count,
        {"values.csv": csv_text(["value"], [[value] for value in iqr_values])},
    )

    edges = [[0, 1], [1, 2], [3, 4], [5, 5], [6, 7], [7, 8], [8, 6], [9, 10]]
    nodes = {node for edge in edges for node in edge}
    parent = {node: node for node in nodes}
    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    for a, b in edges:
        union(a, b)
    components = len({find(node) for node in nodes})
    _task(
        38, "data_analysis_0232",
        "edges.csv has columns source,target describing an undirected graph. "
        "How many connected components does the graph have? Use bash with "
        "python3. Work only inside the current directory. When you are done, "
        "write ONLY the final answer to answer.txt.",
        7,
        components,
        {"edges.csv": csv_text(["source", "target"], edges)},
    )

    inventory_events = [
        ["restock", 40], ["sale", 5], ["sale", 7], ["restock", 12],
        ["sale", 20], ["sale", 3], ["restock", 9], ["sale", 8],
    ]
    stock = 0
    for kind, quantity in inventory_events:
        stock += quantity if kind == "restock" else -quantity
    _task(
        39, "data_analysis_0233",
        "inventory.csv has columns event,quantity. Start with zero units. A "
        "restock event adds quantity; a sale event subtracts quantity. What is "
        "the final stock after all events? Use bash with python3. Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        6,
        stock,
        {"inventory.csv": csv_text(["event", "quantity"], inventory_events)},
    )

    source_a = [["t1", 10], ["t2", 20], ["t3", 30], ["t4", 40]]
    source_b = [["t2", 25], ["t5", 50], ["t4", 35]]
    reconciled = {row[0]: int(row[1]) for row in source_a}
    reconciled.update({row[0]: int(row[1]) for row in source_b})
    _task(
        40, "data_analysis_0234",
        "transactions_a.csv and transactions_b.csv have columns txn_id,amount. "
        "Treat transactions_b.csv as the newer source: for a txn_id present in "
        "both files use the amount from transactions_b.csv, otherwise use the "
        "only available amount. What is the total amount across all distinct "
        "txn_id values? Use bash with python3. Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        7,
        sum(reconciled.values()),
        {
            "transactions_a.csv": csv_text(["txn_id", "amount"], source_a),
            "transactions_b.csv": csv_text(["txn_id", "amount"], source_b),
        },
    )


if __name__ == "__main__":
    generate()
