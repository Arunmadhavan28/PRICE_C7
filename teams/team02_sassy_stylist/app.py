"""
Streamlit Chat Application for Team 2: The Sassy Stylist Bot.
Conversational fashion styling powered by Gemini API / Offline Sassy Engine.
"""

import os
from pathlib import Path
import streamlit as st
from stylist_engine import load_catalog, get_sassy_stylist_response

st.set_page_config(
    page_title="Vivian | The Sassy Stylist Bot",
    page_icon="👠",
    layout="wide"
)

# Custom Styling for Stylist Chat
st.markdown("""
<style>
    .chat-badge {
        background-color: #ff3366;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75em;
        font-weight: bold;
    }
    .product-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Load catalog
catalog_path = Path(__file__).parent / "data" / "catalog_50.json"
catalog = load_catalog(str(catalog_path))

# Sidebar Settings
st.sidebar.title("👠 Stylist Studio")
st.sidebar.caption("Grounded Conversational Commerce with Persona Guidance")

st.sidebar.markdown(f"**Catalog Inventory**: `{len(catalog)} active pieces`")

api_key_input = st.sidebar.text_input(
    "Google Gemini API Key (Free)",
    value=os.getenv("GEMINI_API_KEY", ""),
    type="password",
    help="Get a 100% free Gemini API key in 30 seconds at https://aistudio.google.com/"
)

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Quick Vibe Prompts")
quick_prompts = [
    "What to wear to a beach wedding in Amalfi?",
    "Late-night underground rave in Berlin",
    "First date at an overpriced sushi bar",
    "Casual Friday at a snobby design agency"
]

for qp in quick_prompts:
    if st.sidebar.button(qp, use_container_width=True):
        st.session_state["pending_prompt"] = qp

st.title("👠 Meet Vivian: The Sassy Stylist Bot")
st.caption("Never commit a fashion crime again. Ask for occasion-based styling advice tailored to our exclusive catalog.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Darling, thank heaven you're here. Let's fix your wardrobe before anyone important sees you. Tell me the occasion or vibe you're trying to pull off!",
            "recommendations": []
        }
    ]

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        recs = msg.get("recommendations", [])
        if recs:
            st.markdown("#### ✨ Vivian's Curated Outfit Selection:")
            cols = st.columns(len(recs))
            for i, item in enumerate(recs):
                with cols[i]:
                    img_url = item.get("Image_URL", "https://via.placeholder.com/300")
                    st.image(img_url, use_container_width=True)
                    st.markdown(f"**{item['Product_Name']}**")
                    st.markdown(f"`${item['Price']:.2f}` | *{item['Category']}*")
                    tags_str = " ".join([f"`#{t}`" for t in item.get("Vibe_Tags", [])[:2]])
                    st.markdown(tags_str)
                    st.button(f"Add to Bag 🛍️", key=f"btn_{msg['content'][:10]}_{i}")

# Handle prompt input
prompt = st.chat_input("Tell Vivian what you need an outfit for...")

# Check if sidebar button was clicked
if "pending_prompt" in st.session_state and st.session_state["pending_prompt"]:
    prompt = st.session_state["pending_prompt"]
    st.session_state["pending_prompt"] = None

if prompt:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt, "recommendations": []})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Vivian is judging your options..."):
            response_text, rec_items = get_sassy_stylist_response(
                user_query=prompt,
                chat_history=st.session_state.messages,
                catalog=catalog,
                api_key=api_key_input
            )
            st.markdown(response_text)

            if rec_items:
                st.markdown("#### ✨ Vivian's Curated Outfit Selection:")
                cols = st.columns(len(rec_items))
                for i, item in enumerate(rec_items):
                    with cols[i]:
                        st.image(item["Image_URL"], use_container_width=True)
                        st.markdown(f"**{item['Product_Name']}**")
                        st.markdown(f"`${item['Price']:.2f}` | *{item['Category']}*")
                        tags_str = " ".join([f"`#{t}`" for t in item.get("Vibe_Tags", [])[:2]])
                        st.markdown(tags_str)

    # Save to session history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "recommendations": rec_items
    })
