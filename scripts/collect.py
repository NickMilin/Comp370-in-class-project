import requests
import os.path
import json

script_dir = os.path.dirname(__file__)
raw_path = os.path.join(script_dir, "..", "data", "raw")

authors = {
    "george_orwell": "OL118077A",
    "roald_dahl": "OL34184A"
}

def main():
    
    for key, item in authors.items():
        print(f"Collecting data for {key}...")
        authour_books_url = f"https://openlibrary.org/authors/{item}/works.json" 
        r = requests.get(authour_books_url)
        books_data = r.json()

        fname = os.path.join(script_dir, "..", "data", "raw", f"author_{item}_works.json")
        with open(os.path.join(raw_path, fname), "w") as f:
            json.dump(books_data, f, indent=4)

if __name__ == "__main__":
    main()