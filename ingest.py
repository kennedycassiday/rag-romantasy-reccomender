import json
import sys
import re

def load_seed(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, list) or len(data) == 0:
        print("ERROR: Seed file must be a non-empty JSON array.", file=sys.stderr)
        sys.exit(1)
    return data

def clean_text(t):
    if not t:
        return ""
    t = re.sub(r"<.*?>", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def main():
    try:
        books = load_seed("data/books_seed.json")
        print(f"✅ Successfully loaded {len(books)} books")

        # Show a sample book
        if books:
            sample = books[0]
            print(f"📖 Sample book: {sample['title']}")
            print(f"👤 Author: {', '.join(sample['authors'])}")
            print(f"⭐ Rating: {sample['rating']}")
            print(f"🔥 Spice Level: {sample['spice_level']}")

    except SystemExit:
        # This happens when sys.exit(1) is called
        print("❌ Failed to load book data")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
