from langchain.prompts import PromptTemplate

order_prompt = PromptTemplate(
    input_variables=["input"],
    template="""
You are an assistant at a coffee shop. Extract the order details from the customer's message.

Customer: {input}

Return the response in this JSON format:
{
  "items": [{"item": "Latte", "quantity": 2}, {"item": "Muffin", "quantity": 1}],
  "total": <calculate total price using menu prices>
}
"""
)