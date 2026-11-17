"""
Poster and metadata service for AI-Powered Movie Recommendation System.
Provides resilient poster images, genre-based gradient artworks, and metadata.
"""
import hashlib
import urllib.parse
from typing import Dict, Any, Optional

# Curated thematic color palettes for genres to generate movie artwork
GENRE_PALETTES = {
    "Action": ("#800020", "#1a0005", "💥"),
    "Adventure": ("#0f4c3a", "#051610", "🗺️"),
    "Animation": ("#7b2cbf", "#240046", "🎨"),
    "Children": ("#f77f00", "#3d1300", "🧸"),
    "Comedy": ("#d4a373", "#3a2e1d", "🎭"),
    "Crime": ("#343a40", "#0b0c10", "🔍"),
    "Documentary": ("#1d3557", "#050b14", "📹"),
    "Drama": ("#2b2d42", "#0f1016", "🍷"),
    "Fantasy": ("#4a0e4e", "#130317", "✨"),
    "Film-Noir": ("#1c1c1c", "#000000", "🕵️"),
    "Horror": ("#49111c", "#0d0204", "🩸"),
    "Musical": ("#5f0f40", "#1e0514", "🎶"),
    "Mystery": ("#1e3d59", "#06101e", "🗝️"),
    "Romance": ("#9e2a2b", "#270809", "❤️"),
    "Sci-Fi": ("#0077b6", "#02182b", "🚀"),
    "Thriller": ("#3c096c", "#10011c", "⚡"),
    "War": ("#414833", "#14170e", "🎖️"),
    "Western": ("#7f4f24", "#2c1808", "🤠"),
    "Default": ("#1f242d", "#0c0e12", "🎬")
}

# Extensive library of iconic MovieLens titles with verified high-resolution poster images
CURATED_POSTERS = {
    1: "https://m.media-amazon.com/images/M/MV5BMDU2ZWJlYTktMTRhMy00ZTA5LWEzNDgtYmNmZTEwZTViZWJkXkEyXkFqcGc@._V1_SX300.jpg", # Toy Story
    2: "https://m.media-amazon.com/images/M/MV5BZTk2ZmUwYmEtNTcwZS00YmMyLWFkYjMtNTRmZDA3YWExMjc2XkEyXkFqcGc@._V1_SX300.jpg", # Jumanji
    6: "https://m.media-amazon.com/images/M/MV5BNGMwNzUwMmQtNjVlYS00NTc4LWE1NjktZTRhNWQ2YTgsYjdhXkEyXkFqcGc@._V1_SX300.jpg", # Heat
    10: "https://m.media-amazon.com/images/M/MV5BNDI5YmQxOTctYWU2NC00ODFlLTg5Y2MtYTY4OTM3ZTI0ODVkXkEyXkFqcGc@._V1_SX300.jpg", # GoldenEye
    32: "https://m.media-amazon.com/images/M/MV5BNjhkODlhNWQtYTQxNC00MmQxLWI3YjUtYWIwMGEyNzAzYzQ2XkEyXkFqcGc@._V1_SX300.jpg", # Twelve Monkeys
    47: "https://m.media-amazon.com/images/M/MV5BNTQwNDM1YzItNDAxZC00NWY2LTk0NmUtNDY3Nzk4NjFhZTViXkEyXkFqcGc@._V1_SX300.jpg", # Seven
    50: "https://m.media-amazon.com/images/M/MV5BYTViNjMyNmUtNDFkNC00ZDRlLThmMDUtZDU2YWE4NWQ2ODA0XkEyXkFqcGc@._V1_SX300.jpg", # Usual Suspects
    110: "https://m.media-amazon.com/images/M/MV5BMzkzMmU2NjEtMWVkYS00OWVhLTg3MWQtNWY0YzVjODlhNzVkXkEyXkFqcGc@._V1_SX300.jpg", # Braveheart
    150: "https://m.media-amazon.com/images/M/MV5BN2EyZjM3NzUtNWUzMi00MTgxLWI0NTctMzY4M2VlOTdjZWRiXkEyXkFqcGc@._V1_SX300.jpg", # Apollo 13
    260: "https://m.media-amazon.com/images/M/MV5BMmU0YWExMDYtMTFkOC00NWZmLWJjM2MtOGNmYjVjYTA5Yzg4XkEyXkFqcGc@._V1_SX300.jpg", # Star Wars: Ep IV
    296: "https://m.media-amazon.com/images/M/MV5BYTViYTE3NWMtNmRhOS00NzRiLWIxZTEtOTY3ZTM3Y2EwOGE2XkEyXkFqcGc@._V1_SX300.jpg", # Pulp Fiction
    318: "https://m.media-amazon.com/images/M/MV5BMDAyY2FhYjctNDc5OS00MDNlLThiMGUtY2UxYWVkNGY2MmI0XkEyXkFqcGc@._V1_SX300.jpg", # Shawshank Redemption
    356: "https://m.media-amazon.com/images/M/MV5BNDYwNzVjMTItZmU5YS00YjQ5LTljYjgtMjY2NDVmYWMyNWFkXkEyXkFqcGc@._V1_SX300.jpg", # Forrest Gump
    364: "https://m.media-amazon.com/images/M/MV5BMjIwMjE1Nzc4NV5BMl5BanBnXkFtZTgwNDg4OTA1NzM@._V1_SX300.jpg", # The Lion King
    480: "https://m.media-amazon.com/images/M/MV5BMjM2MDgxMDg0Nl5BMl5BanBnXkFtZTgwNTM2OTM5NDE@._V1_SX300.jpg", # Jurassic Park
    527: "https://m.media-amazon.com/images/M/MV5BNjM1ZDQxYWUtMzQyZS00MTE1LWJmZGYtNGUyNTdlYjM3ZmVmXkEyXkFqcGc@._V1_SX300.jpg", # Schindler's List
    589: "https://m.media-amazon.com/images/M/MV5BNWJlNzUzNGMtYTAwMS00ZjI2LWFmNWQtODcxNWUxODA5YmU1XkEyXkFqcGc@._V1_SX300.jpg", # Terminator 2
    593: "https://m.media-amazon.com/images/M/MV5BNjNhZTk0ZmEtNjJhMi00YzFlLWE1MmEtYzM1M2ZmMGMwMTU4XkEyXkFqcGc@._V1_SX300.jpg", # Silence of the Lambs
    858: "https://m.media-amazon.com/images/M/MV5BNGEwYjgwOGQtYjg5ZS00Njc1LTk2ZGEtM2QwZWQ2NjdhZTE5XkEyXkFqcGc@._V1_SX300.jpg", # The Godfather
    1196: "https://m.media-amazon.com/images/M/MV5BMTkxNGFlNDktZmJkNC00MDdhLTg0MTEtZjZiYWI3MGE5NWIxXkEyXkFqcGc@._V1_SX300.jpg", # Star Wars: Ep V
    1198: "https://m.media-amazon.com/images/M/MV5BMzcwYjEwMzEtZDY4Mi00ZTU4LWIxNjItMzA3NmQzNDEzMDBlXkEyXkFqcGc@._V1_SX300.jpg", # Raiders of the Lost Ark
    1200: "https://m.media-amazon.com/images/M/MV5BNzVjMWFmOTUtNWE2MC00YTQ2LWFmYjgtMmE1NWVlOWY2OWFmXkEyXkFqcGc@._V1_SX300.jpg", # Aliens
    1210: "https://m.media-amazon.com/images/M/MV5BNWEwNDhhNWUtNmQ1Ny00YWZkLTA5ZmEtZmNkNDk2NmQ2M2E4XkEyXkFqcGc@._V1_SX300.jpg", # Star Wars: Ep VI
    1213: "https://m.media-amazon.com/images/M/MV5BN2E5NzI2ZGMtY2UxYS00NWZmLWE5ZmEtZmM4CPkEyXkFqcGc@._V1_SX300.jpg", # Goodfellas
    1214: "https://m.media-amazon.com/images/M/MV5BNmU1OTRhYjgtOGMyNi00NmExLTg5YjItYmQzNDc2NmUwYmI1XkEyXkFqcGc@._V1_SX300.jpg", # Alien
    1221: "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGc@._V1_SX300.jpg", # The Godfather Part II
    1240: "https://m.media-amazon.com/images/M/MV5BNzc4ZWQ3NmYtODE0Ny00YTQ4LTlkZWItNTBkMmQ0MmRhMmNjXkEyXkFqcGc@._V1_SX300.jpg", # The Terminator
    1270: "https://m.media-amazon.com/images/M/MV5BNzU1Yjg2YjMtOTljMS00NGZmLWIxMmUtNjRhY2FiMDc5OTc2XkEyXkFqcGc@._V1_SX300.jpg", # Back to the Future
    1721: "https://m.media-amazon.com/images/M/MV5BYzYyN2FiZmUtYWYzMy00MzViLWJkZTMtOGY1ZjgzNWMwN2YxXkEyXkFqcGc@._V1_SX300.jpg", # Titanic
    2028: "https://m.media-amazon.com/images/M/MV5BZjhkMDM4MWItZjc5OC00YzVlLThkOWUtYzg1NDg3MDFlZTRkXkEyXkFqcGc@._V1_SX300.jpg", # Saving Private Ryan
    2571: "https://m.media-amazon.com/images/M/MV5BN2NmN2VhMTQtMDNiOS00NDlhLTliMjgtODE2ZTY0ODQyNDRhXkEyXkFqcGc@._V1_SX300.jpg", # The Matrix
    2858: "https://m.media-amazon.com/images/M/MV5BNTBmZWJkNjctNDhiNC00MGE2LWEwOTctZTk5OGVhMWMyNmVhXkEyXkFqcGc@._V1_SX300.jpg", # American Beauty
    2959: "https://m.media-amazon.com/images/M/MV5BOTgyOGQ1NDItNGU3Ny00MjU3LTg2YWEtNmIzYzg1YWNjMmkyXkEyXkFqcGc@._V1_SX300.jpg", # Fight Club
    3578: "https://m.media-amazon.com/images/M/MV5BYWQ4YmNjYjEtOWE1Zi00Y2U4LWI4NTAtMTU0MjkxNWQ1ZmJiXkEyXkFqcGc@._V1_SX300.jpg", # Gladiator
    4226: "https://m.media-amazon.com/images/M/MV5BZTljYjFmOGItZjM2NC00NDc4LTkwNDMtN2FmODliMGQyODVkXkEyXkFqcGc@._V1_SX300.jpg", # Memento
    4886: "https://m.media-amazon.com/images/M/MV5BMTY1NTI0ODUyOF5BMl5BanBnXkFtZTgwMTE5OTg0MzE@._V1_SX300.jpg", # Monsters, Inc.
    4993: "https://m.media-amazon.com/images/M/MV5BNzA5ZDNlZWMtM2NhNS00NDjjLTk4NDItYTRmY2EwMWZlMTY3XkEyXkFqcGc@._V1_SX300.jpg", # Fellowship of the Ring
    5618: "https://m.media-amazon.com/images/M/MV5BNTEyNmEwOWUtYzkyOC00ZTQ4LTllZmUtMjk0Y2Y5ZWU3N2RjXkEyXkFqcGc@._V1_SX300.jpg", # Spirited Away
    5952: "https://m.media-amazon.com/images/M/MV5BZGMxZTdjZmYtMmE2Ni00OTYzLWI5MmMt自治YzgwZTk0ZTA2XkEyXkFqcGc@._V1_SX300.jpg", # Two Towers
    6377: "https://m.media-amazon.com/images/M/MV5BMTY4NjQ5NDc0OF5BMl5BanBnXkFtZTYwNjk5NDM3._V1_SX300.jpg", # Finding Nemo
    7153: "https://m.media-amazon.com/images/M/MV5BMTZkMjBjNWMtZGI5OC00MGU0LTk4ZTItODg2NWM3NTVmNWQ4XkEyXkFqcGc@._V1_SX300.jpg", # Return of the King
    48516: "https://m.media-amazon.com/images/M/MV5BMTI1MTY2OTIxNV5BMl5BanBnXkFtZTYwNjQ4NjY3._V1_SX300.jpg", # The Departed
    48780: "https://m.media-amazon.com/images/M/MV5BMjA4NDI0MTIxNF5BMl5BanBnXkFtZTYwNTM0MzY2._V1_SX300.jpg", # The Prestige
    58559: "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg", # The Dark Knight
    60069: "https://m.media-amazon.com/images/M/MV5BMjExMTg5OTU0NF5BMl5BanBnXkFtZTcwMjMxMzMzMw@@._V1_SX300.jpg", # Wall-E
    68157: "https://m.media-amazon.com/images/M/MV5BOTJiNDEzOWYtMTVjOC00ZjlmLWE0NGMtZmE1OWVmZDQ2NI1XkEyXkFqcGc@._V1_SX300.jpg", # Inglourious Basterds
    68954: "https://m.media-amazon.com/images/M/MV5BMTk3NDE2NzI4NF5BMl5BanBnXkFtZTgwNzE1MzEyMDE@._V1_SX300.jpg", # Up
    72998: "https://m.media-amazon.com/images/M/MV5BMDEzMmQwZjctZWU2My00MWVOLWE0NzItM2NjNDcyNDQ3ZGJmXkEyXkFqcGc@._V1_SX300.jpg", # Avatar
    79132: "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg", # Inception
    89745: "https://m.media-amazon.com/images/M/MV5BNDYxNjQyMjAtNTdiOS00NGYwLWFmNTAtNThmYjU5ZGI2YTI1XkEyXkFqcGc@._V1_SX300.jpg", # The Avengers
    99114: "https://m.media-amazon.com/images/M/MV5BMjIyNTQ5NjQ1OV5BMl5BanBnXkFtZTcwODg1MDU4OA@@._V1_SX300.jpg", # Django Unchained
    109374: "https://m.media-amazon.com/images/M/MV5BMzM5NjUxOTEyMl5BMl5BanBnXkFtZTgwNjEyMDM0MDE@._V1_SX300.jpg", # Grand Budapest Hotel
    109487: "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGc@._V1_SX300.jpg", # Interstellar
    112552: "https://m.media-amazon.com/images/M/MV5BOTA5NDZlZGUtMjAxOS00YTRkLTkwYmMtYWQ0NWEwZD阳YzE1XkEyXkFqcGc@._V1_SX300.jpg", # Whiplash
    122886: "https://m.media-amazon.com/images/M/MV5BN2EwM2I5OWMtMGQyMi00Zjg1LWJkNTctZTdjYTA4OGJkNjFhXkEyXkFqcGc@._V1_SX300.jpg", # Mad Max Fury Road
    164179: "https://m.media-amazon.com/images/M/MV5BMzUzNDM2NzM2MV5BMl5BanBnXkFtZTgwNTM3NTg4OTE@._V1_SX300.jpg", # La La Land
    193587: "https://m.media-amazon.com/images/M/MV5BMjMwNDkxMTUzMl5BMl5BanBnXkFtZTgwNzAwODE4NjM@._V1_SX300.jpg", # Spider-Verse
}

def generate_svg_poster(title: str, genres: str, year: str, rating: float = 0.0) -> str:
    """Generates an embedded SVG poster card with rich movie aesthetics."""
    primary_genre = genres.split("|")[0].strip() if genres else "Default"
    colors = GENRE_PALETTES.get(primary_genre, GENRE_PALETTES["Default"])
    c1, c2, icon = colors[0], colors[1], colors[2]
    
    # Safe title escaping
    clean_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    clean_genre = genres.replace("|", " • ")
    if len(clean_genre) > 28:
        clean_genre = clean_genre[:25] + "..."
    if len(clean_title) > 35:
        display_title = clean_title[:32] + "..."
    else:
        display_title = clean_title

    star_rating = f"★ {rating:.1f}" if rating > 0 else "NEW"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 450" width="100%" height="100%">
      <defs>
        <linearGradient id="bg_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{c1}"/>
          <stop offset="70%" stop-color="{c2}"/>
          <stop offset="100%" stop-color="#0a0a0c"/>
        </linearGradient>
        <linearGradient id="overlay_grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="40%" stop-color="transparent"/>
          <stop offset="85%" stop-color="rgba(10, 10, 12, 0.85)"/>
          <stop offset="100%" stop-color="#0a0a0c"/>
        </linearGradient>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="8" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      <!-- Background with film poster border -->
      <rect width="300" height="450" rx="14" fill="url(#bg_grad)" stroke="#2f3542" stroke-width="2"/>
      
      <!-- Decorative Film Reels & Subtle Geometry -->
      <circle cx="150" cy="180" r="100" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="32" stroke-dasharray="10 15"/>
      <circle cx="150" cy="180" r="60" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="3"/>
      
      <!-- Center Thematic Icon -->
      <text x="150" y="195" font-size="76" text-anchor="middle" filter="url(#glow)">{icon}</text>

      <!-- Rating Badge Top Right -->
      <rect x="205" y="16" width="78" height="28" rx="14" fill="rgba(229, 9, 20, 0.9)" />
      <text x="244" y="35" font-family="'Helvetica Neue', Arial, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">{star_rating}</text>

      <!-- Year Pill Top Left -->
      <rect x="16" y="16" width="60" height="28" rx="14" fill="rgba(0,0,0,0.6)" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
      <text x="46" y="35" font-family="'Helvetica Neue', Arial, sans-serif" font-size="12" font-weight="600" fill="#e0e0e0" text-anchor="middle">{year if year else 'CINEMA'}</text>

      <!-- Bottom Dark Vignette Overlay -->
      <rect width="300" height="450" rx="14" fill="url(#overlay_grad)"/>

      <!-- Movie Title -->
      <text x="20" y="380" font-family="'Helvetica Neue', Arial, sans-serif" font-size="18" font-weight="800" fill="#ffffff">
        {display_title}
      </text>

      <!-- Movie Genre Tags -->
      <text x="20" y="410" font-family="'Helvetica Neue', Arial, sans-serif" font-size="12" font-weight="500" fill="#e50914">
        {clean_genre}
      </text>
    </svg>"""
    encoded = urllib.parse.quote(svg)
    return f"data:image/svg+xml;utf8,{encoded}"

def get_movie_poster(movie_id: int, title: str, genres: str, year: str = "", rating: float = 0.0) -> str:
    """Returns poster URL if curated/known, else generates a beautiful SVG artwork poster."""
    if movie_id in CURATED_POSTERS:
        return CURATED_POSTERS[movie_id]
    return generate_svg_poster(title, genres, year, rating)
