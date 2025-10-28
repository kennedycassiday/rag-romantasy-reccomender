import sys
import chromadb
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

EMBED_MODEL = "text-embedding-3-small"
CHROMA_DIR = "db"
COLLECTION_NAME = "romantasy"

client = OpenAI()
chroma = chromadb.PersistentClient(path=CHROMA_DIR)
coll = chroma.get_or_create_collection(name=COLLECTION_NAME)
default_query = "enemies to lovers fae courts medium spice"

#Get user query
if len(sys.argv) > 1:
    query = " ".join(sys.argv[1:])
else:
    query = default_query
print(f"Query: {query}")

#Embed query
resp = client.embeddings.create(model=EMBED_MODEL, input=[query])
query_vector = resp.data[0].embedding

#Search Chroma
results = coll.query(query_embeddings=[query_vector], n_results=3)

#Display results
for i, meta in enumerate(results["metadatas"][0], start=1):
    title = meta.get("title")
    spice = meta.get("spice")
    rating = meta.get("rating")
    url = meta.get("url")
    print(f"{i}. {title}, {spice} spice, {rating} rating")
    print(f"URL: {url}")
