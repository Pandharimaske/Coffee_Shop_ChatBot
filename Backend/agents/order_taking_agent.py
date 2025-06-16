from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSequence
from Backend.utils.logger import logger
from Backend.utils.util import llm
from Backend.Tools.detailsagents_tools.retriever_tool import vectorstore
from Backend.schemas.state_schema import OrderInput , OrderTakingAgentState
from Backend.prompts.order_taking_prompt import parse_prompt

# ---- Agent Class ----
class OrderTakingAgent:
    def __init__(self):
        self.llm = llm
        
        self.parser = PydanticOutputParser(pydantic_object=OrderInput)

        self.parse_prompt = parse_prompt

        # ✅ Properly format prompt with required input variables
        self.llm_parser_chain: RunnableSequence = (
            self.parse_prompt.partial(format_instructions=self.parser.get_format_instructions())
            | self.llm
            | self.parser
        )

        logger.info("OrderAgent initialized")

    def parse_user_input(self, user_input: str) -> OrderInput:
        return self.llm_parser_chain.invoke({"user_input": user_input})

    def process_order(self, order: OrderInput) -> tuple[str, OrderInput]:
        items = order.items
        available_items = []
        unavailable_items = []
        total = 0
        summary_lines = []

        for item in items:
            name = item.name.strip().title()
            results = vectorstore.similarity_search(
                query="",
                k=1,
                filter={"name": {"$eq": name}}
            )

            if results:
                doc = results[0]
                price = doc.metadata.get("price", 0.0)
                line_total = item.quantity * price
                available_items.append(item)
                total += line_total
                summary_lines.append(f"✅ {name} x {item.quantity} @ ${price} = ${line_total}")
            else:
                unavailable_items.append(name)

        summary = "\n".join(summary_lines)

        if unavailable_items:
            unavailable = "\n".join(f"❌ {name}" for name in unavailable_items)
            summary += (
                f"\n\nTotal (for available items): ${total}\n\n"
                f"However, some items are not available:\n{unavailable}\n"
                f"Would you like to replace them?"
            )
        else:
            summary += f"\n\nTotal: ${total}\nShall I place the order?"

        return summary, OrderInput(items=available_items)


    def get_response(self, user_input: str) -> OrderTakingAgentState:
        try:
            logger.info(f"User input: {user_input}")
            parsed_order = self.parse_user_input(user_input)
            logger.info(f"Parsed order: {parsed_order}")
            summary, filtered_order = self.process_order(parsed_order)

            return {
                "order": filtered_order,  # ✅ only available items
                "response_message": summary
            }
        except Exception as e:
            logger.error(f"OrderAgent error: {e}")
            return {
                "order": OrderInput(items=[]),
                "response_message": "Sorry, I couldn’t process your order. Could you please rephrase it?",
            }