# test_pipeline.py

import os
from dotenv import load_dotenv
from rag_pipeline import CoffeeShopRAGPipeline
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec

def main():
    load_dotenv()

    # Load your Pinecone and vectorstore
    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "coffee-products"
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    index = pc.Index(index_name)

    vectorstore = PineconeVectorStore(
        index=index,  # Pinecone v4 index
        embedding=embedding_model,
        text_key="text",  # your metadata should have "text"
    )

    # Initialize pipeline
    pipeline = CoffeeShopRAGPipeline(
        vectorstore=vectorstore,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    # Run test query
    query = "Show me highly rated coffee under 5 dollars"
    final_docs = pipeline.run_pipeline(query)

    # Print results
    print(f"\n=== FINAL RESULTS for query: '{query}' ===")
    for i, doc in enumerate(final_docs):
        print(f"\nResult #{i+1}")
        print(f"Name: {doc.metadata.get('name')}")
        print(f"Category: {doc.metadata.get('category')}")
        print(f"Price: {doc.metadata.get('price')}")
        print(f"Rating: {doc.metadata.get('rating')}")
        print(f"Text: {doc.page_content}")

if __name__ == "__main__":
    main()