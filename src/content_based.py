"""
Content-Based Recommendation Engine for AI-Powered Movie Recommendation System.
Uses TF-IDF Vectorization and Cosine Similarity on movie titles, genres, and tags.
Supports item-to-item similarity, user-profile vector matching, and cold-start preference matching.
"""
import os
import pickle
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedRecommender:
    def __init__(self, movies_df: pd.DataFrame, models_dir: str = None):
        self.movies_df = movies_df.copy().reset_index(drop=True)
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)

        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        self.tfidf_matrix = None
        self.movie_id_to_idx = {mid: idx for idx, mid in enumerate(self.movies_df['movieId'])}
        self.idx_to_movie_id = {idx: mid for idx, mid in enumerate(self.movies_df['movieId'])}

    def fit(self, save_model: bool = True):
        """Fits TF-IDF vectorizer on the metadata soup and generates TF-IDF matrix."""
        # Ensure 'soup' column exists
        if 'soup' not in self.movies_df.columns:
            self.movies_df['soup'] = (
                self.movies_df['clean_title'].fillna('') + " " +
                self.movies_df['genres_clean'].fillna('') + " " +
                self.movies_df['tag'].fillna('')
            ).str.lower().str.strip()

        print("Fitting TF-IDF Vectorizer on movie metadata...")
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.movies_df['soup'])
        print(f"TF-IDF Matrix shape: {self.tfidf_matrix.shape}")

        if save_model:
            model_path = os.path.join(self.models_dir, "tfidf_model.pkl")
            with open(model_path, "wb") as f:
                pickle.dump({
                    "vectorizer": self.tfidf_vectorizer,
                    "tfidf_matrix": self.tfidf_matrix,
                    "movie_id_to_idx": self.movie_id_to_idx
                }, f)
            print(f"Saved TF-IDF model to {model_path}")

    def load_model(self) -> bool:
        """Loads precomputed TF-IDF model if available."""
        model_path = os.path.join(self.models_dir, "tfidf_model.pkl")
        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    data = pickle.load(f)
                    self.tfidf_vectorizer = data["vectorizer"]
                    self.tfidf_matrix = data["tfidf_matrix"]
                    self.movie_id_to_idx = data["movie_id_to_idx"]
                    self.idx_to_movie_id = {idx: mid for mid, idx in self.movie_id_to_idx.items()}
                return True
            except Exception as e:
                print(f"Failed to load TF-IDF model: {e}")
        return False

    def get_similar_movies(self, movie_id: int, top_n: int = 10) -> List[Dict[str, Any]]:
        """Finds movies most similar to a target movie based on cosine similarity of TF-IDF vectors."""
        if self.tfidf_matrix is None:
            if not self.load_model():
                self.fit()

        if movie_id not in self.movie_id_to_idx:
            return []

        target_idx = self.movie_id_to_idx[movie_id]
        target_vec = self.tfidf_matrix[target_idx]

        # Compute cosine similarity with all movies
        sim_scores = cosine_similarity(target_vec, self.tfidf_matrix).flatten()

        # Sort indices by score descending, excluding the target movie itself
        similar_indices = np.argsort(sim_scores)[::-1]
        similar_indices = [idx for idx in similar_indices if idx != target_idx][:top_n]

        results = []
        for idx in similar_indices:
            row = self.movies_df.iloc[idx]
            results.append({
                "movieId": int(row['movieId']),
                "title": row['title'],
                "clean_title": row['clean_title'],
                "year": row['year'],
                "genres": row['genres'],
                "avg_rating": float(row.get('avg_rating', 0.0)),
                "rating_count": int(row.get('rating_count', 0)),
                "similarity_score": round(float(sim_scores[idx]), 4)
            })
        return results

    def recommend_for_user_profile(
        self, 
        user_ratings: List[Dict[str, Any]], 
        top_n: int = 10,
        exclude_rated: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Builds a dynamic user profile vector from movies the user has rated.
        Weights each movie's TF-IDF vector by (user_rating - 2.5) to capture positive vs negative preference.
        Ranks all unseen movies by cosine similarity to this profile vector.
        """
        if self.tfidf_matrix is None:
            if not self.load_model():
                self.fit()

        if not user_ratings:
            return []

        # Filter to ratings for movies that exist in our dataset
        valid_ratings = [r for r in user_ratings if r['movie_id'] in self.movie_id_to_idx]
        if not valid_ratings:
            return []

        # Construct weighted user profile vector
        user_vector = np.zeros((1, self.tfidf_matrix.shape[1]))
        total_weight = 0.0
        rated_movie_ids = set()

        for r in valid_ratings:
            mid = r['movie_id']
            rating = float(r['rating'])
            rated_movie_ids.add(mid)
            idx = self.movie_id_to_idx[mid]
            movie_vec = self.tfidf_matrix[idx].toarray()

            # Center rating around neutral 2.5: weight > 0 for like, < 0 for dislike
            weight = rating - 2.5
            user_vector += weight * movie_vec
            total_weight += abs(weight)

        if total_weight > 0:
            user_vector /= total_weight

        # Compute cosine similarity of user vector against all movies
        sim_scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()

        # Sort indices
        sorted_indices = np.argsort(sim_scores)[::-1]

        results = []
        for idx in sorted_indices:
            mid = int(self.idx_to_movie_id[idx])
            if exclude_rated and mid in rated_movie_ids:
                continue

            row = self.movies_df.iloc[idx]
            score = float(sim_scores[idx])
            if score <= 0:
                continue

            results.append({
                "movieId": mid,
                "title": row['title'],
                "clean_title": row['clean_title'],
                "year": row['year'],
                "genres": row['genres'],
                "avg_rating": float(row.get('avg_rating', 0.0)),
                "rating_count": int(row.get('rating_count', 0)),
                "similarity_score": round(score, 4)
            })
            if len(results) >= top_n:
                break

        return results

    def recommend_by_preferences(
        self, 
        favorite_genres: List[str], 
        keywords: List[str] = None, 
        top_n: int = 10,
        exclude_movie_ids: List[int] = None
    ) -> List[Dict[str, Any]]:
        """Cold-start recommendation matching explicit user preferences (genres + keywords)."""
        if self.tfidf_matrix is None:
            if not self.load_model():
                self.fit()

        exclude_set = set(exclude_movie_ids or [])
        query_terms = list(favorite_genres or [])
        if keywords:
            query_terms.extend(keywords)

        if not query_terms:
            return []

        # Genre repetition gives appropriate emphasis in query vector
        query_str = " ".join(query_terms).lower()
        query_vec = self.tfidf_vectorizer.transform([query_str])

        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        sorted_indices = np.argsort(sim_scores)[::-1]

        results = []
        for idx in sorted_indices:
            mid = int(self.idx_to_movie_id[idx])
            if mid in exclude_set:
                continue

            row = self.movies_df.iloc[idx]
            results.append({
                "movieId": mid,
                "title": row['title'],
                "clean_title": row['clean_title'],
                "year": row['year'],
                "genres": row['genres'],
                "avg_rating": float(row.get('avg_rating', 0.0)),
                "rating_count": int(row.get('rating_count', 0)),
                "similarity_score": round(float(sim_scores[idx]), 4)
            })
            if len(results) >= top_n:
                break

        return results
