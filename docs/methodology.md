# Methodology: AI-Powered Movie Recommendation System

## 1. Data Engineering & Preprocessing Pipeline

The data engineering pipeline transforms raw MovieLens CSV files into structured, feature-rich representations suitable for both text vectorization and matrix decomposition:

### 1.1 Year Extraction & Title Normalization
Raw MovieLens movie titles append the release year in parentheses (e.g. `Toy Story (1995)`). Using regular expressions:
$$\text{Regex}: \quad \backslash((\backslash d\{4\})\backslash)$$
We extract the 4-digit release year and preserve a cleaned title for crisp search indexing and display.

### 1.2 Genre Processing & Metadata Soup
Movie genres in MovieLens are pipe-separated strings (`Action|Adventure|Sci-Fi`). We:
1. Replace `(no genres listed)` with empty tokens.
2. Tokenize genres into discrete lists.
3. Group and concatenate user tags per movie from `tags.csv`.
4. Construct a unified **Metadata Soup** per film:
   $$\text{Soup}_i = \text{CleanTitle}_i \parallel \text{Genres}_i \parallel \text{Tags}_i$$

### 1.3 Bayesian Weighted Rating Calculation
To display meaningful trending movies without small-sample bias (e.g., a movie with 1 rating of 5.0 outranking a classic with 300 ratings averaging 4.5), we apply IMDB's Weighted Rating formula:
$$WR = \left(\frac{v}{v+m}\right) R + \left(\frac{m}{v+m}\right) C$$
Where:
- $v$: Number of ratings for the movie
- $m$: Minimum vote threshold ($m = 10$)
- $R$: Average rating of the movie
- $C$: Mean rating across all movies ($C \approx 3.50$)

---

## 2. Recommendation Methodologies

### 2.1 Content-Based Filtering
- **Feature Extraction**: TF-IDF vectorization with n-gram range $(1, 2)$, English stop words removal, and a maximum vocabulary of 5,000 features.
- **Similarity Metric**: Cosine Similarity between TF-IDF document vectors.
- **Dynamic User Profiling**: Rather than relying only on a single seed movie, CineAI constructs a user preference vector $\mathbf{u}_{profile}$ by computing a weighted average of the TF-IDF vectors of all movies the user has rated, centered around a neutral baseline of 2.5:
  $$\mathbf{u}_{profile} = \frac{\sum_{j \in \text{Rated}} (r_{u,j} - 2.5) \cdot \mathbf{v}_j}{\sum_{j \in \text{Rated}} |r_{u,j} - 2.5|}$$

### 2.2 Collaborative Filtering
- **User-Movie Interaction Matrix**: Constructed using pivot tables over users and movies with rating threshold filtering ($\ge 5$ ratings).
- **Item-Item Collaborative Filtering**: Item vectors $\mathbf{r}_{*i}$ and $\mathbf{r}_{*j}$ are compared using cosine similarity across all user ratings.
- **Rating Prediction**: Unrated candidate movies are scored using similarity-weighted ratings:
  $$\hat{r}_{u, i} = \frac{\sum_{j \in \text{Rated}_u, s_{i,j} > 0.05} s_{i, j} \cdot r_{u, j}}{\sum_{j \in \text{Rated}_u, s_{i,j} > 0.05} s_{i, j}}$$
- **Matrix Factorization (TruncatedSVD)**: Decomposes the interaction matrix into $k=20$ latent factors to discover low-rank representation and capture global taste manifolds.

### 2.3 Hybrid Recommendation Strategy
A weighted linear combination merges normalized Content-Based and Collaborative Filtering scores:
$$\text{Score}_{\text{hybrid}} = \alpha \cdot \text{Score}_{\text{CF}} + (1 - \alpha) \cdot \text{Score}_{\text{Content}} + \text{Boost}_{\text{genre}}$$
The blending weight $\alpha$ adapts dynamically:
- **0 Ratings (Cold-Start)**: $\alpha = 0.0$ (pure content + explicit preferences)
- **1-3 Ratings (Warm-Start)**: $\alpha = 0.35$ (lean toward content with initial CF signal)
- **>3 Ratings (Established)**: $\alpha = 0.60$ (collaborative emphasis with content grounding)
- **Interactive Control**: The user can also override $\alpha$ via a UI slider in the recommendations tab.

---

## 3. Storage & Persistence
- SQLite database (`database/users.db`) with relational integrity, foreign keys, cascading deletions, and timestamping.
- Tables: `users`, `user_preferences`, `user_ratings`, and `recommendation_history`.
- Pickled model artifacts in `models/` for near-instant application startup.
