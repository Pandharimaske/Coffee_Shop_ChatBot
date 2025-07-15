from langchain_core.runnables import Runnable
from langchain_core.messages import HumanMessage, AIMessage
from Backend.graph.states import CoffeeAgentState
from Backend.prompts.response_prompt import refinement_prompt
from Backend.utils.util import load_llm
from Backend.utils.summary_memory import save_messages , save_order

class ResponseNode(Runnable):
    def __init__(self):
        self.llm = load_llm()
        self.chain = refinement_prompt | self.llm

    def invoke(self , state: CoffeeAgentState , config=None) -> CoffeeAgentState:

        user_id = config["configurable"]["user_id"]

        inputs = {
            "user_input": state["user_input"],
            "agent_response": state["response_message"],
            "state": str(state)
        }

        refined_response = self.chain.invoke(inputs).content
        state["response_message"] = refined_response
        state["messages"] = [HumanMessage(content=state["user_input"]),AIMessage(content=state["response_message"])] + state["messages"]

        save_messages(id = user_id , messages=state["messages"])
        save_order(id = user_id , items=state["order"] , final_price=state["final_price"])
    
        return CoffeeAgentState(**state)