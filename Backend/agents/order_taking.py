import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableSequence
from langchain.memory import ConversationBufferMemory
from Backend.pydantic_schemas.agents_schemas import OrderDetails
from prompts.order_taking_prompt import order_prompt
from utils.logger import logger

load_dotenv()

class OrderAgent:
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        llm = ChatGroq(
            model_name=os.getenv("GROQ_MODEL_NAME"),
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        self.chain = order_prompt | llm.with_structured_output(OrderDetails)
        logger.info("OrderAgent initialized")

    def get_response(self, user_input: str) -> dict:
        try:
            logger.info(f"User input: {user_input}")
            result = self.chain.invoke({"input": user_input})
            logger.info(f"Order details: {result}")

            order_summary = ", ".join([f"{item['quantity']} x {item['item']}" for item in result.items])
            return {
                "role": "assistant",
                "content": f"Great! I’ve added the following to your order: {order_summary}. Anything else?",
                "memory": {
                    "agent": "order_taking_agent",
                    "order_items": result.items,
                    "total": result.total
                }
            }

        except Exception as e:
            logger.error(f"OrderAgent error: {e}")
            return {
                "role": "assistant",
                "content": "Sorry, I couldn’t process your order. Could you please repeat it?",
                "memory": {
                    "agent": "order_taking_agent",
                    "order_items": [],
                    "total": 0
                }
            }