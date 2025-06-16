import os
from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from Backend.utils.logger import logger
from Backend.schemas.agents_schemas import AgentDecision
from Backend.prompts.classification_prompt import classification_prompt
from typing import TypedDict, Literal

# Load environment variables
load_dotenv()

class ClassificationAgentOutput(TypedDict):
    target_agent: str
    response_message: str
    chain_of_thought: str

class ClassificationAgent:
    """ClassificationAgent classifies the user input into coffee shop-related tasks."""

    def __init__(self):
        self.client = ChatGroq(
            model_name=os.getenv("GROQ_MODEL_NAME"),
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        self.prompt = classification_prompt
        self.output_parser = PydanticOutputParser(pydantic_object=AgentDecision)

        self.chain = (
            self.prompt
            | self.client
            | self.output_parser
        )

        logger.info("ClassificationAgent initialized")

    def get_response(self, user_input: str) -> ClassificationAgentOutput:
        try:
            logger.debug(f"Invoking classification chain with input: {user_input}")
            result = self.chain.invoke({"user_input": user_input})
            logger.debug(f"Classification result: {result}")
            return {
                "target_agent": result.target_agent,
                "response_message": result.response_message or "Got it. What would you like to know next?",
                "chain_of_thought": result.chain_of_thought
            }

        except Exception as e:
            import traceback
            logger.error("ClassificationAgent error:\n" + traceback.format_exc())
            return {
                "target_agent": "unknown",
                "response_message": "Something went wrong while classifying. Please try again.",
                "chain_of_thought": "Error during classification"
            }

    def __call__(self, user_input: str) -> ClassificationAgentOutput:
        return self.get_response(user_input)