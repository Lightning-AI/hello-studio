import os, json
import litserve as ls
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util

class SimpleRAGAPI(ls.LitAPI):
    def setup(self, device):
        # Initialize embedder and OpenAI client
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        oai_key = os.environ.get("OAI_API_KEY", "your-openai-key")
        self.llm = OpenAI(api_key=oai_key)

        # Load documents from disk
        self.docs = []
        folder = "scraped_data"
        for file in os.listdir(folder):
            try:
                with open(os.path.join(folder, file)) as f:
                    data = json.load(f)
                    self.docs.append({"text": data["text"], "url": data["url"]})
            except Exception as e:
                print(f"⚠️ Skipping {file}: invalid JSON - {e}")

        # Precompute embeddings
        texts = [d["text"] for d in self.docs]
        self.embeddings = self.embedder.encode(texts, convert_to_tensor=True)

    def decode_request(self, request):
        return request["query"]

    def predict(self, query):
        print('-' * 80)
        print(f'RAG question: {query}')
        # Embed the query and find top matches
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, self.embeddings, top_k=3)[0]
        context = "\n\n".join(self.docs[hit["corpus_id"]]["text"][:1000] for hit in hits)

        # Compose prompt and query OpenAI
        prompt = f"Answer this using the context below.\n\nContext:\n{context}\n\nQuestion: {query}"
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        print(f'RAG answer: {answer}')
        return answer

    def encode_response(self, output):
        return {"answer": output}

if __name__ == "__main__":
    server = ls.LitServer(SimpleRAGAPI(), accelerator="auto", max_batch_size=1)
    server.run(port=8000, generate_client_file=False)
