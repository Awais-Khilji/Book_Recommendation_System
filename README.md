# 📚 Bookshelf — Intelligent Book Recommendation System

A full-stack, portfolio-ready book recommendation engine built with **Streamlit**, **Pandas**, and **Scikit-learn**. It blends popularity signals, rule-based filtering, and TF-IDF/cosine-similarity content-based AI to help users discover their next favorite read — similar in spirit to Goodreads or Amazon Books.

---

## ✨ Features

- **Four recommendation strategies**: Popularity-Based, Rule-Based Filtering, Content-Based (TF-IDF + Cosine Similarity), and a weighted Hybrid model.
- **Free-text "reading interest" search** — type a topic like *"artificial intelligence"* or *"dystopia"* and get semantically matched books.
- **Title search with autocomplete suggestions.**
- **Rich sidebar filters**: genre, author, language, minimum rating, and publication-year range.
- **Book cards** with placeholder cover art, star ratings, popularity badges, rating counts, and descriptions.
- **Top Rated / Most Popular / Recently Published / Trending** curated lists.
- **Analytics Dashboard** with 7 interactive Plotly charts (genre distribution, rating histogram, top authors, top 10 lists, and more).
- **Bookmarking (favorites)** and **reading/view history**, kept in-session.
- **Export recommendations to CSV.**
- **Pagination** on long result lists.
- **Random "Surprise Me" recommendation.**
- **Dark mode toggle** with a fully re-themed palette.
- Clean, modular, type-hinted, well-commented Python code.

---

## 🛠️ Technologies Used

| Layer            | Tools |
|-------------------|-------|
| UI                | Streamlit |
| Data              | Pandas, NumPy |
| ML / Similarity   | Scikit-learn (`TfidfVectorizer`, `cosine_similarity`) |
| Visualizations    | Plotly Express |
| Language          | Python 3.10+ |

---

## 📂 Dataset Description

`data/books.csv` contains **115 real, well-known books** spanning genres like Fiction, Fantasy, Science Fiction, Romance, Thriller, Mystery, Horror, Young Adult, Self Help, Business, Technology, AI, Science, Philosophy, History, Biography, and Classics.

| Column              | Description                                   |
|---------------------|------------------------------------------------|
| `book_id`            | Unique identifier                              |
| `title`              | Book title                                     |
| `author`             | Author name                                    |
| `genre`              | Primary genre                                  |
| `language`           | Original / catalogue language                  |
| `publication_year`   | Year first published                           |
| `average_rating`     | Simulated average rating (3.5–4.9)              |
| `num_ratings`        | Simulated number of ratings                    |
| `popularity_score`   | Derived score (0–100) blending rating, ratings volume, and recency |
| `num_pages`          | Page count                                     |
| `description`        | Short synopsis                                 |
| `publisher`          | Original publisher                             |

> Ratings, rating counts, and popularity scores are deterministically simulated (see `generate_dataset.py`) for demonstration purposes — titles, authors, years, and descriptions are real.

---

## 🧠 Recommendation Algorithms

### 1. Popularity-Based
Ranks all books using a weighted blend of `popularity_score`, `average_rating`, and normalized `num_ratings`.

### 2. Rule-Based Filtering
Filters the catalogue by genre, author, language, minimum rating, and publication-year range — returning only exact matches.

### 3. Content-Based (TF-IDF + Cosine Similarity)
Builds a TF-IDF matrix over each book's genre, author, and description, then uses cosine similarity to find the most textually similar titles to a selected book — or to a free-text "reading interest" query.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
```

### 4. Hybrid Recommendation
Combines four normalized signals into one score:

| Signal                  | Weight |
|--------------------------|--------|
| Popularity Score          | 40% |
| Average Rating            | 25% |
| Genre Similarity          | 20% |
| Description Similarity    | 15% |

---

## 📁 Folder Structure

```
book_recommendation_system/
│
├── app.py                 # Streamlit UI
├── recommendation.py       # BookRecommender engine (all 4 algorithms)
├── utils.py                # Data loading, filters, formatting helpers
├── generate_dataset.py     # Reproducible script that builds books.csv
├── data/
│   └── books.csv           # 115-book dataset
├── images/                 # (reserved for custom cover art, optional)
├── assets/                 # (reserved for extra static assets)
├── requirements.txt
└── README.md
```

---

## 🚀 Installation Guide

1. **Clone or download** this project folder.
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage Instructions

Run the app from the project root:

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (typically `http://localhost:8501`).

**In the app:**
1. Use the sidebar to set filters (genre, author, language, rating, year range) and pick a recommendation method.
2. Type a reading interest or a title to search, or click **✨ Recommend Books**.
3. Browse book cards, bookmark favorites (🤍), and export results to CSV.
4. Check the **Analytics Dashboard** tab for catalogue-wide insights.
5. Visit **My Library** to see bookmarks and browsing history.
6. Toggle **🌙 Dark mode** in the sidebar for a re-themed interface.

---

## 🖼️ Screenshots

_Add screenshots here after running the app locally, e.g.:_

```
assets/screenshot-discover.png
assets/screenshot-analytics.png
assets/screenshot-darkmode.png
```

---

## 🔮 Future Improvements

- Replace placeholder covers with real artwork via the Open Library or Google Books API.
- Persist favorites/history to a database (SQLite/Postgres) instead of session state.
- Add collaborative filtering using real user–item interaction data.
- User accounts with authentication.
- A confidence interval / explainability panel for recommendation scores.
- Multi-language UI.

---

## 📄 License

This project is provided as an educational / portfolio sample. Feel free to reuse and adapt it.
