import os
import json
import pandas as pd
from copy import deepcopy
from dotenv import load_dotenv

from Backend.prompts.reccomendation_prompt import classification_prompt, response_prompt

load_dotenv()

class RecommendationAgent:
    def __init__(self, apriori_recommendation_path, popular_recommendation_path):

        # Load recommendation data
        with open(apriori_recommendation_path, 'r') as file:
            self.apriori_recommendations = json.load(file)

        self.popular_recommendations = pd.read_csv(popular_recommendation_path)
        self.products = self.popular_recommendations['product'].tolist()
        self.product_categories = self.popular_recommendations['product_category'].tolist()

        # Chains
        self.classification_chain = classification_prompt | self.client
        self.response_chain = response_prompt | self.client

    def get_apriori_recommendation(self, products, top_k=5):
        recommendation_list = []
        for product in products:
            if product in self.apriori_recommendations:
                recommendation_list += self.apriori_recommendations[product]

        recommendation_list = sorted(recommendation_list, key=lambda x: x['confidence'], reverse=True)

        recommendations = []
        recommendations_per_category = {}
        for recommendation in recommendation_list:
            if recommendation in recommendations:
                continue

            product_category = recommendation['product_category']
            if recommendations_per_category.get(product_category, 0) >= 2:
                continue

            recommendations_per_category[product_category] = recommendations_per_category.get(product_category, 0) + 1
            recommendations.append(recommendation['product'])

            if len(recommendations) >= top_k:
                break

        return recommendations

    def get_popular_recommendation(self, product_categories=None, top_k=5):
        df = self.popular_recommendations
        if isinstance(product_categories, str):
            product_categories = [product_categories]

        if product_categories:
            df = df[df['product_category'].isin(product_categories)]

        df = df.sort_values(by='number_of_transactions', ascending=False)
        return df['product'].tolist()[:top_k] if not df.empty else []

    def recommendation_classification(self, messages):
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        response = self.classification_chain.invoke({
            "input": messages[-1]['content'],
            "products": ", ".join(self.products),
            "categories": ", ".join(self.product_categories)
        })

        try:
            parsed = json.loads(response)
            return {
                "recommendation_type": parsed.get("recommendation_type"),
                "parameters": parsed.get("parameters", [])
            }
        except json.JSONDecodeError:
            return {
                "recommendation_type": None,
                "parameters": []
            }

    def get_response(self, messages):
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        else:
            messages = deepcopy(messages)

        classification = self.recommendation_classification(messages)
        recommendation_type = classification.get('recommendation_type')
        parameters = classification.get('parameters', [])

        if recommendation_type == "apriori":
            recommendations = self.get_apriori_recommendation(parameters)
        elif recommendation_type == "popular":
            recommendations = self.get_popular_recommendation()
        elif recommendation_type == "popular by category":
            recommendations = self.get_popular_recommendation(parameters)
        else:
            recommendations = []

        if not recommendations:
            return {
                "role": "assistant",
                "content": "Sorry, I can't help with that. Can I help you with your order?",
                "memory": {"agent": "recommendation_agent"}
            }

        response = self.response_chain.invoke({
            "input": messages[-1]['content'],
            "recommendations": ", ".join(recommendations)
        })

        return {
            "role": "assistant",
            "content": response,
            "memory": {"agent": "recommendation_agent"}
        }