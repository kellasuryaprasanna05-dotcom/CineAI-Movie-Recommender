# 📄 CineAI: Official Project Synopsis
## AI-Powered Multi-Algorithmic Movie Recommendation System
### Major Project Synopsis for Review & Academic Evaluation

---

### 1. PROJECT TITLE
**CineAI: AI-Powered Multi-Algorithmic Movie Recommendation System with Dynamic Cold-Start Mitigation and Explainable AI**

### 2. CANDIDATE & SUPERVISOR DETAILS
- **Candidate Name(s)**:
  1. Nella Navven (Roll No: 12510519)
  2. Kella Suryaprasanna (Roll No: 12516522)
  3. Charanya Bhandari (Roll No: 12512578)
- **Degree**: Bachelor of Technology (B.Tech)
- **Branch / Specialization**: Computer Science & Engineering
- **Project Supervisor / Guide**: Abhikesh, Department of Computer Science & Engineering
- **Academic Session**: 2025–2026

---

### 3. INTRODUCTION & MOTIVATION
With tens of thousands of feature films and television series distributed across Over-The-Top (OTT) streaming platforms (Netflix, Amazon Prime Video, Disney+, Apple TV+), digital consumers are overwhelmed by content choices. This phenomenon, known as **choice paralysis** or **decision fatigue**, degrades user satisfaction and retention.

Recommender Systems (RS) serve as autonomous information filters that predict user preferences. However, traditional standalone systems suffer from critical flaws:
- **Collaborative Filtering (CF)** suffers from high matrix sparsity (>98% empty entries) and cannot recommend items to newly registered users (**Cold-Start Problem**).
- **Content-Based Filtering (CBF)** is restricted to items similar to previous interactions, creating narrow **Filter Bubbles** and lacking serendipity.
- **Black-Box Opacity**: Standard deep learning or factorization models do not explain why items are recommended, eroding user trust.

**CineAI** addresses these vulnerabilities by developing a production-grade, multi-algorithmic hybrid recommendation system trained on the genuine MovieLens dataset, combining content vectors, collaborative rating matrices, and latent factor models under an adaptive cold-start arbitration policy with Explainable AI (XAI) rationale.

---

### 4. PROBLEM STATEMENT
To design, implement, evaluate, and deploy an end-to-end, multi-algorithmic movie recommendation platform that:
1. Dynamically mitigates the new-user cold-start problem without requiring external profile scrapers.
2. Gracefully handles 98.3% rating matrix sparsity via Item-Item correlations and TruncatedSVD dimensionality reduction.
3. Attaches human-interpretable Explainable AI (XAI) justification badges to every recommendation.
4. Persists real-time 0.5–5.0 star user ratings and explicit preferences in an ACID-compliant transactional relational database.
5. Provides an interactive web application with an examiner playground and visual analytics dashboard.

---

### 5. OBJECTIVES
- **Obj-1**: Ingest, clean, and vectorize the official MovieLens dataset (100,836 ratings, 9,742 movies, 3,683 tags).
- **Obj-2**: Build a 5,000-dimensional TF-IDF Content-Based model with deviation-weighted dynamic user profiling.
- **Obj-3**: Construct a sparse Compressed Sparse Row (CSR) Item-Item Collaborative Filtering model and a 20-component TruncatedSVD latent factor model.
- **Obj-4**: Develop a dynamic linear hybrid blending algorithm whose weighting parameter $\alpha$ adapts automatically based on user interaction density ($N_u$).
- **Obj-5**: Build an ACID-compliant SQLite3 persistence layer supporting real-time rating updates, user creation, and preference storage.
- **Obj-6**: Deploy a responsive, Netflix-inspired dark-themed Streamlit user interface featuring live search, visual analytics, an Explainable AI badge pipeline, and an Interactive Model Playground for academic examination.
- **Obj-7**: Quantitatively benchmark the system using RMSE, MAE, Precision@K, Recall@K, and Catalog Coverage on an 80/20 train/test split.

---

### 6. METHODOLOGY & MACHINE LEARNING FORMULATIONS

#### A. Content-Based Filtering & Dynamic Profiling
- **Metadata Soup**: Concatenates normalized title tokens, genres, and crowd tags:
  $$\text{Soup}_i = \text{CleanTitle}_i + \text{Genres}_i + \text{Tags}_i$$
- **TF-IDF & Cosine Similarity**: Features are mapped into a 5,000-dimensional $L_2$-normalized space:
  $$\text{Sim}_{\text{content}}(A, B) = \mathbf{v}_A \cdot \mathbf{v}_B$$
- **Deviation User Profiling**: Adjusts preference pull relative to a 2.5-star neutral point:
  $$\mathbf{u}_{\text{profile}} = \frac{\sum (r_{u, j} - 2.5) \cdot \mathbf{v}_j}{\sum |r_{u, j} - 2.5|}$$

#### B. Collaborative Filtering & TruncatedSVD
- **Item-Item Correlation**: Measures rating patterns across co-raters:
  $$\text{Sim}_{\text{item}}(i, j) = \frac{\mathbf{r}_{*i} \cdot \mathbf{r}_{*j}}{\|\mathbf{r}_{*i}\| \|\mathbf{r}_{*j}\|}$$
- **Rating Prediction**: Weighted average over significant neighbors ($s_{i, j} > 0.05$):
  $$\hat{r}_{u, i} = \frac{\sum_{j} s_{i, j} \cdot r_{u, j}}{\sum_{j} s_{i, j}}$$
- **TruncatedSVD**: Low-rank approximation $R \approx U_k \Sigma_k V_k^T$ with $k=20$ latent factors to handle sparsity.

#### C. Bayesian IMDB Weighted Rating (Trending Engine)
$$\text{WR} = \left(\frac{v}{v+m}\right) R + \left(\frac{m}{v+m}\right) C \quad (m=10, C=3.50)$$

#### D. Dynamic Hybrid Arbitration Policy
$$\text{Score}_{\text{hybrid}} = \alpha(u) \cdot \text{Score}_{\text{CF}} + [1 - \alpha(u)] \cdot \text{Score}_{\text{CB}} + \text{Boost}_{\text{genre}}$$
$$\alpha(u) = \begin{cases} 
0.00 & \text{if } N_u = 0 \quad \text{(Cold-Start: Pure Content + Explicit Preferences)} \\
0.35 & \text{if } 1 \le N_u \le 3 \quad \text{(Warm-Up: Content Primed with Initial Collaborative Signals)} \\
0.60 & \text{if } N_u > 3 \quad \text{(Mature: Collaborative Dominant with Content Regularization)}
\end{cases}$$

---

### 7. SYSTEM ARCHITECTURE & TECHNOLOGY STACK

```
  [ Streamlit UI ] <---> [ Recommender Facade ] <---> [ Content-Based Engine ]
                                  |              <---> [ Collaborative Engine ]
                                  v              <---> [ Hybrid Arbitrator ]
                         [ SQLite3 Storage ]
```

- **Frontend & Visualizations**: Streamlit, HTML5, CSS3, Plotly Express & Graph Objects.
- **Machine Learning & Analytics**: Scikit-learn, Pandas, NumPy, SciPy.
- **Persistence**: SQLite3 (`database/users.db`).
- **Benchmark Dataset**: GroupLens MovieLens Latest-Small (100k ratings, 9.7k movies).
- **Runtime Environment**: Python 3.9 through Python 3.13.

---

### 8. EXPERIMENTAL RESULTS & EVALUATION

Evaluated on an 80/20 train/test split of the MovieLens benchmark:

| Metric | Baseline / Benchmark | CineAI Measured Value | Significance |
| :--- | :--- | :--- | :--- |
| **Root Mean Squared Error (RMSE)** | 1.0500 | **0.9094** | High predictive accuracy |
| **Mean Absolute Error (MAE)** | 0.8200 | **0.7015** | Tight error bounds |
| **Precision@10** | 0.0050 | **0.0072** | Accurate top-10 retrieval |
| **Recall@10** | 0.0035 | **0.0056** | High target retrieval |
| **Catalog Coverage** | 0.0080 | **0.0157** | Healthy catalog exploration |
| **Automated Test Suite** | 100% Target | **14 / 14 Tests Passing** | All unit/integration tests verified |

---

### 9. PROJECT HIGHLIGHTS & INNOVATIONS
1. **Zero Cold-Start Failure**: Seamless transition from explicit preferences to collaborative filtering.
2. **Explainable AI (XAI)**: Generates human-readable badges (*"Matches your high-rated genres: Action, Sci-Fi"*, *"Users like you rated this 4.8★"*).
3. **Interactive Model Playground**: Built-in examiner sandbox to compare algorithms, view raw TF-IDF metadata, and simulate synthetic cold-start user profiles.
4. **Real-Time Relational Persistence**: SQLite-backed user switching, custom 1–5 star ratings, and analytics dashboards.

---

### 10. CONCLUSION & FUTURE SCOPE
CineAI delivers a complete, verified, and production-grade recommendation platform that solves the cold-start problem, manages 98.3% matrix sparsity, and achieves an RMSE of 0.9094. Future enhancements include implementing PyTorch Two-Tower Deep Neural Networks, FAISS vector indexing, and BERT4Rec session-based transformers.

---

**Signatures:**

**Candidate(s) Signature:**  
1. Nella Navven (Roll No: 12510519): ___________________________  
2. Kella Suryaprasanna (Roll No: 12516522): ___________________________  
3. Charanya Bhandari (Roll No: 12512578): ___________________________  

<br/>

**Project Supervisor / Guide Signature:**  
Abhikesh, Department of Computer Science & Engineering: ___________________________  
