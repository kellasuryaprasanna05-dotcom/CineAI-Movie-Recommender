"""
Database management module for AI-Powered Movie Recommendation System.
Handles SQLite operations for user profiles, preferences, ratings, and history.
"""
import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "users.db")

def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DEFAULT_DB_PATH):
    """Initializes tables for users, preferences, ratings, and watchlists."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # User Preferences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id INTEGER PRIMARY KEY,
        favorite_genres TEXT,
        favorite_actors TEXT,
        favorite_languages TEXT,
        preferred_categories TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # User Ratings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        movie_id INTEGER NOT NULL,
        rating REAL NOT NULL CHECK(rating >= 0.5 AND rating <= 5.0),
        rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, movie_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # Recommendation History / Watchlist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        algorithm_used TEXT NOT NULL,
        movie_ids TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # Pre-seed a default demo user if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username) VALUES (?)", ("demo_cinephile",))
        demo_id = cursor.lastrowid
        cursor.execute("""
        INSERT INTO user_preferences (user_id, favorite_genres, favorite_actors, favorite_languages, preferred_categories)
        VALUES (?, ?, ?, ?, ?)
        """, (demo_id, "Action,Adventure,Sci-Fi", "Tom Hanks,Leonardo DiCaprio,Keanu Reeves", "English", "Blockbuster,Critically Acclaimed"))

    conn.commit()
    conn.close()

def get_or_create_user(username: str, db_path: str = DEFAULT_DB_PATH) -> int:
    """Returns user_id for username, creating if not existing."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username.strip(),))
    row = cursor.fetchone()
    if row:
        user_id = row['id']
    else:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username.strip(),))
        conn.commit()
        user_id = cursor.lastrowid
    conn.close()
    return user_id

def list_users(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, created_at FROM users ORDER BY username ASC")
    rows = cursor.fetchall()
    users = [dict(r) for r in rows]
    conn.close()
    return users

def get_user_preferences(user_id: int, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "favorite_genres": [g.strip() for g in (row["favorite_genres"] or "").split(",") if g.strip()],
            "favorite_actors": [a.strip() for a in (row["favorite_actors"] or "").split(",") if a.strip()],
            "favorite_languages": [l.strip() for l in (row["favorite_languages"] or "").split(",") if l.strip()],
            "preferred_categories": [c.strip() for c in (row["preferred_categories"] or "").split(",") if c.strip()],
        }
    return {
        "favorite_genres": [],
        "favorite_actors": [],
        "favorite_languages": [],
        "preferred_categories": []
    }

def save_user_preferences(
    user_id: int, 
    favorite_genres: List[str], 
    favorite_actors: List[str] = None, 
    favorite_languages: List[str] = None, 
    preferred_categories: List[str] = None, 
    db_path: str = DEFAULT_DB_PATH
):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    g_str = ",".join(favorite_genres) if favorite_genres else ""
    a_str = ",".join(favorite_actors) if favorite_actors else ""
    l_str = ",".join(favorite_languages) if favorite_languages else ""
    c_str = ",".join(preferred_categories) if preferred_categories else ""
    
    cursor.execute("""
    INSERT INTO user_preferences (user_id, favorite_genres, favorite_actors, favorite_languages, preferred_categories, updated_at)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(user_id) DO UPDATE SET
        favorite_genres = excluded.favorite_genres,
        favorite_actors = excluded.favorite_actors,
        favorite_languages = excluded.favorite_languages,
        preferred_categories = excluded.preferred_categories,
        updated_at = CURRENT_TIMESTAMP
    """, (user_id, g_str, a_str, l_str, c_str))
    
    conn.commit()
    conn.close()

def save_user_rating(user_id: int, movie_id: int, rating: float, db_path: str = DEFAULT_DB_PATH):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO user_ratings (user_id, movie_id, rating, rated_at)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(user_id, movie_id) DO UPDATE SET
        rating = excluded.rating,
        rated_at = CURRENT_TIMESTAMP
    """, (user_id, movie_id, float(rating)))
    conn.commit()
    conn.close()

def delete_user_rating(user_id: int, movie_id: int, db_path: str = DEFAULT_DB_PATH):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_ratings WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
    conn.commit()
    conn.close()

def get_user_ratings(user_id: int, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, rating, rated_at FROM user_ratings WHERE user_id = ? ORDER BY rated_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_user_ratings(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, movie_id, rating, rated_at FROM user_ratings")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_recommendation(user_id: int, algorithm: str, movie_ids: List[int], db_path: str = DEFAULT_DB_PATH):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    ids_str = ",".join(str(m) for m in movie_ids)
    cursor.execute("""
    INSERT INTO recommendation_history (user_id, algorithm_used, movie_ids)
    VALUES (?, ?, ?)
    """, (user_id, algorithm, ids_str))
    conn.commit()
    conn.close()

def get_user_history(user_id: int, limit: int = 5, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT algorithm_used, movie_ids, timestamp 
    FROM recommendation_history 
    WHERE user_id = ? 
    ORDER BY timestamp DESC 
    LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
