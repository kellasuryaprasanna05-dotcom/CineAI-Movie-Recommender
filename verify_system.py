"""
Verification script for all modules in AI-Powered Movie Recommendation System.
"""
import os
import sys
import traceback

def test_system():
    print("=" * 60)
    print("VERIFYING CINEAI SYSTEM MODULES & CONNECTIONS")
    print("=" * 60)
    print("Python version:", sys.version)

    try:
        from src.data_preprocessing import DataLoader
        from src.content_based import ContentBasedRecommender
        from src.collaborative_filtering import CollaborativeFilteringRecommender
        from src.hybrid_recommender import HybridRecommender
        from src.recommendation import MovieRecommendationSystem
        from src.database import init_db, get_or_create_user, get_user_ratings, get_user_preferences
        from src.poster_service import get_movie_poster
        from src.evaluation import RecommendationEvaluator
        print("[PASS] All Python imports resolved cleanly.")

        # Check DB
        init_db()
        user_id = get_or_create_user("demo_cinephile")
        prefs = get_user_preferences(user_id)
        ratings = get_user_ratings(user_id)
        print(f"[PASS] SQLite database connected: user_id={user_id}, ratings={len(ratings)}, prefs={prefs.get('favorite_genres')}")

        # Check Recommendation Engine
        engine = MovieRecommendationSystem()
        engine.train_or_load_models()
        print("[PASS] Models loaded successfully into memory.")

        # Test Search
        search_res = engine.search_movies("toy story", limit=3)
        print(f"[PASS] Search movies: found {len(search_res)} items for 'toy story'")
        assert len(search_res) > 0, "Search should return items"

        # Test Popular
        pop_res = engine.get_popular_and_trending(limit=5)
        print(f"[PASS] Popular & Trending: fetched {len(pop_res)} items")
        assert len(pop_res) == 5, "Popular should return 5 items"

        # Test Recommendations (Cold-Start and with ratings)
        rec_hybrid = engine.get_personalized_recommendations(user_id, algorithm="hybrid", top_n=5)
        print(f"[PASS] Hybrid recommendations: generated {len(rec_hybrid)} items")
        assert len(rec_hybrid) == 5, "Hybrid should return 5 items"

        rec_cb = engine.get_personalized_recommendations(user_id, algorithm="content", top_n=5)
        print(f"[PASS] Content-Based recommendations: generated {len(rec_cb)} items")
        assert len(rec_cb) == 5, "Content-based should return 5 items"

        rec_cf = engine.get_personalized_recommendations(user_id, algorithm="collaborative", top_n=5)
        print(f"[PASS] Collaborative Filtering recommendations: generated {len(rec_cf)} items")
        assert len(rec_cf) == 5, "CF should return 5 items"

        # Test Similar Movies
        sample_mid = pop_res[0]["movieId"]
        sim_res = engine.get_similar_movies(sample_mid, top_n=4)
        print(f"[PASS] Similar movies for '{pop_res[0]['clean_title']}': found {len(sim_res)} items")
        assert len(sim_res) == 4, "Similar should return 4 items"

        print("\nALL SYSTEM CHECKS PASSED SUCCESSFULLY!")
        return True
    except Exception as e:
        print("\n[FAIL] An error occurred during verification:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)
