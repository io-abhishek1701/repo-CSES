"""
update_readme.py
Scans all .cpp files in the repo root, matches them to known CSES problems,
and rewrites the AUTO-GENERATED sections in README.md.
"""

import os
import re

# ── Known CSES problems: filename stem → (task_id, category) ──────────────────
CSES_PROBLEMS = {
    # Introductory Problems
    "Weird_Algorithm":          (1068, "Introductory"),
    "Missing_Number":           (1083, "Introductory"),
    "Repetitions":              (1069, "Introductory"),
    "Increasing_Array":         (1094, "Introductory"),
    "Permutations":             (1070, "Introductory"),
    "Number_Spiral":            (1071, "Introductory"),
    "Two_Knights":              (1072, "Introductory"),
    "Apple_Division":           (1623, "Introductory"),
    "Chessboard_and_Queens":    (1624, "Introductory"),
    "Palindrome_Reorder":       (1755, "Introductory"),
    "Trailing_Zeros":           (1618, "Introductory"),
    "Coin_Piles":               (1754, "Introductory"),
    "Two_Sets":                 (1092, "Introductory"),
    "Bit_Strings":              (1617, "Introductory"),
    "Gray_Code":                (1625, "Introductory"),
    # Sorting and Searching
    "Distinct_Numbers":         (1621, "Sorting and Searching"),
    "Apartments":               (1084, "Sorting and Searching"),
    "Ferris_Wheel":             (1090, "Sorting and Searching"),
    "Concert_Tickets":          (1091, "Sorting and Searching"),
    "Restaurant_Customers":     (1619, "Sorting and Searching"),
    "Movie_Festival":           (1629, "Sorting and Searching"),
    "Sum_of_Two_Values":        (1640, "Sorting and Searching"),
    "Maximum_Subarray_Sum":     (1643, "Sorting and Searching"),
    "Stick_Lengths":            (1074, "Sorting and Searching"),
    "Missing_Coin_Sum":         (2183, "Sorting and Searching"),
    "Collecting_Numbers":       (2216, "Sorting and Searching"),
    "Collecting_Numbers_II":    (2217, "Sorting and Searching"),
    "Playlist":                 (1141, "Sorting and Searching"),
    "Towers":                   (1073, "Sorting and Searching"),
    "Traffic_Lights":           (1163, "Sorting and Searching"),
    "Josephus_Problem_I":       (2162, "Sorting and Searching"),
    "Josephus_Problem_II":      (2163, "Sorting and Searching"),
    "Nested_Ranges_Check":      (2168, "Sorting and Searching"),
    "Nested_Ranges_Count":      (2169, "Sorting and Searching"),
    "Room_Allocation":          (1164, "Sorting and Searching"),
    "Factory_Machines":         (1620, "Sorting and Searching"),
    "Tasks_and_Deadlines":      (1630, "Sorting and Searching"),
    "Reading_Books":            (1631, "Sorting and Searching"),
    "Sum_of_Three_Values":      (1641, "Sorting and Searching"),
    "Sum_of_Four_Values":       (1642, "Sorting and Searching"),
    "Minimum_Reachable_Node":   (1686, "Sorting and Searching"),
    "Sliding_Median":           (1076, "Sorting and Searching"),
    "Sliding_Cost":             (1077, "Sorting and Searching"),
    "Movie_Festival_II":        (1632, "Sorting and Searching"),
    "Maximum_Subarray_Sum_II":  (1644, "Sorting and Searching"),
    # Dynamic Programming
    "Minimizing_Coins":         (1634, "Dynamic Programming"),
    "Coin_Combinations_I":      (1635, "Dynamic Programming"),
    "Coin_Combinations_II":     (1636, "Dynamic Programming"),
    "Removing_Digits":          (1637, "Dynamic Programming"),
    "Grid_Paths":               (1638, "Dynamic Programming"),
    "Book_Shop":                (1158, "Dynamic Programming"),
    "Array_Description":        (1746, "Dynamic Programming"),
    "Counting_Towers":          (2413, "Dynamic Programming"),
    "Edit_Distance":            (1639, "Dynamic Programming"),
    "Rectangle_Cutting":        (1744, "Dynamic Programming"),
    "Money_Sums":               (1745, "Dynamic Programming"),
    "Removal_Game":             (1097, "Dynamic Programming"),
    "Two_Sets_II":              (1093, "Dynamic Programming"),
    "Increasing_Subsequence":   (1145, "Dynamic Programming"),
    "Projects":                 (1140, "Dynamic Programming"),
    "Elevator_Rides":           (1653, "Dynamic Programming"),
    "Counting_Tilings":         (2220, "Dynamic Programming"),
    "Counting_Numbers":         (2220, "Dynamic Programming"),
    # Graph Algorithms
    "Counting_Rooms":           (1192, "Graph Algorithms"),
    "Labyrinth":                (1193, "Graph Algorithms"),
    "Building_Roads":           (1666, "Graph Algorithms"),
    "Message_Route":            (1667, "Graph Algorithms"),
    "Building_Teams":           (1668, "Graph Algorithms"),
    "Round_Trip":               (1669, "Graph Algorithms"),
    "Monsters":                 (1194, "Graph Algorithms"),
    "Shortest_Routes_I":        (1671, "Graph Algorithms"),
    "Shortest_Routes_II":       (1672, "Graph Algorithms"),
    "High_Score":               (1673, "Graph Algorithms"),
    "Flight_Discount":          (1195, "Graph Algorithms"),
    "Cycle_Finding":            (1197, "Graph Algorithms"),
    "Flight_Routes":            (1196, "Graph Algorithms"),
    "Round_Trip_II":            (1678, "Graph Algorithms"),
    # String Algorithms
    "Word_Combinations":        (1731, "String Algorithms"),
    "String_Matching":          (1753, "String Algorithms"),
    "Finding_Borders":          (1732, "String Algorithms"),
    "Finding_Periods":          (1733, "String Algorithms"),
    "Minimal_Rotation":         (1734, "String Algorithms"),
    "Longest_Palindrome":       (1111, "String Algorithms"),
    "Required_Substring":       (1112, "String Algorithms"),
}

CSES_BASE_URL = "https://cses.fi/problemset/task/"


# ── Helpers ────────────────────────────────────────────────────────────────────
def friendly_name(stem: str) -> str:
    return stem.replace("_", " ")


def get_problem_info(stem: str):
    """Return (task_id, category) or (None, 'Unknown') for unrecognised files."""
    return CSES_PROBLEMS.get(stem, (None, "Unknown"))


# ── Scan repo root ─────────────────────────────────────────────────────────────
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

problems = []
for f in sorted(os.listdir(repo_root)):
    if not f.endswith(".cpp"):
        continue
    stem = f.replace(".cpp", "")
    task_id, category = get_problem_info(stem)
    problems.append({
        "file":     f,
        "name":     friendly_name(stem),
        "task_id":  task_id,
        "category": category,
    })

# Count by category
category_counts = {}
for p in problems:
    category_counts[p["category"]] = category_counts.get(p["category"], 0) + 1
total = len(problems)


# ── Table generators ───────────────────────────────────────────────────────────
def gen_stats_block():
    rows = ["| Category | Solved |", "|:---|:---:|"]
    for cat, count in sorted(category_counts.items()):
        rows.append(f"| {cat} | **{count}** |")
    rows.append(f"| **Total** | **{total}** |")
    return '<div align="center">\n\n' + "\n".join(rows) + "\n\n</div>"


def gen_problems_table():
    rows = [
        "| # | Problem | Category | Solution |",
        "|:---:|:---|:---|:---:|",
    ]
    for i, p in enumerate(problems, 1):
        name = p["name"]
        cat  = p["category"]
        f    = p["file"]
        if p["task_id"]:
            link = f"[{name}]({CSES_BASE_URL}{p['task_id']})"
        else:
            link = name   # no known task ID yet — plain text
        rows.append(f"| {i} | {link} | {cat} | [Code]({f}) |")
    return "\n".join(rows)


# ── Patch README.md ────────────────────────────────────────────────────────────
readme_path = os.path.join(repo_root, "README.md")

with open(readme_path, "r", encoding="utf-8") as fh:
    content = fh.read()


def replace_section(text: str, tag: str, new_body: str) -> str:
    pattern = rf"(<!-- {tag}_START -->).*?(<!-- {tag}_END -->)"
    return re.sub(pattern, rf"\1\n{new_body}\n\2", text, flags=re.DOTALL)


content = replace_section(content, "AUTO_STATS",  gen_stats_block())
content = replace_section(content, "CSES_TABLE",  gen_problems_table())

# Also patch the solved count badge in the shields.io URL
content = re.sub(
    r"(img\.shields\.io/badge/Solved-)\d+",
    rf"\g<1>{total}",
    content,
)

with open(readme_path, "w", encoding="utf-8") as fh:
    fh.write(content)

print(f"✅ README updated — {total} problems across {len(category_counts)} categories")
