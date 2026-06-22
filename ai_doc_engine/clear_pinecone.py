import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

def clear_pinecone():
    # Connect to Pinecone using your existing .env keys
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    print(f"Connecting to Pinecone index: '{index_name}'...")
    index = pc.Index(index_name)
    
    # Wipe the database
    print("Deleting all vectors...")
    index.delete(delete_all=True)
    
    print("✅ Successfully cleared all documentation from Pinecone!")

if __name__ == "__main__":
    clear_pinecone()
