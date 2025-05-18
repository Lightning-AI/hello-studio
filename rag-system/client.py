import requests
import argparse

def query_rag_server(query, url="http://localhost:8000/predict"):
    try:
        response = requests.post(url, json={"query": query})
        response.raise_for_status()
        data = response.json()
        print("\n📚 Answer:")
        print(data.get("answer", "[No answer in response]"))
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str, help="Your question for the RAG server")
    parser.add_argument("--url", type=str, default="http://localhost:8000/predict", help="RAG server endpoint")
    args = parser.parse_args()

    query_rag_server(args.query, url=args.url)
