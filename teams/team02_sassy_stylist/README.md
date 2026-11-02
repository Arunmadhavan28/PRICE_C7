# Team 2: Stylist Assistant (Conversational AI)

## Team Information
- Track: Conversational AI and Grounded Commerce
- Application Name: Stylist Assistant
- Team Members:
  - Member 1: [Full Name (@github_handle)]
  - Member 2: [Full Name (@github_handle)]
  - Member 3: [Full Name (@github_handle)]

---

## The Core Problem Solved
E-commerce shoppers abandon their shopping carts at significant rates because conventional search bars cannot interpret nuanced, occasion-based queries (e.g., "what to wear to a beach wedding"). Standard keyword search fails on context and occasion.

The Solution: A conversational styling assistant that interprets occasion prompts and recommends curated outfits strictly from an authentic 50-item boutique catalog without hallucination.

## Target End Customer
- Primary: Online Shoppers (B2C) browsing fashion e-commerce storefronts looking for outfit inspiration.
- Secondary: Fashion boutiques seeking to boost average cart size and engagement through conversational discovery.

---

## Technical and Data Requirements
1. Data: data/catalog_50.json containing 50 items with:
   - Product_Name
   - Category (Dresses, Tops, Outerwear, Footwear, Bottoms, Accessories)
   - Price (USD)
   - Vibe_Tags (Occasion keywords: beach wedding, cocktail, formal, casual)
   - Image_URL
   - Description
2. Logic (stylist_engine.py):
   - load_catalog(filepath)
   - search_catalog_by_vibe(query, catalog, top_k)
   - get_sassy_stylist_response(user_query, chat_history, catalog, api_key)
   - recommend_outfit(user_query, catalog, persona_system_prompt)
   - Google Gemini 1.5 Flash Free Tier integration (google-genai), backed by a deterministic offline engine.
3. UI / Chat Interface (app.py):
   - Streamlit conversational chat with st.chat_message and st.chat_input.
   - Product cards below messages featuring photos, prices, tags, and action buttons.
   - Sidebar with API key configuration and prompt selectors.

---

## Execution Strategy and Prompt Log

### Prompt 1: Grounded Fashion Catalog Generation
> "Generate a JSON array of 50 fashion products for a boutique. Each object must have id, Product_Name, Category, Price, Vibe_Tags (list of 3-5 occasion keywords like 'beach wedding', 'smart casual', 'resort'), Image_URL (Unsplash photo links), and Description."

### Prompt 2: Grounded Assistant System Prompt
> "Write a system prompt for an AI fashion assistant. Add a strict grounding rule: The assistant is ONLY allowed to recommend items explicitly present in the provided catalog context, citing exact product names and prices."

### Prompt 3: Streamlit Conversational Chat Interface
> "Write a Streamlit app that implements a chat interface using st.chat_message. When a user submits an occasion query, pass the matched catalog items into the prompt, display recommendations, and render visual product cards beneath the message with photos and prices."

---

## Google Gemini API Setup (Free Tier)
1. Go to Google AI Studio (https://aistudio.google.com/) and sign in.
2. Generate an API key.
3. Copy .env.example to .env:
   ```bash
   cp ../../.env.example .env
   ```
4. Set: GEMINI_API_KEY=your_key_here.
(Note: If no API key is provided, the assistant uses its built-in offline engine automatically.)

---

## How to Run Locally

```bash
# 1. Activate your virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit application
streamlit run app.py
```

## How to Run Automated Unit Tests

```bash
# Run pytest for Team 2
pytest tests/test_team02.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 2
```

## Evaluation Rubric (100 Points to 25 Marks)
- Architecture (20 pts): Directory structure, app.py, stylist_engine.py, clean requirements.
- Logic and Unit Tests (30 pts): Grounded recommendations (zero hallucination), test suite passes.
- Interactive UI (20 pts): st.chat_message, st.chat_input, responsive product cards with images.
- Data Quality (15 pts): Full 50-item catalog with all required JSON attributes.
- Documentation (15 pts): Complete prompt log, customer definition, run instructions.
