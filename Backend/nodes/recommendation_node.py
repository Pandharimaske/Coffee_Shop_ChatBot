from langchain_core.runnables import Runnable

class RecommendationAgentNode(Runnable):
    def __init__(self, recommendation_agent):
        self.recommendation_agent = recommendation_agent

    def invoke(self, state: dict, config=None) -> dict:
        messages = state.get("messages") or state.get("input")

        if not messages:
            return {
                "input": messages,
                "agent": "recommendation_agent",
                "content": "No user message provided to generate a recommendation."
            }

        response = self.recommendation_agent.get_response(messages)

        return {
            "input": messages,
            "agent": "recommendation_agent",
            "content": response["content"],
            "memory": response.get("memory", {})
        }