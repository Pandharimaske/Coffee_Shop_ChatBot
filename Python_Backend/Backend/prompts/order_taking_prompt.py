from langchain.prompts import PromptTemplate

parse_prompt = PromptTemplate.from_template(
            """
You are a helpful assistant for a coffee shop.

Your task is to extract a structured order from the customer's message.

User message:
"{user_input}"

Format Instructuions:
{format_instructions}
"""
)
