import json
import pandas as pd
from src.schemas.agents_schemas import CategoryPrediction
from src.utils.util import call_llm
class RecommendationAgent:
    def __init__(self, apriori_recommendation_path, popular_recommendation_path):

        # Load recommendation data
        with open(apriori_recommendation_path, 'r') as file:
            self.apriori_recommendations = json.load(file)

        self.popular_recommendations = pd.read_csv(popular_recommendation_path)
        self.products = self.popular_recommendations['product'].tolist()
        self.product_categories = self.popular_recommendations['product_category'].tolist()

    def get_apriori_recommendation(self, products, top_k=3):
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

    def get_popular_recommendation(self, user_input:str , top_k:int =5):
        product_categories = call_llm(prompt=user_input , schema=CategoryPrediction).category.value
        print(product_categories)
        recommendation_df = self.popular_recommendations
        
        if product_categories != "General":
            product_categories = [product_categories]
            recommendation_df = recommendation_df[recommendation_df['product_category'].isin(product_categories)]

        recommendation_df = recommendation_df.sort_values(by='number_of_transactions', ascending=False)
        return recommendation_df['product'].tolist()[:top_k] if not recommendation_df.empty else []