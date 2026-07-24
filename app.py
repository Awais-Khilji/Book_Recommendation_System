"""
app.py
------
Streamlit front-end for the Book Recommendation System.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from recommendation import BookRecommender, HybridWeights
from utils import (
    author_options,
    cover_url,
    genre_options,
    language_options,
    load_books,
    star_string,
    to_csv_download,
    truncate,
    year_bounds,
)

# Page configuration
st.set_page_config(
    page_title="Bookshelf — Discover Your Next Read",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "favorites" not in st.session_state:
    st.session_state.favorites = set()
if "history" not in st.session_state:
    st.session_state.history = []
if "page" not in st.session_state:
    st.session_state.page = 1

PAGE_SIZE = 6
APP_VERSION = "1.1.0"

# Theme — a warm, library-inspired palette (not the default Streamlit look).
# Applied both to our own HTML/CSS *and* to Streamlit's native widgets
# (buttons, tabs, sliders, inputs, sidebar) so the whole app feels cohesive
# in both light and dark mode, rather than mixing our colors with Streamlit's
# stock red-accent defaults.
LIGHT = {
    "bg": "#F6F1E7", "surface": "#FFFFFF", "text": "#2B2118",
    "muted": "#7A6C58", "accent": "#7A2E2E", "accent2": "#C08A3E",
    "card_border": "#E4D9C4", "sidebar_bg": "#EFE6D6", "input_bg": "#FFFFFF",
    "shadow": "rgba(43,33,24,0.10)",
}
DARK = {
    "bg": "#15120E", "surface": "#211C16", "text": "#F1E9DA",
    "muted": "#C7B8A0", "accent": "#E4967A", "accent2": "#E8C36E",
    "card_border": "#3A3128", "sidebar_bg": "#1B1712", "input_bg": "#2A241C",
    "shadow": "rgba(0,0,0,0.45)",
}
T = DARK if st.session_state.dark_mode else LIGHT

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}
.stApp {{
    background-color: {T['bg']};
    color: {T['text']};
}}

/* Hide only the Deploy button / main menu / status widget inside
   Streamlit's default header — but KEEP the header itself, because the
   "expand sidebar" arrow (shown after collapsing the sidebar) lives
   inside this same element and disappears if we remove it entirely. */
header[data-testid="stHeader"] {{
    background: transparent !important;
    height: 2.6rem;
    min-height: 2.6rem;
}}
header[data-testid="stHeader"] [data-testid="stToolbarActions"],
header[data-testid="stHeader"] [data-testid="stMainMenu"],
header[data-testid="stHeader"] [data-testid="stStatusWidget"],
header[data-testid="stHeader"] [data-testid="stAppDeployButton"] {{
    display: none !important;
}}
div[data-testid="stAppViewContainer"] {{
    padding-top: 0 !important;
}}
div[data-testid="stMainBlockContainer"] {{
    padding-top: 0.4rem !important;
}}
section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] {{
    padding-top: 0.8rem !important;
}}
h1, h2, h3, .hero-title, .navbar-brand {{
    font-family: 'Fraunces', serif !important;
}}

/* ---------------- Navbar ---------------- */
.navbar {{
    display: flex;
    align-items: center;
    gap: 1.4rem;
    padding: 0.55rem 0.2rem;
}}
.navbar-brand {{
    font-size: 1.45rem;
    font-weight: 700;
    color: {T['text']};
    white-space: nowrap;
}}
.navbar-links {{
    display: flex;
    gap: 0.4rem;
    flex-wrap: wrap;
}}
.navbar-links span {{
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    color: {T['muted']};
    background: {T['surface']};
    border: 1px solid {T['card_border']};
}}

/* ---------------- Hero strip ---------------- */
.hero {{
    padding: 1rem 1.5rem;
    border-radius: 16px;
    background: linear-gradient(120deg, {T['accent']} 0%, {T['accent2']} 100%);
    color: #FFF6EA;
    margin: 0.3rem 0 1.2rem 0;
}}
.hero-sub {{
    font-size: 0.95rem;
    opacity: 0.92;
}}

/* ---------------- Book cards ---------------- */
.book-card {{
    background: {T['surface']};
    border: 1px solid {T['card_border']};
    border-radius: 14px;
    padding: 0.9rem;
    margin-bottom: 1rem;
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}}
.cover-thumb {{
    width: 100%;
    max-width: 165px;
    height: 175px;
    object-fit: cover;
    border-radius: 10px;
    display: block;
    margin: 0 auto 0.6rem auto;
    box-shadow: 0 4px 12px {T['shadow']};
}}
.book-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 20px {T['shadow']};
}}
.book-title {{
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.05rem;
    margin-bottom: 0.1rem;
    color: {T['text']};
}}
.book-meta {{
    color: {T['muted']};
    font-size: 0.85rem;
    margin-bottom: 0.35rem;
}}
.badge {{
    display: inline-block;
    background: {T['accent']}22;
    color: {T['accent']};
    border-radius: 999px;
    padding: 0.1rem 0.6rem;
    font-size: 0.75rem;
    margin-right: 0.3rem;
    margin-bottom: 0.25rem;
    font-weight: 600;
}}
.score-pill {{
    display: inline-block;
    background: {T['accent2']};
    color: #2B2118;
    border-radius: 999px;
    padding: 0.1rem 0.65rem;
    font-size: 0.75rem;
    font-weight: 700;
    float: right;
}}
.section-label {{
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.78rem;
    color: {T['muted']};
    font-weight: 600;
    margin: 1.2rem 0 0.4rem 0;
}}
hr {{ border-color: {T['card_border']}; }}

/* ---------------- Native Streamlit widget re-skin ---------------- */
section[data-testid="stSidebar"] {{
    background-color: {T['sidebar_bg']};
    border-right: 1px solid {T['card_border']};
}}
div[data-testid="stSidebarUserContent"] {{
    padding-top: 0.6rem;
}}

/* Buttons */
.stButton > button, .stDownloadButton > button {{
    border-radius: 10px !important;
    border: 1px solid {T['accent']}55 !important;
    color: {T['text']} !important;
    background: {T['surface']} !important;
    transition: all 0.12s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    border-color: {T['accent']} !important;
    color: {T['accent']} !important;
}}
.stButton > button[kind="primary"] {{
    background: {T['accent']} !important;
    border-color: {T['accent']} !important;
    color: #FFF6EA !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: {T['accent2']} !important;
    border-color: {T['accent2']} !important;
    color: #2B2118 !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.3rem;
    border-bottom: 1px solid {T['card_border']};
}}
.stTabs [data-baseweb="tab"] {{
    color: {T['muted']};
    font-weight: 600;
}}
.stTabs [aria-selected="true"] {{
    color: {T['accent']} !important;
    border-bottom-color: {T['accent']} !important;
}}

/* Inputs, selects, sliders */
div[data-testid="stTextInput"] input,
div[data-baseweb="select"] > div {{
    background-color: {T['input_bg']} !important;
    border-color: {T['card_border']} !important;
    color: {T['text']} !important;
    border-radius: 8px !important;
}}
div[data-testid="stSlider"] [role="slider"] {{
    background-color: {T['accent']} !important;
}}
div[data-testid="stSlider"] > div > div > div {{
    background: {T['accent']} !important;
}}
div[data-testid="stToggle"] label div[data-checked="true"] {{
    background-color: {T['accent']} !important;
}}

/* Popover / expander */
div[data-testid="stPopoverBody"], details {{
    background-color: {T['surface']} !important;
    border-color: {T['card_border']} !important;
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Data + engine (cached — TF-IDF matrix and dataframe are built only once
# per session, not on every rerun/click, which keeps interactions snappy)
@st.cache_resource(show_spinner=False)
def get_engine() -> BookRecommender:
    df = load_books()
    return BookRecommender(df)


engine = get_engine()
df_all = engine.df

# Top navbar — brand/name, decorative section pills, and a menu/about popover
nav_col, menu_col = st.columns([6, 1])
with nav_col:
    st.markdown(
        """
        <div class="navbar">
            <span class="navbar-brand">📚 Bookshelf</span>
            <span class="navbar-links">
                <span>🔎 Discover</span>
                <span>📈 Trending</span>
                <span>📊 Analytics</span>
                <span>❤️ My Library</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with menu_col:
    with st.popover("☰ Menu", width="stretch"):
        st.markdown("#### 📚 Bookshelf")
        st.caption(f"Version {APP_VERSION}")
        st.write(
            "An intelligent book recommendation engine that blends "
            "popularity signals, rule-based filters, and AI-driven "
            "content similarity (TF-IDF + cosine similarity) to help "
            "you find your next great read."
        )
        st.markdown("---")
        st.markdown(
            "**Built with:** Streamlit · Pandas · Scikit-learn · Plotly\n\n"
            "**Algorithms:** Popularity-Based · Rule-Based · Content-Based · Hybrid"
        )

st.markdown(
    """
    <div class="hero">
        <div class="hero-sub">Find your next great read — powered by popularity, rules, and content-based AI recommendations.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar — filters.
# This panel is intentionally "static": every widget here stays visible and
# keeps its state no matter which tab is open below. Only the *results*
# area re-renders dynamically based on what you pick here.
with st.sidebar:
    st.markdown("### 🎛️ Filters")

    genre = st.selectbox("Genre", genre_options(df_all))
    author = st.selectbox("Author (optional)", author_options(df_all))
    language = st.selectbox("Language", language_options(df_all))
    min_rating = st.slider("Minimum rating ⭐", 0.0, 5.0, 0.0, 0.1)

    y_lo, y_hi = year_bounds(df_all)
    year_range = st.slider("Publication year range", y_lo, y_hi, (y_lo, y_hi))

    interest = st.text_input(
        "Reading interest (free text)",
        placeholder="e.g. artificial intelligence, dystopia, self growth...",
    )

    search_query = st.text_input("🔎 Search by title", placeholder="Start typing a title...")
    if search_query:
        suggestions = engine.autocomplete_titles(search_query)
        if suggestions:
            st.caption("Suggestions: " + " · ".join(suggestions[:5]))

    st.markdown("---")
    method = st.radio(
        "Recommendation method",
        ["Hybrid (recommended)", "Popularity-Based", "Rule-Based", "Content-Based"],
        index=0,
    )
    recommend_clicked = st.button("✨ Recommend Books", width="stretch", type="primary")

    st.markdown("---")
    if st.button("🎲 Surprise me with a random book", width="stretch"):
        st.session_state["_random_pick"] = engine.random_recommendation(1)

    st.markdown("<span class='section-label'>Catalogue</span>", unsafe_allow_html=True)
    st.caption(f"{len(df_all)} books · {df_all['genre'].nunique()} genres · {df_all['author'].nunique()} authors")


# Book card rendering
#
# `section` disambiguates widget keys (bookmark/prev/next/download buttons)
# across the different places the same book can appear at once (Discover's
# default list, Trending, My Library, etc.) — without this, Streamlit raises
# a StreamlitDuplicateElementKey error the moment a book shows up twice on
# the same page, which is what was breaking Trending/Analytics/My Library.
def render_book_card(row: pd.Series, section: str, score_label: str | None = None, score_value: float | None = None):
    cols = st.columns([1, 4])
    with cols[0]:
        cover = cover_url(row["book_id"], row["title"], row["author"])
        st.markdown(f'<img src="{cover}" class="cover-thumb" />', unsafe_allow_html=True)
        fav_key = f"fav_{section}_{row['book_id']}"
        is_fav = row["book_id"] in st.session_state.favorites
        if st.button("💔 Remove" if is_fav else "🤍 Bookmark", key=fav_key, width="stretch"):
            if is_fav:
                st.session_state.favorites.discard(row["book_id"])
            else:
                st.session_state.favorites.add(row["book_id"])
                st.session_state.history.append(row["book_id"])
            st.rerun()

    with cols[1]:
        score_html = f"<span class='score-pill'>{score_label} {score_value:.1f}</span>" if score_label else ""
        st.markdown(
            f"""
            <div class="book-card">
                {score_html}
                <div class="book-title">{row['title']}</div>
                <div class="book-meta">by {row['author']} · {row['publication_year']} · {row['publisher']}</div>
                <span class="badge">{row['genre']}</span>
                <span class="badge">{row['language']}</span>
                <span class="badge">{star_string(row['average_rating'])}</span>
                <span class="badge">🔥 {row['popularity_score']:.1f}</span>
                <span class="badge">👥 {int(row['num_ratings']):,} ratings</span>
                <span class="badge">📄 {int(row['num_pages'])} pages</span>
                <p style="margin-top:0.5rem; color:{T['muted']};">{truncate(row['description'], 180)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_results(df: pd.DataFrame, section: str, score_col: str | None = None, score_label: str = "Score", paginate: bool = True):
    if df.empty:
        st.info("No books matched. Try widening your filters.")
        return

    if paginate and len(df) > PAGE_SIZE:
        page_key = f"page_{section}"
        st.session_state.setdefault(page_key, 1)
        total_pages = (len(df) - 1) // PAGE_SIZE + 1
        st.session_state[page_key] = min(st.session_state[page_key], total_pages)
        start = (st.session_state[page_key] - 1) * PAGE_SIZE
        page_df = df.iloc[start:start + PAGE_SIZE]
    else:
        page_key = None
        page_df = df
        total_pages = 1

    for _, row in page_df.iterrows():
        score_val = row[score_col] if score_col and score_col in row else None
        render_book_card(row, section, score_label if score_val is not None else None, score_val)

    if paginate and total_pages > 1:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("⬅️ Prev", key=f"prev_{section}", disabled=st.session_state[page_key] <= 1):
                st.session_state[page_key] -= 1
                st.rerun()
        with c2:
            st.markdown(f"<div style='text-align:center;'>Page {st.session_state[page_key]} of {total_pages}</div>", unsafe_allow_html=True)
        with c3:
            if st.button("Next ➡️", key=f"next_{section}", disabled=st.session_state[page_key] >= total_pages):
                st.session_state[page_key] += 1
                st.rerun()

    st.download_button(
        "⬇️ Export these recommendations to CSV",
        data=to_csv_download(df),
        file_name="recommendations.csv",
        mime="text/csv",
        key=f"dl_{section}",
    )


# Tabs
tab_discover, tab_trending, tab_analytics, tab_library = st.tabs(
    ["🔎 Discover", "📈 Trending & Top Lists", "📊 Analytics Dashboard", "❤️ My Library"]
)

# ----------------------------- DISCOVER ------------------------------------ #
with tab_discover:
    if "_random_pick" in st.session_state:
        st.markdown("<span class='section-label'>Random Pick</span>", unsafe_allow_html=True)
        render_results(st.session_state["_random_pick"], section="random", paginate=False)
        st.markdown("---")

    if search_query:
        st.markdown(f"<span class='section-label'>Search results for “{search_query}”</span>", unsafe_allow_html=True)
        render_results(engine.search_by_title(search_query), section="search")

    elif recommend_clicked or interest:
        if interest and method != "Rule-Based":
            st.markdown("<span class='section-label'>Based on your reading interest</span>", unsafe_allow_html=True)
            render_results(engine.search_by_interest(interest), section="interest", score_col="similarity_score", score_label="Match")

        elif method == "Popularity-Based":
            st.markdown("<span class='section-label'>Top Popular Picks</span>", unsafe_allow_html=True)
            render_results(engine.popularity_based(top_n=30), section="disc_pop", score_col="popularity_score", score_label="🔥")

        elif method == "Rule-Based":
            st.markdown("<span class='section-label'>Books Matching Your Filters</span>", unsafe_allow_html=True)
            yr = year_range if year_range != (y_lo, y_hi) else None
            render_results(
                engine.rule_based_filter(
                    genre=genre, author=author, language=language,
                    min_rating=min_rating, year_range=yr,
                ),
                section="disc_rule",
                score_col="average_rating", score_label="⭐",
            )

        elif method == "Content-Based":
            if not search_query:
                st.markdown("<span class='section-label'>Pick a book to find similar titles</span>", unsafe_allow_html=True)
                pick = st.selectbox("Choose a book you like", df_all["title"].tolist(), key="content_pick")
                if pick:
                    st.session_state.history.append(int(df_all[df_all["title"] == pick]["book_id"].iloc[0]))
                    render_results(engine.content_based(pick, top_n=30), section="disc_content", score_col="similarity_score", score_label="Match")

        else:  # Hybrid
            st.markdown("<span class='section-label'>Hybrid Recommendations For You</span>", unsafe_allow_html=True)
            base_title = None
            if st.session_state.history:
                last_id = st.session_state.history[-1]
                match = df_all[df_all["book_id"] == last_id]
                base_title = match["title"].iloc[0] if not match.empty else None
            result = engine.hybrid_recommend(
                title=base_title, genre=genre if genre != "Any" else None,
                top_n=30, weights=HybridWeights(),
            )
            render_results(result, section="disc_hybrid", score_col="recommendation_score", score_label="Score")
    else:
        st.markdown("<span class='section-label'>Top Rated Books</span>", unsafe_allow_html=True)
        render_results(engine.top_rated(top_n=30), section="disc_default", score_col="average_rating", score_label="⭐")

# ----------------------------- TRENDING ------------------------------------ #
with tab_trending:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<span class='section-label'>🔥 Most Popular</span>", unsafe_allow_html=True)
        for _, row in engine.most_popular(5).iterrows():
            st.markdown(
                f"**{row['title']}** — *{row['author']}* &nbsp; "
                f"<span class='badge'>🔥 {row['popularity_score']:.1f}</span>",
                unsafe_allow_html=True,
            )
    with c2:
        st.markdown("<span class='section-label'>🆕 Recently Published</span>", unsafe_allow_html=True)
        for _, row in engine.recently_published(5).iterrows():
            st.markdown(
                f"**{row['title']}** — *{row['author']}* ({row['publication_year']})",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("<span class='section-label'>📈 Trending Now</span>", unsafe_allow_html=True)
    render_results(engine.trending(top_n=12), section="trending", score_col="popularity_score", score_label="🔥", paginate=False)

# ----------------------------- ANALYTICS ------------------------------------ #
with tab_analytics:
    st.markdown("<span class='section-label'>Catalogue Analytics</span>", unsafe_allow_html=True)

    plot_theme = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
    color_seq = [T["accent"], T["accent2"], "#5C7A5A", "#4A6FA5", "#9B6B9E", "#B85450"]
    paper_bg = T["surface"]

    def _style(fig):
        fig.update_layout(
            height=380,
            paper_bgcolor=paper_bg,
            plot_bgcolor=paper_bg,
            font_color=T["text"],
            margin=dict(t=50, b=30, l=10, r=10),
        )
        return fig

    c1, c2 = st.columns(2)
    with c1:
        genre_counts = df_all["genre"].value_counts().reset_index()
        genre_counts.columns = ["genre", "count"]
        fig = px.bar(genre_counts, x="genre", y="count", title="Books per Genre",
                     color_discrete_sequence=[T["accent"]], template=plot_theme)
        fig.update_layout(xaxis_tickangle=-40)
        st.plotly_chart(_style(fig), width="stretch")

    with c2:
        fig = px.pie(genre_counts, names="genre", values="count", title="Top Genres Share",
                      color_discrete_sequence=color_seq, template=plot_theme, hole=0.45)
        st.plotly_chart(_style(fig), width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        fig = px.histogram(df_all, x="average_rating", nbins=20, title="Rating Distribution",
                            color_discrete_sequence=[T["accent2"]], template=plot_theme)
        st.plotly_chart(_style(fig), width="stretch")

    with c4:
        fig = px.histogram(df_all, x="publication_year", nbins=25, title="Publication Year Distribution",
                            color_discrete_sequence=[T["accent"]], template=plot_theme)
        st.plotly_chart(_style(fig), width="stretch")

    c5, c6 = st.columns(2)
    with c5:
        top_authors = df_all["author"].value_counts().head(10).reset_index()
        top_authors.columns = ["author", "books"]
        fig = px.bar(top_authors, x="books", y="author", orientation="h", title="Most Popular Authors (by # books)",
                     color_discrete_sequence=[T["accent2"]], template=plot_theme)
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=420)
        st.plotly_chart(_style(fig), width="stretch")

    with c6:
        top10_rated = df_all.sort_values("average_rating", ascending=False).head(10)
        fig = px.bar(top10_rated, x="average_rating", y="title", orientation="h",
                     title="Top 10 Highest Rated Books", color_discrete_sequence=[T["accent"]], template=plot_theme)
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=420)
        st.plotly_chart(_style(fig), width="stretch")

    top10_pop = df_all.sort_values("popularity_score", ascending=False).head(10)
    fig = px.bar(top10_pop, x="popularity_score", y="title", orientation="h",
                 title="Top 10 Most Popular Books", color_discrete_sequence=[T["accent2"]], template=plot_theme)
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=420)
    st.plotly_chart(_style(fig), width="stretch")

# ----------------------------- MY LIBRARY ------------------------------------ #
with tab_library:
    st.markdown("<span class='section-label'>❤️ Bookmarked Favorites</span>", unsafe_allow_html=True)
    fav_df = df_all[df_all["book_id"].isin(st.session_state.favorites)]
    if fav_df.empty:
        st.info("You haven't bookmarked any books yet. Tap 🤍 Bookmark on a book card to save it here.")
    else:
        render_results(fav_df, section="lib_fav", paginate=False)

    st.markdown("---")
    st.markdown("<span class='section-label'>🕘 Reading / View History</span>", unsafe_allow_html=True)
    if not st.session_state.history:
        st.caption("No history yet — books you bookmark or explore for similarities will show up here.")
    else:
        hist_ids = list(dict.fromkeys(reversed(st.session_state.history)))  # unique, most-recent-first
        hist_df = df_all[df_all["book_id"].isin(hist_ids)]
        st.dataframe(
            hist_df[["title", "author", "genre", "average_rating", "publication_year"]],
            width="stretch", hide_index=True,
        )

st.markdown("---")
st.caption(f"Bookshelf v{APP_VERSION} · Built with Streamlit · Pandas · Scikit-learn · Plotly")