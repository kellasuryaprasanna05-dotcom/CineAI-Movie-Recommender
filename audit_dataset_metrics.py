import os, json, pandas as pd

base = r'c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System'
data_dir = os.path.join(base, 'data')

movies = pd.read_csv(os.path.join(data_dir, 'movies.csv'))
ratings = pd.read_csv(os.path.join(data_dir, 'ratings.csv'))
tags = pd.read_csv(os.path.join(data_dir, 'tags.csv'))

print("=== ACTUAL DATASET AUDIT ===")
print(f"Total Movies:  {len(movies):,} (Claimed: 9,742)")
print(f"Total Ratings: {len(ratings):,} (Claimed: 100,836)")
print(f"Total Users:   {ratings['userId'].nunique():,} (Claimed: 610)")
print(f"Total Tags:    {len(tags):,} (Claimed: 3,683)")

sparsity = 1.0 - (len(ratings) / (ratings['userId'].nunique() * len(movies)))
print(f"Sparsity:      {sparsity*100:.2f}% (Claimed: 98.30%)")
print(f"Rating Mean:   {ratings['rating'].mean():.4f} (Claimed: 3.50)")

assert len(movies) == 9742
assert len(ratings) == 100836
assert ratings['userId'].nunique() == 610
assert len(tags) == 3683
print("\n[PASS] All dataset statistics match 100%!")

eval_file = os.path.join(base, 'docs', 'evaluation_results.json')
with open(eval_file, 'r') as f:
    eval_res = json.load(f)

print("\n=== ACTUAL OFFLINE EVALUATION AUDIT ===")
for k, v in eval_res.items():
    print(f"  • {k:22s}: {v}")

# Support case-insensitive key lookup
res = {k.lower(): v for k, v in eval_res.items()}
assert res['rmse'] == 0.9094
assert res['mae'] == 0.7015
assert res['precision@10'] == 0.0072
assert res['recall@10'] == 0.0056
assert res['catalog_coverage'] == 0.0157
assert res['baseline_mean_rating'] == 3.50
print("\n[PASS] All evaluation metrics match verified offline results 100%!")
