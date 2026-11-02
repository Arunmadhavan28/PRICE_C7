# 👠 Team 2: The Sassy Stylist Bot (Conversational AI)

## 👥 Team Information
- **Track**: Conversational AI & Grounded Commerce
- **Application Name**: The Sassy Stylist Bot ("Vivian")
- **Team Members**:
  - Member 1: [Full Name (@github_handle)]
  - Member 2: [Full Name (@github_handle)]
  - Member 3: [Full Name (@github_handle)]

---

## 🎯 The Core Problem Solved
E-commerce shoppers abandon their shopping carts at staggering rates because conventional search bars cannot interpret nuanced, occasion-based queries (e.g., *"What should I wear to a windy beach wedding where my ex will be?"*). Standard keyword search fails on vibes.

**The Solution**: An opinionated, fiercely witty AI stylist bot named **Vivian**. Vivian interprets complex occasion prompts, critiques fashion dilemmas with playful sarcasm, and strictly recommends curated outfits from an authentic 50-item boutique catalog without hallucination.

## 🛍️ Target End Customer
- **Primary**: Online Shoppers (B2C) browsing fashion e-commerce storefronts looking for curated outfit inspiration.
- **Secondary**: Fashion boutiques seeking to boost average cart size and engagement through conversational discovery.

---

## 📊 Technical & Data Requirements
1. **Data**: `data/catalog_50.json` containing 50 items with:
   - `Product_Name`
   - `Category` (Dresses, Tops, Outerwear, Footwear, Bottoms, Accessories)
   - `Price` (USD)
   - `Vibe_Tags` (Occasion keywords: beach wedding, cocktail, rave, quiet luxury)
   - `Image_URL` (High-resolution fashion imagery)
   - `Description`
2. **Logic (`stylist_engine.py`)**:
   - `load_catalog(filepath)`
   - `search_catalog_by_vibe(query, catalog, top_k)`
   - `get_sassy_stylist_response(user_query, chat_history, catalog, api_key)`
   - `recommend_outfit(user_query, catalog, persona_system_prompt)`
   - Google Gemini 1.5 Flash Free Tier integration (`google-genai`), backed by a deterministic sassy offline engine.
3. **UI / Chat Interface (`app.py`)**:
   - Streamlit conversational chat with `st.chat_message` and `st.chat_input`.
   - Rich product cards below messages featuring photos, prices, tags, and "Add to Bag".
   - Sidebar with API key configuration and clickable quick-prompt pills.

---

## 🤖 Vibe-Coding Execution Strategy & Prompt Log
*Students used the following curated AI prompts to build this bot:*

### Prompt 1: 50-Item Grounded Fashion Catalog Generation
> *"Generate a JSON array of 50 trendy fashion products for an indie boutique. Each object must have id, Product_Name, Category, Price, Vibe_Tags (list of 3-5 occasion keywords like 'beach wedding', 'streetwear', 'resort'), Image_URL (Unsplash photo links), and Description."*

### Prompt 2: Strict Sassy Persona System Prompt
> *"Write a system prompt for an AI fashion assistant named Vivian. Vivian is hilarious, stylish, brutally honest, and uses sassy modern fashion slang (honey, runway-ready, fashion crime). Add a strict grounding rule: She is ONLY allowed to recommend items explicitly present in the provided catalog context."*

### Prompt 3: Streamlit Conversational Chat Interface
> *"Write a Streamlit app that implements a chat interface using st.chat_message. When a user submits an occasion query, pass the matched catalog items into the prompt, display Vivian's witty advice, and render visual product cards beneath the message with photos and prices."*

---

## 🔑 Google Gemini API Setup (100% Free)
1. Go to **[Google AI Studio](https://aistudio.google.com/)** and sign in with your Google account.
2. Click **Get API key** -> **Create API key**.
3. Create a `.env` file from `.env.example`:
   ```bash
   cp ../../.env.example .env
   ```
4. Add your key: `GEMINI_API_KEY=your_key_here`.
*(Note: If no API key is provided, the bot uses its built-in offline Sassy Engine seamlessly!)*

---

## 🚀 How to Run Locally

```bash
# 1. Activate your virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit application
streamlit run app.py
```

## 🧪 How to Run Automated Unit Tests

```bash
# Run pytest for Team 2
pytest tests/test_team02.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 2
```

## 🏆 Evaluation Rubric (100 Points -> 25 Marks)
- **Architecture (20 pts)**: Directory structure, `app.py`, `stylist_engine.py`, clean requirements.
- **Logic & Unit Tests (30 pts)**: Sassy persona, catalog grounding (zero hallucination), test suite passes.
- **Interactive UI (20 pts)**: `st.chat_message`, `st.chat_input`, responsive product cards with images.
- **Data Quality (15 pts)**: Full 50-item catalog with all required JSON attributes.
- **Documentation (15 pts)**: Complete prompt log, customer definition, run instructions.
