# Algorithms & Mathematical Formulation: CineAI

## 1. Content-Based Recommendation Algorithm

### Step 1: Text Vectorization via TF-IDF
Given a collection of movie metadata documents $D = \{d_1, d_2, \dots, d_M\}$, each term $t$ in document $d$ is assigned a TF-IDF weight:
$$\text{TF}(t, d) = \frac{f_{t, d}}{\sum_{t' \in d} f_{t', d}}$$
$$\text{IDF}(t, D) = \log \left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
$$\mathbf{v}_{i} = \left[ \text{TF-IDF}(t_1, d_i), \text{TF-IDF}(t_2, d_i), \dots, \text{TF-IDF}(t_V, d_i) \right]$$
The resulting vector is $L_2$-normalized:
$$\hat{\mathbf{v}}_i = \frac{\mathbf{v}_i}{\|\mathbf{v}_i\|_2}$$

### Step 2: Cosine Similarity Matrix
The similarity between movie $i$ and movie $j$ is:
$$\text{Sim}_{\text{content}}(i, j) = \hat{\mathbf{v}}_i \cdot \hat{\mathbf{v}}_j = \frac{\sum_{k=1}^V v_{i,k} v_{j,k}}{\sqrt{\sum_{k=1}^V v_{i,k}^2} \sqrt{\sum_{k=1}^V v_{j,k}^2}}$$

### Step 3: Top-N Item Similarity Search
For a query movie $q$:
$$\mathcal{S}_{\text{top}}(q) = \operatorname{arg\,top}_N \left\{ \text{Sim}_{\text{content}}(q, j) \mid j \in M, j \neq q \right\}$$

---

## 2. Collaborative Filtering Algorithms

### Approach A: Item-Based Collaborative Filtering
Item-Based CF assumes that users prefer items similar to what they have rated highly in the past.

Given user ratings $R \in \mathbb{R}^{U \times M}$, the similarity between movie $i$ and movie $j$ across all observed users is:
$$s_{i, j} = \frac{\sum_{u \in U_{ij}} (R_{u, i} - \bar{R}_i)(R_{u, j} - \bar{R}_j)}{\sqrt{\sum_{u \in U_{ij}} (R_{u, i} - \bar{R}_i)^2} \sqrt{\sum_{u \in U_{ij}} (R_{u, j} - \bar{R}_j)^2}}$$

#### Rating Prediction
For active user $a$ and candidate unrated movie $i$:
$$\hat{R}_{a, i} = \frac{\sum_{j \in \text{Rated}_a, s_{i, j} > \tau} s_{i, j} \cdot R_{a, j}}{\sum_{j \in \text{Rated}_a, s_{i, j} > \tau} |s_{i, j}|}$$
where $\tau = 0.05$ filters out noisy negative or near-zero correlations.

### Approach B: Matrix Factorization via TruncatedSVD
To uncover latent semantic concepts (e.g. moody pacing, witty dialogue, high-octane action):
$$R \approx U_k \Sigma_k V_k^T$$
- $U_k \in \mathbb{R}^{U \times k}$: User representations in latent factor space ($k=20$).
- $\Sigma_k \in \mathbb{R}^{k \times k}$: Singular values representing factor importances.
- $V_k^T \in \mathbb{R}^{k \times M}$: Movie representations in latent factor space.

---

## 3. Hybrid Blending Algorithm

```
Algorithm 1: Dynamic Hybrid Movie Recommendation
Input: User ratings R_u, User favorite genres G_u, Target count N, Custom weight alpha
Output: Top-N Recommended Movies List

1: if |R_u| == 0 then
2:    Candidates <- ContentRecommender.RecommendByPreferences(G_u, top=50)
3:    Return Candidates[:N]
4: end if

5: if alpha is None then
6:    alpha <- (|R_u| <= 3) ? 0.35 : 0.60
7: end if

8: CF_Recs <- CollaborativeFiltering.PredictRatings(R_u, top=50)
9: CB_Recs <- ContentRecommender.RecommendForUserProfile(R_u, top=50)

10: CandidateSet <- Union(Keys(CF_Recs), Keys(CB_Recs))
11: for each movie m in CandidateSet do
12:    s_cf <- Normalize(CF_Recs.get(m, 0.0))
13:    s_cb <- Normalize(CB_Recs.get(m, 0.0))
14:    boost <- ComputeGenreMatchBoost(m.genres, G_u)
15:    Score[m] <- alpha * s_cf + (1 - alpha) * s_cb + boost
16: end for

17: RankedList <- SortDescending(CandidateSet, by=Score)
18: Return RankedList[:N]
```

---

## 4. Evaluation Metrics & Experimental Results

Evaluated on an 80/20 train/test split of the MovieLens Latest-Small dataset:

| Metric | Formula | Value | Interpretation |
| :--- | :--- | :--- | :--- |
| **RMSE** | $\sqrt{\frac{1}{N}\sum_{i=1}^N (y_i - \hat{y}_i)^2}$ | **0.9094** | Strong predictive accuracy for 5-star rating scale |
| **MAE** | $\frac{1}{N}\sum_{i=1}^N \|y_i - \hat{y}_i\|$ | **0.7015** | Average rating deviation is < 0.75 stars |
| **Precision@10** | $\frac{\|\text{Rec} \cap \text{Relevant}\|}{10}$ | **0.0072** | Top-10 ranking relevance on unobserved test items |
| **Recall@10** | $\frac{\|\text{Rec} \cap \text{Relevant}\|}{\|\text{Relevant}\|}$ | **0.0056** | Retrieval rate of user's favorite test items |
| **Catalog Coverage** | $\frac{\|\bigcup \text{Rec}\|}{\|Catalog\|}$ | **0.0157** | Diversity of recommended items across evaluation cohort |
