# 🧪 CineAI: Examiner's Quick-Start & Code Review Guide
## Practical Guide for University Evaluation Panels, Internal Guides & External Examiners

This guide provides step-by-step instructions for running, testing, demonstrating, and code-reviewing the **CineAI** system during project evaluation sessions.

---

## ⚡ 1. QUICK-START EXECUTION (UNDER 2 MINUTES)

### Step 1: Open Terminal in Project Directory
```powershell
cd C:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System
```

### Step 2: Run Preflight System Verification
Execute the preflight verification script to confirm all Python modules, database connections, and ML models load cleanly:
```powershell
python verify_system.py
```
*Expected Output:*
```
============================================================
VERIFYING CINEAI SYSTEM MODULES & CONNECTIONS
============================================================
[PASS] All Python imports resolved cleanly.
[PASS] SQLite database connected: user_id=1, ratings=0, prefs=['Action', 'Adventure', 'Sci-Fi']
[PASS] Models loaded successfully into memory.
[PASS] Search movies: found 3 items for 'toy story'
[PASS] Popular & Trending: fetched 5 items
[PASS] Hybrid recommendations: generated 5 items
[PASS] Content-Based recommendations: generated 5 items
[PASS] Collaborative Filtering recommendations: generated 5 items
[PASS] Similar movies for 'Shawshank Redemption, The': found 4 items

ALL SYSTEM CHECKS PASSED SUCCESSFULLY!
```

### Step 3: Run the 14-Point Automated Test Suite
```powershell
python tests/test_recommendations.py
```
*Expected Output:*
```
..............
----------------------------------------------------------------------
Ran 14 tests in 9.539s

OK
```

### Step 4: Launch the Interactive Web Application
```powershell
python -m streamlit run app.py
```
Open your browser at:
👉 **`http://localhost:8501`**

---

## 🧭 2. RECOMMENDED EXAMINER DEMO FLOW (10-MINUTE WALKTHROUGH)

Follow this 5-stage walkthrough to observe all core features and academic requirements:

### Stage 1: Home & Curated Trending (Explore IMDB Bayesian Weighted Rating)
1. Go to **🏠 Home & Trending** in the sidebar.
2. Observe the hero banner and the **Top-Rated & Trending** movie cards.
3. Click on the genre chips (e.g., `Sci-Fi`, `Action`, `Drama`) to observe instantaneous client-side filtering.
4. *Academic Highlight*: Point out to examiners that movies are ranked not by simple raw average (which favors titles with 1 five-star rating), but by **IMDB Bayesian Weighted Rating** with a prior mean $C=3.50$ and minimum vote threshold $m=10$.

### Stage 2: Live Search & 5-Star Interactive Rating (SQLite Persistence)
1. Navigate to **🔍 Search & Rate Movies**.
2. Type `"Matrix"` or `"Toy Story"` in the keyword box.
3. Open a movie card and expand **"Rate this Movie"**.
4. Rate the movie **5.0 Stars**.
5. Observe the instant green confirmation message indicating the rating was committed to SQLite (`database/users.db`).

### Stage 3: Cold-Start Mitigation & Dynamic Hybrid Recommendations
1. In the sidebar, under **👤 User Profile**, click **➕ Create New Profile** and enter `"examiner_demo"`.
2. Notice this brand-new user has **0 ratings** (The classic Cold-Start dilemma).
3. Navigate to **🎯 AI Recommendations**.
4. Observe that CineAI **does not crash or show an empty list**!
5. It immediately defaults to $\alpha = 0.0$ and displays cold-start recommendations matching either popular titles or explicit preferences with an Explainable AI badge: *"Matches your selected genre preference: Action"*.
6. Switch the algorithm selector between **Hybrid**, **Content-Based**, and **Collaborative Filtering** to observe differences. Notice that Collaborative Filtering explicitly warns that cold-start fallback is active until ratings are added.

### Stage 4: User Dashboard & Visual Analytics (Plotly Charts)
1. Navigate to **📊 User Dashboard**.
2. Switch back to a profile with ratings (e.g., `demo_cinephile`).
3. Observe the key metric cards: **Total Movies Rated**, **Average Star Rating**, **Top Preferred Genre**.
4. Inspect the interactive Plotly **Genre Distribution Bar Chart** and **Star Rating Distribution Pie Chart**.
5. Inspect the **Rated Movies History Table**, where ratings can be modified or deleted in real time.

### Stage 5: Academic Showcase: Interactive Model Playground
1. Navigate to **🔬 Interactive Model Playground**.
2. Under **Tab 1: Similarity Comparator**, select a movie (e.g., `"Shawshank Redemption, The"`).
3. Observe the side-by-side comparison:
   - **Content-Based Similarity** (Cosine similarity of genres and TF-IDF tags).
   - **Collaborative Filtering Similarity** (Item co-rating correlation).
4. Under **Tab 2: TF-IDF Vocabulary Inspector**, inspect the raw tokens, extracted release year, and feature vector density for any selected movie.
5. Under **Tab 3: Synthetic Cold-Start Simulator**, observe the interactive simulation of $\alpha$ transitioning from $0.00 \to 0.35 \to 0.60$.

---

## 📂 3. CODE REVIEW & ARCHITECTURAL SITES

For professors and examiners wishing to inspect the codebase, here are the exact file locations and responsibilities:

| Subsystem | File Path | Key Functions / Classes | Responsibility |
| :--- | :--- | :--- | :--- |
| **Data Ingestion** | `src/data_preprocessing.py` | `DataLoader`, `clean_title_and_year` | Parses CSVs, applies regex, computes IMDB weighted rating |
| **Content Engine** | `src/content_based.py` | `ContentBasedRecommender` | Builds 5000-dim TF-IDF matrix, Cosine Sim, dynamic profiling |
| **Collaborative Engine**| `src/collaborative_filtering.py`| `CollaborativeFilteringRecommender` | Builds sparse CSR matrix, Item-Item Cosine Sim, TruncatedSVD |
| **Hybrid Engine** | `src/hybrid_recommender.py` | `HybridRecommender` | Dynamic $\alpha$ blending, cold-start fallback, XAI badges |
| **Facade Layer** | `src/recommendation.py` | `MovieRecommendationSystem` | Unifies search, trending, caching, and model calls |
| **Database Store** | `src/database.py` | `init_db`, `save_user_rating`, `get_user_ratings` | Thread-safe SQLite3 CRUD operations |
| **UI Presentation** | `app.py` | Streamlit Multi-Page App | Dark-themed frontend, Plotly charts, Playground |
| **Artwork Service**| `src/poster_service.py` | `get_movie_poster` | Curated CDN posters + Dynamic SVG fallback generator |
| **Evaluation** | `src/evaluation.py` | `RecommendationEvaluator` | Computes RMSE (0.9094), MAE, Precision@K, Recall@K |
| **Unit Tests** | `tests/test_recommendations.py`| `TestMovieRecommendationSystem` | Complete 14-point automated test suite |

---

## 📊 4. VERIFYING QUANTITATIVE METRICS

The offline benchmark metrics are persisted in `docs/evaluation_results.json`:
```json
{
  "rmse": 0.9094,
  "mae": 0.7015,
  "precision_at_5": 0.0075,
  "precision_at_10": 0.0072,
  "recall_at_5": 0.0041,
  "recall_at_10": 0.0056,
  "catalog_coverage": 0.0157,
  "baseline_mean_rating": 3.50,
  "test_ratings_evaluated": 20168
}
```
To re-train the models from scratch and re-run evaluation:
```powershell
python train_model.py
```
*(Executes full preprocessing, TF-IDF vectorization, Item-Item matrix computation, TruncatedSVD factorization, serialization of `.pkl` files, and prints evaluation metrics in ~45 seconds).*
