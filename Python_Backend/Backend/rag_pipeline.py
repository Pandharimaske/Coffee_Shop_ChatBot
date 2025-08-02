class CoffeeShopRAGPipeline:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def retrieve(self, query):
        retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={
            "k": 3
        })
        docs = retriever.invoke(query)
        print(f"Retrieved {len(docs)} docs.")
        return docs

    def run_pipeline(self, query):
        docs = self.retrieve(query)
        return docs
    