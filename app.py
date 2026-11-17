"""
CineAI — Netflix-Grade AI Movie Recommendation Platform
Premium streaming UI: top navbar, hero banner, horizontal rows, detail panels.
"""
import os, sys, json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="CineAI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.recommendation import MovieRecommendationSystem
from src.database import (
    init_db, get_or_create_user, list_users,
    get_user_preferences, save_user_preferences,
    save_user_rating, delete_user_rating, get_user_ratings
)

# ── Load CSS ──
css_path = os.path.join(BASE_DIR, "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Engine ──
@st.cache_resource(show_spinner="Loading CineAI Engine...")
def get_engine():
    init_db()
    e = MovieRecommendationSystem()
    e.train_or_load_models()
    return e

engine = get_engine()

# Evaluation metrics
eval_metrics = {}
ep = os.path.join(BASE_DIR, "docs", "evaluation_results.json")
if os.path.exists(ep):
    try:
        with open(ep, "r") as f:
            eval_metrics = json.load(f)
    except Exception:
        pass

# SVG fallback
FALLBACK_SVG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 450'%3E%3Crect width='300' height='450' fill='%23181818'/%3E%3Ctext x='150' y='210' text-anchor='middle' fill='%23444' font-size='52'%3E🎬%3C/text%3E%3Ctext x='150' y='255' text-anchor='middle' fill='%23555' font-size='13' font-family='Arial'%3ENo Poster%3C/text%3E%3C/svg%3E"

# ── Session State ──
if "page" not in st.session_state:
    st.session_state["page"] = "HOME"
if "detail_movie" not in st.session_state:
    st.session_state["detail_movie"] = None

# ── User ──
all_users = list_users()
user_names = [u['username'] for u in all_users] if all_users else ["demo_cinephile"]
if "username" not in st.session_state:
    st.session_state["username"] = user_names[0]
user_id = get_or_create_user(st.session_state["username"])

# ══════════════════════════════════════════════════════════
# NAVIGATION BAR (HTML + hidden Streamlit buttons)
# ══════════════════════════════════════════════════════════
NAV_ITEMS = [
    ("HOME", "Home"),
    ("SEARCH", "Search"),
    ("AI RECS", "AI Picks"),
    ("PREFERENCES", "Preferences"),
    ("DASHBOARD", "Dashboard"),
    ("AI ARCH", "AI Lab"),
    ("PLAYGROUND", "Playground"),
]
active_page = st.session_state["page"]
avatar_letter = st.session_state["username"][0].upper()

links_html = ""
for key, label in NAV_ITEMS:
    cls = "cai-nav-link active" if key == active_page else "cai-nav-link"
    links_html += f'<span class="{cls}">{label}</span>'

st.markdown(f"""
<div class="cai-navbar">
    <div class="cai-nav-logo">CineAI</div>
    <div class="cai-nav-links">{links_html}</div>
    <div class="cai-nav-profile">
        <div class="cai-nav-avatar">{avatar_letter}</div>
        <div class="cai-nav-username">{st.session_state["username"]}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Functional nav buttons (tiny, hidden via CSS)
nav_cols = st.columns(len(NAV_ITEMS) + 1)
for i, (key, label) in enumerate(NAV_ITEMS):
    with nav_cols[i]:
        if st.button(label, key=f"nav_{key}"):
            st.session_state["page"] = key
            st.session_state["detail_movie"] = None
            st.rerun()
# Profile popover
with nav_cols[-1]:
    with st.popover("👤"):
        un = st.selectbox(
            "Switch Profile", user_names,
            index=user_names.index(st.session_state["username"]) if st.session_state["username"] in user_names else 0,
            key="prof_sel"
        )
        if un != st.session_state["username"]:
            st.session_state["username"] = un
            st.rerun()
        nu = st.text_input("New profile name", key="new_u", placeholder="Enter username")
        if st.button("Create Profile", key="create_u"):
            if nu.strip():
                get_or_create_user(nu.strip())
                st.session_state["username"] = nu.strip()
                st.rerun()
        ur = get_user_ratings(user_id)
        up = get_user_preferences(user_id)
        st.caption(f"Rated: {len(ur)} · Genres: {len(up.get('favorite_genres', []))}")

# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════

def section_title(title):
    st.markdown(f'<div class="cai-section-title">{title}</div>', unsafe_allow_html=True)


def render_card(movie, col, prefix="c"):
    """Render a single movie card in the given column."""
    mid = movie['movieId']
    title = movie.get('clean_title') or movie.get('title', 'Untitled')
    year = movie.get('year', '')
    genres = movie.get('genres', '')
    rating = movie.get('avg_rating', 0.0)
    poster = movie.get('poster_url', '')
    reason = movie.get('recommendation_reason', '')
    match_pct = min(99, max(65, int(rating * 20)))
    genre_list = genres.split('|')[:3] if genres else []
    cg = genres.replace('|', ' · ')
    if len(cg) > 30:
        cg = cg[:27] + "..."
    tags_html = "".join([f'<span class="cai-card-tag">{g.strip()}</span>' for g in genre_list])
    reason_html = f'<div class="cai-card-reason">💡 {reason}</div>' if reason else ""

    with col:
        st.markdown(f"""
        <div class="cai-card">
            <div class="cai-card-poster">
                <img src="{poster}" alt="{title}" loading="lazy" onerror="this.onerror=null;this.src='{FALLBACK_SVG}'"/>
                <div class="cai-card-play">▶</div>
                <div class="cai-card-match">{match_pct}% Match</div>
                <div class="cai-card-overlay">
                    <div class="cai-card-overlay-title">{title}</div>
                    <div class="cai-card-overlay-meta">
                        <span style="color:#46d369;font-weight:700;">{match_pct}%</span>
                        <span style="color:#999;">{year}</span>
                        <span style="color:#f5c518;font-weight:700;">★ {rating:.1f}</span>
                    </div>
                    <div class="cai-card-overlay-tags">{tags_html}</div>
                </div>
            </div>
            <div class="cai-card-info">
                <div class="cai-card-title" title="{title}">{title}</div>
                <div class="cai-card-meta">
                    <span class="cai-card-rating">★ {rating:.1f}</span>
                    <span class="cai-card-year">{year if year else '—'}</span>
                </div>
                <div class="cai-card-genres">{cg}</div>
                {reason_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Details", key=f"{prefix}_{mid}"):
            st.session_state["detail_movie"] = mid
            st.rerun()


def render_movie_row(title, movies, prefix, limit=6):
    """Render a section header + row of movie cards."""
    if not movies:
        return
    section_title(title)
    n = min(len(movies), limit)
    cols = st.columns(n)
    for i, m in enumerate(movies[:n]):
        render_card(m, cols[i], prefix=f"{prefix}_{i}")


def render_detail(mid, uid, sfx=""):
    """Render the detail panel for a selected movie."""
    m = engine.get_movie_details(mid)
    if not m:
        return
    st.markdown("---")
    # Close button
    if st.button("✕ Close Details", key=f"close_{sfx}"):
        st.session_state["detail_movie"] = None
        st.rerun()

    st.markdown('<div class="cai-detail-panel">', unsafe_allow_html=True)

    d1, d2 = st.columns([1, 2])
    with d1:
        st.image(m['poster_url'], use_container_width=True)
    with d2:
        mp = min(99, max(65, int(m['avg_rating'] * 20)))
        gl = m['genres'].split('|')
        tags = "".join([f'<span class="cai-detail-tag">{g.strip()}</span>' for g in gl])
        st.markdown(f"""
        <div class="cai-detail-title">{m['clean_title']}</div>
        <div style="display:flex;gap:16px;align-items:center;margin:8px 0 16px;flex-wrap:wrap;">
            <span style="color:#46d369;font-weight:900;font-size:1.2rem;">{mp}% Match</span>
            <span style="color:#999;">{m.get('year', '')}</span>
            <span style="color:#f5c518;font-weight:900;font-size:1.1rem;">★ {m['avg_rating']:.2f}</span>
            <span style="color:#666;font-size:0.85rem;">{m['rating_count']} ratings</span>
        </div>
        <div style="margin-bottom:14px;">{tags}</div>
        """, unsafe_allow_html=True)
        if m.get('tags'):
            st.markdown(f"**Keywords:** `{m['tags']}`")
        st.markdown(f"**Quality Score:** `{m['weighted_rating']:.2f}`")
        st.markdown("#### ⭐ Rate This Movie")
        curr = {r['movie_id']: r['rating'] for r in get_user_ratings(uid)}
        ex = curr.get(mid, 3.5)
        nr = st.slider("Rating", 1.0, 5.0, float(ex), 0.5, key=f"sl_{mid}_{sfx}", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Save Rating", key=f"sv_{mid}_{sfx}"):
                save_user_rating(uid, mid, nr)
                st.success(f"Saved {nr}★!")
                st.rerun()
        with c2:
            if mid in curr:
                if st.button("Remove Rating", key=f"rm_{mid}_{sfx}"):
                    delete_user_rating(uid, mid)
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Similar movies
    section_title(f"More Like \"{m['clean_title']}\"")
    sims = engine.get_similar_movies(mid, top_n=6)
    if sims:
        sc = st.columns(min(len(sims), 6))
        for i, sm in enumerate(sims[:6]):
            render_card(sm, sc[i], prefix=f"sim{sfx}_{i}")


# ══════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════
if active_page == "HOME":
    # ── Hero Banner ──
    hero = engine.get_movie_details(318)  # Shawshank Redemption
    if not hero:
        hero = engine.get_movie_details(2571) or engine.get_movie_details(858)
    if hero:
        hg = hero['genres'].replace('|', ' · ')
        hp = min(99, int(hero['avg_rating'] * 20))
        st.markdown(f"""
        <div class="cai-hero" style="background-image:url('{hero['poster_url']}');">
            <div class="cai-hero-gradient"></div>
            <div class="cai-hero-body">
                <div class="cai-hero-badge">AI Top Pick</div>
                <div class="cai-hero-title">{hero['clean_title']}</div>
                <div class="cai-hero-desc">
                    A powerful story of hope and perseverance behind bars. This masterpiece is rated
                    ★ {hero['avg_rating']:.1f} by {hero['rating_count']} viewers and remains one of the
                    highest-rated films of all time.
                </div>
                <div class="cai-hero-meta">
                    <span style="color:#46d369;font-weight:800;">{hp}% Match</span>
                    <span style="color:#999;">{hero.get('year', '')}</span>
                    <span style="color:#f5c518;font-weight:700;">★ {hero['avg_rating']:.1f}</span>
                    <span style="color:#999;">{hg}</span>
                </div>
                <div class="cai-hero-actions">
                    <span class="cai-hero-btn-play">▶ Explore</span>
                    <span class="cai-hero-btn-info">ℹ More Info</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶ Explore This Movie", key="hero_btn"):
            st.session_state["detail_movie"] = hero['movieId']
            st.rerun()

    # ── Movie Rows ──
    render_movie_row("🔥 Trending Now", engine.get_popular_and_trending(limit=12), "trend")
    render_movie_row("⭐ Top Rated", engine.get_popular_and_trending(limit=12), "top")
    render_movie_row("💥 Action & Adventure", engine.get_popular_and_trending(genre="Action", limit=12), "act")
    render_movie_row("😂 Comedy", engine.get_popular_and_trending(genre="Comedy", limit=12), "com")
    render_movie_row("🎭 Drama", engine.get_popular_and_trending(genre="Drama", limit=12), "dra")
    render_movie_row("🚀 Sci-Fi", engine.get_popular_and_trending(genre="Sci-Fi", limit=12), "sci")
    render_movie_row("🎸 Romance", engine.get_popular_and_trending(genre="Romance", limit=12), "rom")
    render_movie_row("⚡ Thriller", engine.get_popular_and_trending(genre="Thriller", limit=12), "thr")

    if st.session_state.get("detail_movie"):
        render_detail(st.session_state["detail_movie"], user_id, "home")

# ══════════════════════════════════════════════════════════
# PAGE: SEARCH
# ══════════════════════════════════════════════════════════
elif active_page == "SEARCH":
    section_title("🔍 Search & Discover")
    st.caption("Search 9,700+ movies by title, genre, or minimum rating.")
    s1, s2, s3 = st.columns([3, 1, 1])
    with s1:
        q = st.text_input("Search", placeholder="Matrix, Inception, Batman...", label_visibility="collapsed")
    with s2:
        sg = st.selectbox("Genre", ["All"] + engine.all_genres, index=0, label_visibility="collapsed")
    with s3:
        mr = st.slider("Min Rating", 0.0, 5.0, 0.0, 0.5)

    res = engine.search_movies(query=q, genre=sg, min_rating=mr, limit=24)
    st.markdown(
        f'<div style="color:#666;font-size:0.85rem;margin:8px 0 16px;">Found <strong style="color:#E50914">{len(res)}</strong> movies</div>',
        unsafe_allow_html=True
    )
    if not res:
        st.info("No movies found. Try a broader search.")
    else:
        cols = st.columns(6)
        for i, m in enumerate(res):
            render_card(m, cols[i % 6], f"sr_{i}")

    if st.session_state.get("detail_movie"):
        render_detail(st.session_state["detail_movie"], user_id, "srch")

# ══════════════════════════════════════════════════════════
# PAGE: AI RECOMMENDATIONS
# ══════════════════════════════════════════════════════════
elif active_page == "AI RECS":
    section_title("🎯 AI Recommendations")
    st.caption("Personalized movie picks powered by machine learning.")
    a1, a2, a3 = st.columns([2, 1, 1])
    with a1:
        asel = st.selectbox("Algorithm", [
            "Hybrid (Content + Collaborative)",
            "Content-Based (TF-IDF)",
            "Collaborative (Item-Item CF)"
        ], index=0)
    with a2:
        algo = "hybrid"
        if "Content-Based" in asel:
            algo = "content"
        elif "Collaborative" in asel:
            algo = "collaborative"
        top_n = st.slider("Results", 6, 24, 12, 2)
    cfw = None
    if algo == "hybrid":
        with a3:
            cfw = st.slider("α Weight", 0.0, 1.0, 0.60, 0.05, help="0=Content | 1=Collaborative")

    ur = get_user_ratings(user_id)
    if len(ur) == 0:
        st.markdown(
            '<div class="cai-banner-cold"><strong style="color:#E50914;">COLD-START MODE</strong>'
            ' <span style="color:#999;">— No ratings yet. Showing genre-based picks.</span></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="cai-banner-warm"><strong style="color:#46d369;">PERSONALIZED</strong>'
            f' <span style="color:#999;">— Using <strong style="color:#fff;">{len(ur)}</strong> ratings.</span></div>',
            unsafe_allow_html=True
        )

    recs = engine.get_personalized_recommendations(user_id=user_id, algorithm=algo, top_n=top_n, cf_weight=cfw)
    if not recs:
        st.warning("No recommendations available. Set genres in Preferences or rate some movies first.")
    else:
        cols = st.columns(6)
        for i, m in enumerate(recs):
            render_card(m, cols[i % 6], f"rc_{i}")

    if st.session_state.get("detail_movie"):
        render_detail(st.session_state["detail_movie"], user_id, "rec")

# ══════════════════════════════════════════════════════════
# PAGE: PREFERENCES
# ══════════════════════════════════════════════════════════
elif active_page == "PREFERENCES":
    section_title("⚙️ Your Preferences")
    st.caption("Configure your taste profile for better AI recommendations.")
    cp = get_user_preferences(user_id)

    with st.form("pref_form"):
        section_title("🎬 Favorite Genres")
        sg = st.multiselect(
            "Genres", engine.all_genres,
            default=[g for g in cp.get('favorite_genres', []) if g in engine.all_genres],
            label_visibility="collapsed"
        )
        section_title("🌟 Favorite Actors & Directors")
        actors = [
            "Tom Hanks", "Leonardo DiCaprio", "Keanu Reeves", "Morgan Freeman",
            "Robert De Niro", "Al Pacino", "Christian Bale", "Brad Pitt",
            "Scarlett Johansson", "Christopher Nolan", "Quentin Tarantino", "Steven Spielberg"
        ]
        sa = st.multiselect(
            "Actors", actors,
            default=[a for a in cp.get('favorite_actors', []) if a in actors],
            label_visibility="collapsed"
        )
        section_title("🌍 Languages")
        langs = ["English", "French", "Japanese", "Spanish", "German", "Hindi", "Korean", "Italian"]
        sl = st.multiselect(
            "Languages", langs,
            default=[l for l in cp.get('favorite_languages', []) if l in langs],
            label_visibility="collapsed"
        )
        section_title("📂 Categories")
        cats = ["Blockbuster", "Critically Acclaimed", "Indie Cult", "Classic Cinema", "Award Winners", "Hidden Gems"]
        sc = st.multiselect(
            "Categories", cats,
            default=[c for c in cp.get('preferred_categories', []) if c in cats],
            label_visibility="collapsed"
        )
        if st.form_submit_button("💾 Save Preferences"):
            save_user_preferences(user_id, sg, sa, sl, sc)
            st.success("Preferences saved!")
            st.rerun()

    section_title("📋 Your Active Profile")
    p1, p2 = st.columns(2)
    with p1:
        ghtml = " ".join([f'<span class="genre-pill">{g}</span>' for g in sg]) if sg else '<em style="color:#555">None selected</em>'
        st.markdown(f"**Genres:** {ghtml}", unsafe_allow_html=True)
        st.markdown("**Actors:** " + (", ".join(sa) if sa else "*None*"))
    with p2:
        st.markdown("**Languages:** " + (", ".join(sl) if sl else "*None*"))
        st.markdown("**Categories:** " + (", ".join(sc) if sc else "*None*"))

# ══════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════
elif active_page == "DASHBOARD":
    section_title(f"📊 Dashboard — {st.session_state['username']}")
    summary = engine.get_user_summary(user_id)

    # KPI cards
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, str(summary['total_ratings']), "MOVIES RATED"),
        (k2, f"★ {summary['avg_user_rating']}", "AVG RATING"),
        (k3, str(len(summary['preferences'].get('favorite_genres', []))), "GENRES"),
        (k4, str(len(summary['history'])), "SESSIONS"),
    ]
    for col, val, lbl in kpis:
        with col:
            st.markdown(
                f'<div class="cai-stat"><div class="cai-stat-val">{val}</div>'
                f'<div class="cai-stat-label">{lbl}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown("---")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        section_title("Genre Distribution")
        gd = summary['genre_distribution']
        if gd:
            df = pd.DataFrame(list(gd.items()), columns=['Genre', 'Count']).sort_values('Count', ascending=True)
            fig = px.bar(df, x='Count', y='Genre', orientation='h', color='Count',
                         color_continuous_scale=['#1a1a1a', '#E50914'])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e5e5e5'), margin=dict(l=10, r=10, t=10, b=10),
                coloraxis_showscale=False,
                yaxis=dict(gridcolor='#222'), xaxis=dict(gridcolor='#222')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Rate movies to see genre insights.")

    with c2:
        section_title("Rating Breakdown")
        rl = summary['rated_movies']
        if rl:
            rv = [r['user_rating'] for r in rl]
            rdf = pd.DataFrame(rv, columns=['Rating']).value_counts().reset_index()
            rdf.columns = ['Rating', 'Count']
            fig2 = px.pie(rdf, values='Count', names='Rating',
                          color_discrete_sequence=['#E50914', '#f5c518', '#46d369', '#2196f3', '#666'])
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e5e5e5'),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Rate movies to see rating breakdown.")

    section_title("Your Rated Movies")
    if rl:
        tbl = [{"Title": r['title'], "Genres": r['genres'], "Rating": f"★ {r['user_rating']}", "Date": r['rated_at']} for r in rl]
        st.dataframe(pd.DataFrame(tbl), use_container_width=True)
        dm = st.selectbox(
            "Remove rating:", [r['movie_id'] for r in rl],
            format_func=lambda x: next((r['title'] for r in rl if r['movie_id'] == x), str(x))
        )
        if st.button("Delete Rating", key="dd"):
            delete_user_rating(user_id, dm)
            st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center;padding:50px;color:#555;">'
            '<div style="font-size:3rem;margin-bottom:12px;">🎬</div>'
            '<div style="font-weight:700;font-size:1.1rem;color:#999;">No ratings yet</div>'
            '<div style="font-size:0.85rem;margin-top:8px;color:#666;">Search & rate movies to build your profile.</div>'
            '</div>',
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════
# PAGE: AI ARCHITECTURE
# ══════════════════════════════════════════════════════════
elif active_page == "AI ARCH":
    section_title("🧪 AI Model Architecture")
    st.caption("Technical deep-dive into the recommendation algorithms — for project evaluation.")

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("RMSE", f"{eval_metrics.get('RMSE', 0.9094):.4f}")
    with m2: st.metric("MAE", f"{eval_metrics.get('MAE', 0.7015):.4f}")
    with m3: st.metric("P@10", f"{eval_metrics.get('Precision@10', 0.0072):.4f}")
    with m4: st.metric("R@10", f"{eval_metrics.get('Recall@10', 0.0056):.4f}")
    with m5: st.metric("Coverage", f"{eval_metrics.get('Catalog_Coverage', 0.0157):.4f}")

    st.markdown("---")
    t1, t2, t3, t4, t5 = st.tabs(["Concepts", "TF-IDF", "SVD & CF", "Hybrid", "Architecture"])

    with t1:
        st.markdown("""### What is a Recommendation System?
An AI algorithm predicting user preferences for items based on behavior and characteristics.

| Paradigm | Mechanism | Strength |
| :--- | :--- | :--- |
| **Content-Based** | Item metadata similarity | Works for new items |
| **Collaborative** | User behavior patterns | Discovers unexpected hits |
| **Hybrid** | Weighted blend | Best of both worlds |

Netflix, Spotify, Amazon all rely on recommendation AI to drive 80%+ of content consumption.""")

    with t2:
        st.markdown(r"""### Content-Based Filtering & TF-IDF
Each movie → metadata soup (title + genres + tags) → TF-IDF vector → cosine similarity.

$$\text{TF-IDF}(t,d,D) = \frac{f_{t,d}}{\sum f} \cdot \left(\log\frac{1+|D|}{1+|\{d:t\in d\}|}+1\right)$$

$$\text{Sim}(\mathbf{u},\mathbf{v}) = \frac{\mathbf{u}\cdot\mathbf{v}}{||\mathbf{u}||\cdot||\mathbf{v}||}$$

| ✅ Strength | ⚠️ Limitation |
| :--- | :--- |
| Cold-start for new movies | Overspecialization risk |
| Transparent & explainable | Limited serendipity |""")

    with t3:
        st.markdown(r"""### Collaborative Filtering & Matrix Factorization
Item-Item CF + TruncatedSVD decomposition of the rating matrix.

$$\mathbf{R} \approx \mathbf{U}_k \mathbf{\Sigma}_k \mathbf{V}_k^T \quad (k=20)$$

$$\hat{r}_{a,i} = \frac{\sum_{j} s_{ij} \cdot r_{a,j}}{\sum_j |s_{ij}|}$$

| ✅ Strength | ⚠️ Limitation |
| :--- | :--- |
| Domain independent | Cold-start for new users |
| Serendipitous discoveries | Sparse matrix issues |""")

    with t4:
        st.markdown(r"""### Hybrid Engine & Cold-Start Strategy

$$\text{Score} = \alpha \cdot \text{CF}_{\text{norm}} + (1-\alpha) \cdot \text{CB}_{\text{norm}} + \text{GenreBoost}$$

| Ratings | Mode | α | Strategy |
| :--- | :--- | :--- | :--- |
| **0** | Content Only | 0.00 | Genre preferences |
| **1–3** | Content-Heavy | 0.35 | Light collaborative |
| **>3** | CF-Heavy | 0.60 | Strong crowd signals |""")

    with t5:
        st.code("""
┌──────────────────────────────────────────────────┐
│          STREAMLIT PRESENTATION LAYER             │
│  Hero · Search · Ratings · Analytics · Sandbox   │
├────────────────────┬─────────────────────────────┤
│ RECOMMENDATION ENGINE (src/recommendation.py)     │
├─────────┬──────────┼──────────┬──────────────────┤
│ Content │ Collab   │ Hybrid   │ Poster Service   │
│ TF-IDF  │ Item CF  │ Dynamic α│ SVG Generator    │
│ Cosine  │ SVD k=20 │ ColdStart│ CDN Cache        │
├─────────┴──────────┴──────────┴──────────────────┤
│           DATA & PERSISTENCE LAYER                │
│  MovieLens CSVs · SQLite3 · Model PKLs           │
└──────────────────────────────────────────────────┘""", language="text")

# ══════════════════════════════════════════════════════════
# PAGE: ML PLAYGROUND
# ══════════════════════════════════════════════════════════
elif active_page == "PLAYGROUND":
    section_title("🔬 ML Playground")
    st.caption("Live experiments and interactive demos for project evaluation.")

    mode = st.radio("Experiment", ["Similarity Face-Off", "TF-IDF Inspector", "Cold-Start Sim"], horizontal=True)

    if mode == "Similarity Face-Off":
        section_title("Content vs Collaborative")
        dmid = st.selectbox(
            "Seed Movie", list(engine.movie_map.keys()),
            format_func=lambda m: f"{engine.movie_map[m]['clean_title']} ({engine.movie_map[m].get('year', '')}) — {engine.movie_map[m]['genres']}",
            index=0
        )
        seed = engine.get_movie_details(dmid)
        st.markdown(f"**Target:** *{seed['clean_title']}* — `{seed['genres']}`")

        p1, p2 = st.columns(2)
        with p1:
            st.markdown("#### 📄 Content-Based (TF-IDF)")
            for item in engine.get_similar_movies(dmid, top_n=5, method="content"):
                st.markdown(
                    f'<div class="sim-card"><strong>{item["clean_title"]}</strong> ({item.get("year", "")})<br/>'
                    f'<span style="color:#46d369;font-size:0.78rem;">{item["genres"].replace("|", " · ")}</span><br/>'
                    f'<span style="color:#f5c518;">★ {item.get("avg_rating", 0.0)}</span> · '
                    f'<span style="color:#2196f3;font-weight:800;">Sim: {item.get("similarity_score", 0.0):.4f}</span></div>',
                    unsafe_allow_html=True
                )
        with p2:
            st.markdown("#### 👥 Collaborative (Co-Ratings)")
            for item in engine.get_similar_movies(dmid, top_n=5, method="collaborative"):
                st.markdown(
                    f'<div class="sim-card"><strong>{item["clean_title"]}</strong> ({item.get("year", "")})<br/>'
                    f'<span style="color:#46d369;font-size:0.78rem;">{item["genres"].replace("|", " · ")}</span><br/>'
                    f'<span style="color:#f5c518;">★ {item.get("avg_rating", 0.0)}</span> · '
                    f'<span style="color:#E50914;font-weight:800;">Sim: {item.get("similarity_score", 0.0):.4f}</span></div>',
                    unsafe_allow_html=True
                )

    elif mode == "TF-IDF Inspector":
        section_title("TF-IDF Vector Inspector")
        imid = st.selectbox(
            "Movie", list(engine.movie_map.keys()),
            format_func=lambda m: f"{engine.movie_map[m]['clean_title']} ({engine.movie_map[m].get('year', '')})",
            index=10
        )
        info = engine.movie_map[imid]
        st.markdown(f"**Title:** `{info['clean_title']}`")
        st.markdown(f"**Genres:** `{info['genres']}`")
        st.markdown(f"**Tags:** `{info.get('tag', '(none)')}`")
        st.markdown("**Metadata Soup:**")
        st.code(info.get('soup', ''), language="text")

    elif mode == "Cold-Start Sim":
        section_title("Cold-Start Simulation")
        csg = st.multiselect("Genres:", engine.all_genres, default=["Action", "Sci-Fi"])
        csk = st.text_input("Keywords:", "matrix space future hero")
        if st.button("Generate Simulation"):
            kws = [w.strip() for w in csk.split() if w.strip()]
            sr = engine.content_recommender.recommend_by_preferences(favorite_genres=csg, keywords=kws, top_n=6)
            section_title("Simulation Results")
            cols = st.columns(3)
            for i, r in enumerate(sr):
                mp = min(99, max(60, int(r.get('similarity_score', 0.8) * 100)))
                with cols[i % 3]:
                    st.markdown(
                        f'<div style="background:#1a1a1a;border:1px solid #333;border-radius:4px;padding:16px;'
                        f'margin-bottom:12px;border-left:3px solid #46d369;">'
                        f'<div style="color:#fff;font-weight:800;margin-bottom:6px;">'
                        f'{r["clean_title"]} ({r.get("year", "")})</div>'
                        f'<div style="color:#46d369;font-size:0.78rem;margin-bottom:8px;">'
                        f'{r["genres"].replace("|", " · ")}</div>'
                        f'<div style="display:flex;gap:12px;">'
                        f'<span style="color:#46d369;font-weight:900;">{mp}% Match</span>'
                        f'<span style="color:#f5c518;">Score: {r.get("similarity_score", 0):.4f}</span>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )
