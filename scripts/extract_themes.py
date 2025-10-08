import os.path
import json
import csv
script_dir = os.path.dirname(__file__)
raw_path = os.path.join(script_dir, "..", "data", "raw")

authors = {
    "george_orwell": "OL118077A",
    "roald_dahl": "OL34184A"
}

def main():

    for key, item in authors.items():
        
        fname = os.path.join(script_dir, "..", "data", "raw", f"author_{item}_works.json")
        with open(fname, 'r') as file:
            data = json.load(file)
        
        themes = dict()
        
        entries = data["entries"]
        for entry in entries:
            if "subjects" in entry:
                for subject in entry["subjects"]:
                    themes[subject] = themes.get(subject, 0) + 1


        # prepare output directory
        themes_dir = os.path.join(script_dir, "..", "data", "themes")
        os.makedirs(themes_dir, exist_ok=True)

        fname = os.path.join(themes_dir, f"author_{item}_themes.csv")
        fieldnames = ["theme", "count"]

        # convert themes dict to list of dict rows and sort by count desc
        rows = [
            {"theme": theme, "count": count}
            for theme, count in sorted(themes.items(), key=lambda kv: -kv[1])
        ]

        with open(fname, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    main()