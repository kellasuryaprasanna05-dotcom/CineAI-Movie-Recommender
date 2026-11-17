"""
Script to download and extract MovieLens latest-small dataset.
Dataset source: https://grouplens.org/datasets/movielens/latest/
Contains: movies.csv, ratings.csv, tags.csv, links.csv
"""
import os
import sys
import zipfile
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATASET_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
ZIP_PATH = os.path.join(DATA_DIR, "ml-latest-small.zip")

def download_and_extract():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Check if files already exist
    movies_path = os.path.join(DATA_DIR, "movies.csv")
    ratings_path = os.path.join(DATA_DIR, "ratings.csv")
    
    if os.path.exists(movies_path) and os.path.exists(ratings_path):
        print(f"MovieLens dataset files already present in {DATA_DIR}.")
        return

    print(f"Downloading MovieLens latest-small dataset from {DATASET_URL}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    # Try with verification first, fallback to verify=False if Windows certificates are missing
    try:
        response = requests.get(DATASET_URL, headers=headers, timeout=30)
    except requests.exceptions.SSLError:
        print("Retrying with unverified SSL...")
        response = requests.get(DATASET_URL, headers=headers, verify=False, timeout=30)
        
    response.raise_for_status()
    with open(ZIP_PATH, 'wb') as out_file:
        out_file.write(response.content)
        
    print(f"Extracting {ZIP_PATH}...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        for member in zip_ref.namelist():
            filename = os.path.basename(member)
            if filename:
                target_file = os.path.join(DATA_DIR, filename)
                with zip_ref.open(member) as source, open(target_file, "wb") as target:
                    target.write(source.read())
                    print(f"Extracted: {filename}")
                    
    # Clean up zip
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
        
    print("Dataset download and extraction complete!")

if __name__ == "__main__":
    download_and_extract()
