import os
from copy import deepcopy
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from Backend.utils.logger import logger

from Backend.pydantic_schemas.agents_schemas import AgentDecision  # Ensure path is correct
from Backend.prompts.classification_prompt import classification_prompt

# Load environment variables
load_dotenv()

class ClassificationAgent:
    def __init__(self):
        # Set up the model client
        self.client = ChatGroq(
            model_name=os.getenv("GROQ_MODEL_NAME"),
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        # Classification prompt
        self.prompt = classification_prompt

        # Output parser
        self.output_parser = PydanticOutputParser(pydantic_object=AgentDecision)

        # ✅ Build chain correctly
        self.chain = (
            self.prompt
            | self.client
            | self.output_parser
        )

    def get_response(self, messages: list[dict]):
        # Use recent messages for context
        messages = deepcopy(messages)
        recent_messages = messages[-3:]
        input_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])

        # Run the chain and return postprocessed output
        chain_output = self.chain.invoke({"input": input_text})
        logger.info(f"Input: {input_text}")
        logger.info(f"Decision: {chain_output}")
        return self.postprocess(chain_output)

    def postprocess(self, output):
        if isinstance(output, AgentDecision):
            decision = output.decision
            message = output.message
        else:
            decision = output['decision']
            message = output.get('message', '')

        return {
            "role": "assistant",
            "content": message,
            "agent": "classification_agent",
            "classification_output": {
                "classification_decision": decision,
                "chain_of_thought": output.chain_of_thought
            }
        }
    