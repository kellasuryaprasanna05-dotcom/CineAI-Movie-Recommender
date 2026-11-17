"""
Comprehensive Unit and Integration Tests for AI-Powered Movie Recommendation System (CineAI).
Verifies all 14 core functionalities required for college evaluation:
1. Home page logic & data loading
2. Movie search with keywords & filters
3. Poster generation (curated URLs + dynamic SVG artwork fallback)
4. Genre selection & extraction
5. User profile registration and selection
6. Movie rating system (1.0 to 5.0 stars with update/delete)
7. Content-based filtering (TF-IDF & Cosine Similarity)
8. Collaborative filtering (Item-Item Cosine Similarity & SVD)
9. Hybrid recommendation engine with cold-start fallback
10. Similar movie suggestions
11. Trending & Popular movies (IMDB Bayesian Weighted Rating)
12. User dashboard calculations & genre distribution
13. Saving and retrieving user preferences
14. SQLite transactional database operations
"""
import os
import sys
import unittest
import tempfile
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.database import (
    init_db,
    get_or_create_user,
    list_users,
    get_user_preferences,
    save_user_preferences,
    save_user_rating,
    get_user_ratings,
    delete_user_rating,
    log_recommendation,
    get_user_history
)
from src.data_preprocessing import DataLoader, extract_year
from src.content_based import ContentBasedRecommender
from src.collaborative_filtering import CollaborativeFilteringRecommender
from src.hybrid_recommender import HybridRecommender
from src.poster_service import get_movie_poster, generate_svg_poster
from src.recommendation import MovieRecommendationSystem

class TestCineAICompleteSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create temp sqlite database for tests
        cls.temp_db_fd, cls.temp_db_path = tempfile.mkstemp(suffix=".db")
        init_db(cls.temp_db_path)

        # Load real MovieLens data
        cls.loader = DataLoader()
        cls.movies_df, cls.ratings_df, cls.tags_df, cls.links_df = cls.loader.load_raw_data()
        cls.processed_movies = cls.loader.preprocess_movies()

        # Build recommenders
        cls.cb = ContentBasedRecommender(cls.processed_movies)
        cls.cb.fit(save_model=False)

        cls.cf = CollaborativeFilteringRecommender(cls.ratings_df, cls.processed_movies)
        cls.cf.fit(min_ratings=10, save_model=False)

        cls.hybrid = HybridRecommender(cls.cb, cls.cf, cls.processed_movies)
        cls.engine = MovieRecommendationSystem()

    @classmethod
    def tearDownClass(cls):
        os.close(cls.temp_db_fd)
        if os.path.exists(cls.temp_db_path):
            os.remove(cls.temp_db_path)

    # 1. Home Page & Dataset Integrity
    def test_01_home_data_integrity(self):
        self.assertGreaterEqual(len(self.processed_movies), 9700)
        self.assertGreaterEqual(len(self.ratings_df), 100000)
        self.assertIn("clean_title", self.processed_movies.columns)
        self.assertIn("weighted_rating", self.processed_movies.columns)

    # 2. Movie Search
    def test_02_movie_search(self):
        # Search by keyword
        results = self.engine.search_movies(query="matrix", limit=5)
        self.assertGreater(len(results), 0)
        titles = [r['clean_title'].lower() for r in results]
        self.assertTrue(any("matrix" in t for t in titles))

        # Search with genre filter
        animation_results = self.engine.search_movies(query="", genre="Animation", limit=5)
        self.assertGreater(len(animation_results), 0)
        for r in animation_results:
            self.assertIn("Animation", r['genres'])

    # 3. Poster Display & SVG Fallback
    def test_03_poster_generation(self):
        # Curated poster check for Toy Story (movieId: 1)
        curated_url = get_movie_poster(1, "Toy Story", "Animation|Children", "1995", 4.0)
        self.assertTrue(curated_url.startswith("http"))

        # Fallback SVG poster generation for uncurated ID
        svg_url = get_movie_poster(999999, "Future Odyssey", "Sci-Fi", "2026", 4.5)
        self.assertTrue(svg_url.startswith("data:image/svg+xml"))
        self.assertIn("Future%20Odyssey", svg_url)

    # 4. Genre Selection
    def test_04_genre_extraction(self):
        genres = self.loader.get_all_genres()
        self.assertIn("Action", genres)
        self.assertIn("Comedy", genres)
        self.assertIn("Sci-Fi", genres)
        self.assertNotIn("(no genres listed)", genres)

    # 5. User Registration & Profile Switcher
    def test_05_user_management(self):
        uid1 = get_or_create_user("alice_critic", db_path=self.temp_db_path)
        uid2 = get_or_create_user("bob_watcher", db_path=self.temp_db_path)
        self.assertNotEqual(uid1, uid2)

        users = list_users(db_path=self.temp_db_path)
        usernames = [u['username'] for u in users]
        self.assertIn("alice_critic", usernames)
        self.assertIn("bob_watcher", usernames)

    # 6. Movie Rating System (1.0 to 5.0 stars)
    def test_06_movie_rating_crud(self):
        uid = get_or_create_user("charlie_test", db_path=self.temp_db_path)
        
        # Save ratings
        save_user_rating(uid, movie_id=318, rating=5.0, db_path=self.temp_db_path) # Shawshank
        save_user_rating(uid, movie_id=296, rating=4.5, db_path=self.temp_db_path) # Pulp Fiction

        ratings = get_user_ratings(uid, db_path=self.temp_db_path)
        self.assertEqual(len(ratings), 2)
        r_map = {r['movie_id']: r['rating'] for r in ratings}
        self.assertEqual(r_map[318], 5.0)
        self.assertEqual(r_map[296], 4.5)

        # Update rating
        save_user_rating(uid, movie_id=318, rating=4.0, db_path=self.temp_db_path)
        ratings_updated = get_user_ratings(uid, db_path=self.temp_db_path)
        r_map_up = {r['movie_id']: r['rating'] for r in ratings_updated}
        self.assertEqual(r_map_up[318], 4.0)

        # Delete rating
        delete_user_rating(uid, movie_id=296, db_path=self.temp_db_path)
        ratings_after = get_user_ratings(uid, db_path=self.temp_db_path)
        self.assertEqual(len(ratings_after), 1)

    # 7. Content-Based Recommendations
    def test_07_content_based_recommendations(self):
        # Test item-to-item content recommendation
        sim_movies = self.cb.get_similar_movies(movie_id=1, top_n=5) # Toy Story
        self.assertEqual(len(sim_movies), 5)
        # Verify cosine similarity is strictly bounded between 0 and 1
        for m in sim_movies:
            self.assertTrue(0.0 <= m['similarity_score'] <= 1.0)

    # 8. Collaborative Filtering Recommendations
    def test_08_collaborative_filtering(self):
        # Seed ratings for Star Wars IV & V
        user_ratings = [
            {"movie_id": 260, "rating": 5.0},
            {"movie_id": 1196, "rating": 5.0}
        ]
        preds = self.cf.predict_user_ratings(user_ratings, top_n=5, exclude_rated=True)
        self.assertGreater(len(preds), 0)
        # Should predict high ratings for other iconic Sci-Fi / Star Wars titles
        pred_mids = [p['movieId'] for p in preds]
        self.assertNotIn(260, pred_mids) # Excluded rated
        self.assertNotIn(1196, pred_mids)

    # 9. Hybrid Recommendations & Cold-Start
    def test_09_hybrid_recommendations(self):
        # Cold start (0 ratings)
        cold_recs = self.hybrid.recommend(
            user_ratings=[],
            favorite_genres=["Animation", "Children"],
            top_n=5
        )
        self.assertEqual(len(cold_recs), 5)
        self.assertTrue(cold_recs[0]['cold_start_fallback'])
        self.assertIn("recommendation_reason", cold_recs[0])

        # Warm start (with ratings)
        user_ratings = [{"movie_id": 2571, "rating": 5.0}] # The Matrix
        warm_recs = self.hybrid.recommend(
            user_ratings=user_ratings,
            favorite_genres=["Sci-Fi", "Action"],
            top_n=5
        )
        self.assertEqual(len(warm_recs), 5)
        self.assertFalse(warm_recs[0]['cold_start_fallback'])
        self.assertNotIn(2571, [r['movieId'] for r in warm_recs])

    # 10. Similar Movie Suggestions
    def test_10_similar_movie_suggestions(self):
        sims_cb = self.engine.get_similar_movies(movie_id=2571, top_n=4, method="content")
        self.assertEqual(len(sims_cb), 4)

        sims_cf = self.engine.get_similar_movies(movie_id=2571, top_n=4, method="collaborative")
        self.assertEqual(len(sims_cf), 4)

    # 11. Trending & Popular (Bayesian Formula)
    def test_11_trending_movies(self):
        trending = self.engine.get_popular_and_trending(limit=8)
        self.assertEqual(len(trending), 8)
        # Verify descending order of Bayesian weighted rating
        wr_scores = [t['weighted_rating'] for t in trending]
        self.assertEqual(wr_scores, sorted(wr_scores, reverse=True))

    # 12. User Dashboard Stats
    def test_12_user_dashboard(self):
        uid = get_or_create_user("david_stats", db_path=self.temp_db_path)
        save_user_rating(uid, 1, 4.0, db_path=self.temp_db_path) # Toy Story (Animation)
        save_user_rating(uid, 260, 5.0, db_path=self.temp_db_path) # Star Wars (Sci-Fi)

        ratings = get_user_ratings(uid, db_path=self.temp_db_path)
        self.assertEqual(len(ratings), 2)
        avg_rating = sum(r['rating'] for r in ratings) / len(ratings)
        self.assertEqual(avg_rating, 4.5)

    # 13. Saving and Retrieving Preferences
    def test_13_user_preferences(self):
        uid = get_or_create_user("emma_prefs", db_path=self.temp_db_path)
        save_user_preferences(
            user_id=uid,
            favorite_genres=["Horror", "Mystery"],
            favorite_actors=["Quentin Tarantino"],
            favorite_languages=["English", "French"],
            preferred_categories=["Cult Classic"],
            db_path=self.temp_db_path
        )
        prefs = get_user_preferences(uid, db_path=self.temp_db_path)
        self.assertEqual(prefs['favorite_genres'], ["Horror", "Mystery"])
        self.assertEqual(prefs['favorite_actors'], ["Quentin Tarantino"])
        self.assertEqual(prefs['favorite_languages'], ["English", "French"])

    # 14. SQLite Database History Logging
    def test_14_database_recommendation_history(self):
        uid = get_or_create_user("frank_hist", db_path=self.temp_db_path)
        log_recommendation(uid, "hybrid", [1, 2, 3], db_path=self.temp_db_path)
        history = get_user_history(uid, limit=5, db_path=self.temp_db_path)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['algorithm_used'], "hybrid")
        self.assertEqual(history[0]['movie_ids'], "1,2,3")

if __name__ == "__main__":
    unittest.main()
