"""
Stylist Engine for Team 2: The Sassy Stylist Bot.
Conversational AI persona grounded strictly in a 50-item fashion catalog.
Supports Google Gemini Free API with robust offline fallback.

Three-Layer Architecture:
- Layer 1: Data and Math functions (vibe similarity, budget metrics, catalog operations).
- Layer 2: Pytest unit test coverage.
- Layer 3: Interactive Streamlit and Plotly UI.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set

DEFAULT_CATALOG_PATH = Path(__file__).resolve().parent / "data" / "catalog_50.json"
FALLBACK_API_KEY = os.getenv("GEMINI_API_KEY", "")

SASSY_PERSONA_PROMPT = """You are "Vivian", a world-class, fiercely chic, and unapologetically sassy fashion stylist.
Your personality traits:
- Razor-sharp wit with high fashion standards. You have zero tolerance for boring, uninspired outfits.
- Playfully sarcastic, but you genuinely want the user to look breathtaking and stop traffic.
- Grounding constraint: You can ONLY recommend items from the provided 50-item catalog. Never hallucinate items outside the catalog!
- When recommending items, mention their exact Product_Name, Price, and explain with savage humor why it cures their fashion dilemma.
- Keep responses engaging, punchy, and formatted with markdown bullet points.
"""


# ---------------------------------------------------------------------------
# Layer 1: Data and Math Functions
# ---------------------------------------------------------------------------

def load_catalog(filepath: str = None) -> List[Dict[str, Any]]:
    """
    Loads and validates the 50-item product catalog.
    
    Inputs:
        filepath (str, optional): Custom path to catalog JSON file.
    Outputs:
        List[Dict[str, Any]]: List of 50 validated catalog item dictionaries.
    """
    path = Path(filepath) if filepath else DEFAULT_CATALOG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Catalog file not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    if not isinstance(catalog, list):
        raise ValueError("Catalog must be a JSON array of items.")
    return catalog


def calculate_vibe_similarity(query: str, item: Dict[str, Any]) -> float:
    """
    Mathematical similarity function calculating normalized relevance score [0.0, 1.0]
    between a search query and a fashion catalog item.
    
    Mathematical Formulation:
        Score = 5 * (term matches in Vibe_Tags)
              + 3 * (term matches in Product_Name)
              + 2 * (term matches in Category)
              + 1 * (term matches in Description)
        Normalized by a theoretical ceiling factor of 25.0, capped at 1.0.
    
    Inputs:
        query (str): User style/occasion prompt.
        item (Dict[str, Any]): Single catalog product dictionary.
    Outputs:
        float: Bounded similarity score between 0.0 and 1.0.
    """
    query_terms = set(query.lower().split())
    if not query_terms:
        return 0.0

    raw_score = 0.0
    tags = [t.lower() for t in item.get("Vibe_Tags", [])]
    name = item.get("Product_Name", "").lower()
    desc = item.get("Description", "").lower()
    category = item.get("Category", "").lower()

    for term in query_terms:
        tag_hits = sum(1 for tag in tags if term in tag)
        raw_score += 5.0 * tag_hits

        if term in name:
            raw_score += 3.0

        if term in category:
            raw_score += 2.0

        if term in desc:
            raw_score += 1.0

    norm_factor = max(len(query_terms) * 10.0, 10.0)
    normalized = min(raw_score / norm_factor, 1.0)
    return round(normalized, 4)


def calculate_outfit_budget_breakdown(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Mathematical aggregation of recommended outfit financial metrics.
    
    Inputs:
        items (List[Dict[str, Any]]): Curated items in outfit.
    Outputs:
        Dict[str, Any]:
            - total_cost (float): Sum of item prices.
            - average_price (float): Mean price per item.
            - item_count (int): Total number of items.
            - min_price (float): Minimum item price.
            - max_price (float): Maximum item price.
            - category_counts (Dict[str, int]): Distribution across categories.
    """
    if not items:
        return {
            "total_cost": 0.0,
            "average_price": 0.0,
            "item_count": 0,
            "min_price": 0.0,
            "max_price": 0.0,
            "category_counts": {}
        }

    prices = [float(item.get("Price", 0.0)) for item in items]
    total_cost = sum(prices)
    average_price = total_cost / len(prices)

    category_counts: Dict[str, int] = {}
    for item in items:
        cat = item.get("Category", "Uncategorized")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        "total_cost": round(total_cost, 2),
        "average_price": round(average_price, 2),
        "item_count": len(items),
        "min_price": round(min(prices), 2),
        "max_price": round(max(prices), 2),
        "category_counts": category_counts
    }


def filter_catalog_by_budget(catalog: List[Dict[str, Any]], max_price: float) -> List[Dict[str, Any]]:
    """
    Filters catalog items strictly under a maximum cost ceiling.
    
    Inputs:
        catalog (List[Dict[str, Any]]): Product catalog.
        max_price (float): Budget upper limit in USD.
    Outputs:
        List[Dict[str, Any]]: Filtered catalog items.
    """
    return [item for item in catalog if float(item.get("Price", 0.0)) <= max_price]


def search_catalog_by_vibe(query: str, catalog: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Ranks catalog items based on mathematical vibe similarity score.
    
    Inputs:
        query (str): User style or occasion prompt.
        catalog (List[Dict[str, Any]]): Full 50-item product catalog.
        top_k (int): Number of top recommendations to return.
    Outputs:
        List[Dict[str, Any]]: Shortlist of top matching catalog items.
    """
    scored = []
    for item in catalog:
        sim = calculate_vibe_similarity(query, item)
        scored.append((sim, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_items = [item for score, item in scored if score > 0][:top_k]

    if not top_items:
        fallback_indices = [0, 1, 4] if len(catalog) >= 5 else list(range(min(len(catalog), top_k)))
        top_items = [catalog[i] for i in fallback_indices]

    return top_items


def format_catalog_context(items: List[Dict[str, Any]]) -> str:
    """Formats shortlisted catalog items for the LLM context prompt."""
    lines = []
    for item in items:
        lines.append(
            f"- [{item['Product_Name']}] (Category: {item['Category']}, Price: ${item['Price']:.2f}): "
            f"Tags: {', '.join(item.get('Vibe_Tags', []))}. {item.get('Description', '')}"
        )
    return "\n".join(lines)


def call_gemini_api(prompt: str, api_key: str = None) -> str:
    """Calls Google Gemini API using free tier credentials with automatic failover."""
    key = api_key or os.getenv("GEMINI_API_KEY") or FALLBACK_API_KEY
    if not key:
        return ""

    try:
        from google import genai
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        if response and response.text:
            return response.text
    except Exception:
        pass

    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
    except Exception:
        pass

    return ""


def get_sassy_stylist_response(
    user_query: str,
    chat_history: List[Dict[str, str]] = None,
    catalog: List[Dict[str, Any]] = None,
    api_key: str = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Main entry point for generating stylist responses.
    
    Inputs:
        user_query (str): User request or occasion prompt.
        chat_history (List[Dict[str, str]], optional): Conversational thread.
        catalog (List[Dict[str, Any]], optional): Boutique catalog.
        api_key (str, optional): Gemini API Key.
    Returns:
        Tuple[str, List[Dict[str, Any]]]:
            (stylist_critique_text, list_of_recommended_catalog_items)
    """
    if catalog is None:
        catalog = load_catalog()

    matched_items = search_catalog_by_vibe(user_query, catalog, top_k=3)
    catalog_context = format_catalog_context(matched_items)

    system_instruction = f"""{SASSY_PERSONA_PROMPT}

AVAILABLE CATALOG ITEMS (You may ONLY recommend from these):
{catalog_context}

User's Request: "{user_query}"
Give your sassy, fashionable critique and recommendations:"""

    llm_output = call_gemini_api(system_instruction, api_key=api_key)

    if llm_output and len(llm_output.strip()) > 20:
        return llm_output, matched_items

    item1 = matched_items[0]
    item2 = matched_items[1] if len(matched_items) > 1 else matched_items[0]
    item3 = matched_items[2] if len(matched_items) > 2 else matched_items[0]

    budget_info = calculate_outfit_budget_breakdown(matched_items)

    fallback_response = (
        f"Darling, for '{user_query}', please tell me you weren't going to wear sweatpants. "
        f"I have pulled a breathtaking, traffic-stopping ensemble straight from our catalog:\n\n"
        f"1. **{item1['Product_Name']}** (${item1['Price']:.2f}) — {item1['Description']}\n"
        f"2. **{item2['Product_Name']}** (${item2['Price']:.2f}) — {item2['Description']}\n"
        f"3. **{item3['Product_Name']}** (${item3['Price']:.2f}) — {item3['Description']}\n\n"
        f"Total Outfit Investment: **${budget_info['total_cost']:.2f}** for {budget_info['item_count']} head-turning pieces."
    )
    return fallback_response, matched_items


def recommend_outfit(user_query: str, catalog: List[Dict[str, Any]] = None, persona_system_prompt: str = None) -> List[Dict[str, Any]]:
    """Helper function to return recommended items for evaluation tests."""
    if catalog is None:
        catalog = load_catalog()
    return search_catalog_by_vibe(user_query, catalog, top_k=3)
