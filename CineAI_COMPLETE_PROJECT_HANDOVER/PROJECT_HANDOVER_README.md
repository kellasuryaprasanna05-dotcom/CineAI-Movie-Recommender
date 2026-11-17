# AI-Powered Movie Recommendation System (CineAI)
## Complete Engineering Project Handover & System Documentation

### Project Attribution
- **Project Title:** AI-Powered Movie Recommendation System (CineAI)
- **Academic Department:** Department of Computer Science & Engineering
- **Project Guide:** Abhikesh
- **Student Team:**
  1. **Nella Navven** (Roll No: `12510519`)
  2. **Kella Suryaprasanna** (Roll No: `12516522`)
  3. **Charanya Bhandari** (Roll No: `12512578`)
- **Submission Date:** November 2026

---

## 1. Executive Summary
CineAI is an enterprise-grade movie recommendation application that resolves information overload and cold-start dilemmas in digital streaming platforms. Built with **Streamlit**, **Scikit-Learn**, and **SQLite**, it combines **Content-Based Filtering (TF-IDF + Cosine Similarity)** and **Collaborative Filtering (TruncatedSVD Matrix Factorization)** through a dynamically tunable hybrid engine (&alpha; = 0.50).

---

## 2. Directory Structure of Handover Package
```text
CineAI_COMPLETE_PROJECT_HANDOVER/
├── INSTALLATION_GUIDE.pdf              # Environment setup, execution & troubleshooting
├── PROJECT_ARCHITECTURE.pdf            # 3-Tier layered architecture & SVG diagrams
├── DATASET_DOCUMENTATION.pdf           # MovieLens Latest-Small census & data pipeline
├── MACHINE_LEARNING_DOCUMENTATION.pdf  # Mathematical formulas, TF-IDF, SVD & hybrid equations
├── MODEL_EVALUATION_REPORT.pdf         # Verified benchmarks (RMSE: 0.9094, MAE: 0.7015)
├── API_AND_DATABASE_DOCUMENTATION.pdf  # SQLite schema (4 tables) and offline poster engine
├── VIVA_QUICK_REVISION.pdf             # Top 30 high-yield viva questions & answers
├── PROJECT_HANDOVER_README.md          # Comprehensive markdown handover guide
├── PROJECT_BACKUP.zip                  # Full source code, models, data, db & test suite
└── FINAL_HANDOVER_CHECKLIST.md         # Final engineering audit and checksum validation
```

---

## 3. Quick Start & Execution Instructions

### Prerequisites
- Python 3.10+ (64-bit)
- 4 GB+ RAM
- Windows 10/11, macOS, or Linux

### Step 1: Environment Setup
```bash
# Clone or navigate to the project directory
cd AI-Movie-Recommendation-System

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate
```

### Step 2: Install Required Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Verify Integrity & Run Automated Tests
```bash
# Verify datasets and model artifacts
python verify_system.py

# Run test suite (14 unit and integration tests)
python -m unittest tests.test_recommendations
```

### Step 4: Run the Streamlit Application
```bash
streamlit run app.py --server.port 8501 --server.address 127.0.0.1
```
Open your browser and navigate to: **`http://127.0.0.1:8501`**

---

## 4. Key Architectural Features
1. **Multi-Paradigm Hybrid Engine:** Seamlessly combines content similarity and community rating matrices.
2. **Cold-Start Resilience:** Automatically activates Bayesian weighted popularity ratings when a user has < 5 ratings.
3. **Offline-First Poster Engine:** Zero-crash dual-engine architecture (40+ curated high-res posters + procedural SVG gradient artworks) requiring zero third-party API keys.
4. **Interactive AI Playground:** Real-time parameter slider enabling faculty/users to adjust &alpha; weight dynamically.
5. **Production SQLite Store:** ACID-compliant user authentication, custom preferences, and audit history across 4 relational tables (`users`, `user_preferences`, `user_ratings`, `recommendation_history`).

---

## 5. Model Evaluation Summary (Verified Ground Truth)
| Metric | Verified Value | Interpretation |
| :--- | :---: | :--- |
| **RMSE (Root Mean Squared Error)** | **0.9094** | Outperforms 1.05 global baseline on 5,000 test sample |
| **MAE (Mean Absolute Error)** | **0.7015** | Average rating prediction error is ~0.70 stars |
| **Precision@10 (Test Holdout)** | **0.0072 (0.72%)** | Top-10 hits on 98.3% sparse unobserved test matrix |
| **Recall@10 (Test Holdout)** | **0.0056 (0.56%)** | Retrieval rate of relevant test-set movies |
| **Catalog Coverage** | **0.0157 (1.57%)** | 153 unique movies recommended in sample top-10 lists |
| **Query Latency** | **< 35 ms** | Real-time interactive UI updates |

---

## 6. Troubleshooting FAQ
- **Port 8501 collision:** Run `streamlit run app.py --server.port 8502`.
- **Missing Models:** Run `python train_model.py` to regenerate `cf_model.pkl` and `tfidf_model.pkl`.
- **PowerShell Script Policy:** Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

---
*CineAI Handover Package | Prepared by Nella Navven, Kella Suryaprasanna, Charanya Bhandari | Guided by Abhikesh*
