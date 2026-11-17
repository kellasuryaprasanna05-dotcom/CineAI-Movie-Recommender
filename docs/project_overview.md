# Project Overview: AI-Powered Movie Recommendation System

## 1. Executive Summary
The **AI-Powered Movie Recommendation System** (**CineAI**) is an end-to-end machine learning platform that solves the digital choice overload problem in modern entertainment streaming. Users often spend excessive time searching through thousands of movies rather than enjoying content. 

CineAI combines **Content-Based Filtering (TF-IDF & Cosine Similarity)**, **Item-Item Collaborative Filtering**, and **TruncatedSVD Matrix Factorization** into a unified **Hybrid Recommendation Engine** backed by an interactive, Netflix-inspired dark-theme Streamlit interface and an SQLite transactional store.

---

## 2. Problem Statement
With thousands of titles available across modern video streaming catalogs, users face cognitive fatigue when choosing what to watch. Traditional recommendation engines suffer from:
1. **The Cold-Start Problem**: Inability to recommend relevant titles to newly registered users without historical watch data.
2. **Sparsity**: User-item rating matrices have >98% unobserved entries, making purely collaborative techniques fragile.
3. **Filter Bubbles**: Content-based recommenders may only suggest near-duplicate genres without discovering serendipitous titles.

---

## 3. Project Objectives
- Build an intelligent, multi-algorithmic movie recommender suggesting movies based on user ratings, explicit preferences, movie genres, similarity between movies, and previous watch histories.
- Implement real quantitative machine learning pipelines using Scikit-learn, Pandas, and NumPy trained on the genuine **MovieLens** dataset (100,000+ ratings, 9,700+ movies).
- Handle new user cold-start through preference-driven vector matching and Bayesian weighted popularity metrics.
- Provide a responsive streaming UI with movie posters, interactive 1-5 star ratings, and real-time dashboard analytics.
- Evaluate model performance using standard information retrieval and prediction metrics: RMSE, MAE, Precision@K, Recall@K, and Catalog Coverage.

---

## 4. System Architecture

```
+------------------------------------------------------------------------+
|                      Streamlit Frontend (CineAI UI)                    |
|   - Hero Banner       - Search & Filters      - Interactive 5-Star     |
|   - Genre Badges      - User Dashboard        - Model Evaluation Views |
+-----------------------------------+------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
|                     Recommendation Engine Facade                       |
|                      (src/recommendation.py)                           |
+---------+-------------------------+--------------------------+---------+
          |                         |                          |
          v                         v                          v
+-------------------+     +--------------------+     +-------------------+
|   Content-Based   |     |   Collaborative    |     |      Hybrid       |
|    Recommender    |     |     Filtering      |     |    Recommender    |
| - TF-IDF Vectors  |     | - Item-Item Cosine |     | - Dynamic Blending|
| - Cosine Sim      |     | - TruncatedSVD     |     | - Cold-Start Mode |
| - User Profiling  |     | - Rating Prediction|     | - Genre Boosting  |
+---------+---------+     +---------+----------+     +---------+---------+
          |                         |                          |
          +-------------------------+--------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
|                           Data & Storage Layer                         |
|   - MovieLens Dataset (movies.csv, ratings.csv, tags.csv, links.csv)   |
|   - SQLite Database (users.db: profiles, preferences, ratings, logs)   |
|   - Trained Artifacts (models/tfidf_model.pkl, models/cf_model.pkl)   |
+------------------------------------------------------------------------+
```

---

## 5. Technology Stack
- **Frontend / UI**: Streamlit 1.67+, HTML5, CSS3, Plotly Data Visualizations
- **Backend / Core Engine**: Python 3.13, SQLite3
- **Machine Learning**: Scikit-learn, Pandas, NumPy, Scipy
- **Dataset**: GroupLens MovieLens Latest-Small (100,836 ratings, 9,742 movies, 3,683 tags)
- **Evaluation**: Train-Test 80/20 split, RMSE, MAE, Precision@5/10, Recall@5/10, Catalog Coverage
