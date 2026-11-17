"""
Model Evaluation Module for AI-Powered Movie Recommendation System.
Computes real quantitative metrics on the MovieLens dataset:
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- Precision@K (K=5, K=10)
- Recall@K (K=5, K=10)
- Catalog Coverage
"""
import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationEvaluator:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_dir = data_dir
        self.ratings_path = os.path.join(data_dir, "ratings.csv")
        self.movies_path = os.path.join(data_dir, "movies.csv")

    def run_full_evaluation(self, test_size: float = 0.20, random_state: int = 42) -> Dict[str, Any]:
        """Runs train/test evaluation on MovieLens ratings and computes metrics."""
        print(f"Loading ratings from {self.ratings_path}...")
        ratings_df = pd.read_csv(self.ratings_path)
        movies_df = pd.read_csv(self.movies_path)
        total_unique_movies = movies_df['movieId'].nunique()

        print(f"Splitting {len(ratings_df)} ratings into 80% train / 20% test...")
        train_df, test_df = train_test_split(ratings_df, test_size=test_size, random_state=random_state)

        # Build train user-item matrix
        # Filter popular items in train set to reduce noise
        item_counts = train_df['movieId'].value_counts()
        valid_items = item_counts[item_counts >= 3].index
        train_filtered = train_df[train_df['movieId'].isin(valid_items)]

        train_matrix = train_filtered.pivot_table(index='userId', columns='movieId', values='rating').fillna(0)
        item_sim = cosine_similarity(train_matrix.T)
        item_sim_df = pd.DataFrame(item_sim, index=train_matrix.columns, columns=train_matrix.columns)

        global_mean = train_df['rating'].mean()
        user_means = train_filtered.groupby('userId')['rating'].mean().to_dict()

        # Evaluate RMSE & MAE on test set
        print("Evaluating Rating Prediction (RMSE & MAE)...")
        y_true = []
        y_pred = []

        # Sample 5000 test ratings for fast and accurate metric evaluation
        test_sample = test_df[test_df['movieId'].isin(item_sim_df.columns)].sample(
            n=min(5000, len(test_df)), random_state=random_state
        )

        for _, row in test_sample.iterrows():
            u = row['userId']
            m = row['movieId']
            actual = row['rating']

            if u in train_matrix.index and m in item_sim_df.columns:
                user_ratings = train_matrix.loc[u]
                rated_items = user_ratings[user_ratings > 0].index
                if len(rated_items) > 0 and m in item_sim_df.index:
                    sims = item_sim_df.loc[m, rated_items]
                    pos_mask = sims > 0.05
                    if np.any(pos_mask):
                        sim_pos = sims[pos_mask]
                        ratings_pos = user_ratings[sim_pos.index]
                        pred = np.sum(sim_pos * ratings_pos) / np.sum(sim_pos)
                    else:
                        pred = user_means.get(u, global_mean)
                else:
                    pred = user_means.get(u, global_mean)
            else:
                pred = global_mean

            pred = max(0.5, min(5.0, pred))
            y_true.append(actual)
            y_pred.append(pred)

        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mae = float(mean_absolute_error(y_true, y_pred))

        # Evaluate Precision@K and Recall@K for top recommendations
        # Relevant items: test set rating >= 4.0
        print("Evaluating Ranking Quality (Precision@K, Recall@K)...")
        precisions_5, recalls_5 = [], []
        precisions_10, recalls_10 = [], []
        recommended_all = set()

        # Evaluate on users who have active test interactions
        test_users = test_df['userId'].unique()
        sample_users = np.random.RandomState(random_state).choice(test_users, size=min(100, len(test_users)), replace=False)

        for u in sample_users:
            u_test = test_df[test_df['userId'] == u]
            relevant_items = set(u_test[u_test['rating'] >= 4.0]['movieId'])
            if len(relevant_items) == 0:
                continue

            if u in train_matrix.index:
                u_train = train_matrix.loc[u]
                rated_items = u_train[u_train > 0].index
                
                # Score unrated candidate items
                candidates = [m for m in item_sim_df.columns if m not in rated_items]
                scores = []
                for m in candidates[:200]:  # Evaluate top candidates
                    sims = item_sim_df.loc[m, rated_items]
                    pos_mask = sims > 0.05
                    if np.any(pos_mask):
                        sim_pos = sims[pos_mask]
                        score = np.sum(sim_pos * u_train[sim_pos.index]) / np.sum(sim_pos)
                        scores.append((m, score))
                scores.sort(key=lambda x: x[1], reverse=True)
                top_10 = [m for m, _ in scores[:10]]
            else:
                continue

            top_5 = top_10[:5]
            recommended_all.update(top_10)

            # Precision & Recall @ 5
            hits_5 = len(set(top_5).intersection(relevant_items))
            precisions_5.append(hits_5 / 5.0)
            recalls_5.append(hits_5 / len(relevant_items))

            # Precision & Recall @ 10
            hits_10 = len(set(top_10).intersection(relevant_items))
            precisions_10.append(hits_10 / 10.0)
            recalls_10.append(hits_10 / len(relevant_items))

        avg_p5 = float(np.mean(precisions_5)) if precisions_5 else 0.0
        avg_r5 = float(np.mean(recalls_5)) if recalls_5 else 0.0
        avg_p10 = float(np.mean(precisions_10)) if precisions_10 else 0.0
        avg_r10 = float(np.mean(recalls_10)) if recalls_10 else 0.0
        coverage = float(len(recommended_all) / total_unique_movies)

        metrics = {
            "dataset": "MovieLens Latest-Small",
            "total_ratings": len(ratings_df),
            "total_movies": total_unique_movies,
            "test_sample_size": len(y_true),
            "RMSE": round(rmse, 4),
            "MAE": round(mae, 4),
            "Precision@5": round(avg_p5, 4),
            "Recall@5": round(avg_r5, 4),
            "Precision@10": round(avg_p10, 4),
            "Recall@10": round(avg_r10, 4),
            "Catalog_Coverage": round(coverage, 4),
            "baseline_mean_rating": round(float(global_mean), 2)
        }

        # Save metrics to docs directory
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
        os.makedirs(docs_dir, exist_ok=True)
        out_path = os.path.join(docs_dir, "evaluation_results.json")
        with open(out_path, "w") as f:
            json.dump(metrics, f, indent=4)

        print("Evaluation Complete. Results:")
        print(json.dumps(metrics, indent=2))
        return metrics

if __name__ == "__main__":
    evaluator = RecommendationEvaluator()
    evaluator.run_full_evaluation()
