import os.path
import json
import sys
import argparse
from collections import OrderedDict


script_dir = os.path.dirname(__file__)

authors = {
    "george_orwell": "OL118077A",
    "roald_dahl": "OL34184A"
}


def read_theme_counts(path):
    """Read a JSON file and return a dict of theme->count.

    If the file contains a mapping, return it. If it contains a list,
    return a frequency mapping. Otherwise try reasonable fallbacks.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, 'r') as f:
        data = json.load(f)

    if isinstance(data, dict):
        # assume values are counts
        try:
            return {str(k): int(v) for k, v in data.items()}
        except Exception:
            # fallback: treat keys as themes with implicit count 1
            return {str(k): 1 for k in data.keys()}

    if isinstance(data, list):
        counts = {}
        for item in data:
            counts[str(item)] = counts.get(str(item), 0) + 1
        return counts

    # unexpected shape
    return {str(data): 1}


def top_n(counts, n):
    return OrderedDict(sorted(counts.items(), key=lambda kv: -kv[1])[:n])


def percent(count, total):
    return f"{(count/total*100):5.1f}%" if total else "  0.0%"


def print_top_list(author_label, counts_map):
    total = sum(counts_map.values())
    print(f"{author_label} — top {len(counts_map)} themes (total tags: {total})")
    print("-" * 60)
    for theme, cnt in counts_map.items():
        print(f"{cnt:4d}  {percent(cnt, total)}  {theme}")
    print()


def print_side_by_side(table_themes, left_label, left_counts, right_label, right_counts):
    # compute totals
    left_total = sum(left_counts.values())
    right_total = sum(right_counts.values())

    # compute column widths
    theme_width = min(max((len(t) for t in table_themes), default=10), 50)
    left_col = max(len(left_label), 8)
    right_col = max(len(right_label), 8)

    title = f"Top themes comparison ({left_label} vs {right_label})"
    print(title)
    print("=" * len(title))

    header = f"{'Theme':{theme_width}}  {left_label:>{left_col}}   {right_label:>{right_col}}"
    print(header)
    print("-" * len(header))

    for theme in table_themes:
        lcnt = left_counts.get(theme, 0)
        rcnt = right_counts.get(theme, 0)
        lperc = percent(lcnt, left_total)
        rperc = percent(rcnt, right_total)
        left_cell = f"{lcnt:4d} {lperc}"
        right_cell = f"{rcnt:4d} {rperc}"
        print(f"{theme:{theme_width}}  {left_cell:>{left_col+7}}   {right_cell:>{right_col+7}}")
    print()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare top themes between authors")
    parser.add_argument("-n", "--top", type=int, default=10, help="Top N themes to compare per author")
    args = parser.parse_args(argv)

    # load theme counts for each author
    theme_counts = {}
    for label, aid in authors.items():
        fname = os.path.join(script_dir, "..", "data", "themes", f"author_{aid}_themes.json")
        try:
            counts = read_theme_counts(fname)
        except FileNotFoundError:
            print(f"Warning: themes file not found for {label}: {fname}")
            counts = {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for {label}: {e}")
            counts = {}
        theme_counts[label] = counts

    # per-author top lists
    tops = {label: top_n(counts, args.top) for label, counts in theme_counts.items()}

    # print header
    heading = "Theme comparison report"
    print("\n" + heading)
    print("=" * len(heading) + "\n")

    for label, counts in tops.items():
        print_top_list(label, counts)

    # side-by-side: union of top themes from both authors
    labels = list(tops.keys())
    if len(labels) >= 2:
        left, right = labels[0], labels[1]
        union_themes = list(OrderedDict.fromkeys(list(tops[left].keys()) + list(tops[right].keys())))
        # sort union by max count across authors (desc)
        union_themes.sort(key=lambda t: -(theme_counts[left].get(t, 0) + theme_counts[right].get(t, 0)))
        print_side_by_side(union_themes, left, theme_counts[left], right, theme_counts[right])

        # shared and unique among the top-N sets
        left_set = set(tops[left].keys())
        right_set = set(tops[right].keys())
        shared = left_set & right_set
        left_unique = left_set - right_set
        right_unique = right_set - left_set

        def _print_list(title, items):
            print(title)
            print("-" * len(title))
            if not items:
                print("(none)\n")
                return
            for t in sorted(items):
                l = theme_counts[left].get(t, 0)
                r = theme_counts[right].get(t, 0)
                print(f"  - {t}  ({left}: {l}, {right}: {r})")
            print()

        _print_list(f"Shared top-{args.top} themes ({len(shared)})", shared)
        _print_list(f"Top-{args.top} unique to {left} ({len(left_unique)})", left_unique)
        _print_list(f"Top-{args.top} unique to {right} ({len(right_unique)})", right_unique)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled error: {e}", file=sys.stderr)
        raise