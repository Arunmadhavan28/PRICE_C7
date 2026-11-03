"""
Emotion & Sentiment Engine for Team 5: The Empathy Engine.
Classifies qualitative customer reviews into distinct emotions (Joy, Frustration, Confusion, Satisfaction, Neutral).
Supports zero-cost lexicon NLP engine and Google Gemini API.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd

DEFAULT_REVIEWS_PATH = Path(__file__).resolve().parent / "data" / "customer_reviews.txt"

EMOTION_KEYWORDS = {
    "Joy": [
        "thrilled", "amazing", "love", "stunning", "fantastic", "bespoke", "luxurious",
        "compliments", "lovely", "perfection", "superb", "exceeded", "dream"
    ],
    "Frustration": [
        "broke", "unacceptable", "delayed", "ignored", "cheap", "sandpaper", "twice",
        "ridiculous", "stain", "ruined", "wrong item", "terrible", "worst", "beyond frustrating",
        "zero stars", "furious", "unraveling", "disaster", "nightmare"
    ],
    "Confusion": [
        "puzzled", "makes no sense", "confusing", "broken link", "cannot figure out",
        "conflicting", "inconsistent", "why did", "why does", "misleading", "unclear",
        "sizing chart", "contradictory", "error"
    ],
    "Satisfaction": [
        "happy", "polite", "resolved", "fast delivery", "great experience", "intuitive",
        "decent", "true to size", "good quality", "recommend", "clean packaging"
    ]
}


def load_reviews(filepath: str = None) -> List[str]:
    """Loads text reviews from file."""
    path = Path(filepath) if filepath else DEFAULT_REVIEWS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Reviews file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        reviews = [line.strip() for line in f if line.strip()]
    return reviews


def analyze_review(review_text: str) -> Dict[str, Any]:
    """
    Classifies an individual review into an emotion and polarity score.
    Returns:
        dict with 'emotion', 'sentiment_score', 'matched_keywords', 'review_text'
    """
    clean_text = review_text.lower()

    scores = {"Joy": 0, "Frustration": 0, "Confusion": 0, "Satisfaction": 0}
    matched = []

    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in clean_text:
                scores[emotion] += 2
                matched.append(kw)

    # Determine dominant emotion
    max_emotion = max(scores, key=scores.get)
    if scores[max_emotion] == 0:
        dominant_emotion = "Neutral"
        polarity = 0.0
    else:
        dominant_emotion = max_emotion
        if dominant_emotion in ["Joy", "Satisfaction"]:
            polarity = min(1.0, 0.4 + (scores[dominant_emotion] * 0.15))
        elif dominant_emotion == "Frustration":
            polarity = max(-1.0, -0.5 - (scores[dominant_emotion] * 0.15))
        else:  # Confusion
            polarity = -0.2

    return {
        "review_text": review_text,
        "emotion": dominant_emotion,
        "polarity": round(polarity, 2),
        "matched_keywords": list(set(matched)),
        "scores": scores
    }


def compute_emotion_distribution(reviews_list: List[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Computes percentage and count distribution of emotions across all reviews.
    """
    results = [analyze_review(r) for r in reviews_list if r.strip()]
    if not results:
        return pd.DataFrame(), {}

    df = pd.DataFrame(results)
    counts = df["emotion"].value_counts().to_dict()
    total = len(df)

    dist_rows = []
    for emotion in ["Joy", "Frustration", "Confusion", "Satisfaction", "Neutral"]:
        cnt = counts.get(emotion, 0)
        pct = round((cnt / total) * 100.0, 1)
        dist_rows.append({"Emotion": emotion, "Count": cnt, "Percentage": pct})

    dist_df = pd.DataFrame(dist_rows)

    positive_share = dist_df[dist_df["Emotion"].isin(["Joy", "Satisfaction"])]["Percentage"].sum()
    friction_share = dist_df[dist_df["Emotion"].isin(["Frustration", "Confusion"])]["Percentage"].sum()

    metrics = {
        "total_reviews": total,
        "satisfaction_rate": round(positive_share, 1),
        "friction_index": round(friction_share, 1),
        "avg_polarity": round(float(df["polarity"].mean()), 2),
        "top_friction_emotion": "Frustration" if counts.get("Frustration", 0) >= counts.get("Confusion", 0) else "Confusion"
    }

    return dist_df, metrics


def analyze_bulk_reviews(reviews_list: List[str]) -> pd.DataFrame:
    """Helper returning a DataFrame of analyzed reviews with emotions and sentiment."""
    results = [analyze_review(r) for r in reviews_list if r.strip()]
    return pd.DataFrame(results)


def generate_gemini_cx_summary(metrics: Dict[str, Any], reviews_sample: List[str], api_key: str = None) -> str:
    """
    Uses Google Gemini API to generate an executive CX root-cause summary and actionable recommendations.
    Falls back gracefully if the API is unreachable or key is missing.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        return (
            "Gemini API Key not detected. To enable AI-generated executive summaries, "
            "set GEMINI_API_KEY in your .env file or input it in the sidebar."
        )

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = (
        "You are an expert Customer Experience (CX) Director in Retail.\n"
        f"Analyze the following customer review feedback data:\n"
        f"- Total Reviews Analyzed: {metrics.get('total_reviews')}\n"
        f"- Satisfaction Rate: {metrics.get('satisfaction_rate')}%\n"
        f"- Friction Index: {metrics.get('friction_index')}%\n"
        f"- Average Polarity: {metrics.get('avg_polarity')}\n"
        f"- Top Friction Emotion: {metrics.get('top_friction_emotion')}\n\n"
        f"Sample Reviews:\n" + "\n".join(f"- {r}" for r in reviews_sample[:10]) + "\n\n"
        "Please provide:\n"
        "1. Executive Sentiment Summary (2-3 sentences)\n"
        "2. Top 3 CX Friction Points & Root Causes\n"
        "3. High-Priority Actionable Recommendations for Retail Ops & Support\n"
        "Format cleanly in Markdown with bold titles and bullet points."
    )

    try:
        from google import genai
        client = genai.Client(api_key=key)
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text
    except Exception as e1:
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=key)
            model = legacy_genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e2:
            return f"Gemini API request note: {str(e1)} / {str(e2)}"
