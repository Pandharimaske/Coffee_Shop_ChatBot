from langchain_core.runnables import Runnable
from langchain_core.messages import HumanMessage, AIMessage
from Backend.graph.states import CoffeeAgentState
from Backend.prompts.response_prompt import refinement_prompt
from Backend.utils.util import load_llm

class ResponseNode(Runnable):
    def __init__(self):
        self.llm = load_llm()
        self.chain = refinement_prompt | self.llm

    def invoke(self , state: CoffeeAgentState , config=None) -> CoffeeAgentState:

        # Compose prompt
        inputs = {
            "user_input": state["user_input"],
            "agent_response": state["response_message"],
            "state": str(state)
        }

        refined_response = self.chain.invoke(inputs).content
        state["response_message"] = refined_response

        # if "messages" not in state or state["messages"] is None:
        #     state["messages"] = []


        # Append to message history
        state["messages"] = [HumanMessage(content=state["user_input"]),AIMessage(content=state["response_message"])] + state["messages"]
    
        return CoffeeAgentState(**state)