"""
Collaborative Filtering Module for AI-Powered Movie Recommendation System.
Implements:
1. Item-Based Collaborative Filtering (Cosine Similarity over User-Item interactions).
2. Matrix Factorization (Truncated SVD / Latent Factor Model).
3. User rating prediction and neighbor-based recommendations.
"""
import os
import pickle
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

class CollaborativeFilteringRecommender:
    def __init__(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame, models_dir: str = None):
        self.ratings_df = ratings_df.copy()
        self.movies_df = movies_df.copy()
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)

        self.user_movie_matrix: pd.DataFrame = None
        self.item_similarity_df: pd.DataFrame = None
        self.svd_model = None
        self.user_factors = None
        self.item_factors = None
        self.movie_info_map = {
            int(r['movieId']): {
                "title": r['title'],
                "clean_title": r.get('clean_title', r['title']),
                "year": r.get('year', ''),
                "genres": r['genres'],
                "avg_rating": float(r.get('avg_rating', 0.0)),
                "rating_count": int(r.get('rating_count', 0))
            }
            for _, r in self.movies_df.iterrows()
        }

    def fit(self, min_ratings: int = 5, n_components: int = 20, save_model: bool = True):
        """Constructs user-item matrix, computes item-item cosine similarity, and fits SVD."""
        print("Constructing user-movie interaction matrix...")
        # Keep movies with at least min_ratings to avoid extreme sparsity
        movie_counts = self.ratings_df['movieId'].value_counts()
        popular_movies = movie_counts[movie_counts >= min_ratings].index

        filtered = self.ratings_df[self.ratings_df['movieId'].isin(popular_movies)]
        
        # User-Movie matrix: rows=users, cols=movies
        self.user_movie_matrix = filtered.pivot_table(index='userId', columns='movieId', values='rating').fillna(0)
        print(f"User-Movie Matrix: {self.user_movie_matrix.shape[0]} users x {self.user_movie_matrix.shape[1]} movies")

        # Movie-Movie Cosine Similarity (Item-Based CF)
        # Transpose so rows are movies, cols are users
        movie_user_matrix = self.user_movie_matrix.T
        item_sim = cosine_similarity(movie_user_matrix)
        self.item_similarity_df = pd.DataFrame(
            item_sim, 
            index=self.user_movie_matrix.columns, 
            columns=self.user_movie_matrix.columns
        ).astype("float32")
        print("Item-Item Cosine Similarity Matrix computed successfully.")

        # Matrix Factorization via TruncatedSVD
        print(f"Fitting TruncatedSVD with {n_components} components...")
        self.svd_model = TruncatedSVD(n_components=min(n_components, self.user_movie_matrix.shape[1]-1), random_state=42)
        self.user_factors = self.svd_model.fit_transform(self.user_movie_matrix).astype("float32")
        self.item_factors = self.svd_model.components_.astype("float32")

        if save_model:
            model_path = os.path.join(self.models_dir, "cf_model.pkl")
            with open(model_path, "wb") as f:
                pickle.dump({
                    "user_movie_matrix": self.user_movie_matrix,
                    "item_similarity_df": self.item_similarity_df,
                    "svd_model": self.svd_model,
                    "user_factors": self.user_factors,
                    "item_factors": self.item_factors
                }, f)
            print(f"Saved Collaborative Filtering model to {model_path}")

    def load_model(self) -> bool:
        model_path = os.path.join(self.models_dir, "cf_model.pkl")
        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    data = pickle.load(f)
                    self.user_movie_matrix = data["user_movie_matrix"]
                    self.item_similarity_df = data["item_similarity_df"]
                    self.svd_model = data["svd_model"]
                    self.user_factors = data["user_factors"]
                    self.item_factors = data["item_factors"]
                return True
            except Exception as e:
                print(f"Failed to load CF model: {e}")
        return False

    def get_similar_items(self, movie_id: int, top_n: int = 10) -> List[Dict[str, Any]]:
        """Finds items with highest user rating correlation / cosine similarity."""
        if self.item_similarity_df is None:
            if not self.load_model():
                self.fit()

        if movie_id not in self.item_similarity_df.columns:
            return []

        series = self.item_similarity_df[movie_id].drop(labels=[movie_id])
        top_similar = series.sort_values(ascending=False).head(top_n)

        results = []
        for mid, sim in top_similar.items():
            mid_int = int(mid)
            info = self.movie_info_map.get(mid_int, {})
            results.append({
                "movieId": mid_int,
                "title": info.get("title", f"Movie {mid_int}"),
                "clean_title": info.get("clean_title", ""),
                "year": info.get("year", ""),
                "genres": info.get("genres", ""),
                "avg_rating": info.get("avg_rating", 0.0),
                "rating_count": info.get("rating_count", 0),
                "similarity_score": round(float(sim), 4)
            })
        return results

    def predict_user_ratings(
        self, 
        user_ratings: List[Dict[str, Any]], 
        top_n: int = 10,
        exclude_rated: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Predicts ratings for unrated movies for an active user using item-based collaborative filtering:
        predicted_rating = sum(sim(i, j) * r_j) / sum(abs(sim(i, j)))
        """
        if self.item_similarity_df is None:
            if not self.load_model():
                self.fit()

        if not user_ratings:
            return []

        # User's rated items present in similarity matrix
        user_rated_map = {
            int(r['movie_id']): float(r['rating'])
            for r in user_ratings
            if int(r['movie_id']) in self.item_similarity_df.columns
        }

        if not user_rated_map:
            return []

        rated_mids = set(user_rated_map.keys())
        candidate_movies = [m for m in self.item_similarity_df.columns if m not in rated_mids] if exclude_rated else list(self.item_similarity_df.columns)

        predictions = []
        for candidate_mid in candidate_movies:
            # Extract similarities between candidate and items rated by user
            sim_subseries = self.item_similarity_df.loc[candidate_mid, list(rated_mids)]
            sim_values = sim_subseries.values
            rating_values = np.array([user_rated_map[m] for m in sim_subseries.index])

            # Filter positive similarities to avoid inverse recommendation bias
            pos_mask = sim_values > 0.05
            if not np.any(pos_mask):
                continue

            sim_pos = sim_values[pos_mask]
            ratings_pos = rating_values[pos_mask]

            sum_sim = np.sum(sim_pos)
            if sum_sim > 0:
                pred_rating = np.sum(sim_pos * ratings_pos) / sum_sim
                # Boost confidence if candidate is similar to multiple rated movies
                confidence = min(len(sim_pos) / 3.0, 1.0)
                predictions.append((candidate_mid, pred_rating, confidence))

        if not predictions:
            return []

        # Sort by predicted rating descending
        predictions.sort(key=lambda x: (x[1] * x[2]), reverse=True)
        top_preds = predictions[:top_n]

        results = []
        for mid, pred, conf in top_preds:
            mid_int = int(mid)
            info = self.movie_info_map.get(mid_int, {})
            results.append({
                "movieId": mid_int,
                "title": info.get("title", f"Movie {mid_int}"),
                "clean_title": info.get("clean_title", ""),
                "year": info.get("year", ""),
                "genres": info.get("genres", ""),
                "avg_rating": info.get("avg_rating", 0.0),
                "rating_count": info.get("rating_count", 0),
                "predicted_rating": round(float(pred), 2),
                "confidence": round(float(conf), 2)
            })

        return results
