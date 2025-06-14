import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableSequence
from Backend.pydantic_schemas.ordertakingagents_tools_schemas import OrderDetails
from Backend.prompts.order_taking_prompt import order_prompt
from Backend.utils.logger import logger
from Backend.Tools.detailsagents_tools.availability import check_availability_tool
from Backend.Tools.detailsagents_tools.get_price import get_price_tool
from Backend.Tools.detailsagents_tools.retriever_tool import rag_tool
from Backend.Tools.ordertakingagents_tools.total import calculate_final_price_tool

load_dotenv()

class OrderTakingAgent:
    def __init__(self):
        base_llm = ChatGroq(
            model_name=os.getenv("GROQ_MODEL_NAME"),
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        llm = base_llm.bind_tools([
            check_availability_tool,
            get_price_tool,
            rag_tool , 
            calculate_final_price_tool
        ])

        self.chain = order_prompt | llm.with_structured_output(OrderDetails)
        logger.info("OrderAgent initialized")

    def get_response(self, user_input: str) -> dict:
        try:
            logger.info(f"User input: {user_input}")
            result = self.chain.invoke({"input": user_input})
            logger.info(f"Order details: {result}")

            order_summary_lines = []
            for item in result.items:
                line = f"{item['quantity']} x {item['item']}"
                if item.get('preferences'):
                    pref_str = "; ".join(f"{k}: {v}" for k, v in item['preferences'].items())
                    line += f" (Preferences: {pref_str})"
                order_summary_lines.append(line)
            order_summary = "\n".join(order_summary_lines)
            print("\n📝 Order Preview:")
            print(order_summary)
            confirm = input("\n✅ Confirm this order? (yes/no): ").strip().lower()
            if confirm != "yes":
                return {
                    "role": "assistant",
                    "content": "Okay, I’ve canceled that order. Let me know if you’d like to make changes.",
                    "memory": {
                        "agent": "order_taking_agent",
                        "order_items": [],
                        "total": 0
                    }
                }

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
                "agent": "order_taking_agent",
                "order_items": [],
                "total": 0
            }