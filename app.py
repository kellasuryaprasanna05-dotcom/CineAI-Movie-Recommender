"""
AI-POWERED MOVIE RECOMMENDATION SYSTEM (CineAI)
Production-Ready Full-Stack Web Application for College Project Demonstration.
Integrates Content-Based, Collaborative Filtering, Hybrid Engine, SQLite DB, and Interactive Playground.
"""
import os
import sys
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="CineAI | Intelligent Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.recommendation import MovieRecommendationSystem
from src.database import (
    init_db,
    get_or_create_user,
    list_users,
    get_user_preferences,
    save_user_preferences,
    save_user_rating,
    delete_user_rating,
    get_user_ratings
)

# Load custom CSS
css_path = os.path.join(BASE_DIR, "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Cache Recommender System instance
@st.cache_resource(show_spinner="🎬 Initializing CineAI Engine & Machine Learning Models...")
def get_engine():
    init_db()
    engine = MovieRecommendationSystem()
    engine.train_or_load_models()
    return engine

engine = get_engine()

# Load Offline Evaluation Metrics
eval_metrics = {}
eval_path = os.path.join(BASE_DIR, "docs", "evaluation_results.json")
if os.path.exists(eval_path):
    try:
        with open(eval_path, "r", encoding="utf-8") as f:
            eval_metrics = json.load(f)
    except Exception:
        pass

# -------------------------------------------------------------
# SIDEBAR: USER SELECTION & NAVIGATION
# -------------------------------------------------------------
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0 16px;">
    <h2 style="color: #e50914; margin-bottom: 2px; font-weight: 800; letter-spacing: -0.5px;">🎬 CineAI</h2>
    <p style="color: #a0aec0; font-size: 0.82rem; margin: 0;">AI Movie Recommendation Platform</p>
</div>
""", unsafe_allow_html=True)

# User Profile Switcher
st.sidebar.subheader("👤 User Profile")
all_users = list_users()
user_names = [u['username'] for u in all_users] if all_users else ["demo_cinephile"]

selected_username = st.sidebar.selectbox("Active Profile", user_names, index=0)
user_id = get_or_create_user(selected_username)

# Create New User Form
with st.sidebar.expander("➕ Create New Profile"):
    new_user_input = st.text_input("New Username", placeholder="e.g. maya_films")
    if st.button("Add User", key="btn_add_user"):
        if new_user_input.strip():
            new_uid = get_or_create_user(new_user_input.strip())
            st.success(f"Profile '{new_user_input.strip()}' created!")
            st.rerun()

# User Quick Stats in Sidebar
user_ratings = get_user_ratings(user_id)
user_prefs = get_user_preferences(user_id)
st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.03); border: 1px solid #2d3748; border-radius: 8px; padding: 12px; margin: 10px 0 18px;">
    <div style="font-size: 0.8rem; color: #a0aec0;">Profile: <strong style="color: #fff;">{selected_username}</strong></div>
    <div style="font-size: 0.8rem; color: #a0aec0; margin-top: 4px;">Rated Movies: <strong style="color: #ffb800;">{len(user_ratings)}</strong></div>
    <div style="font-size: 0.8rem; color: #a0aec0; margin-top: 4px;">Fav Genres: <strong style="color: #e50914;">{len(user_prefs.get('favorite_genres', []))}</strong></div>
</div>
""", unsafe_allow_html=True)

# Navigation
st.sidebar.subheader("🧭 Navigation")
nav_options = [
    "🏠 Home & Trending",
    "🔍 Search & Rate Movies",
    "🎯 AI Recommendations",
    "⚙️ My Preferences",
    "📊 User Dashboard",
    "🧪 AI Model Explanation & Architecture",
    "🔬 Interactive Model Playground"
]

# Query parameter integration for direct navigation and screenshot capture
query_nav = st.query_params.get("nav", "")
default_nav_idx = 0
if "search" in query_nav.lower() or "rate" in query_nav.lower():
    default_nav_idx = 1
elif "rec" in query_nav.lower():
    default_nav_idx = 2
elif "pref" in query_nav.lower():
    default_nav_idx = 3
elif "dash" in query_nav.lower():
    default_nav_idx = 4
elif "expl" in query_nav.lower() or "arch" in query_nav.lower():
    default_nav_idx = 5
elif "play" in query_nav.lower():
    default_nav_idx = 6

nav_choice = st.sidebar.radio(
    "Go to",
    nav_options,
    index=default_nav_idx
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-size: 0.72rem; color: #718096; line-height: 1.5;">
    <strong>CineAI Architecture:</strong><br/>
    • TF-IDF & Cosine Similarity<br/>
    • Item-Item Collaborative Filtering<br/>
    • TruncatedSVD Matrix Factorization<br/>
    • Dynamic Hybrid Cold-Start Blending<br/>
    • MovieLens (100k Ratings, 9.7k Movies)<br/>
    • SQLite3 Database
</div>
""", unsafe_allow_html=True)

# Helper function to render a movie card grid
def render_movie_card(movie: dict, col, key_prefix: str = "card"):
    mid = movie['movieId']
    title = movie.get('clean_title') or movie.get('title', 'Untitled')
    year = movie.get('year', '')
    genres = movie.get('genres', '')
    clean_genres = genres.replace('|', ' • ')
    if len(clean_genres) > 28:
        clean_genres = clean_genres[:25] + "..."
    rating = movie.get('avg_rating', 0.0)
    poster = movie.get('poster_url', '')
    reason = movie.get('recommendation_reason', '')

    reason_html = f"<div class='rec-reason-badge'>💡 {reason}</div>" if reason else ""

    with col:
        st.markdown(f"""
        <div class="movie-card">
            <div class="movie-poster-wrap">
                <img src="{poster}" alt="{title}" loading="lazy"/>
            </div>
            <div class="movie-info">
                <div>
                    <div class="movie-title" title="{title}">{title}</div>
                    <div class="movie-meta">
                        <span class="movie-rating">★ {rating:.1f}</span>
                        <span class="movie-year">{year if year else 'N/A'}</span>
                    </div>
                    <div class="movie-genre-tags" title="{genres}">{clean_genres}</div>
                    {reason_html}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            if st.button("Details", key=f"{key_prefix}_det_{mid}", use_container_width=True):
                st.session_state["selected_movie_id"] = mid
        with btn_col2:
            if st.button("Similar", key=f"{key_prefix}_sim_{mid}", use_container_width=True):
                st.session_state["similar_to_movie_id"] = mid
                st.session_state["nav_to_similar"] = True

# -------------------------------------------------------------
# TAB 1: HOME & TRENDING
# -------------------------------------------------------------
if nav_choice == "🏠 Home & Trending":
    # Hero Banner
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">AI Recommendation Engine</span>
        <h1 class="hero-title">Discover Movies Tailored to Your Taste</h1>
        <p class="hero-subtitle">
            Harnessing Content-Based TF-IDF vectorization and Item-Item Collaborative Filtering
            on the MovieLens dataset. Experience personalized recommendations, genre matching, and ratings.
        </p>
        <div class="hero-stats">
            <div class="hero-stat-item">🎬 <strong>9,742</strong> Movies</div>
            <div class="hero-stat-item">⭐ <strong>100,836</strong> Ratings</div>
            <div class="hero-stat-item">🧠 <strong>3</strong> Recommender Algorithms</div>
            <div class="hero-stat-item">⚡ <strong>Real-time</strong> SQLite Persistence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Genre quick filter
    st.subheader("🔥 Explore by Genre")
    genre_options = ["All"] + engine.all_genres
    selected_home_genre = st.selectbox("Filter Genre", genre_options, index=0, label_visibility="collapsed")

    # Trending & Popular Section
    st.markdown(f"### 🌟 Top Rated & Trending Movies ({selected_home_genre})")
    st.caption("Ranked using the IMDB Bayesian Weighted Rating formula: WR = (v / (v + m)) * R + (m / (v + m)) * C")

    trending_movies = engine.get_popular_and_trending(genre=selected_home_genre, limit=12)

    cols = st.columns(4)
    for idx, movie in enumerate(trending_movies):
        render_movie_card(movie, cols[idx % 4], key_prefix=f"trend_{idx}")

    # Modal / Expanded Movie Details if clicked
    if "selected_movie_id" in st.session_state and st.session_state["selected_movie_id"]:
        sel_mid = st.session_state["selected_movie_id"]
        m_details = engine.get_movie_details(sel_mid)
        if m_details:
            st.markdown("---")
            st.markdown("### 🎬 Movie Spotlight")
            dcol1, dcol2 = st.columns([1, 2])
            with dcol1:
                st.image(m_details['poster_url'], use_container_width=True)
            with dcol2:
                st.markdown(f"## {m_details['clean_title']} ({m_details['year']})")
                st.markdown(f"**Genres:** {m_details['genres'].replace('|', ', ')}")
                st.markdown(f"**Community Rating:** ★ **{m_details['avg_rating']:.2f}** / 5.0 ({m_details['rating_count']} ratings)")
                st.markdown(f"**Weighted Quality Score:** {m_details['weighted_rating']:.2f}")
                if m_details['tags']:
                    st.markdown(f"**Keywords / Tags:** `{m_details['tags']}`")

                # Interactive User Rating
                st.markdown("#### ⭐ Rate This Movie")
                curr_ratings = {r['movie_id']: r['rating'] for r in get_user_ratings(user_id)}
                existing_rating = curr_ratings.get(sel_mid, 3.5)

                new_r = st.slider(
                    "Your Rating (1.0 to 5.0 stars)", 
                    min_value=1.0, 
                    max_value=5.0, 
                    value=float(existing_rating), 
                    step=0.5,
                    key=f"slider_rate_{sel_mid}"
                )
                rcol1, rcol2 = st.columns(2)
                with rcol1:
                    if st.button("💾 Save Rating", key=f"btn_save_r_{sel_mid}", use_container_width=True):
                        save_user_rating(user_id, sel_mid, new_r)
                        st.success(f"Saved {new_r}★ rating for '{m_details['clean_title']}'!")
                        st.rerun()
                with rcol2:
                    if sel_mid in curr_ratings:
                        if st.button("🗑️ Remove Rating", key=f"btn_del_r_{sel_mid}", use_container_width=True):
                            delete_user_rating(user_id, sel_mid)
                            st.info("Rating deleted.")
                            st.rerun()

            # Find similar
            st.markdown(f"#### 🎭 Movies Similar to *{m_details['clean_title']}*")
            sim_movies = engine.get_similar_movies(sel_mid, top_n=4)
            sim_cols = st.columns(4)
            for sidx, sm in enumerate(sim_movies):
                render_movie_card(sm, sim_cols[sidx % 4], key_prefix=f"sim_spot_{sidx}")

# -------------------------------------------------------------
# TAB 2: SEARCH & RATE MOVIES
# -------------------------------------------------------------
elif nav_choice == "🔍 Search & Rate Movies":
    st.markdown("## 🔍 Search & Discover Movies")
    st.caption("Search across 9,700+ movies, filter by genre or rating, and rate titles to train your recommendation model.")

    scol1, scol2, scol3 = st.columns([2, 1, 1])
    with scol1:
        search_query = st.text_input("Search movie title", placeholder="e.g. Matrix, Inception, Toy Story, Batman...", value="")
    with scol2:
        search_genre = st.selectbox("Genre Filter", ["All"] + engine.all_genres, index=0)
    with scol3:
        min_star = st.slider("Minimum Rating", 0.0, 5.0, 0.0, step=0.5)

    search_results = engine.search_movies(query=search_query, genre=search_genre, min_rating=min_star, limit=16)

    st.markdown(f"**Found {len(search_results)} movies matching criteria**")

    if not search_results:
        st.warning("No movies matched your search query. Try broadening your keywords or resetting filters.")
    else:
        cols = st.columns(4)
        for idx, movie in enumerate(search_results):
            render_movie_card(movie, cols[idx % 4], key_prefix=f"search_{idx}")

    # Display Movie Details / Rating Modal
    if "selected_movie_id" in st.session_state and st.session_state["selected_movie_id"]:
        sel_mid = st.session_state["selected_movie_id"]
        m_details = engine.get_movie_details(sel_mid)
        if m_details:
            st.markdown("---")
            st.markdown("### 🎬 Movie Details & Interactive Rating")
            dcol1, dcol2 = st.columns([1, 2])
            with dcol1:
                st.image(m_details['poster_url'], use_container_width=True)
            with dcol2:
                st.markdown(f"## {m_details['clean_title']} ({m_details['year']})")
                st.markdown(f"**Genres:** {m_details['genres'].replace('|', ', ')}")
                st.markdown(f"**Community Rating:** ★ **{m_details['avg_rating']:.2f}** / 5.0 ({m_details['rating_count']} ratings)")
                if m_details['tags']:
                    st.markdown(f"**Keywords / Tags:** `{m_details['tags']}`")

                # User rating widget
                curr_ratings = {r['movie_id']: r['rating'] for r in get_user_ratings(user_id)}
                user_curr = curr_ratings.get(sel_mid, 3.5)

                new_r = st.slider("Your Rating (1.0 to 5.0 stars)", 1.0, 5.0, float(user_curr), step=0.5, key=f"search_rate_sl_{sel_mid}")
                rcol1, rcol2 = st.columns(2)
                with rcol1:
                    if st.button("💾 Save Rating", key=f"search_save_{sel_mid}", use_container_width=True):
                        save_user_rating(user_id, sel_mid, new_r)
                        st.success(f"Rated '{m_details['clean_title']}' with {new_r}★!")
                        st.rerun()
                with rcol2:
                    if sel_mid in curr_ratings:
                        if st.button("🗑️ Remove Rating", key=f"search_del_{sel_mid}", use_container_width=True):
                            delete_user_rating(user_id, sel_mid)
                            st.info("Rating cleared.")
                            st.rerun()

            st.markdown(f"#### 🎭 More Like *{m_details['clean_title']}*")
            sim_movies = engine.get_similar_movies(sel_mid, top_n=4)
            sim_cols = st.columns(4)
            for sidx, sm in enumerate(sim_movies):
                render_movie_card(sm, sim_cols[sidx % 4], key_prefix=f"sim_search_{sidx}")

# -------------------------------------------------------------
# TAB 3: AI RECOMMENDATIONS
# -------------------------------------------------------------
elif nav_choice == "🎯 AI Recommendations":
    st.markdown("## 🎯 Personalized AI Recommendations")
    st.caption("Explore recommendations tailored to your profile using state-of-the-art machine learning algorithms.")

    # Algorithm selector
    acol1, acol2, acol3 = st.columns([1.5, 1.5, 1])
    with acol1:
        selected_algo = st.selectbox(
            "Recommendation Algorithm",
            [
                "Hybrid (Recommended - Content + Collaborative)",
                "Content-Based (TF-IDF & Metadata Cosine Similarity)",
                "Collaborative Filtering (Item-Item Cosine Similarity)"
            ],
            index=0
        )
    with acol2:
        algo_code = "hybrid"
        if "Content-Based" in selected_algo:
            algo_code = "content"
        elif "Collaborative" in selected_algo:
            algo_code = "collaborative"

        top_n = st.slider("Number of Recommendations", 8, 20, 12, step=2)

    # Hybrid blending weight slider if Hybrid selected
    cf_weight = None
    if algo_code == "hybrid":
        with acol3:
            cf_weight = st.slider(
                "Collaborative vs Content Weight (α)",
                min_value=0.0,
                max_value=1.0,
                value=0.60,
                step=0.05,
                help="0.0 = Pure Content-Based; 1.0 = Pure Collaborative Filtering"
            )

    # Status of user ratings
    user_ratings = get_user_ratings(user_id)
    user_prefs = get_user_preferences(user_id)
    n_ratings = len(user_ratings)

    if n_ratings == 0:
        st.info("ℹ️ **Cold-Start Mode Active:** You haven't rated any movies yet. Showing intelligent recommendations based on your **Favorite Genres & Keywords** in User Preferences.")
    else:
        st.success(f"✨ Generating personalized recommendations using **{n_ratings} movies** you've rated! (Rated movies are strictly excluded from results).")

    # Fetch recommendations
    recommendations = engine.get_personalized_recommendations(
        user_id=user_id,
        algorithm=algo_code,
        top_n=top_n,
        cf_weight=cf_weight
    )

    if not recommendations:
        st.warning("No recommendations could be generated. Please select some favorite genres in 'My Preferences' or rate a few movies.")
    else:
        cols = st.columns(4)
        for idx, movie in enumerate(recommendations):
            render_movie_card(movie, cols[idx % 4], key_prefix=f"rec_{idx}")

    # Inspecting Similar Movie Triggered from Button
    if "similar_to_movie_id" in st.session_state and st.session_state.get("nav_to_similar"):
        target_mid = st.session_state["similar_to_movie_id"]
        target_info = engine.get_movie_details(target_mid)
        if target_info:
            st.markdown("---")
            st.markdown(f"### 🔗 Deep Dive: Similar to *{target_info['clean_title']}*")
            method = st.radio("Similarity Algorithm", ["Content-Based (TF-IDF Genres & Tags)", "Collaborative (User Co-ratings)"], horizontal=True)
            m_code = "collaborative" if "Collaborative" in method else "content"
            sim_list = engine.get_similar_movies(target_mid, top_n=4, method=m_code)
            sim_cols = st.columns(4)
            for sidx, sm in enumerate(sim_list):
                render_movie_card(sm, sim_cols[sidx % 4], key_prefix=f"sim_deep_{sidx}")

# -------------------------------------------------------------
# TAB 4: USER PREFERENCES
# -------------------------------------------------------------
elif nav_choice == "⚙️ My Preferences":
    st.markdown("## ⚙️ Customize Your Movie Preferences")
    st.caption("Tell CineAI what you love so cold-start and hybrid recommenders can personalize your suggestions.")

    current_prefs = get_user_preferences(user_id)
    curr_genres = current_prefs.get('favorite_genres', [])
    curr_actors = current_prefs.get('favorite_actors', [])
    curr_langs = current_prefs.get('favorite_languages', [])
    curr_cats = current_prefs.get('preferred_categories', [])

    with st.form("preferences_form"):
        st.subheader("1. Favorite Movie Genres")
        selected_genres = st.multiselect(
            "Select your favorite genres (multiple choices allowed)",
            options=engine.all_genres,
            default=[g for g in curr_genres if g in engine.all_genres]
        )

        st.subheader("2. Favorite Actors & Directors")
        popular_actors = [
            "Tom Hanks", "Leonardo DiCaprio", "Keanu Reeves", "Morgan Freeman",
            "Robert De Niro", "Al Pacino", "Christian Bale", "Brad Pitt",
            "Scarlett Johansson", "Christopher Nolan", "Quentin Tarantino", "Steven Spielberg"
        ]
        selected_actors = st.multiselect(
            "Select or type favorite actors / directors",
            options=popular_actors,
            default=[a for a in curr_actors if a in popular_actors]
        )

        st.subheader("3. Preferred Languages")
        language_options = ["English", "French", "Japanese", "Spanish", "German", "Hindi", "Korean", "Italian"]
        selected_langs = st.multiselect(
            "Select preferred movie languages",
            options=language_options,
            default=[l for l in curr_langs if l in language_options]
        )

        st.subheader("4. Preferred Movie Categories")
        category_options = ["Blockbuster", "Critically Acclaimed", "Indie Cult", "Classic Cinema", "Award Winners", "Hidden Gems"]
        selected_cats = st.multiselect(
            "Select categories",
            options=category_options,
            default=[c for c in curr_cats if c in category_options]
        )

        submitted = st.form_submit_button("💾 Save Preferences")
        if submitted:
            save_user_preferences(
                user_id=user_id,
                favorite_genres=selected_genres,
                favorite_actors=selected_actors,
                favorite_languages=selected_langs,
                preferred_categories=selected_cats
            )
            st.success("Preferences saved successfully to SQLite database!")
            st.rerun()

    st.markdown("### 📋 Active Preference Summary")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown("**Genres:** " + (" ".join([f"<span class='genre-pill'>{g}</span>" for g in selected_genres]) if selected_genres else "*None selected*"), unsafe_allow_html=True)
        st.markdown("**Actors/Directors:** " + (", ".join(selected_actors) if selected_actors else "*None selected*"))
    with p2:
        st.markdown("**Languages:** " + (", ".join(selected_langs) if selected_langs else "*None selected*"))
        st.markdown("**Categories:** " + (", ".join(selected_cats) if selected_cats else "*None selected*"))

# -------------------------------------------------------------
# TAB 5: USER DASHBOARD
# -------------------------------------------------------------
elif nav_choice == "📊 User Dashboard":
    st.markdown(f"## 📊 Cinephile Dashboard: {selected_username}")
    st.caption("Overview of your viewing history, rating metrics, genre distribution, and algorithm activity.")

    summary = engine.get_user_summary(user_id)

    # Top KPI metrics
    kcol1, kcol2, kcol3, kcol4 = st.columns(4)
    with kcol1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{summary['total_ratings']}</div>
            <div class="stat-label">Movies Rated</div>
        </div>
        """, unsafe_allow_html=True)
    with kcol2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">★ {summary['avg_user_rating']}</div>
            <div class="stat-label">Average Rating Given</div>
        </div>
        """, unsafe_allow_html=True)
    with kcol3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(summary['preferences'].get('favorite_genres', []))}</div>
            <div class="stat-label">Favorite Genres</div>
        </div>
        """, unsafe_allow_html=True)
    with kcol4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(summary['history'])}</div>
            <div class="stat-label">Recommendation Sessions</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Genre Distribution Chart
    g_dist = summary['genre_distribution']
    chart_col1, chart_col2 = st.columns([1.2, 1])

    with chart_col1:
        st.subheader("📈 Your Genre Preferences (From Ratings)")
        if g_dist:
            chart_df = pd.DataFrame(list(g_dist.items()), columns=['Genre', 'Count']).sort_values(by='Count', ascending=True)
            fig = px.bar(
                chart_df, 
                x='Count', 
                y='Genre', 
                orientation='h', 
                color='Count',
                color_continuous_scale=['#4a5568', '#e50914'],
                labels={'Count': 'Rated Movies'}
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f7fafc'),
                margin=dict(l=20, r=20, t=20, b=20),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No genre chart available yet. Rate a few movies to see your personalized taste graph!")

    with chart_col2:
        st.subheader("⭐ Rating Distribution")
        rated_list = summary['rated_movies']
        if rated_list:
            r_vals = [r['user_rating'] for r in rated_list]
            r_df = pd.DataFrame(r_vals, columns=['Rating']).value_counts().reset_index()
            r_df.columns = ['Rating', 'Count']
            r_df = r_df.sort_values(by='Rating')
            fig_pie = px.pie(
                r_df, 
                values='Count', 
                names='Rating', 
                color_discrete_sequence=['#ffb800', '#f6ad55', '#e50914', '#ed8936', '#cbd5e0']
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f7fafc'),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Rate movies to view your score breakdown.")

    # Rated Movies Table with Delete / Edit Option
    st.markdown("### 📝 Movies You Have Rated")
    if rated_list:
        rated_table_data = []
        for r in rated_list:
            rated_table_data.append({
                "Movie ID": r['movie_id'],
                "Title": r['title'],
                "Genres": r['genres'],
                "Your Rating": f"★ {r['user_rating']}",
                "Rated On": r['rated_at']
            })
        st.dataframe(pd.DataFrame(rated_table_data), use_container_width=True)

        del_mid = st.selectbox("Select movie to remove from ratings:", [r['movie_id'] for r in rated_list], format_func=lambda mid: next((r['title'] for r in rated_list if r['movie_id'] == mid), mid))
        if st.button("🗑️ Delete Selected Rating", key="dash_del_btn"):
            delete_user_rating(user_id, del_mid)
            st.success("Rating removed.")
            st.rerun()
    else:
        st.write("You haven't rated any movies yet. Explore the **Search & Rate** tab to begin building your profile!")

# -------------------------------------------------------------
# TAB 6: AI MODEL EXPLANATION & ARCHITECTURE (DEMO SHOWCASE)
# -------------------------------------------------------------
elif nav_choice == "🧪 AI Model Explanation & Architecture":
    st.markdown("## 🧪 AI Model Explanation & System Architecture")
    st.caption("A comprehensive technical guide prepared for college evaluations, Viva examinations, and project reviews.")

    # Top KPI Metrics from real MovieLens evaluation
    mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    with mcol1:
        st.metric("RMSE (Test Error)", f"{eval_metrics.get('RMSE', 0.9094):.4f}", help="Root Mean Squared Error on 20% test ratings split")
    with mcol2:
        st.metric("MAE (Mean Error)", f"{eval_metrics.get('MAE', 0.7015):.4f}", help="Mean Absolute Error on test split")
    with mcol3:
        st.metric("Precision@10", f"{eval_metrics.get('Precision@10', 0.0072):.4f}", help="Fraction of top-10 recommendations rated >= 4.0")
    with mcol4:
        st.metric("Recall@10", f"{eval_metrics.get('Recall@10', 0.0056):.4f}", help="Fraction of user relevant movies retrieved in top-10")
    with mcol5:
        st.metric("Catalog Coverage", f"{eval_metrics.get('Catalog_Coverage', 0.0157):.4f}", help="Proportion of total catalog recommended")

    st.markdown("---")

    # Explanation Sections
    t1, t2, t3, t4, t5 = st.tabs([
        "1. Core Concepts", 
        "2. Content-Based & TF-IDF", 
        "3. Collaborative Filtering & SVD", 
        "4. Hybrid Recommender",
        "5. System Architecture"
    ])

    with t1:
        st.markdown("""
        ### 📖 What is a Recommendation System?
        A **Recommendation System** is an artificial intelligence algorithm that predicts the preference, rating, or affinity a user would assign to an item (e.g., movies, songs, products).
        
        #### Why do modern platforms need them?
        1. **Choice Overload**: Modern streaming platforms catalog tens of thousands of media assets.
        2. **Serendipity & Discovery**: Surfaces niche films ("hidden gems") users would not have searched for manually.
        3. **Engagement & Retention**: Higher recommendation relevance directly correlates with user session time.
        
        #### The Three Fundamental Paradigms:
        - **Content-Based Filtering**: Suggests items similar to what the user liked in the past based on descriptive metadata (genres, actors, plots).
        - **Collaborative Filtering**: Suggests items by identifying patterns among groups of users who share similar rating histories ("wisdom of the crowd").
        - **Hybrid Systems**: Strategically blends both techniques to combine their strengths and compensate for their weaknesses.
        """)

    with t2:
        st.markdown("""
        ### 🎯 Content-Based Filtering & TF-IDF
        
        #### What is Content-Based Filtering?
        Content-Based Filtering models recommend items based on the **intrinsic features** of the items themselves. In CineAI, each movie is represented by its **Metadata Soup**:
        $$\\text{Soup}_i = \\text{CleanTitle}_i \\parallel \\text{Genres}_i \\parallel \\text{Tags}_i$$

        #### What is TF-IDF (Term Frequency - Inverse Document Frequency)?
        TF-IDF transforms variable-length text into fixed-length numerical feature vectors, discounting commonly repeated stop words while highlighting descriptive keywords:
        $$\\text{TF}(t, d) = \\frac{\\text{Frequency of term } t \\text{ in document } d}{\\text{Total words in document } d}$$
        $$\\text{IDF}(t, D) = \\log \\left( \\frac{1 + |D|}{1 + |\\{d \\in D : t \\in d\\}|} \\right) + 1$$
        $$\\text{TF-IDF}(t, d, D) = \\text{TF}(t, d) \\times \\text{IDF}(t, D)$$

        #### What is Cosine Similarity?
        Cosine Similarity calculates the cosine of the angle between two high-dimensional vectors in $n$-dimensional space, measuring orientation rather than magnitude:
        $$\\text{Sim}_{\\text{cosine}}(\\mathbf{u}, \\mathbf{v}) = \\frac{\\mathbf{u} \\cdot \\mathbf{v}}{\\|\\mathbf{u}\\| \\|\\mathbf{v}\\|} = \\frac{\\sum_{i=1}^n u_i v_i}{\\sqrt{\\sum_{i=1}^n u_i^2} \\sqrt{\\sum_{i=1}^n v_i^2}}$$
        A score of $1.0$ indicates identical thematic alignment, while $0.0$ indicates orthogonality (no common terms).

        #### Strengths & Limitations:
        - ✅ **Cold-Start for New Movies**: Can recommend brand-new movies immediately upon release without waiting for user reviews.
        - ✅ **Transparent & Explainable**: High visibility into why a recommendation was made (matching genres/keywords).
        - ⚠️ **Overspecialization**: Struggles to recommend outside the user's established genre comfort zone.
        """)

    with t3:
        st.markdown("""
        ### 👥 Collaborative Filtering & Latent Matrix Factorization
        
        #### What is Collaborative Filtering?
        Collaborative Filtering assumes that if User $A$ and User $B$ have agreed on movie ratings in the past, they will likely agree in the future.
        
        #### Item-Item Collaborative Filtering
        In CineAI, we adopt an **Item-Based approach** because items (movies) are more static and stable than dynamic users:
        1. Form the interaction matrix $\\mathbf{R} \\in \\mathbb{R}^{610 \\times 3650}$ (610 MovieLens users by 3,650 popular movies).
        2. Compute cosine similarity between movie rating column vectors $\\mathbf{r}_{*i}$ and $\\mathbf{r}_{*j}$.
        3. Predict rating $\\hat{r}_{u, i}$ for unrated movie $i$ using neighbor similarities:
        $$\\hat{r}_{u, i} = \\frac{\\sum_{j \\in \\text{Rated}_u, s_{i, j} > 0.05} s_{i, j} \\cdot r_{u, j}}{\\sum_{j \\in \\text{Rated}_u, s_{i, j} > 0.05} |s_{i, j}|}$$

        #### Matrix Factorization via TruncatedSVD
        Decomposes the sparse interaction matrix into rank-$k$ low-dimensional latent spaces:
        $$\\mathbf{R} \\approx \\mathbf{U}_k \\mathbf{\\Sigma}_k \\mathbf{V}_k^T$$
        Where $k=20$ represents latent thematic factors (e.g. moody noir tones, fast pacing, comedic timing) automatically learned from rating correlations.

        #### Strengths & Limitations:
        - ✅ **Domain Independent**: No metadata or manual tagging required.
        - ✅ **Serendipitous**: Recommends unexpected titles that share subtle user interest clusters.
        - ⚠️ **The Cold-Start Dilemma**: Cannot provide recommendations for brand-new users with zero ratings.
        """)

    with t4:
        st.markdown("""
        ### ⚡ The CineAI Hybrid Engine & Cold-Start Strategy
        
        #### Why a Hybrid Engine?
        Content-Based and Collaborative Filtering have complementary strengths. CineAI strategically combines them through dynamic linear score blending:
        $$\\text{Score}_{\\text{hybrid}} = \\alpha \\cdot \\text{Norm}(\\text{Score}_{\\text{CF}}) + (1 - \\alpha) \\cdot \\text{Norm}(\\text{Score}_{\\text{Content}}) + \\text{Boost}_{\\text{genre}}$$

        #### Dynamic Cold-Start Mitigation Table:
        | User Rating Count | Recommender Mode | Weight $\\alpha$ | Recommendation Rationale |
        | :--- | :--- | :--- | :--- |
        | **0 Ratings (Cold)** | Pure Content + Preferences | $\\alpha = 0.00$ | Matches explicit genres & actors selected in user preferences. |
        | **1 - 3 Ratings (Warm)** | Content-Leaning Hybrid | $\\alpha = 0.35$ | Explores similar content while gingerly introducing collaborative co-ratings. |
        | **> 3 Ratings (Established)** | Collaborative-Leaning Hybrid | $\\alpha = 0.60$ | Strong collaborative crowd-signals with content thematic grounding. |
        """)

    with t5:
        st.markdown("""
        ### 🏗️ CineAI End-to-End System Architecture
        """)
        st.markdown("""
```
 +------------------------------------------------------------------------+
 |                      Streamlit Presentation Layer                     |
 |  - Hero Banner        - Search & Filters      - Star Rating Widget    |
 |  - Preference Form    - Analytics Dashboard   - Educational Sandbox   |
 +-----------------------------------+------------------------------------+
                                     |
                                     v
 +------------------------------------------------------------------------+
 |                  Recommendation Engine Facade Layer                    |
 |                       (src/recommendation.py)                          |
 +---------+-------------------------+--------------------------+---------+
           |                         |                          |
           v                         v                          v
 +-------------------+     +--------------------+     +-------------------+
 |   Content-Based   |     |   Collaborative    |     |      Hybrid       |
 |    Recommender    |     |     Filtering      |     |    Recommender    |
 | - TF-IDF Vectors  |     | - Item-Item Cosine |     | - Linear Blending |
 | - Cosine Sim      |     | - TruncatedSVD     |     | - Cold-Start Mode |
 | - User Profiling  |     | - Rating Prediction|     | - Genre Boosting  |
 +---------+---------+     +---------+----------+     +---------+---------+
           |                         |                          |
           +-------------------------+--------------------------+
                                     |
                                     v
 +------------------------------------------------------------------------+
 |                        Data & Persistence Layer                        |
 |  - GroupLens MovieLens Dataset (movies.csv, ratings.csv, tags.csv)     |
 |  - Serialized Artifacts (models/tfidf_model.pkl, models/cf_model.pkl) |
 |  - Transactional SQLite Store (database/users.db: profiles, ratings)   |
 +------------------------------------------------------------------------+
```
        """)

# -------------------------------------------------------------
# TAB 7: INTERACTIVE MODEL PLAYGROUND (VIVA DEMO FEATURE)
# -------------------------------------------------------------
elif nav_choice == "🔬 Interactive Model Playground":
    st.markdown("## 🔬 Interactive Machine Learning Playground")
    st.caption("Live mathematical demonstration environment designed for college project presentations and examiners.")

    p_mode = st.radio(
        "Select Experiment Mode",
        [
            "1. Movie-to-Movie Cosine Similarity Comparison (Content vs. Collaborative)",
            "2. Live TF-IDF Metadata Vector Inspection",
            "3. Cold-Start Preference Simulation"
        ],
        horizontal=True
    )

    if "1. Movie-to-Movie" in p_mode:
        st.subheader("1. Item-to-Item Similarity Face-Off")
        st.caption("Compare how Content-Based Filtering (text metadata) vs Collaborative Filtering (rating patterns) view similarity for any movie.")

        # Movie selector
        demo_mid = st.selectbox(
            "Select Seed Movie to Analyze",
            list(engine.movie_map.keys()),
            format_func=lambda m: f"{engine.movie_map[m]['clean_title']} ({engine.movie_map[m].get('year', '')}) — {engine.movie_map[m]['genres']}",
            index=0
        )
        seed_movie = engine.get_movie_details(demo_mid)

        st.markdown(f"**Target Movie:** *{seed_movie['clean_title']}* ({seed_movie['genres']})")

        pcol1, pcol2 = st.columns(2)
        with pcol1:
            st.markdown("#### 📄 Content-Based Similarity (TF-IDF)")
            cb_sims = engine.get_similar_movies(demo_mid, top_n=5, method="content")
            for item in cb_sims:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); border: 1px solid #2d3748; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
                    <strong>{item['clean_title']}</strong> ({item.get('year','')})<br/>
                    <small style="color: #90cdf4;">{item['genres'].replace('|', ' • ')}</small><br/>
                    <span style="color: #ffb800; font-size: 0.8rem;">★ {item.get('avg_rating', 0.0)}</span> | 
                    <span style="color: #48bb78; font-size: 0.8rem;">Cosine Sim: <strong>{item.get('similarity_score', 0.0):.4f}</strong></span>
                </div>
                """, unsafe_allow_html=True)

        with pcol2:
            st.markdown("#### 👥 Collaborative Filtering Similarity (Co-Ratings)")
            cf_sims = engine.get_similar_movies(demo_mid, top_n=5, method="collaborative")
            for item in cf_sims:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); border: 1px solid #2d3748; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
                    <strong>{item['clean_title']}</strong> ({item.get('year','')})<br/>
                    <small style="color: #90cdf4;">{item['genres'].replace('|', ' • ')}</small><br/>
                    <span style="color: #ffb800; font-size: 0.8rem;">★ {item.get('avg_rating', 0.0)}</span> | 
                    <span style="color: #e50914; font-size: 0.8rem;">Co-Rating Sim: <strong>{item.get('similarity_score', 0.0):.4f}</strong></span>
                </div>
                """, unsafe_allow_html=True)

    elif "2. Live TF-IDF" in p_mode:
        st.subheader("2. TF-IDF Metadata Vector Inspection")
        st.caption("Inspect the processed metadata soup and highest weighted tokens extracted for any film.")

        inspect_mid = st.selectbox(
            "Choose a movie to inspect:",
            list(engine.movie_map.keys()),
            format_func=lambda m: f"{engine.movie_map[m]['clean_title']} ({engine.movie_map[m].get('year', '')})",
            index=10
        )
        selected_info = engine.movie_map[inspect_mid]

        st.markdown(f"**Clean Title:** `{selected_info['clean_title']}`")
        st.markdown(f"**Genres:** `{selected_info['genres']}`")
        st.markdown(f"**Aggregated Tags:** `{selected_info.get('tag', '(none)')}`")
        st.markdown(f"**Raw Metadata Soup for TF-IDF:**")
        st.code(selected_info.get('soup', ''), language="text")

    elif "3. Cold-Start" in p_mode:
        st.subheader("3. Cold-Start Preference Simulation")
        st.caption("Test how the AI recommender behaves for a hypothetical brand new user with 0 ratings.")

        sim_genres = st.multiselect("Select Hypothetical Favorite Genres:", engine.all_genres, default=["Action", "Sci-Fi"])
        sim_keywords = st.text_input("Simulated Favorite Actors/Keywords:", "matrix space future hero")

        if st.button("Generate Cold-Start Simulation"):
            kw_list = [w.strip() for w in sim_keywords.split() if w.strip()]
            sim_recs = engine.content_recommender.recommend_by_preferences(
                favorite_genres=sim_genres,
                keywords=kw_list,
                top_n=6
            )
            st.markdown(f"**Top Simulated Cold-Start Recommendations:**")
            cols = st.columns(3)
            for idx, r in enumerate(sim_recs):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div style="background: #171923; border: 1px solid #2d3748; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                        <h4 style="margin: 0 0 6px 0; color: #fff;">{r['clean_title']} ({r.get('year','')})</h4>
                        <div style="color: #90cdf4; font-size: 0.8rem; margin-bottom: 6px;">{r['genres'].replace('|', ' • ')}</div>
                        <div style="color: #48bb78; font-weight: bold; font-size: 0.85rem;">Match Score: {r['similarity_score']:.4f}</div>
                    </div>
                    """, unsafe_allow_html=True)
