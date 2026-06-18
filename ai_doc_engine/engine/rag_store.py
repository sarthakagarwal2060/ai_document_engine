import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class DocVectorStore:
    def __init__(self):
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        
        # Check if index exists, else create it
        if self.index_name not in self.pc.list_indexes().names():
            print(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=384, # Match sentence-transformers all-MiniLM-L6-v2 dimension
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        
        self.index = self.pc.Index(self.index_name)
        
        # Initialize local embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def upsert_doc(self, doc_id, text, metadata=None, unit=None):
        """Embed and insert a documentation chunk into Pinecone."""
        if unit:
            metadata = {
                "unit_type": unit.unit_type,
                "name": unit.name,
                "file_path": doc_id,
                "text": text # Pinecone requires storing the text in metadata to retrieve it later!
            }
        
        if metadata is None:
            metadata = {"text": text}
        elif "text" not in metadata:
            metadata["text"] = text
            
        # Convert text to vector
        vector = self.model.encode(text).tolist()
        
        # Upsert to Pinecone
        self.index.upsert(
            vectors=[{
                "id": doc_id,
                "values": vector,
                "metadata": metadata
            }]
        )

    def search(self, query, n_results=3):
        """Retrieve relevant documentation chunks for chat."""
        # Convert query to vector
        query_vector = self.model.encode(query).tolist()
        
        results = self.index.query(
            vector=query_vector,
            top_k=n_results,
            include_metadata=True
        )
        
        if not results.matches:
            return []
            
        # Return the text from the top match
        return results.matches[0].metadata.get("text", "")

    def search_with_citations(self, query, n_results=10):
        """Retrieve relevant documentation chunks AND their metadata for citations."""
        query_vector = self.model.encode(query).tolist()
        
        results = self.index.query(
            vector=query_vector,
            top_k=n_results,
            include_metadata=True
        )
        
        if not results.matches:
            return [], []
            
        docs = []
        metas = []
        for match in results.matches:
            docs.append(match.metadata.get("text", ""))
            metas.append(match.metadata)
            
        return docs, metas

    def get_doc(self, doc_id):
        """Fetch a single document by its exact ID."""
        try:
            result = self.index.fetch(ids=[doc_id])
            if result and result.vectors and doc_id in result.vectors:
                return result.vectors[doc_id].metadata.get("text", "")
        except Exception:
            pass
        return None