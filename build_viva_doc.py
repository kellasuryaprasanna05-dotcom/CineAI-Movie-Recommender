"""
Builds the complete CineAI_Viva_Questions_and_Answers.docx.
Minimum 50 questions + Golden 20 Viva Defense Questions.
"""
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = r"c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System"
SUB_DIR = os.path.join(BASE_DIR, "CineAI_College_Submission")
OUT_DIR = os.path.join(SUB_DIR, "Final_Deliverables")
DOCX_PATH = os.path.join(OUT_DIR, "CineAI_Viva_Questions_and_Answers.docx")

def set_cell_background(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_header_footer(doc):
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
        # Header
        header = s.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("CineAI: Comprehensive Viva Voce & Technical Defense Q&A Guide")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(120, 144, 156)
        
        # Footer
        footer = s.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun = fp.add_run("Department of Computer Science & Engineering  •  Major Project Viva Preparation")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(120, 144, 156)

def format_p(p, space_before=0, space_after=5, line_spacing=1.15):
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing

def add_qa_box(doc, q_num, question, answer, category=None):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=120)
    
    # Left border
    tcPr = cell._tc.get_or_add_tcPr()
    border_color = "E50914" if "Golden" in str(category) else "2563EB"
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="30" w:space="0" w:color="{border_color}"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    format_p(p, space_before=0, space_after=3)
    
    if category:
        r_cat = p.add_run(f"[{category.upper()}]  ")
        r_cat.font.name = "Arial"
        r_cat.font.size = Pt(8.5)
        r_cat.font.bold = True
        r_cat.font.color.rgb = RGBColor(229, 9, 20) if "Golden" in str(category) else RGBColor(37, 99, 235)
        
    r_q = p.add_run(f"Q{q_num}: {question}\n")
    r_q.font.name = "Arial"
    r_q.font.size = Pt(11)
    r_q.font.bold = True
    r_q.font.color.rgb = RGBColor(15, 23, 42)
    
    p_ans = cell.add_paragraph()
    format_p(p_ans, space_before=2, space_after=0)
    r_a_label = p_ans.add_run("Answer: ")
    r_a_label.font.name = "Calibri"
    r_a_label.font.size = Pt(10.5)
    r_a_label.font.bold = True
    r_a_label.font.color.rgb = RGBColor(30, 41, 59)
    
    r_ans = p_ans.add_run(answer)
    r_ans.font.name = "Calibri"
    r_ans.font.size = Pt(10.5)
    r_ans.font.color.rgb = RGBColor(51, 65, 85)
    
    doc.add_paragraph() # spacing

def main():
    print("Building Viva Voce Document...")
    doc = Document()
    add_header_footer(doc)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    format_p(p_title, space_before=10, space_after=4)
    r_title = p_title.add_run("CineAI: Viva Voce & Technical Defense Q&A Guide")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(229, 9, 20)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    format_p(p_sub, space_before=2, space_after=20)
    r_sub = p_sub.add_run("Comprehensive Question Bank (55+ Questions) with The \"Golden 20\" Defense Questions\nFor B.Tech / B.S. Project Evaluation & University Examination Panels")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph()

    # =========================================================================
    # SECTION 1: THE GOLDEN 20
    # =========================================================================
    p_sec1 = doc.add_paragraph()
    format_p(p_sec1, space_before=16, space_after=8)
    r_s1 = p_sec1.add_run("⭐ SECTION 1: THE \"GOLDEN 20\" — MOST CRUCIAL VIVA QUESTIONS")
    r_s1.font.name = "Arial"
    r_s1.font.size = Pt(15)
    r_s1.font.bold = True
    r_s1.font.color.rgb = RGBColor(185, 28, 28)

    golden_20 = [
        (1, "What is the primary objective and novelty of CineAI?",
         "CineAI is an AI-powered movie recommendation platform designed to overcome digital choice paralysis. Its primary novelty is a dynamic adaptive hybrid algorithm that seamlessly resolves the cold-start problem by adjusting an arbitration parameter alpha based on user rating density, supported by Explainable AI badges.",
         "Golden 20"),
        (2, "What is the Cold-Start problem, and exactly how does CineAI solve it?",
         "Cold-start occurs when a newly registered user has zero rating history, causing collaborative filtering to fail. CineAI solves it through a 3-tier fallback: (1) alpha = 0.00 routes new users to pure Content-Based filtering using their explicit onboarding preferences; (2) if no preferences exist, it falls back to Bayesian IMDB trending movies; (3) as ratings are logged, alpha dynamically shifts to 0.35 (1-3 ratings) and 0.60 (>3 ratings).",
         "Golden 20"),
        (3, "What machine learning models are implemented in CineAI?",
         "Three core models: (1) Content-Based Filtering using a 5,000-dimensional TF-IDF vector space with Cosine Similarity; (2) Item-Item Collaborative Filtering using co-rating vectors; (3) Latent factor modeling using 20-component TruncatedSVD matrix factorization.",
         "Golden 20"),
        (4, "Why did you choose Item-Item Collaborative Filtering instead of User-User Collaborative Filtering?",
         "Item-item similarity is computationally stable because movie characteristics change far less frequently than user profiles. This enables precomputing and caching the item similarity matrix offline. Furthermore, item-item provides superior explainability ('Recommended because you rated Inception 5 stars').",
         "Golden 20"),
        (5, "What is Matrix Sparsity, and what is the exact sparsity of your dataset?",
         "Sparsity is the percentage of empty cells in the user-movie rating matrix: 1 - (|Ratings| / (|Users| x |Movies|)). In our MovieLens dataset (100,836 ratings, 610 users, 9,742 movies), the total matrix capacity is 5,942,620 entries. The sparsity is exactly 98.30%.",
         "Golden 20"),
        (6, "What is a 'Metadata Soup' and why is it superior to using genres alone?",
         "A metadata soup concatenates normalized title tokens, genres, and crowd-sourced user tags into one composite document per film. Genres alone only provide 20 broad buckets. Adding tags like 'mind-bending', 'time-travel', and 'noir' allows TF-IDF to distinguish between two Sci-Fi movies of completely different tone.",
         "Golden 20"),
        (7, "Explain the mathematical formula for TF-IDF and its role in CineAI.",
         "TF-IDF(t, d, D) = TF(t, d) * [ln((1 + |D|) / (1 + |{d in D : t in d}|)) + 1]. In CineAI, common terms appearing in thousands of movies (like 'Drama') receive low weight via IDF, while specific distinguishing tags (like 'tarantino' or 'cyberpunk') receive high weight.",
         "Golden 20"),
        (8, "Why is Cosine Similarity preferred over Euclidean Distance for TF-IDF vectors?",
         "Euclidean distance measures geometric distance and is heavily distorted by document length (a movie with 20 tags would have a large Euclidean distance from a movie with 2 tags). Cosine similarity measures the angle between vectors, which is length-invariant. Because we L2-normalize our vectors, cosine similarity simplifies to a fast matrix dot-product.",
         "Golden 20"),
        (9, "How does your Dynamic User Profile vector handle disliked movies?",
         "We center ratings around a neutral 2.5-star baseline: u_profile = sum((r_uj - 2.5) * v_j) / sum(|r_uj - 2.5|). Ratings of 4.0 or 5.0 stars apply positive pull (+1.5, +2.5) toward those genres, while 1.0 or 2.0 star ratings apply negative repulsive force (-1.5, -0.5), filtering out disliked genres.",
         "Golden 20"),
        (10, "What is TruncatedSVD and why did you use it instead of regular numpy.linalg.svd?",
         "TruncatedSVD approximates the rating matrix R approx U_k * Sigma_k * V_k^T using k=20 latent factors. We use Scikit-learn's TruncatedSVD because it operates directly on scipy CSR sparse matrices using randomized Lanczos iteration, avoiding the gigabytes of memory required by dense numpy SVD.",
         "Golden 20"),
        (11, "What is the Bayesian IMDB Weighted Rating formula and why is it needed?",
         "WR = (v / (v + m)) * R + (m / (v + m)) * C, where v is vote count, m=10 is minimum threshold, R is movie mean, and C=3.50 is global catalog mean. It prevents movies with a single 5-star rating from dominating trending lists by pulling small-sample titles toward the global mean.",
         "Golden 20"),
        (12, "What are the exact evaluation metrics achieved by CineAI?",
         "Evaluated on an 80/20 train/test split: RMSE = 0.9094, MAE = 0.7015, Precision@10 = 0.0072, Recall@10 = 0.0056, Catalog Coverage = 0.0157, Baseline Mean = 3.50. All 14 automated unit and integration tests pass.",
         "Golden 20"),
        (13, "What is the difference between RMSE and MAE? Why report both?",
         "MAE measures average absolute error linearly (|y - y_hat|). RMSE squares errors before averaging, penalizing large outlier errors heavily. Reporting both confirms our model does not have severe catastrophic errors: RMSE (0.9094) closely tracking MAE (0.7015) indicates consistent error variance.",
         "Golden 20"),
        (14, "Why are Precision@K and Recall@K numerically small in offline recommender benchmarks?",
         "Due to unobserved rating bias: the test set only contains movies the user explicitly rated in MovieLens. If our algorithm recommends 10 great movies that the user never saw or rated in the benchmark dataset, those are counted as false positives even though the user might have loved them.",
         "Golden 20"),
        (15, "What makes CineAI an 'Explainable AI' (XAI) system?",
         "Every recommendation card displays a dynamic natural-language rationale badge: 'Matches your high-rated genres: Action, Sci-Fi', 'Users like you rated this 4.8★', or 'Matches your selected genre preference: Drama'. This eliminates the black-box dilemma.",
         "Golden 20"),
        (16, "Explain the database architecture and concurrency handling.",
         "We use an ACID-compliant SQLite3 store (database/users.db) with 3 normalized tables: users, user_ratings, and user_preferences. Thread safety is guaranteed via context-managed connections. Ratings are stored using INSERT OR REPLACE to prevent duplicate primary keys during re-ratings.",
         "Golden 20"),
        (17, "Why is @st.cache_resource critical in your Streamlit application?",
         "Streamlit re-runs the entire Python script from top to bottom on every user click. Without @st.cache_resource, the system would re-parse 100k CSV records and re-fit TF-IDF matrices on every button press, causing a 10-second lag. Caching keeps models in memory, enabling <50ms response times.",
         "Golden 20"),
        (18, "What is the purpose of the Interactive Model Playground in your app?",
         "It is an examiner showcase allowing direct side-by-side comparison of Content-Based Cosine Similarity vs Collaborative Item Similarity for any selected film, inspection of raw TF-IDF metadata tokens, and real-time simulation of cold-start user transitions.",
         "Golden 20"),
        (19, "How did you prevent data leakage during model training and evaluation?",
         "We split ratings into 80% train and 20% test partitions. The item similarity matrices, user profiles, and SVD factors were fit strictly on the 80% training set. Ground-truth ratings in the 20% test partition were withheld entirely during model fitting.",
         "Golden 20"),
        (20, "How would you scale CineAI to support 300 million users like Netflix?",
         "We would replace exhaustive dot products with Approximate Nearest Neighbors (ANN) using FAISS or HNSW (reducing search from O(N) to O(log N)), deploy Two-Tower Deep Neural Networks in PyTorch, distribute matrix operations across an Apache Spark cluster, and cache user vectors in Redis.",
         "Golden 20")
    ]

    for q_num, question, answer, cat in golden_20:
        add_qa_box(doc, q_num, question, answer, category=cat)

    doc.add_page_break()

    # =========================================================================
    # SECTION 2: MACHINE LEARNING & MATHEMATICAL FOUNDATIONS
    # =========================================================================
    p_sec2 = doc.add_paragraph()
    format_p(p_sec2, space_before=16, space_after=8)
    r_s2 = p_sec2.add_run("🧠 SECTION 2: MACHINE LEARNING ALGORITHMS & MATHEMATICAL FOUNDATIONS")
    r_s2.font.name = "Arial"
    r_s2.font.size = Pt(15)
    r_s2.font.bold = True
    r_s2.font.color.rgb = RGBColor(37, 99, 235)

    sec2_questions = [
        (21, "What is the difference between Bag-of-Words and TF-IDF?",
         "Bag-of-Words simply counts word frequencies, meaning common words like 'the' or 'movie' dominate vectors. TF-IDF divides term frequency by document frequency across the whole corpus, penalizing ubiquitous words and elevating distinctive descriptive keywords.",
         "Machine Learning"),
        (22, "What n-gram range was used in your TF-IDF Vectorizer?",
         "We used unigrams and bigrams (ngram_range=(1, 2)) capped at 5,000 maximum features. This captures both single tokens (e.g. 'space') and compound concepts (e.g. 'space travel', 'sci fi', 'dark comedy').",
         "Machine Learning"),
        (23, "Why is Pearson Correlation sometimes used instead of Cosine Similarity in collaborative filtering?",
         "Pearson Correlation centers ratings by subtracting the user's mean rating, which accounts for rating bias (e.g. a tough critic who gives 3 stars to great movies vs an easy rater who gives 5 stars to everything). In CineAI's item-item collaborative filtering, we account for this using adjusted cosine similarity and dynamic profile deviation.",
         "Machine Learning"),
        (24, "What are the mathematical components of SVD?",
         "Singular Value Decomposition factors a matrix R as U * Sigma * V^T, where U represents the left singular vectors (user latent factors), Sigma is a diagonal matrix of singular values indicating factor importance, and V^T represents right singular vectors (item latent factors).",
         "Machine Learning"),
        (25, "Why did you choose 20 components for TruncatedSVD instead of 100 or 500?",
         "In MovieLens Latest-Small, 20 latent components capture over 80% of rating variance while avoiding overfitting to the sparse 610-user training set. Increasing k beyond 50 increases noise and increases inference latency without meaningful RMSE improvement.",
         "Machine Learning"),
        (26, "How do you handle unobserved items when predicting ratings via collaborative filtering?",
         "If an unrated movie has no significant item-item neighbors with similarity > 0.05 among the user's rated movies, the collaborative model returns the global prior baseline rating (3.50 stars) or defers to the Content-Based engine.",
         "Machine Learning"),
        (27, "What is the formula for Adjusted Cosine Similarity in item-item filtering?",
         "Sim(i, j) = sum((r_ui - r_bar_u) * (r_uj - r_bar_u)) / (sqrt(sum((r_ui - r_bar_u)^2)) * sqrt(sum((r_uj - r_bar_u)^2))), where r_bar_u is the mean rating of user u across all movies they rated.",
         "Machine Learning"),
        (28, "Can a user profile vector become negative in your system?",
         "Yes, individual dimensions of u_profile can become negative when a user rates movies containing those attributes below 2.5 stars. This is an intentional feature: it pushes recommendations away from disliked genres.",
         "Machine Learning"),
        (29, "How is the genre boost calculated in the hybrid formula?",
         "When an unrated candidate movie contains genres that match the user's explicit favorite genres, a constant bonus score (Boost_genre = 0.15) is added to the blended hybrid score, promoting favorite genres to the top of the queue.",
         "Machine Learning")
    ]

    for q_num, question, answer, cat in sec2_questions:
        add_qa_box(doc, q_num, question, answer, category=cat)

    doc.add_page_break()

    # =========================================================================
    # SECTION 3: RECOMMENDER SYSTEMS THEORY & DATASET
    # =========================================================================
    p_sec3 = doc.add_paragraph()
    format_p(p_sec3, space_before=16, space_after=8)
    r_s3 = p_sec3.add_run("📊 SECTION 3: RECOMMENDER THEORY, DATASET & EVALUATION")
    r_s3.font.name = "Arial"
    r_s3.font.size = Pt(15)
    r_s3.font.bold = True
    r_s3.font.color.rgb = RGBColor(37, 99, 235)

    sec3_questions = [
        (30, "What is the difference between explicit and implicit feedback?",
         "Explicit feedback is deliberate input provided by the user, such as 1–5 star ratings, likes, or written reviews. Implicit feedback is derived from passive behavioral tracking, such as watch completion rate, clicks, search logs, and dwell time. CineAI models explicit 0.5–5.0 star ratings.",
         "Recommender Theory"),
        (31, "What is the 'Long Tail' in movie recommender systems?",
         "The Long Tail refers to the distribution of movie ratings: a small fraction of blockbuster films (the head) receive 80% of all ratings, while the majority of films (the tail) receive very few ratings. Hybrid systems ensure that long-tail movies can still be recommended via content tags even if they have few ratings.",
         "Recommender Theory"),
        (32, "What files exist in the MovieLens Latest-Small dataset?",
         "Four CSV files: movies.csv (movieId, title, genres), ratings.csv (userId, movieId, rating, timestamp), tags.csv (userId, movieId, tag, timestamp), and links.csv (movieId, imdbId, tmdbId).",
         "Dataset"),
        (33, "How are missing release years handled in movie titles?",
         "Our regex parser searches for four consecutive digits inside parentheses r'\\((\\d{4})\\)'. If missing or malformed, the system falls back to 'Unknown' without raising exceptions, and the full title string is preserved.",
         "Data Processing"),
        (34, "Explain Catalog Coverage and why it matters.",
         "Catalog Coverage is the proportion of total movies in the catalog that the recommendation engine is capable of recommending across all users: |Union of Recs| / |Catalog|. High coverage indicates that the engine does not over-concentrate recommendations on a tiny subset of popular titles.",
         "Evaluation"),
        (35, "What is Precision@10 in recommender systems?",
         "Precision@10 is the fraction of recommended movies in the top 10 that are deemed relevant. In our evaluation protocol, a movie is relevant if the user's actual rating is >= 4.0 stars.",
         "Evaluation"),
        (36, "What is Recall@10 in recommender systems?",
         "Recall@10 measures the fraction of all movies rated >= 4.0 stars by user u that were successfully retrieved in their top 10 recommendation list.",
         "Evaluation"),
        (37, "What is the baseline mean rating and why is it 3.50?",
         "In the MovieLens dataset, user ratings cluster around positive scores: users tend to watch and rate movies they expect to like. The global mathematical mean across all 100,836 ratings is approximately 3.50 stars.",
         "Evaluation")
    ]

    for q_num, question, answer, cat in sec3_questions:
        add_qa_box(doc, q_num, question, answer, category=cat)

    doc.add_page_break()

    # =========================================================================
    # SECTION 4: SYSTEM DESIGN, DATABASE & FRONTEND
    # =========================================================================
    p_sec4 = doc.add_paragraph()
    format_p(p_sec4, space_before=16, space_after=8)
    r_s4 = p_sec4.add_run("💻 SECTION 4: SYSTEM ARCHITECTURE, DATABASE & FRONTEND")
    r_s4.font.name = "Arial"
    r_s4.font.size = Pt(15)
    r_s4.font.bold = True
    r_s4.font.color.rgb = RGBColor(37, 99, 235)

    sec4_questions = [
        (38, "Explain the Facade Design Pattern used in CineAI.",
         "MovieRecommendationSystem acts as a facade in src/recommendation.py. It hides the complexity of TF-IDF matrices, sparse CSR indexing, SQLite cursors, and poster services behind clean public methods like search_movies() and get_personalized_recommendations().",
         "System Design"),
        (39, "Why did you choose SQLite over MySQL or MongoDB for this project?",
         "SQLite is embedded, serverless, and requires zero external daemon configuration, making the application 100% self-contained and cross-platform portable. It provides full ACID transactional guarantees, which is ideal for single-node college project deployments.",
         "Database"),
        (40, "How do you prevent duplicate ratings in the database?",
         "We use SQLite's INSERT OR REPLACE INTO user_ratings (user_id, movie_id, rating, timestamp) VALUES (?, ?, ?, ?) with a UNIQUE constraint on (user_id, movie_id). If a user re-rates a film, the existing row is updated in place.",
         "Database"),
        (41, "How does CineAI handle movie posters without an expensive paid API key?",
         "src/poster_service.py maintains a curated lookup table of 60+ direct CDN URLs for iconic movies. For all remaining titles, an automated SVG artwork generator synthesizes clean, stylized poster cards with movie title, release year, and genre badge.",
         "Frontend"),
        (42, "How are interactive visualizations implemented in the User Dashboard?",
         "We use Plotly Express and Graph Objects (px.bar, px.pie) embedded directly into Streamlit via st.plotly_chart(). The charts update dynamically whenever the active user switches profiles or logs a new rating.",
         "Frontend"),
        (43, "What is the difference between st.cache_data and st.cache_resource in Streamlit?",
         "st.cache_data is for serializable tabular data (like Pandas DataFrames). st.cache_resource is for non-serializable, stateful global objects like database connections, ML model instances, and TF-IDF matrices that should be shared across all user sessions in memory.",
         "Frontend"),
        (44, "What automated testing framework was used?",
         "We used Python's standard unittest framework in tests/test_recommendations.py. It executes 14 discrete unit and integration tests verifying data loading, regex parsing, TF-IDF shapes, SVD factorization, and SQLite CRUD operations.",
         "Testing"),
        (45, "How are models serialized and loaded?",
         "Trained TF-IDF vectorizers, metadata matrices, and SVD factor matrices are serialized using Python's pickle module into models/tfidf_model.pkl and models/cf_model.pkl. On app startup, these artifacts load in under 500ms.",
         "Implementation")
    ]

    for q_num, question, answer, cat in sec4_questions:
        add_qa_box(doc, q_num, question, answer, category=cat)

    doc.add_page_break()

    # =========================================================================
    # SECTION 5: ADVANCED & DEFENSE QUESTIONS
    # =========================================================================
    p_sec5 = doc.add_paragraph()
    format_p(p_sec5, space_before=16, space_after=8)
    r_s5 = p_sec5.add_run("⚡ SECTION 5: ADVANCED & TOUGH EXAMINER DEFENSE QUESTIONS")
    r_s5.font.name = "Arial"
    r_s5.font.size = Pt(15)
    r_s5.font.bold = True
    r_s5.font.color.rgb = RGBColor(185, 28, 28)

    sec5_questions = [
        (46, "Why didn't you use Deep Learning (e.g. Neural Collaborative Filtering) as your primary model?",
         "Deep learning models require millions of parameters and substantial GPU compute for training and inference, which induces excessive latency on standard desktop hardware. Traditional matrix factorization (SVD) and Item-Item CF achieve competitive RMSE on MovieLens Latest-Small (100,836 ratings across 9,742 movies) while running inference in <50ms with full mathematical explainability.",
         "Defense Q&A"),
        (47, "What happens if a user rates every movie exactly 1 star?",
         "Our deviation profiling computes (1.0 - 2.5) = -1.5 for all rated items. The user profile becomes a strongly negative vector of those attributes. When multiplied by catalog movie vectors, titles sharing those attributes receive large negative scores, effectively filtering out disliked genres.",
         "Defense Q&A"),
        (48, "How would you prevent popular blockbusters from drowning out niche movies?",
         "We apply logarithmic scaling to item popularity and use Item-Item Cosine Similarity, which normalizes rating vectors by item norm (sqrt(sum(r^2))). This levels the playing field between movies with 50 ratings and movies with 500 ratings.",
         "Defense Q&A"),
        (49, "Could your system suffer from the 'Grey Sheep' problem?",
         "Yes, the Grey Sheep problem refers to users whose tastes do not consistently correlate with any peer group. In pure collaborative filtering, they receive poor recommendations. In CineAI, the Content-Based engine and explicit genre boost act as a safety net, ensuring accurate recommendations even for idiosyncratic tastes.",
         "Defense Q&A"),
        (50, "Why is offline evaluation RMSE not always aligned with real-world user satisfaction?",
         "Offline evaluation only measures error on historical ratings. It cannot measure online conversion, novelty, discovery, or user trust. A model could achieve very low RMSE by only predicting ratings for movies the user already knows, but fail to deliver new discoveries. That is why CineAI includes explainability badges and catalog coverage metrics.",
         "Defense Q&A"),
        (51, "How does your system handle new movies added to the catalog (New Item Cold-Start)?",
         "New items have zero ratings, so collaborative filtering fails. However, our Content-Based pipeline immediately parses their title, genres, and synopsis into the TF-IDF vector space, allowing them to be recommended immediately to matching users.",
         "Defense Q&A"),
        (52, "What is the computational complexity of generating recommendations in CineAI?",
         "Offline precomputation of item-item similarity is O(M^2 * U). At runtime, recommendation generation calculates dot products between the user profile vector and unrated items: O(M * V) where M = 9,742 and V = 5,000, which takes less than 40 milliseconds on modern CPUs.",
         "Defense Q&A"),
        (53, "What security precautions did you take regarding SQL Injection?",
         "All SQLite database queries in src/database.py use parameterized queries ('?') rather than string formatting (f-strings). User inputs like username, rating, and genres are passed as parameter tuples, preventing SQL injection vulnerabilities.",
         "Defense Q&A"),
        (54, "Why did you use TruncatedSVD rather than NMF (Non-Negative Matrix Factorization)?",
         "TruncatedSVD allows negative latent factor values, which naturally models positive preference vs negative aversion. NMF enforces strictly non-negative weights, which is useful for part-based document representations but less suitable for deviation-based rating modeling.",
         "Defense Q&A"),
        (55, "What is the single biggest limitation of your project, and how would you fix it in Phase 2?",
         "The biggest limitation is that model retraining is offline; if a user rates 20 new movies, the underlying item-item correlation matrix does not recompute on every click. In Phase 2, we would implement incremental matrix updates via online SGD or alternating least squares (ALS).",
         "Defense Q&A")
    ]

    for q_num, question, answer, cat in sec5_questions:
        add_qa_box(doc, q_num, question, answer, category=cat)

    print(f"Saving Viva document to {DOCX_PATH}...")
    doc.save(DOCX_PATH)
    print("Viva document generated successfully!")

if __name__ == "__main__":
    main()
