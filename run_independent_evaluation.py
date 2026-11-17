"""
Independently execute the recommendation evaluation pipeline on MovieLens ratings.
Computes RMSE, MAE, Precision@10, Recall@10, and Catalog Coverage from scratch.
"""
import sys, os
sys.path.insert(0, r"c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System")

from src.evaluation import RecommendationEvaluator

evaluator = RecommendationEvaluator()
results = evaluator.run_full_evaluation(test_size=0.20, random_state=42)

print("\n" + "="*50)
print("INDEPENDENT EVALUATION RESULTS")
print("="*50)
for k, v in results.items():
    print(f"{k:25s}: {v}")
print("="*50)
