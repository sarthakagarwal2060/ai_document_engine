import chromadb

class DocVectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="repo_docs")

    def upsert_doc(self, doc_id, text, metadata=None, unit=None):
        """Insert or update a documentation chunk."""
        if unit:
            metadata = {
                "unit_type": unit.unit_type,
                "name": unit.name,
                "file_path": doc_id,
            }
        
        if metadata is None:
            metadata = {}
            
        self.collection.upsert(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def search(self, query, n_results=3):
        """Retrieve relevant documentation chunks for chat."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []

    def search_with_citations(self, query, n_results=10):
        """Retrieve relevant documentation chunks AND their metadata for citations."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results or not results['documents']:
            return [], []
            
        return results['documents'][0], results['metadatas'][0]