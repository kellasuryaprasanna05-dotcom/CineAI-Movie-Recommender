"""
Data Preprocessing Module for AI-Powered Movie Recommendation System.
Cleans MovieLens dataset, extracts features, calculates ratings metrics, and builds matrices.
"""
import os
import re
from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np

def extract_year(title: str) -> Tuple[str, str]:
    """Extracts 4-digit release year from title and returns (clean_title, year)."""
    match = re.search(r'\((\d{4})\)', title)
    if match:
        year = match.group(1)
        clean_title = re.sub(r'\s*\(\d{4}\)', '', title).strip()
        return clean_title, year
    return title.strip(), ""

class DataLoader:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_dir = data_dir
        self.movies_df: pd.DataFrame = None
        self.ratings_df: pd.DataFrame = None
        self.tags_df: pd.DataFrame = None
        self.links_df: pd.DataFrame = None
        self.processed_movies_df: pd.DataFrame = None
        self.user_movie_matrix: pd.DataFrame = None

    def load_raw_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        movies_path = os.path.join(self.data_dir, "movies.csv")
        ratings_path = os.path.join(self.data_dir, "ratings.csv")
        tags_path = os.path.join(self.data_dir, "tags.csv")
        links_path = os.path.join(self.data_dir, "links.csv")

        if not os.path.exists(movies_path) or not os.path.exists(ratings_path):
            raise FileNotFoundError(f"MovieLens data files not found in {self.data_dir}. Run download_data.py first.")

        self.movies_df = pd.read_csv(movies_path)
        self.ratings_df = pd.read_csv(ratings_path)
        self.tags_df = pd.read_csv(tags_path) if os.path.exists(tags_path) else pd.DataFrame(columns=['userId', 'movieId', 'tag'])
        self.links_df = pd.read_csv(links_path) if os.path.exists(links_path) else pd.DataFrame(columns=['movieId', 'imdbId', 'tmdbId'])

        return self.movies_df, self.ratings_df, self.tags_df, self.links_df

    def preprocess_movies(self) -> pd.DataFrame:
        """Cleans movies, parses release year, aggregates tags, and computes IMDB weighted ratings."""
        if self.movies_df is None:
            self.load_raw_data()

        df = self.movies_df.copy()
        df = df.drop_duplicates(subset=['movieId'])
        df = df.dropna(subset=['movieId', 'title'])

        # Parse Clean Title and Year
        title_year_pairs = [extract_year(t) for t in df['title']]
        df['clean_title'] = [p[0] for p in title_year_pairs]
        df['year'] = [p[1] for p in title_year_pairs]

        # Clean Genres: Replace '(no genres listed)' with ''
        df['genres_clean'] = df['genres'].apply(
            lambda g: "" if g == "(no genres listed)" or pd.isna(g) else g.replace("|", " ")
        )
        df['genre_list'] = df['genres'].apply(
            lambda g: [] if g == "(no genres listed)" or pd.isna(g) else [x.strip() for x in g.split("|")]
        )

        # Aggregate user tags per movie
        if not self.tags_df.empty:
            clean_tags = self.tags_df.dropna(subset=['tag']).copy()
            clean_tags['tag'] = clean_tags['tag'].astype(str).str.lower().str.strip()
            tags_agg = clean_tags.groupby('movieId')['tag'].apply(lambda t: " ".join(t.unique())).reset_index()
            df = df.merge(tags_agg, on='movieId', how='left')
            df['tag'] = df['tag'].fillna('')
        else:
            df['tag'] = ''

        # Compute rating metrics (count, mean) from ratings_df
        rating_stats = self.ratings_df.groupby('movieId').agg(
            rating_count=('rating', 'count'),
            avg_rating=('rating', 'mean')
        ).reset_index()
        df = df.merge(rating_stats, on='movieId', how='left')
        df['rating_count'] = df['rating_count'].fillna(0).astype(int)
        df['avg_rating'] = df['avg_rating'].fillna(0.0).round(2)

        # Compute IMDB Weighted Rating (WR)
        # WR = (v / (v + m)) * R + (m / (v + m)) * C
        # v = rating_count, R = avg_rating, C = global mean rating, m = threshold min votes
        C = self.ratings_df['rating'].mean()
        m = 10  # Minimum 10 ratings to qualify for weighted score
        df['weighted_rating'] = df.apply(
            lambda row: round((row['rating_count'] / (row['rating_count'] + m) * row['avg_rating']) +
                              (m / (row['rating_count'] + m) * C), 2)
            if row['rating_count'] > 0 else 0.0, axis=1
        )

        # Metadata soup for TF-IDF: clean_title repeated + genres + tags
        df['soup'] = (df['clean_title'] + " " + df['genres_clean'] + " " + df['tag']).str.lower().str.strip()

        self.processed_movies_df = df
        return df

    def get_user_movie_matrix(self, min_movie_ratings: int = 5) -> pd.DataFrame:
        """Constructs a user-movie interaction matrix for collaborative filtering."""
        if self.ratings_df is None:
            self.load_raw_data()

        # Filter movies with at least min_movie_ratings to keep matrix manageable and reduce noise
        valid_movies = self.ratings_df['movieId'].value_counts()
        valid_movies = valid_movies[valid_movies >= min_movie_ratings].index

        filtered_ratings = self.ratings_df[self.ratings_df['movieId'].isin(valid_movies)]
        matrix = filtered_ratings.pivot_table(index='userId', columns='movieId', values='rating').fillna(0)
        self.user_movie_matrix = matrix
        return matrix

    def get_all_genres(self) -> List[str]:
        """Extracts unique genres from the dataset."""
        if self.processed_movies_df is None:
            self.preprocess_movies()
        genres = set()
        for g_list in self.processed_movies_df['genre_list']:
            genres.update(g_list)
        return sorted([g for g in genres if g and g != "(no genres listed)"])
