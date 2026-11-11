"""Generate the 34 new search tasks (``search/solvable/0007``..``0040``)."""

from __future__ import annotations

import random
from collections import Counter, defaultdict, deque

from common import create_task, csv_text


def _task(index: int, task_id: str, instruction: str, reward: int,
          expected, files: dict[str, str], check: str = "exact_str") -> None:
    create_task(
        category="search",
        index=index,
        task_id=task_id,
        instruction=instruction,
        reward=reward,
        check=check,
        expected=str(expected),
        workspace=files,
    )


def generate() -> None:
    _task(
        7, "search_0201",
        "The directory docs contains project notes. What version is documented "
        "in docs/README.md? Use file tools or bash (ls, grep, cat) to find it. "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        1,
        "3.7.2",
        {"docs/README.md": "# Project notes\n\nCurrent release: 3.7.2\n\nSee the changelog for details.\n"},
    )

    log_files = {}
    error_line = "2026-11-10T09:14:03Z ERROR ConnectionRefusedError: port 5432"
    for number in range(1, 13):
        lines = [f"2026-11-10T09:{number:02d}:00Z INFO worker {number} started"]
        if number == 7:
            lines.append(error_line)
        lines.append(f"2026-11-10T09:{number:02d}:30Z INFO worker {number} stopped")
        log_files[f"logs/service-{number:02d}.log"] = "\n".join(lines) + "\n"
    _task(
        8, "search_0202",
        "The exact text 'ConnectionRefusedError: port 5432' appears in one "
        "file under logs. Which file contains it? Answer with the file name "
        "only, for example service-01.log. Use file tools or bash (ls, grep, "
        "cat). Work only inside the current directory. When you are done, write "
        "ONLY the final answer to answer.txt.",
        2,
        "service-07.log",
        log_files,
    )

    md_files = {}
    for number in range(1, 13):
        md_files[f"docs/note-{number:02d}.md"] = f"# Note {number}\n\nBody {number}.\n"
    for number in range(1, 8):
        md_files[f"docs/raw-{number:02d}.txt"] = f"raw {number}\n"
    _task(
        9, "search_0203",
        "How many files with the .md extension are under docs, including "
        "nested directories? Use file tools or bash (ls, find, grep). Work "
        "only inside the current directory. When you are done, write ONLY the "
        "final answer to answer.txt.",
        2,
        sum(1 for path in md_files if path.endswith(".md")),
        md_files,
        "exact_int",
    )

    size_files = {
        "data/alpha.txt": "a" * 120,
        "data/beta.txt": "b" * 340,
        "data/gamma.txt": "c" * 95,
        "data/delta.txt": "d" * 280,
        "data/epsilon.txt": "e" * 410,
    }
    _task(
        10, "search_0204",
        "Five text files are under data. Which one has the largest size in "
        "bytes? Answer with the file name only. Use file tools or bash (ls, "
        "wc, find). Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        3,
        max(size_files, key=lambda path: len(size_files[path])).split("/")[-1],
        size_files,
    )

    app_lines = ["import os", "", "def start():", "    return os.getcwd()", ""]
    app_lines += [f"VALUE_{number} = {number}" for number in range(1, 26)]
    app_lines.insert(36, "# TODO: replace the temporary path")
    app_lines += ["", "def finish():", "    return VALUE_1"]
    todo_line = app_lines.index("# TODO: replace the temporary path") + 1
    _task(
        11, "search_0205",
        "The file src/app.py contains a TODO comment. On which 1-based line "
        "number is it? Use file tools or bash (grep -n, cat). Work only inside "
        "the current directory. When you are done, write ONLY the final answer "
        "to answer.txt.",
        2,
        todo_line,
        {"src/app.py": "\n".join(app_lines) + "\n"},
        "exact_int",
    )

    _task(
        12, "search_0206",
        "The file src/worker.py contains a TODO comment with a name in "
        "parentheses, for example TODO(alice). What name appears there? Use "
        "file tools or bash (grep, cat). Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        2,
        "maria",
        {"src/worker.py": "# TODO(maria): add backoff\n\ndef run():\n    return 1\n"},
    )

    _task(
        13, "search_0207",
        "The file config.ini has several sections and port values. What is "
        "the port in the [server] section? Use file tools or bash (grep, cat). "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        2,
        8443,
        {"config.ini": "[server]\nhost = 0.0.0.0\nport = 8443\n\n[db]\nport = 5432\n"},
        "exact_int",
    )

    _task(
        14, "search_0208",
        "old.txt and new.txt each contain one token per line. Which token "
        "appears in both files? Answer with the token. Use file tools or bash "
        "(sort, comm, grep). Work only inside the current directory. When you "
        "are done, write ONLY the final answer to answer.txt.",
        3,
        "tangerine",
        {
            "old.txt": "apple\nkiwi\ntangerine\npear\n",
            "new.txt": "melon\ntangerine\nplum\n",
        },
    )

    _task(
        15, "search_0209",
        "The files under src contain Python functions. Which function calls "
        "parse_header? Answer with the function name only. Use file tools or "
        "bash (grep, cat). Work only inside the current directory. When you "
        "are done, write ONLY the final answer to answer.txt.",
        4,
        "load_request",
        {
            "src/parser.py": "def parse_header(line):\n    return line.split(':', 1)\n",
            "src/router.py": "from parser import parse_header\n\ndef load_request(line):\n    return parse_header(line)\n",
            "src/main.py": "from router import load_request\n\ndef main(line):\n    return load_request(line)\n",
        },
    )

    _task(
        16, "search_0210",
        "Configuration is merged in this order: config/base.ini, then "
        "config/prod.ini, then config/local.ini, with later files overriding "
        "earlier ones. What is the effective timeout value? Use file tools or "
        "bash (grep, cat). Work only inside the current directory. When you "
        "are done, write ONLY the final answer to answer.txt.",
        5,
        60,
        {
            "config/base.ini": "[service]\ntimeout = 30\nworkers = 2\n",
            "config/prod.ini": "[service]\ntimeout = 45\n",
            "config/local.ini": "[service]\ntimeout = 60\n",
        },
        "exact_int",
    )

    _task(
        17, "search_0211",
        "The Markdown files under docs contain links. One relative link points "
        "to a file that does not exist. What is the missing target path as "
        "written in the link? Use file tools or bash (grep, find, cat). Work "
        "only inside the current directory. When you are done, write ONLY the "
        "final answer to answer.txt.",
        4,
        "guides/missing/page.md",
        {
            "docs/index.md": "# Index\n\nSee [install](install.md) and [guide](guides/missing/page.md).\n",
            "docs/install.md": "# Install\n\nBack to [index](index.md).\n",
            "docs/guides/known/page.md": "# Known\n\nContent.\n",
        },
    )

    rng = random.Random(201)
    ips = [f"192.0.2.{number}" for number in range(10, 18)]
    log_lines = []
    error_counts = Counter()
    for number in range(80):
        ip = rng.choice(ips)
        status = rng.choice([200, 200, 301, 404, 500, 500, 503])
        if status == 500:
            error_counts[ip] += 1
        log_lines.append(
            f'{ip} - - [10/Nov/2026:11:{number:02d}:00 +0000] '
            f'"GET /report/{number} HTTP/1.1" {status} {200 + number}'
        )
    # Make one address clearly win.
    for number in range(20):
        log_lines.append(f'198.51.100.77 - - [10/Nov/2026:12:00:{number:02d} +0000] "GET /fail HTTP/1.1" 500 10')
    all_counts = Counter(ip for ip in error_counts)
    all_counts["198.51.100.77"] += 20
    winner = max(all_counts, key=all_counts.get)
    assert list(all_counts.values()).count(all_counts[winner]) == 1
    _task(
        18, "search_0212",
        "access.log is in the common log format. Which client IP has the most "
        "responses with status 500? Use file tools or bash (grep, sort, uniq, "
        "awk). Work only inside the current directory. When you are done, "
        "write ONLY the final answer to answer.txt.",
        5,
        winner,
        {"access.log": "\n".join(log_lines) + "\n"},
    )

    _task(
        19, "search_0213",
        "The file CHANGELOG.md lists releases. What is the most recent version "
        "number? Answer without a leading v. Use file tools or bash (grep, "
        "head, cat). Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        3,
        "2.4.1",
        {"CHANGELOG.md": "# Changelog\n\n## 2.4.1 - 2026-10-02\n\n## 2.3.0 - 2026-08-14\n\n## 2.2.7 - 2026-05-01\n"},
    )

    _task(
        20, "search_0214",
        "The files under mail form one thread, ordered by file name. Who sent "
        "the last message in the thread? Answer with the sender name only. Use "
        "file tools or bash (ls, cat). Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        4,
        "Nina",
        {
            "mail/01.txt": "From: Omar\nSubject: Deploy\n\nStarting the rollout.\n",
            "mail/02.txt": "From: Petra\nSubject: Re: Deploy\n\nPlease wait for QA.\n",
            "mail/03.txt": "From: Nina\nSubject: Re: Deploy\n\nQA is green, deploy now.\n",
        },
    )

    _task(
        21, "search_0215",
        "kb/people.md lists people, their mentors and their employers; "
        "kb/companies.md lists companies and headquarters cities. In which "
        "city is the employer of the mentor of Lena Ortiz headquartered? Use "
        "file tools or bash (grep, cat). Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        6,
        "Lisbon",
        {
            "kb/people.md": "- Lena Ortiz: mentor=Tom Reed, employer=Blue Harbor\n- Tom Reed: employer=Northwind Labs\n",
            "kb/companies.md": "- Blue Harbor: city=Riga\n- Northwind Labs: city=Lisbon\n",
        },
    )

    _task(
        22, "search_0216",
        "people_old.csv and people_new.csv list the same people in different "
        "formats. Find the id of the person named Alex Morgan. Answer with the "
        "id from the files. Use file tools or bash (grep, cat). Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        5,
        "u-17",
        {
            "people_old.csv": csv_text(["id", "name"], [["u-11", "Lena Ortiz"], ["u-17", "Alex Morgan"]]),
            "people_new.csv": csv_text(["id", "display_name"], [["u-17", "A. Morgan"], ["u-11", "L. Ortiz"]]),
        },
    )

    _task(
        23, "search_0217",
        "src/app.py imports modules, and requirements.txt lists the installed "
        "third-party packages. One imported third-party module is missing from "
        "requirements.txt. Which module is it? Use file tools or bash (grep, "
        "cat). Work only inside the current directory. When you are done, "
        "write ONLY the final answer to answer.txt.",
        5,
        "numpy",
        {
            "src/app.py": "import json\nimport numpy as np\nimport requests\n\nprint(np.__version__)\n",
            "requirements.txt": "requests==2.32.0\n",
        },
    )

    _task(
        24, "search_0218",
        "The default worker count is in config/default.yaml. The deployment "
        "override is in deploy/prod.env, and the override wins. What worker "
        "count is effective? Use file tools or bash (grep, cat). Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        4,
        9,
        {
            "config/default.yaml": "workers: 4\nlog_level: info\n",
            "deploy/prod.env": "WORKERS=9\n",
        },
        "exact_int",
    )

    _task(
        25, "search_0219",
        "Three notes under notes contain one part of an access code each, in "
        "lines of the form part=... . Read the parts in file-name order and "
        "concatenate them without spaces. What is the code? Use file tools or "
        "bash (ls, cat). Work only inside the current directory. When you are "
        "done, write ONLY the final answer to answer.txt.",
        4,
        "QX731",
        {
            "notes/01.txt": "part=QX\n",
            "notes/02.txt": "part=7\n",
            "notes/03.txt": "part=31\n",
        },
    )

    target_word = "observability"
    letters = list(target_word)
    letters.pop(letters.index("i"))
    rng = random.Random(202)
    rng.shuffle(letters)
    anagram = "".join(letters)
    word_pool = [
        "amber", "bridge", "cobalt", "delta", "ember", "forest", "granite",
        "harbor", "island", "jungle", "kettle", "lantern", "meadow", "nectar",
        "orchard", "pebble", "quartz", "ripple", "signal", "timber", "umber",
        "valley", "willow", "xenon", "yonder", "zephyr",
    ]
    corpus = {}
    target_file = "corpus/file-23.txt"
    for number in range(1, 41):
        words = [rng.choice(word_pool) for _ in range(14)]
        if number == 23:
            words.insert(5, anagram)
        corpus[f"corpus/file-{number:02d}.txt"] = " ".join(words) + "\n"
    # Guard against an accidental second match.
    matches = []
    for path, text in corpus.items():
        for word in text.split():
            if sorted(word.lower()) == sorted(anagram.lower()):
                matches.append(path)
    assert matches == [target_file], matches
    _task(
        26, "search_0220",
        "One letter was removed from the word observability and the remaining "
        "letters were shuffled. The result appears as a word in one file under "
        "corpus, where words are separated by spaces. Which file contains it? "
        "Answer with the file name only, for example file-01.txt. Use file "
        "tools or bash (grep, python3). Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        6,
        target_file.split("/")[-1],
        corpus,
    )

    _task(
        27, "search_0221",
        "A build artifact is described in three files under build. Each file "
        "contains one line starting with key=; the parts form a checksum when "
        "concatenated in file-name order. What is the checksum? Use file tools "
        "or bash (ls, grep, cat). Work only inside the current directory. When "
        "you are done, write ONLY the final answer to answer.txt.",
        4,
        "a7f3c9",
        {
            "build/01.txt": "key=a7\nnoise=1\n",
            "build/02.txt": "key=f3\nnoise=2\n",
            "build/03.txt": "key=c9\nnoise=3\n",
        },
    )

    _task(
        28, "search_0222",
        "traceback.txt records a failure. In which source file is the function "
        "where the exception was raised defined? Answer with the path exactly "
        "as it appears in the traceback. Use file tools or bash (grep, cat). "
        "Work only inside the current directory. When you are done, write ONLY "
        "the final answer to answer.txt.",
        5,
        "src/handlers.py",
        {
            "traceback.txt": 'Traceback (most recent call last):\n  File "src/main.py", line 9, in <module>\n    main()\n  File "src/handlers.py", line 42, in handle\n    raise ValueError("bad input")\nValueError: bad input\n',
            "src/main.py": "from handlers import handle\n\ndef main():\n    handle()\n",
            "src/handlers.py": "def handle():\n    raise ValueError('bad input')\n",
        },
    )

    network_edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("A", "F"), ("F", "E")]
    graph = defaultdict(list)
    for left, right in network_edges:
        graph[left].append(right)
        graph[right].append(left)
    distances = {"A": 0}
    queue = deque(["A"])
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if neighbour not in distances:
                distances[neighbour] = distances[node] + 1
                queue.append(neighbour)
    _task(
        29, "search_0223",
        "network/edges.txt lists undirected links between routers, one pair "
        "per line. How many hops are in the shortest path from A to E? Use "
        "file tools or bash (grep, cat, python3). Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        6,
        distances["E"],
        {"network/edges.txt": "".join(f"{left} {right}\n" for left, right in network_edges)},
        "exact_int",
    )

    _task(
        30, "search_0224",
        "The environment is defined in .env and then overridden by "
        "deploy/override.env, where the later file wins. What is the effective "
        "LOG_LEVEL? Use file tools or bash (grep, cat). Work only inside the "
        "current directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        3,
        "debug",
        {
            ".env": "LOG_LEVEL=info\nPORT=8080\n",
            "deploy/override.env": "LOG_LEVEL=debug\n",
        },
    )

    _task(
        31, "search_0225",
        "Two operations documents disagree about the API port. Which file "
        "states that the port is 8081? Answer with the file path. Use file "
        "tools or bash (grep, cat). Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        3,
        "docs/ops.md",
        {
            "docs/api.md": "# API\n\nThe service listens on port 8080.\n",
            "docs/ops.md": "# Operations\n\nThe service listens on port 8081 after the firewall change.\n",
        },
    )

    _task(
        32, "search_0226",
        "The Python files under src form an import graph. List all modules "
        "that belong to the only import cycle, sorted by file path and "
        "separated by commas. Include the src/ prefix and the .py suffix. Use "
        "file tools or bash (grep, cat, python3). Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        6,
        "src/a.py, src/b.py, src/c.py",
        {
            "src/a.py": "import b\n",
            "src/b.py": "import c\n",
            "src/c.py": "import a\n",
            "src/d.py": "import a\n",
        },
    )

    _task(
        33, "search_0227",
        "The tests under tests use several fixture files from "
        "tests/fixtures. One fixture is never referenced by any test. Answer "
        "with its file name. Use file tools or bash (grep, cat). Work only "
        "inside the current directory. When you are done, write ONLY the "
        "final answer to answer.txt.",
        5,
        "legacy.json",
        {
            "tests/test_users.py": 'def test_users():\n    data = "users.json"\n    assert data\n',
            "tests/test_orders.py": 'def test_orders():\n    data = "orders.json"\n    assert data\n',
            "tests/fixtures/users.json": "{}\n",
            "tests/fixtures/orders.json": "{}\n",
            "tests/fixtures/legacy.json": "{}\n",
        },
    )

    _task(
        34, "search_0228",
        "The files under releases are named after versions. Which file has "
        "the highest version when the numeric parts are compared as numbers? "
        "Answer with the file name only. Use file tools or bash (ls, sort, "
        "python3). Work only inside the current directory. When you are done, "
        "write ONLY the final answer to answer.txt.",
        4,
        "v1.10.0.txt",
        {
            "releases/v1.2.9.txt": "old\n",
            "releases/v1.10.0.txt": "new\n",
            "releases/v1.9.12.txt": "middle\n",
        },
    )

    path_edges = [("S", "A", 2), ("S", "B", 5), ("A", "B", 1), ("A", "C", 4), ("B", "C", 1), ("C", "T", 3)]
    path_graph = defaultdict(list)
    for left, right, weight in path_edges:
        path_graph[left].append((right, weight))
        path_graph[right].append((left, weight))
    best = {"S": 0}
    frontier = [("S", 0)]
    while frontier:
        frontier.sort(key=lambda item: item[1])
        node, distance = frontier.pop(0)
        if distance != best.get(node):
            continue
        for neighbour, weight in path_graph[node]:
            candidate = distance + weight
            if candidate < best.get(neighbour, 10**9):
                best[neighbour] = candidate
                frontier.append((neighbour, candidate))
    _task(
        35, "search_0229",
        "edges.csv has columns source,target,weight for an undirected graph. "
        "What is the total weight of the shortest path from S to T? Use file "
        "tools or bash (grep, cat, python3). Work only inside the current "
        "directory. When you are done, write ONLY the final answer to "
        "answer.txt.",
        7,
        best["T"],
        {"edges.csv": csv_text(["source", "target", "weight"], path_edges)},
        "exact_int",
    )

    rng = random.Random(203)
    corpus_files = {}
    needle_file = "corpus/deep/level-7/shard-214.txt"
    for number in range(1, 301):
        folder = f"corpus/deep/level-{number % 9}/"
        words = [rng.choice(["alpha", "beta", "gamma", "delta", "omega", "sigma"]) for _ in range(12)]
        if number == 214:
            words.insert(3, "MAGENTA-FOX-42")
        corpus_files[f"{folder}shard-{number:03d}.txt"] = " ".join(words) + "\n"
    _task(
        36, "search_0230",
        "The directory corpus contains many text files. Exactly one file "
        "contains the token MAGENTA-FOX-42. What is its path relative to the "
        "current directory? Use file tools or bash (grep -R, find). Work only "
        "inside the current directory. When you are done, write ONLY the final "
        "answer to answer.txt.",
        7,
        needle_file,
        corpus_files,
    )

    _task(
        37, "search_0231",
        "The file README.md has a section named Quick start. What is the first "
        "command shown in that section? Answer with the command exactly as "
        "written, without the shell prompt. Use file tools or bash (grep, "
        "sed, cat). Work only inside the current directory. When you are done, "
        "write ONLY the final answer to answer.txt.",
        2,
        "python3 -m app --port 8080",
        {"README.md": "# Demo\n\n## Quick start\n\n```bash\npython3 -m app --port 8080\n```\n\n## Tests\n\nRun pytest.\n"},
    )

    _task(
        38, "search_0232",
        "The file CHANGELOG.md records releases with dates. On what date was "
        "version 2.3.0 released? Answer in YYYY-MM-DD form. Use file tools or "
        "bash (grep, cat). Work only inside the current directory. When you "
        "are done, write ONLY the final answer to answer.txt.",
        3,
        "2024-09-14",
        {"CHANGELOG.md": "# Changelog\n\n## 2.4.0 - 2025-01-10\n\n## 2.3.0 - 2024-09-14\n\n## 2.2.0 - 2024-04-02\n"},
    )

    _task(
        39, "search_0233",
        "CODEOWNERS assigns owners to paths. Who owns services/api/? Answer "
        "with the owner exactly as written, including the @ sign. Use file "
        "tools or bash (grep, cat). Work only inside the current directory. "
        "When you are done, write ONLY the final answer to answer.txt.",
        3,
        "@backend-team",
        {"CODEOWNERS": "# owners\nservices/api/ @backend-team\nservices/web/ @frontend-team\n"},
    )

    _task(
        40, "search_0234",
        "The ticket docs/tickets/123.md refers to a numbered RFC. Which RFC "
        "number does it implement? Answer in the form RFC-NNNN. Use file tools "
        "or bash (grep, cat). Work only inside the current directory. When you "
        "are done, write ONLY the final answer to answer.txt.",
        4,
        "RFC-0042",
        {
            "docs/tickets/123.md": "# Ticket 123\n\nThis change implements RFC-0042 and closes the rollout.\n",
            "docs/tickets/124.md": "# Ticket 124\n\nUnrelated cleanup.\n",
        },
    )


if __name__ == "__main__":
    generate()
