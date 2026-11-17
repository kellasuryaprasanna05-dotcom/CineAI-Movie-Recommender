"""
Recommendation Engine Facade for AI-Powered Movie Recommendation System.
Central service integrating Preprocessing, Content-Based, Collaborative, Hybrid, and SQLite DB.
"""
import os
from typing import List, Dict, Any, Optional
import pandas as pd

from .data_preprocessing import DataLoader
from .content_based import ContentBasedRecommender
from .collaborative_filtering import CollaborativeFilteringRecommender
from .hybrid_recommender import HybridRecommender
from .database import (
    init_db,
    get_or_create_user,
    get_user_preferences,
    save_user_preferences,
    save_user_rating,
    delete_user_rating,
    get_user_ratings,
    log_recommendation,
    get_user_history
)
from .poster_service import get_movie_poster

class MovieRecommendationSystem:
    _instance = None

    def __init__(self, data_dir: str = None, models_dir: str = None):
        self.loader = DataLoader(data_dir=data_dir)
        self.movies_df, self.ratings_df, self.tags_df, self.links_df = self.loader.load_raw_data()
        self.processed_movies_df = self.loader.preprocess_movies()

        # Initialize SQLite database
        init_db()

        # Initialize recommenders
        self.content_recommender = ContentBasedRecommender(self.processed_movies_df, models_dir=models_dir)
        self.cf_recommender = CollaborativeFilteringRecommender(self.ratings_df, self.processed_movies_df, models_dir=models_dir)
        self.hybrid_recommender = HybridRecommender(self.content_recommender, self.cf_recommender, self.processed_movies_df)

        # Lookup caches
        self.movie_map = {int(r['movieId']): r.to_dict() for _, r in self.processed_movies_df.iterrows()}
        self.all_genres = self.loader.get_all_genres()

    def train_or_load_models(self):
        """Loads models if cached, else trains and caches them."""
        print("Initializing Content-Based Model...")
        if not self.content_recommender.load_model():
            self.content_recommender.fit(save_model=True)

        print("Initializing Collaborative Filtering Model...")
        if not self.cf_recommender.load_model():
            self.cf_recommender.fit(save_model=True)
        print("Recommendation models ready.")

    def search_movies(
        self, 
        query: str = "", 
        genre: str = None, 
        min_rating: float = 0.0, 
        limit: int = 24
    ) -> List[Dict[str, Any]]:
        """Search movies by title with optional genre and rating filters."""
        df = self.processed_movies_df

        if query:
            clean_q = query.strip().lower()
            mask = df['title'].str.lower().str.contains(clean_q, regex=False) | \
                   df['clean_title'].str.lower().str.contains(clean_q, regex=False)
            df = df[mask]

        if genre and genre != "All":
            df = df[df['genre_list'].apply(lambda g_list: genre in g_list)]

        if min_rating > 0.0:
            df = df[df['avg_rating'] >= min_rating]

        # Prioritize movies with high rating count and score
        df_sorted = df.sort_values(by=['weighted_rating', 'rating_count'], ascending=[False, False]).head(limit)
        
        results = []
        for _, row in df_sorted.iterrows():
            mid = int(row['movieId'])
            poster = get_movie_poster(mid, row['title'], row['genres'], row['year'], row['avg_rating'])
            results.append({
                "movieId": mid,
                "title": row['title'],
                "clean_title": row['clean_title'],
                "year": row['year'],
                "genres": row['genres'],
                "avg_rating": float(row['avg_rating']),
                "rating_count": int(row['rating_count']),
                "weighted_rating": float(row['weighted_rating']),
                "poster_url": poster
            })
        return results

    def get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Fetches complete movie details including poster and metadata."""
        row = self.movie_map.get(movie_id)
        if not row:
            return None
        poster = get_movie_poster(movie_id, row['title'], row['genres'], row.get('year', ''), row.get('avg_rating', 0.0))
        return {
            "movieId": int(row['movieId']),
            "title": row['title'],
            "clean_title": row.get('clean_title', row['title']),
            "year": row.get('year', ''),
            "genres": row['genres'],
            "genre_list": row.get('genre_list', []),
            "avg_rating": float(row.get('avg_rating', 0.0)),
            "rating_count": int(row.get('rating_count', 0)),
            "weighted_rating": float(row.get('weighted_rating', 0.0)),
            "tags": row.get('tag', ''),
            "poster_url": poster
        }

    def get_popular_and_trending(self, genre: str = None, limit: int = 12) -> List[Dict[str, Any]]:
        """Returns top-rated popular movies using IMDB Weighted Rating."""
        df = self.processed_movies_df
        if genre and genre != "All":
            df = df[df['genre_list'].apply(lambda g_list: genre in g_list)]

        top = df.sort_values(by='weighted_rating', ascending=False).head(limit)
        results = []
        for _, row in top.iterrows():
            mid = int(row['movieId'])
            poster = get_movie_poster(mid, row['title'], row['genres'], row['year'], row['avg_rating'])
            results.append({
                "movieId": mid,
                "title": row['title'],
                "clean_title": row['clean_title'],
                "year": row['year'],
                "genres": row['genres'],
                "avg_rating": float(row['avg_rating']),
                "rating_count": int(row['rating_count']),
                "weighted_rating": float(row['weighted_rating']),
                "poster_url": poster
            })
        return results

    def get_similar_movies(self, movie_id: int, top_n: int = 10, method: str = "content") -> List[Dict[str, Any]]:
        """Returns movies similar to target movie using either Content-Based or Collaborative Filtering."""
        if method == "collaborative":
            items = self.cf_recommender.get_similar_items(movie_id, top_n=top_n)
        else:
            items = self.content_recommender.get_similar_movies(movie_id, top_n=top_n)

        for item in items:
            mid = item['movieId']
            item['poster_url'] = get_movie_poster(mid, item['title'], item['genres'], item.get('year', ''), item.get('avg_rating', 0.0))
        return items

    def get_personalized_recommendations(
        self, 
        user_id: int, 
        algorithm: str = "hybrid", 
        top_n: int = 12,
        cf_weight: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates personalized movie recommendations using specified algorithm:
        'content', 'collaborative', or 'hybrid'.
        """
        ratings = get_user_ratings(user_id)
        prefs = get_user_preferences(user_id)
        fav_genres = prefs.get('favorite_genres', [])
        fav_actors = prefs.get('favorite_actors', [])

        if algorithm == "content":
            if ratings:
                raw_recs = self.content_recommender.recommend_for_user_profile(ratings, top_n=top_n)
                for item in raw_recs:
                    if "recommendation_reason" not in item:
                        item["recommendation_reason"] = f"TF-IDF Profile Match: {int(item.get('similarity_score', 0.8)*100)}% thematic alignment"
            else:
                raw_recs = self.content_recommender.recommend_by_preferences(fav_genres, fav_actors, top_n=top_n)
                for item in raw_recs:
                    if "recommendation_reason" not in item:
                        item["recommendation_reason"] = f"Preference Match: {int(item.get('similarity_score', 0.8)*100)}% genre alignment"
        elif algorithm == "collaborative":
            if ratings:
                raw_recs = self.cf_recommender.predict_user_ratings(ratings, top_n=top_n)
                for item in raw_recs:
                    if "recommendation_reason" not in item:
                        item["recommendation_reason"] = f"Predicted Rating: ★ {item.get('predicted_rating', 4.5):.1f}/5.0 from viewer co-ratings"
            else:
                # Cold start fallback for pure CF
                raw_recs = self.content_recommender.recommend_by_preferences(fav_genres, fav_actors, top_n=top_n)
                for item in raw_recs:
                    if "recommendation_reason" not in item:
                        item["recommendation_reason"] = f"Cold-Start Fallback: Matches your favorite genres"
        else:  # hybrid
            raw_recs = self.hybrid_recommender.recommend(
                user_ratings=ratings, 
                favorite_genres=fav_genres, 
                favorite_actors=fav_actors, 
                top_n=top_n,
                cf_weight=cf_weight
            )

        # Enhance with posters and metadata
        results = []
        rec_ids = []
        for item in raw_recs:
            mid = item['movieId']
            rec_ids.append(mid)
            item['poster_url'] = get_movie_poster(mid, item['title'], item['genres'], item.get('year', ''), item.get('avg_rating', 0.0))
            results.append(item)

        if rec_ids:
            log_recommendation(user_id, algorithm, rec_ids)

        return results

    def get_user_summary(self, user_id: int) -> Dict[str, Any]:
        """Returns comprehensive stats for the user dashboard."""
        ratings = get_user_ratings(user_id)
        prefs = get_user_preferences(user_id)
        history = get_user_history(user_id)

        # Compute rated movie details
        rated_details = []
        genre_distribution = {}
        for r in ratings:
            mid = r['movie_id']
            m_info = self.movie_map.get(mid, {})
            title = m_info.get('title', f"Movie {mid}")
            genres = m_info.get('genres', '')
            rated_details.append({
                "movie_id": mid,
                "title": title,
                "genres": genres,
                "user_rating": r['rating'],
                "rated_at": r.get('rated_at', '')
            })
            for g in m_info.get('genre_list', []):
                genre_distribution[g] = genre_distribution.get(g, 0) + 1

        avg_user_rating = round(sum(r['rating'] for r in ratings) / len(ratings), 2) if ratings else 0.0

        return {
            "user_id": user_id,
            "total_ratings": len(ratings),
            "avg_user_rating": avg_user_rating,
            "preferences": prefs,
            "rated_movies": rated_details,
            "genre_distribution": genre_distribution,
            "history": history
        }
