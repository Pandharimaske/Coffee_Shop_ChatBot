from langchain.output_parsers import PydanticOutputParser
from Backend.utils.logger import logger
from Backend.utils.util import load_llm
from Backend.schemas.agents_schemas import AgentDecision
from Backend.prompts.classification_prompt import classification_prompt
from Backend.schemas.state_schema import ClassificationAgentState


class ClassificationAgent:
    """ClassificationAgent classifies the user input into coffee shop-related tasks."""

    def __init__(self):
        self.llm = load_llm()

        self.prompt = classification_prompt
        self.output_parser = PydanticOutputParser(pydantic_object=AgentDecision)

        self.chain = (
            self.prompt
            | self.llm
            | self.output_parser
        )

        logger.info("ClassificationAgent initialized")

    def get_response(self, user_input: str) -> ClassificationAgentState:
        try:
            logger.debug(f"Invoking classification chain with input: {user_input}")
            result = self.chain.invoke({"user_input": user_input})
            logger.debug(f"Classification result: {result}")
            return {
                "target_agent": result.target_agent,
                "response_message": result.response_message or "Got it. What would you like to know next?",
            }

        except Exception as e:
            import traceback
            logger.error("ClassificationAgent error:\n" + traceback.format_exc())
            return {
                "target_agent": "unknown",
                "response_message": "Something went wrong while classifying. Please try again.",
            }

    def __call__(self, user_input: str) -> ClassificationAgentState:
        return self.get_response(user_input)