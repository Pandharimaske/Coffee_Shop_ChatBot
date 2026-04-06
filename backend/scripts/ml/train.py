"""
Train and evaluate the HybridRecommender.
Tracks all experiments to DagsHub via MLflow.

Setup (one-time):
    export DAGSHUB_USER=your_dagshub_username
    export DAGSHUB_TOKEN=your_dagshub_token
    export DAGSHUB_REPO=coffee-shop-ml

Run:
    cd backend/
    python scripts/ml/train.py
    python scripts/ml/train.py --popularity 0.3 --apriori 0.4 --content 0.3

Then view runs at:
    https://dagshub.com/<your_username>/coffee-shop-ml/experiments
"""

import os
import sys
import json
import argparse
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import mlflow
import mlflow.sklearn
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── DagsHub / MLflow setup ────────────────────────────────────────────────────
DAGSHUB_USER  = os.getenv("DAGSHUB_USER")
DAGSHUB_TOKEN = os.getenv("DAGSHUB_TOKEN")
DAGSHUB_REPO  = os.getenv("DAGSHUB_REPO", "coffee-shop-ml")

def setup_mlflow():
    if DAGSHUB_USER and DAGSHUB_TOKEN:
        import dagshub
        dagshub.init(repo_owner=DAGSHUB_USER, repo_name=DAGSHUB_REPO, mlflow=True)
        logger.info(f"MLflow tracking → DagsHub: {DAGSHUB_USER}/{DAGSHUB_REPO}")
    else:
        # Fallback — local MLflow UI (run `mlflow ui` to view)
        mlflow.set_tracking_uri("mlruns")
        logger.warning("DAGSHUB_USER/TOKEN not set — using local MLflow tracking")

    mlflow.set_experiment("hybrid-recommender")


# ── Evaluation ────────────────────────────────────────────────────────────────
def evaluate(rec) -> dict:
    """
    Intrinsic evaluation — no labels needed.

    Metrics:
        coverage        — % of catalog recommendable
        apriori_hit_rate — % of apriori rules that resolve to known products
        avg_score       — mean recommendation score across test cases
        diversity       — avg unique categories across sample recommendations
    """
    from itertools import islice

    products = list(rec.products.keys())

    # coverage
    coverage = rec.coverage()

    # apriori hit rate
    total_rules, valid_rules = 0, 0
    for rules in rec.apriori.values():
        for rule in rules:
            total_rules += 1
            if rule["product"] in rec.products:
                valid_rules += 1
    apriori_hit_rate = valid_rules / max(total_rules, 1)

    # avg score + diversity across 5 test cases
    test_cases = [
        {"cart": ["Cappuccino"], "likes": ["sweet"], "allergies": []},
        {"cart": ["Latte"], "likes": ["chocolate"], "allergies": []},
        {"cart": [], "likes": ["spicy", "ginger"], "allergies": ["nuts"]},
        {"cart": ["Espresso shot"], "likes": [], "allergies": []},
        {"cart": [], "likes": [], "allergies": []},
    ]

    all_scores, all_categories = [], []
    for tc in test_cases:
        recs = rec.recommend(**tc, top_k=3)
        all_scores.extend([r["score"] for r in recs])
        all_categories.extend([r["category"] for r in recs])

    avg_score = sum(all_scores) / max(len(all_scores), 1)
    diversity = len(set(all_categories)) / max(len(all_categories), 1)

    return {
        "coverage": round(coverage, 4),
        "apriori_hit_rate": round(apriori_hit_rate, 4),
        "avg_recommendation_score": round(avg_score, 4),
        "category_diversity": round(diversity, 4),
        "catalog_size": rec.catalog_size(),
        "apriori_rules_count": total_rules,
    }


# ── Train ─────────────────────────────────────────────────────────────────────
def train(popularity_w: float, apriori_w: float, content_w: float):
    from src.recommender import HybridRecommender

    setup_mlflow()

    with mlflow.start_run(run_name=f"pop{popularity_w}_apr{apriori_w}_con{content_w}"):

        # ── Log params ────────────────────────────────────────────────────────
        mlflow.log_params({
            "popularity_weight": popularity_w,
            "apriori_weight":    apriori_w,
            "content_weight":    content_w,
            "model_type":        "HybridRecommender",
            "data_version":      "v1_inr_prices",
        })

        # ── Fit ───────────────────────────────────────────────────────────────
        logger.info(f"Fitting model: pop={popularity_w} apr={apriori_w} con={content_w}")
        rec = HybridRecommender(
            popularity_weight=popularity_w,
            apriori_weight=apriori_w,
            content_weight=content_w,
        ).fit()

        # ── Evaluate ──────────────────────────────────────────────────────────
        metrics = evaluate(rec)
        mlflow.log_metrics(metrics)
        logger.info(f"Metrics: {metrics}")

        # ── Log sample recommendations as artifact ────────────────────────────
        samples = {
            "cappuccino_cart": rec.recommend(cart=["Cappuccino"], likes=["sweet"], top_k=3),
            "cold_start": rec.recommend(cart=[], likes=[], top_k=3),
            "nut_allergy": rec.recommend(cart=[], likes=["chocolate"], allergies=["nuts"], top_k=3),
        }
        sample_path = "/tmp/sample_recommendations.json"
        with open(sample_path, "w") as f:
            json.dump(samples, f, indent=2)
        mlflow.log_artifact(sample_path, artifact_path="samples")

        # ── Save + log model ──────────────────────────────────────────────────
        artifact_path = "artifacts/hybrid_recommender.joblib"
        os.makedirs("artifacts", exist_ok=True)
        rec.save(artifact_path)
        mlflow.log_artifact(artifact_path, artifact_path="model")
        mlflow.sklearn.log_model(rec, artifact_path="sklearn_model")

        run_id = mlflow.active_run().info.run_id
        logger.info(f"✅ Run complete — run_id: {run_id}")
        logger.info(f"   coverage:           {metrics['coverage']}")
        logger.info(f"   apriori_hit_rate:   {metrics['apriori_hit_rate']}")
        logger.info(f"   avg_score:          {metrics['avg_recommendation_score']}")
        logger.info(f"   diversity:          {metrics['category_diversity']}")

        return rec, metrics


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--popularity", type=float, default=0.2, help="Popularity weight")
    parser.add_argument("--apriori",   type=float, default=0.5, help="Apriori weight")
    parser.add_argument("--content",   type=float, default=0.3, help="Content weight")
    args = parser.parse_args()

    assert abs(args.popularity + args.apriori + args.content - 1.0) < 1e-6, \
        "Weights must sum to 1.0"

    train(args.popularity, args.apriori, args.content)
