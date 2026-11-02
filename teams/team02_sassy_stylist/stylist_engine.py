"""
Stylist Engine for Team 2: The Sassy Stylist Bot.
Conversational AI persona grounded strictly in a 50-item fashion catalog.
Supports Google Gemini Free API with robust offline fallback.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

DEFAULT_CATALOG_PATH = Path(__file__).resolve().parent / "data" / "catalog_50.json"

SASSY_PERSONA_PROMPT = """You are "Vivian", a world-class, fiercely chic, and unapologetically sassy fashion stylist.
Your personality traits:
- Razor-sharp wit with high fashion standards. You have zero tolerance for boring, uninspired outfits.
- Playfully sarcastic, but you genuinely want the user to look breathtaking and stop traffic.
- Grounding constraint: You can ONLY recommend items from the provided 50-item catalog. Never hallucinate items outside the catalog!
- When recommending items, mention their exact Product_Name, Price, and explain with savage humor why it cures their fashion dilemma.
- Keep responses engaging, punchy, and formatted with markdown bullet points.
"""


def load_catalog(filepath: str = None) -> List[Dict[str, Any]]:
    """Loads and validates the 50-item product catalog."""
    path = Path(filepath) if filepath else DEFAULT_CATALOG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Catalog file not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    if not isinstance(catalog, list):
        raise ValueError("Catalog must be a JSON array of items.")
    return catalog


def search_catalog_by_vibe(query: str, catalog: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Ranks catalog items based on keyword/vibe overlap with the user query.
    Extracts matches across Vibe_Tags, Product_Name, Category, and Description.
    """
    query_terms = set(query.lower().split())
    scored_items = []

    for item in catalog:
        score = 0
        tags = [t.lower() for t in item.get("Vibe_Tags", [])]
        name = item.get("Product_Name", "").lower()
        desc = item.get("Description", "").lower()
        category = item.get("Category", "").lower()

        # Score tag matches heavily
        for term in query_terms:
            if any(term in tag for tag in tags):
                score += 5
            if term in name:
                score += 3
            if term in category:
                score += 2
            if term in desc:
                score += 1

        scored_items.append((score, item))

    # Sort descending by match score
    scored_items.sort(key=lambda x: x[0], reverse=True)
    top_items = [item for score, item in scored_items if score > 0][:top_k]

    # If no specific match found, fallback to diverse featured pieces
    if not top_items:
        top_items = [catalog[0], catalog[1], catalog[4]]

    return top_items


def format_catalog_context(items: List[Dict[str, Any]]) -> str:
    """Formats shortlisted catalog items for the LLM context."""
    lines = []
    for item in items:
        lines.append(
            f"- [{item['Product_Name']}] (Category: {item['Category']}, Price: ${item['Price']}): "
            f"Tags: {', '.join(item.get('Vibe_Tags', []))}. {item.get('Description', '')}"
        )
    return "\n".join(lines)


def call_gemini_api(prompt: str, api_key: str = None) -> str:
    """Calls Google Gemini API using free tier."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        return ""

    # Attempt 1: Modern google.genai SDK
    try:
        from google import genai
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception:
        pass

    # Attempt 2: google.generativeai legacy SDK
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
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
    Returns:
        (stylist_message_text, list_of_recommended_catalog_items)
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

    # Deterministic Sassy Fallback (Zero-cost / Offline mode)
    item1 = matched_items[0]
    item2 = matched_items[1] if len(matched_items) > 1 else matched_items[0]
    item3 = matched_items[2] if len(matched_items) > 2 else matched_items[0]

    fallback_response = (
        f"Oh honey, thank goodness you came to me before stepping out looking like a retail clearance rack accident! 💅✨\n\n"
        f"For **'{user_query}'**, we are serving pure luxury, not tragic confusion. Here is the exact look you are going to wear, and no, you don't get to argue:\n\n"
        f"1. **{item1['Product_Name']}** (${item1['Price']:.2f}) — *{item1['Description']}* Why? Because it immediately commands respect and screams taste.\n"
        f"2. **{item2['Product_Name']}** (${item2['Price']:.2f}) — *{item2['Description']}* Pair this immediately to elevate your silhouette from 'amateur' to 'runway-ready'.\n"
        f"3. **{item3['Product_Name']}** (${item3['Price']:.2f}) — Finish the vibe with this. Without it, you're merely dressed; with it, you are an event."
    )
    return fallback_response, matched_items


def recommend_outfit(user_query: str, catalog: List[Dict[str, Any]] = None, persona_system_prompt: str = None) -> List[Dict[str, Any]]:
    """Helper function to return recommended items for evaluation tests."""
    if catalog is None:
        catalog = load_catalog()
    return search_catalog_by_vibe(user_query, catalog, top_k=3)
