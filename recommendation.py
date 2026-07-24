"""
recommendation.py
------------------
Core recommendation engine for the Book Recommendation System.

Implements four recommendation strategies:
    1. Popularity-Based Recommendation
    2. Rule-Based Filtering
    3. Content-Based Recommendation (TF-IDF + Cosine Similarity)
    4. Hybrid Recommendation (weighted combination of the above signals)

The engine is intentionally kept dependency-light (pandas, numpy, scikit-learn)
and fully type-hinted so it is easy to read, test, and extend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class HybridWeights:
    """Weights used by the hybrid recommender. Must sum to 1.0."""
    popularity: float = 0.40
    rating: float = 0.25
    genre_similarity: float = 0.20
    description_similarity: float = 0.15


class BookRecommender:
    """
    Encapsulates all recommendation logic for a book catalogue.

    Parameters
    ----------
    data : pd.DataFrame
        Must contain the columns produced by utils.load_books().
    """

    def __init__(self, data: pd.DataFrame):
        self.df = data.reset_index(drop=True).copy()
        self._build_content_index()

    # ------------------------------------------------------------------ #
    # Setup
    # ------------------------------------------------------------------ #
    def _build_content_index(self) -> None:
        """Builds the TF-IDF matrix used for content-based similarity."""
        self.df["content_soup"] = (
            self.df["genre"].fillna("") + " " +
            self.df["author"].fillna("") + " " +
            self.df["description"].fillna("")
        )
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df["content_soup"])
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)

        # Precompute a genre-only TF-IDF for the hybrid recommender's
        # "genre similarity" component.
        self.genre_vectorizer = TfidfVectorizer(stop_words="english")
        self.genre_matrix = self.genre_vectorizer.fit_transform(self.df["genre"].fillna(""))
        self.genre_similarity_matrix = cosine_similarity(self.genre_matrix)

    def _title_to_index(self, title: str) -> Optional[int]:
        matches = self.df.index[self.df["title"].str.lower() == title.lower()]
        if len(matches) == 0:
            return None
        return int(matches[0])

    # ------------------------------------------------------------------ #
    # Method 1: Popularity-Based
    # ------------------------------------------------------------------ #
    def popularity_based(self, top_n: int = 10) -> pd.DataFrame:
        """Ranks books by a blend of popularity score, rating, and rating count."""
        df = self.df.copy()
        df["_norm_ratings"] = self._normalize(df["num_ratings"])
        df["_score"] = (
            df["popularity_score"] * 0.5
            + df["average_rating"] * 10 * 0.3
            + df["_norm_ratings"] * 100 * 0.2
        )
        return df.sort_values("_score", ascending=False).head(top_n).drop(columns=["_norm_ratings", "_score"], errors="ignore")

    # ------------------------------------------------------------------ #
    # Method 2: Rule-Based Filtering
    # ------------------------------------------------------------------ #
    def rule_based_filter(
        self,
        genre: Optional[str] = None,
        author: Optional[str] = None,
        language: Optional[str] = None,
        min_rating: float = 0.0,
        year_range: Optional[tuple[int, int]] = None,
    ) -> pd.DataFrame:
        """Filters the catalogue according to explicit rules/criteria."""
        df = self.df.copy()

        if genre and genre != "Any":
            df = df[df["genre"].str.lower() == genre.lower()]
        if author and author != "Any":
            df = df[df["author"].str.lower() == author.lower()]
        if language and language != "Any":
            df = df[df["language"].str.lower() == language.lower()]
        if min_rating:
            df = df[df["average_rating"] >= min_rating]
        if year_range:
            lo, hi = year_range
            df = df[(df["publication_year"] >= lo) & (df["publication_year"] <= hi)]

        return df.sort_values(["average_rating", "popularity_score"], ascending=False)

    # ------------------------------------------------------------------ #
    # Method 3: Content-Based (TF-IDF + Cosine Similarity)
    # ------------------------------------------------------------------ #
    def content_based(self, title: str, top_n: int = 10) -> pd.DataFrame:
        """Recommends books similar to the given title using TF-IDF cosine similarity."""
        idx = self._title_to_index(title)
        if idx is None:
            return pd.DataFrame(columns=self.df.columns)

        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        sim_scores = [s for s in sim_scores if s[0] != idx]
        sim_scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = [i for i, _ in sim_scores[:top_n]]
        scores = [round(s * 100, 1) for _, s in sim_scores[:top_n]]

        result = self.df.iloc[top_indices].copy()
        result["similarity_score"] = scores
        return result

    def search_by_interest(self, interest_text: str, top_n: int = 10) -> pd.DataFrame:
        """
        Recommends books based on a free-text 'reading interest' by projecting
        it into the same TF-IDF space as the catalogue.
        """
        if not interest_text or not interest_text.strip():
            return pd.DataFrame(columns=self.df.columns)

        query_vec = self.vectorizer.transform([interest_text])
        sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = sims.argsort()[::-1][:top_n]

        result = self.df.iloc[top_indices].copy()
        result["similarity_score"] = [round(sims[i] * 100, 1) for i in top_indices]
        return result[result["similarity_score"] > 0]

    # ------------------------------------------------------------------ #
    # Method 4: Hybrid Recommendation
    # ------------------------------------------------------------------ #
    def hybrid_recommend(
        self,
        title: Optional[str] = None,
        genre: Optional[str] = None,
        top_n: int = 10,
        weights: HybridWeights = HybridWeights(),
    ) -> pd.DataFrame:
        """
        Combines popularity, rating, genre similarity, and description similarity
        into a single weighted recommendation score.

        If `title` is provided, similarity components are computed relative to
        that book. If only `genre` is provided, similarity is computed relative
        to the average profile of books in that genre.
        """
        df = self.df.copy()
        n = len(df)

        norm_popularity = self._normalize(df["popularity_score"])
        norm_rating = self._normalize(df["average_rating"])

        idx = self._title_to_index(title) if title else None

        if idx is not None:
            desc_sim = self.similarity_matrix[idx]
            genre_sim = self.genre_similarity_matrix[idx]
        elif genre and genre != "Any":
            mask = (df["genre"].str.lower() == genre.lower()).values
            if mask.any():
                desc_sim = self.similarity_matrix[:, mask].mean(axis=1)
                genre_sim = self.genre_similarity_matrix[:, mask].mean(axis=1)
            else:
                desc_sim = np.zeros(n)
                genre_sim = np.zeros(n)
        else:
            desc_sim = np.zeros(n)
            genre_sim = np.zeros(n)

        df["_score"] = (
            weights.popularity * norm_popularity
            + weights.rating * norm_rating
            + weights.genre_similarity * self._normalize(pd.Series(genre_sim))
            + weights.description_similarity * self._normalize(pd.Series(desc_sim))
        ) * 100

        if idx is not None:
            df = df.drop(index=idx)

        return df.sort_values("_score", ascending=False).head(top_n).rename(
            columns={"_score": "recommendation_score"}
        )

    # ------------------------------------------------------------------ #
    # Convenience / analytics-support helpers
    # ------------------------------------------------------------------ #
    def top_rated(self, top_n: int = 10) -> pd.DataFrame:
        return self.df.sort_values("average_rating", ascending=False).head(top_n)

    def most_popular(self, top_n: int = 10) -> pd.DataFrame:
        return self.df.sort_values("popularity_score", ascending=False).head(top_n)

    def recently_published(self, top_n: int = 10) -> pd.DataFrame:
        return self.df.sort_values("publication_year", ascending=False).head(top_n)

    def search_by_title(self, query: str) -> pd.DataFrame:
        if not query:
            return self.df.copy()
        return self.df[self.df["title"].str.contains(query, case=False, na=False)]

    def random_recommendation(self, n: int = 1) -> pd.DataFrame:
        return self.df.sample(n=min(n, len(self.df)))

    def trending(self, top_n: int = 10) -> pd.DataFrame:
        """A simple 'trending' heuristic: recent books with strong popularity."""
        df = self.df.copy()
        df = df[df["publication_year"] >= df["publication_year"].max() - 15]
        df["_trend_score"] = df["popularity_score"] * 0.7 + df["average_rating"] * 10 * 0.3
        return df.sort_values("_trend_score", ascending=False).head(top_n).drop(columns=["_trend_score"])

    def autocomplete_titles(self, prefix: str, limit: int = 8) -> list[str]:
        if not prefix:
            return []
        matches = self.df[self.df["title"].str.lower().str.startswith(prefix.lower())]
        return matches["title"].head(limit).tolist()

    # ------------------------------------------------------------------ #
    # Utilities
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize(series: pd.Series) -> pd.Series:
        """Min-max normalizes a numeric series to the [0, 1] range."""
        s = series.astype(float)
        rng = s.max() - s.min()
        if rng == 0:
            return s * 0
        return (s - s.min()) / rng
