"""
Master Training and Offline Evaluation Script.
Trains the Content-Based (TF-IDF) and Collaborative Filtering models,
saves artifacts to models/, and executes model evaluation.
"""
import os
import sys
import time

# Ensure src is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.data_preprocessing import DataLoader
from src.content_based import ContentBasedRecommender
from src.collaborative_filtering import CollaborativeFilteringRecommender
from src.evaluation import RecommendationEvaluator
from src.database import init_db

def main():
    print("=" * 60)
    print("AI-POWERED MOVIE RECOMMENDATION SYSTEM - MODEL TRAINING")
    print("=" * 60)

    start_time = time.time()

    # 1. Initialize SQLite Database
    print("\n[1/5] Initializing SQLite Database...")
    init_db()
    print("Database initialized at database/users.db")

    # 2. Load and Preprocess Data
    print("\n[2/5] Loading and Preprocessing MovieLens Dataset...")
    loader = DataLoader()
    movies_df, ratings_df, tags_df, links_df = loader.load_raw_data()
    processed_movies = loader.preprocess_movies()
    print(f"Loaded {len(processed_movies)} movies and {len(ratings_df)} ratings.")

    # 3. Train and Save Content-Based Model
    print("\n[3/5] Training Content-Based (TF-IDF) Recommender...")
    cb = ContentBasedRecommender(processed_movies)
    cb.fit(save_model=True)

    # 4. Train and Save Collaborative Filtering Model
    print("\n[4/5] Training Collaborative Filtering Recommender...")
    cf = CollaborativeFilteringRecommender(ratings_df, processed_movies)
    cf.fit(save_model=True)

    # 5. Run Model Evaluation
    print("\n[5/5] Running Offline Evaluation (RMSE, MAE, Precision@K, Recall@K)...")
    evaluator = RecommendationEvaluator()
    results = evaluator.run_full_evaluation()

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"TRAINING COMPLETE IN {elapsed:.2f} SECONDS")
    print("Evaluation Summary:")
    print(f"  - RMSE:          {results.get('RMSE')}")
    print(f"  - MAE:           {results.get('MAE')}")
    print(f"  - Precision@10:  {results.get('Precision@10')}")
    print(f"  - Recall@10:     {results.get('Recall@10')}")
    print(f"  - Catalog Cov.:  {results.get('Catalog_Coverage')}")
    print("Artifacts saved to models/ and docs/evaluation_results.json")
    print("=" * 60)

if __name__ == "__main__":
    main()
