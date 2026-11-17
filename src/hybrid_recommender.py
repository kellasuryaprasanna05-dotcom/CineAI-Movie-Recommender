"""
Hybrid Recommendation Engine for AI-Powered Movie Recommendation System.
Blends Content-Based Filtering, Collaborative Filtering, and User Preferences.
Handles the Cold-Start problem dynamically based on user interaction depth.
Provides explainable recommendation reasons for full transparency.
"""
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from .content_based import ContentBasedRecommender
from .collaborative_filtering import CollaborativeFilteringRecommender

class HybridRecommender:
    def __init__(
        self, 
        content_recommender: ContentBasedRecommender, 
        cf_recommender: CollaborativeFilteringRecommender,
        movies_df: pd.DataFrame
    ):
        self.cb = content_recommender
        self.cf = cf_recommender
        self.movies_df = movies_df.copy()
        self.movie_info_map = {
            int(r['movieId']): {
                "title": r['title'],
                "clean_title": r.get('clean_title', r['title']),
                "year": r.get('year', ''),
                "genres": r['genres'],
                "genre_list": r.get('genre_list', [x.strip() for x in r['genres'].split('|')]),
                "avg_rating": float(r.get('avg_rating', 0.0)),
                "rating_count": int(r.get('rating_count', 0)),
                "weighted_rating": float(r.get('weighted_rating', 0.0))
            }
            for _, r in self.movies_df.iterrows()
        }

    def recommend(
        self,
        user_ratings: List[Dict[str, Any]],
        favorite_genres: List[str] = None,
        favorite_actors: List[str] = None,
        top_n: int = 10,
        cf_weight: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates hybrid recommendations with explanations:
        - Cold-Start (0 ratings): Uses favorite genres + content-based metadata ranking.
        - Warm-Start (1-3 ratings): 35% CF + 65% Content.
        - Established (>3 ratings): 60% CF + 40% Content (or custom cf_weight).
        Strictly excludes any movie the user has already rated.
        """
        favorite_genres = favorite_genres or []
        rated_movie_ids = {int(r['movie_id']) for r in user_ratings}
        n_ratings = len(user_ratings)

        # Determine dynamic alpha (weight for Collaborative Filtering)
        if cf_weight is not None:
            alpha = float(cf_weight)
        elif n_ratings == 0:
            alpha = 0.0
        elif n_ratings <= 3:
            alpha = 0.35
        else:
            alpha = 0.60

        combined_scores: Dict[int, Dict[str, Any]] = {}

        # 1. Fetch Collaborative Filtering Candidates if alpha > 0
        if alpha > 0 and n_ratings > 0:
            cf_results = self.cf.predict_user_ratings(
                user_ratings=user_ratings, 
                top_n=60, 
                exclude_rated=True
            )
            for item in cf_results:
                mid = item['movieId']
                if mid in rated_movie_ids:
                    continue
                # Normalize predicted rating (0.5 to 5.0) to [0, 1]
                norm_cf = max(0.0, min(1.0, (item['predicted_rating'] - 0.5) / 4.5))
                combined_scores[mid] = {
                    "cf_score": norm_cf,
                    "content_score": 0.0,
                    "predicted_rating": item['predicted_rating'],
                    "confidence": item['confidence']
                }

        # 2. Fetch Content-Based Candidates
        if n_ratings > 0:
            cb_results = self.cb.recommend_for_user_profile(
                user_ratings=user_ratings, 
                top_n=60, 
                exclude_rated=True
            )
        else:
            cb_results = self.cb.recommend_by_preferences(
                favorite_genres=favorite_genres, 
                keywords=favorite_actors, 
                top_n=60,
                exclude_movie_ids=list(rated_movie_ids)
            )

        for item in cb_results:
            mid = item['movieId']
            if mid in rated_movie_ids:
                continue
            norm_cb = max(0.0, min(1.0, item['similarity_score']))
            if mid not in combined_scores:
                combined_scores[mid] = {
                    "cf_score": 0.0,
                    "content_score": norm_cb,
                    "predicted_rating": 0.0,
                    "confidence": 0.0
                }
            else:
                combined_scores[mid]["content_score"] = norm_cb

        # If combined candidates are fewer than requested, inject top rated items
        if len(combined_scores) < top_n:
            top_popular = self.movies_df.sort_values(by='weighted_rating', ascending=False)
            for _, r in top_popular.iterrows():
                mid = int(r['movieId'])
                if mid not in rated_movie_ids and mid not in combined_scores:
                    combined_scores[mid] = {
                        "cf_score": 0.0,
                        "content_score": 0.25,
                        "predicted_rating": float(r.get('avg_rating', 3.5)),
                        "confidence": 0.5
                    }
                if len(combined_scores) >= 50:
                    break

        # 3. Compute final weighted scores, genre preference boost, and human-readable explanation
        final_list = []
        fav_genres_set = set(g.strip().lower() for g in favorite_genres)

        for mid, scores in combined_scores.items():
            if mid in rated_movie_ids:
                continue

            info = self.movie_info_map.get(mid)
            if not info:
                continue

            # Genre alignment bonus
            movie_genres = [g.lower() for g in info.get('genre_list', [])]
            matched_genres = [g.capitalize() for g in info.get('genre_list', []) if g.lower() in fav_genres_set]
            match_count = len(matched_genres)
            genre_boost = min(0.20, match_count * 0.08)

            c_score = scores["content_score"]
            cf_score = scores["cf_score"]
            
            if alpha == 0:
                final_score = c_score + genre_boost
            elif cf_score == 0 and c_score > 0:
                final_score = ((1 - alpha) * c_score) + genre_boost
            elif c_score == 0 and cf_score > 0:
                final_score = (alpha * cf_score) + genre_boost
            else:
                final_score = (alpha * cf_score) + ((1 - alpha) * c_score) + genre_boost

            # Generate natural language AI explanation
            if n_ratings == 0:
                if matched_genres:
                    genres_str = ", ".join(matched_genres[:2])
                    reason = f"Matches your favorite genre: {genres_str} (Community ★ {info['avg_rating']:.1f})"
                else:
                    reason = f"Top-rated community classic (Weighted Score: {info['weighted_rating']:.1f})"
            else:
                if cf_score > 0.4 and c_score > 0.4:
                    if matched_genres:
                        reason = f"High taste match ({int(cf_score*100)}%) + aligns with {matched_genres[0]}"
                    else:
                        reason = f"Strong collaborative pattern ({int(cf_score*100)}%) & thematic similarity"
                elif cf_score > 0.4:
                    pred_r = scores.get("predicted_rating", 0.0)
                    reason = f"Users with your taste rated this ★ {pred_r:.1f}/5.0"
                elif matched_genres:
                    reason = f"Content similarity ({int(c_score*100)}%) + favorite genre {matched_genres[0]}"
                else:
                    reason = f"Content match ({int(c_score*100)}%) with movies you've rated"

            final_list.append({
                "movieId": mid,
                "title": info["title"],
                "clean_title": info["clean_title"],
                "year": info["year"],
                "genres": info["genres"],
                "avg_rating": info["avg_rating"],
                "rating_count": info["rating_count"],
                "hybrid_score": round(float(final_score), 4),
                "cf_score": round(float(cf_score), 4),
                "content_score": round(float(c_score), 4),
                "recommendation_reason": reason,
                "cold_start_fallback": n_ratings == 0
            })

        # Sort descending by hybrid_score
        final_list.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return final_list[:top_n]
