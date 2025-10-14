import json
import sys
import re
# import chromadb
# from openai import OpenAI

EMBED_MODEL = "text-embedding-3-small"
CHROMA_DIR = "db"
COLLECTION_NAME = "romantasy"

REQUIRED_FIELDS = [
    "id", "title", "authors", "description",
    "genres", "tropes", "spice_level", "source_url",
    "rating", "year"
]

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

def validate_book(x):
    issues = []

    for f in REQUIRED_FIELDS:
        if f not in x:
            issues.append(f"missing field: {f}")

    if "title" in x and not isinstance(x["title"], str):
        issues.append("title must be a string")

    if "authors" in x:
        a = x["authors"]
        if not isinstance(a, list) or not all(isinstance(s, str) for s in a):
            issues.append("authors must be a list[str]")

    if "description" in x:
        d = x["description"] or ""
        if not isinstance(d, str) or len(d.strip()) < 40:
            issues.append("description must be a string with at least 40 chars")

    if "genres" in x:
        g = x["genres"]
        if not isinstance(g, list) or not all(isinstance(s, str) for s in g):
            issues.append("genres must be a list[str]")

    if "tropes" in x:
        t = x["tropes"]
        if not isinstance(t, list) or not all(isinstance(s, str) for s in t):
            issues.append("tropes must be a list[str]")

    if "spice_level" in x:
        if x["spice_level"] not in {"low", "medium", "high", "unknown"}:
            issues.append("spice_level must be one of: low|medium|high|unknown")

    if "source_url" in x and not isinstance(x["source_url"], str):
        issues.append("source_url must be a string (URL)")

    return issues

def build_embed_text(book):
    title = book["title"]
    description = book["description"]
    genres = ", ".join(book["genres"])
    tropes = ", ".join(book["tropes"])
    spice = book["spice_level"]
    return f"Title: {title}\nDescription: {description}\nGenres: {genres}\nTropes: {tropes}\nSpice: {spice}"

def batch(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i: i + size]

def main():
    path = "data/books_seed.json"
    reset = True
    batch_size = 64

    # if not os.getenv("OPENAI_API_KEY"):
    #     print("ERROR: set OPENAI_API_KEY in your environment.", file=sys.stderr)
    #     sys.exit(1)

    try:
        #Load data
        books = load_seed(path)
        print(f"Successfully loaded {len(books)} books")

        #Clean data
        cleaned = []
        skipped = 0

        for book in books:
            book["title"] = (book.get("title") or "").strip()
            book["description"] = clean_text(book.get("description") or "")

        #Validate data:
            issues = validate_book(book)
            if issues:
                skipped += 1
                print(f"Skipping {book.get('id')} - {book.get('title')}:")
                for issue in issues:
                    print(f"    • {issue}")
                continue
            cleaned.append(book)
        print(f"Cleaned: {len(cleaned)}, Skipped: {skipped}.")

    # Prepare IDs, documents (embedding text), and metadata (for filters/reranking)
    ids = [book['id'] for book in cleaned]
    documents = [build_embed_text(book) for book in cleaned]
    metadatas = [{
        "title": book["title"],
        "authors": book["authors"],
        "genres": book["genres"],
        "tropes": book["tropes"],
        "spice": book.["spice_level"],
        "url": book["source_url"],
        "rating": book["rating"],
        "year": book["year"]
    } for book in cleaned]

    # Initialize OpenAI + Chroma
    client = OpenAI()
    chroma = chromadb.PersistentClient(path=CHROMA_DIR)


        #Show sample book
        if books:
            sample = books[0]
            print(f"Sample book: {sample['title']}")
            print(f"Author: {', '.join(sample['authors'])}")
            print(f"Rating: {sample['rating']}")
            print(f"Spice Level: {sample['spice_level']}")

    except SystemExit:
        print("Failed to load book data")
    except Exception as e:
        print(f"Unexpected error: {e}")



if __name__ == "__main__":
    main()
