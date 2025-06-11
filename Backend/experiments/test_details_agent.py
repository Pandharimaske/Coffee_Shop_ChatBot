from Backend.agents.details_agent import DetailsAgent

if __name__ == "__main__":
    agent = DetailsAgent()

    # Example query - you can test any query you want here
    user_query = "is Latte available?"

    response = agent.get_response(user_query)

    print("Response content:")
    print(response["content"])


    """python -m Backend.experiments.test_details_agent"""
