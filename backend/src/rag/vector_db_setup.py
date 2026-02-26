"""
Vector Database Setup for Coffee Shop Products (RAG folder)
This module handles:
- Loading product data
- Creating embeddings
- Upserting to Pinecone with normalized metadata

This is a direct move from the project root into `src/rag/` and kept
largely the same so other code that imports it can be updated later.
"""
import os
import pandas as pd
import dotenv
import uuid
from typing import List, Dict
from time import time
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEndpointEmbeddings

# Load environment variables
dotenv.load_dotenv()


class VectorDBSetup:
    """Handles vector database initialization and data ingestion"""
    
    def __init__(self):
        """Initialize embeddings model and Pinecone client"""
        self.embedding_model = os.getenv("EMBEDDING_MODEL")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.hf_api_key = os.getenv("HF_API_KEY")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEndpointEmbeddings(
            model=self.embedding_model,
            huggingfacehub_api_token=self.hf_api_key
        )
        
        self.index = None
        self.index_name = "coffee-products"
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for better matching
        - Converts to lowercase
        - Strips extra whitespace
        """
        return text.lower().strip()
    
    def create_product_text(self, row: pd.Series) -> str:
        """
        Create searchable text from product data
        
        Args:
            row: DataFrame row with product info
            
        Returns:
            Formatted text string for embedding
        """
        text = (
            f"{row['name']}:\n"
            f"{row['description']}\n"
            f"Ingredients: {row['ingredients']}\n"
            f"Price: ₹{row['price']}\n"
            f"Rating: {row['rating']}"
        )
        return text
    
    def load_product_data(self, file_path: str) -> pd.DataFrame:
        """
        Load product data from JSONL file
        
        Args:
            file_path: Path to products.jsonl file
            
        Returns:
            DataFrame with product data
        """
        print(f"📁 Loading data from {file_path}...")
        df = pd.read_json(file_path, lines=True)
        
        # Create searchable text field
        df['text'] = df.apply(self.create_product_text, axis=1)
        
        # Add normalized product name for exact matching
        df['name_normalized'] = df['name'].apply(self.normalize_text)
        
        print(f"✅ Loaded {len(df)} products")
        return df
    
    def create_index(self, dimension: int = 768):
        """
        Create Pinecone index if it doesn't exist
        
        Args:
            dimension: Embedding dimension (default 768 for most HF models)
        """
        print(f"🔍 Checking if index '{self.index_name}' exists...")
        
        if self.index_name not in self.pc.list_indexes().names():
            print(f"🏗️  Creating new index '{self.index_name}'...")
            self.pc.create_index(
                self.index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print("✅ Index created successfully")
        else:
            print("✅ Index already exists")
        
        self.index = self.pc.Index(self.index_name)
    
    def prepare_vectors(self, df: pd.DataFrame, batch_size: int = 100) -> List[Dict]:
        """
        Prepare vectors with embeddings and metadata in batches
        
        Args:
            df: DataFrame with product data
            batch_size: Number of texts to embed at once
            
        Returns:
            List of vector dictionaries for upsert
        """
        vectors = []
        total_rows = len(df)
        
        print(f"🔄 Generating embeddings for {total_rows} products...")
        start_time = time()
        
        # Process in batches for speed
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            texts = batch_df['text'].tolist()
            
            # Generate embeddings in batch (much faster!)
            try:
                batch_embeddings = self.embeddings.embed_documents(texts)
            except Exception as e:
                print(f"⚠️  Batch embedding failed, falling back to individual: {e}")
                batch_embeddings = [self.embeddings.embed_query(text) for text in texts]
            
            # Create vector objects
            for idx, (_, row) in enumerate(batch_df.iterrows()):
                metadata = {
                    "text": row["text"],
                    "name": row["name"],
                    "name_normalized": row["name_normalized"],  # For exact matching
                    "category": row["category"],
                    "price": float(row["price"]),
                    "rating": float(row["rating"]),
                    "ingredients": str(row["ingredients"])
                }
                
                vectors.append({
                    "id": str(uuid.uuid4()),
                    "values": batch_embeddings[idx],
                    "metadata": metadata
                })
            
            print(f"  📊 Processed {min(i+batch_size, total_rows)}/{total_rows} products")
        
        elapsed = time() - start_time
        print(f"✅ Generated {len(vectors)} embeddings in {elapsed:.2f}s")
        return vectors
    
    def upsert_vectors(self, vectors: List[Dict], batch_size: int = 100):
        """
        Upsert vectors to Pinecone in batches
        
        Args:
            vectors: List of vector dictionaries
            batch_size: Number of vectors to upsert at once
        """
        total_vectors = len(vectors)
        print(f"⬆️  Upserting {total_vectors} vectors to Pinecone...")
        start_time = time()
        
        # Upsert in batches
        for i in range(0, total_vectors, batch_size):
            batch = vectors[i:i+batch_size]
            self.index.upsert(vectors=batch)
            print(f"  📤 Upserted {min(i+batch_size, total_vectors)}/{total_vectors} vectors")
        
        elapsed = time() - start_time
        print(f"✅ Upload complete in {elapsed:.2f}s")
    
    def verify_index(self):
        """Verify the index statistics"""
        stats = self.index.describe_index_stats()
        print("\n📊 Index Statistics:")
        print(f"  Total vectors: {stats['total_vector_count']}")
        print(f"  Dimension: {stats['dimension']}")
    
    def setup_complete_pipeline(self, data_file_path: str):
        """
        Run the complete setup pipeline
        
        Args:
            data_file_path: Path to products.jsonl file
        """
        print("🚀 Starting Vector DB Setup Pipeline...\n")
        total_start = time()
        
        # Step 1: Load data
        df = self.load_product_data(data_file_path)
        
        # Step 2: Create index
        self.create_index()
        
        # Step 3: Prepare vectors
        vectors = self.prepare_vectors(df)
        
        # Step 4: Upsert to Pinecone
        self.upsert_vectors(vectors)
        
        # Step 5: Verify
        self.verify_index()
        
        total_elapsed = time() - total_start
        print(f"\n🎉 Pipeline complete in {total_elapsed:.2f}s!")


if __name__ == "__main__":
    DATA_FILE = "./data/products_data/products.jsonl"
    
    setup = VectorDBSetup()
    setup.setup_complete_pipeline(DATA_FILE)
