import requests
import os.path
import json
import argparse

script_dir = os.path.dirname(__file__)
raw_path = os.path.join(script_dir, "..", "data", "raw")

def main():

    parse = argparse.ArgumentParser()
    parse.add_argument("author")
    args = parse.parse_args()
    author_name = args.author.replace(" ", "%20")

    # author_name = r"octavia%20butler"

    # Get authour key
    query_url = "https://openlibrary.org/search/authors.json?q=" + author_name
    r = requests.get(query_url)
    author_data = r.json()
    author_key = author_data["docs"][0]["key"]
    print("Authour key:", author_key)

    # Query for the books
    books_url = f"https://openlibrary.org/authors/{author_key}/works"
    r = requests.get(query_url)
    books_data = r.json()

    fname = f"author_{author_key}_works.json"
    with open(os.path.join(raw_path, fname), "w") as f:
        json.dump(books_data, f, indent=4)

if __name__ == "__main__":
    main()