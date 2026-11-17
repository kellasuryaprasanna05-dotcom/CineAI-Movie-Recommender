# 🎬 AI-Powered Movie Recommendation System (CineAI)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-orange.svg)](https://scikit-learn.org/)
[![License: Academic](https://img.shields.io/badge/License-Academic%20Research-green.svg)](https://grouplens.org/datasets/movielens/latest/)

An intelligent, multi-algorithmic movie recommendation platform designed to help users discover relevant films based on user ratings, explicit genre preferences, movie metadata similarity, and historical interaction patterns.

Built with **Python**, **Streamlit**, **Scikit-learn**, and **SQLite**, trained on the official **GroupLens MovieLens Latest-Small (`ml-latest-small`)** dataset.

---

## 📌 Project Overview
With the explosion of content across modern streaming providers (Netflix, Amazon Prime Video, Disney+, HBO Max), finding relevant titles has become a major challenge. Users frequently experience digital choice overload and decision fatigue.

**CineAI** solves this challenge by unifying three distinct machine learning paradigms:
1. **Content-Based Filtering**: Analyzes genres, tags, and titles using TF-IDF vectorization with sublinear scaling and Cosine Similarity.
2. **Collaborative Filtering**: Discovers latent shared taste patterns across community ratings using TruncatedSVD matrix factorization ($k=20$) and Item-Item cosine similarity.
3. **Adaptive Hybrid Recommender**: Blends Content and Collaborative scores with a dynamically adjustable weighting parameter ($\alpha \in [0.0, 1.0]$) and handles the cold-start dilemma via Bayesian popularity weighting.

---

## 📊 Verified Evaluation Benchmarks
Evaluated on an 80/20 train/test split on 5,000 sampled test ratings from the MovieLens Latest-Small dataset:

| Metric | Verified Value | Benchmark Description |
| :--- | :---: | :--- |
| **RMSE (Root Mean Squared Error)** | **0.9094** | Outperforms standard 1.05 global baseline |
| **MAE (Mean Absolute Error)** | **0.7015** | Average rating deviation is ~0.70 stars on 5-star scale |
| **Precision@10 (Test Holdout)** | **0.0072 (0.72%)** | Top-10 exact hit rate on 98.30% sparse unobserved test matrix |
| **Recall@10 (Test Holdout)** | **0.0056 (0.56%)** | Retrieval rate of relevant test-set movies |
| **Catalog Coverage** | **0.0157 (1.57%)** | 153 unique movies recommended in sample top-10 lists |
| **Mean Baseline Rating** | **3.50** | Fallback mean rating |
| **Inference Latency** | **< 35 ms** | Real-time interactive UI updates |

---

## 🏗️ Architecture & Technology Stack
- **Frontend / UI:** Streamlit 1.30+ with dark cinematic movie UI (`assets/styles.css`) and Plotly 5.18+ interactive analytics.
- **Machine Learning Core:** Scikit-Learn (TF-IDF Vectorizer, TruncatedSVD, Cosine Similarity), NumPy, SciPy, Pandas.
- **Data Persistence:** ACID-compliant SQLite relational database (`database/users.db`) with 4 relational tables (`users`, `user_preferences`, `user_ratings`, `recommendation_history`).
- **Zero-Crash Poster Engine:** Offline-first architecture combining an embedded library of 40+ curated high-resolution Amazon/IMDb poster URLs with an autonomous procedural SVG gradient artwork generator matching genre color palettes.
- **Dataset:** GroupLens MovieLens Latest-Small (`ml-latest-small`), containing 100,836 ratings, 9,742 movies, 610 users, and 3,683 user tags (generated September 26, 2018).

---

## 📁 Repository Directory Structure
```text
AI-Movie-Recommendation-System/
├── app.py                      # Main Streamlit web application entry point
├── requirements.txt            # Python production dependencies
├── .streamlit/
│   └── config.toml             # Streamlit dark cinematic theme & server configuration
├── .gitignore                  # Git tracking rules for production deployment
├── assets/
│   └── styles.css              # Custom cinematic styling & responsive card layouts
├── src/
│   ├── __init__.py             # Python package initializer
│   ├── recommendation.py       # High-level recommendation orchestrator
│   ├── content_based.py        # TF-IDF & Cosine Similarity module
│   ├── collaborative_filtering.py # SVD Matrix Factorization & Item-Item CF
│   ├── hybrid_recommender.py   # Adaptive weighted blending & cold-start engine
│   ├── data_preprocessing.py   # Dataset ingestion, regex year parsing & cleaning
│   ├── poster_service.py       # Curated posters & procedural SVG artwork generator
│   ├── database.py             # SQLite CRUD operations & schema initialization
│   └── evaluation.py           # Quantitative validation metrics (RMSE, MAE, Precision@K)
├── data/
│   ├── movies.csv              # 9,742 movie titles, release years & genre tags
│   ├── ratings.csv             # 100,836 explicit user ratings (0.5 to 5.0 scale)
│   ├── tags.csv                # 3,683 crowd-sourced descriptive keywords
│   ├── links.csv               # IMDb and TMDB foreign ID mappings
│   └── README.txt              # Official GroupLens dataset documentation
├── models/
│   ├── tfidf_model.pkl         # Serialized TF-IDF vectorizer & metadata matrix
│   └── cf_model.pkl            # Optimized SVD latent factors & item similarity matrix
├── database/
│   └── users.db                # SQLite database with users, preferences & history
├── docs/
│   ├── evaluation_results.json # Verified quantitative evaluation metrics
│   ├── algorithms.md           # Algorithmic & mathematical specifications
│   ├── methodology.md          # Scientific experimental methodology
│   └── project_overview.md     # System architecture overview
├── tests/
│   └── test_recommendations.py # 14 automated unit & integration tests
├── verify_system.py            # Automated system readiness verification script
├── train_model.py              # Offline model training & serialization script
└── download_data.py            # MovieLens dataset downloader utility
```

---

## 🚀 Local Installation & Setup

### Prerequisites
- Python 3.10 to 3.13 (64-bit)
- 4 GB+ System RAM
- Windows 10/11, macOS, or Linux

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/CineAI-Movie-Recommender.git
cd CineAI-Movie-Recommender
```

### 2. Set Up Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
venv\Scripts\activate.bat

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run System Verification & Automated Tests
```bash
# Verify dataset integrity and model artifacts
python verify_system.py

# Run the 14 automated unit and integration tests
python -m unittest tests.test_recommendations
```

### 5. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser and navigate to: **`http://localhost:8501`**

---

## ☁️ Deployment on Streamlit Community Cloud
CineAI is optimized for instant one-click deployment on **Streamlit Community Cloud**:
1. Fork or push this repository to your GitHub account.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/) using your GitHub account.
3. Click **"New app"**.
4. Select your repository: `CineAI-Movie-Recommender`.
5. Set Main file path: `app.py`.
6. Click **"Deploy!"**.
7. Streamlit Cloud automatically installs dependencies from `requirements.txt`, loads the pre-trained models, initializes the SQLite database, and launches your public application URL!

---

## 👥 Academic Team Attribution
- **Institution:** Department of Computer Science & Engineering
- **Project Guide:** Abhikesh
- **Student Team:**
  - **Nella Navven** (Roll No: `12510519`)
  - **Kella Suryaprasanna** (Roll No: `12516522`)
  - **Charanya Bhandari** (Roll No: `12512578`)
- **Date:** November 2026
