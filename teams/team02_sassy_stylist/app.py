"""
Streamlit Chat Application for Team 2: Stylist Assistant.
Conversational fashion styling powered by Gemini API / Offline Engine.
"""

import os
from pathlib import Path
import streamlit as st
from stylist_engine import load_catalog, get_sassy_stylist_response

st.set_page_config(
    page_title="Stylist Assistant | Retail AI",
    layout="wide"
)

# Custom Styling for Stylist Chat
st.markdown("""
<style>
    .chat-badge {
        background-color: #2563eb;
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
st.sidebar.title("Stylist Studio")
st.sidebar.caption("Grounded Conversational Commerce with Persona Guidance")

st.sidebar.markdown(f"**Catalog Inventory**: `{len(catalog)} active pieces`")

api_key_input = st.sidebar.text_input(
    "Google Gemini API Key (Free)",
    value=os.getenv("GEMINI_API_KEY", ""),
    type="password",
    help="Get a free Gemini API key at https://aistudio.google.com/"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Sample Prompts")
quick_prompts = [
    "What to wear to a beach wedding in Amalfi?",
    "Evening formal dinner in the city",
    "First date at a quiet bistro",
    "Casual Friday at a design studio"
]

for qp in quick_prompts:
    if st.sidebar.button(qp, use_container_width=True):
        st.session_state["pending_prompt"] = qp

st.title("Stylist Assistant")
st.caption("Ask for occasion-based styling advice tailored strictly to our local product catalog.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Welcome! Tell me the occasion or style you are looking for, and I will recommend curated items from our catalog.",
            "recommendations": []
        }
    ]

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        recs = msg.get("recommendations", [])
        if recs:
            st.markdown("#### Curated Outfit Selection:")
            cols = st.columns(len(recs))
            for i, item in enumerate(recs):
                with cols[i]:
                    img_url = item.get("Image_URL", "https://via.placeholder.com/300")
                    st.image(img_url, use_container_width=True)
                    st.markdown(f"**{item['Product_Name']}**")
                    st.markdown(f"`${item['Price']:.2f}` | *{item['Category']}*")
                    tags_str = " ".join([f"`#{t}`" for t in item.get("Vibe_Tags", [])[:2]])
                    st.markdown(tags_str)
                    st.button(f"Add to Bag", key=f"btn_{msg['content'][:10]}_{i}")

# Handle prompt input
prompt = st.chat_input("Describe the occasion or outfit requirements...")

if "pending_prompt" in st.session_state and st.session_state["pending_prompt"]:
    prompt = st.session_state["pending_prompt"]
    st.session_state["pending_prompt"] = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "recommendations": []})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Reviewing catalog options..."):
            response_text, rec_items = get_sassy_stylist_response(
                user_query=prompt,
                chat_history=st.session_state.messages,
                catalog=catalog,
                api_key=api_key_input
            )
            st.markdown(response_text)

            if rec_items:
                st.markdown("#### Curated Outfit Selection:")
                cols = st.columns(len(rec_items))
                for i, item in enumerate(rec_items):
                    with cols[i]:
                        st.image(item["Image_URL"], use_container_width=True)
                        st.markdown(f"**{item['Product_Name']}**")
                        st.markdown(f"`${item['Price']:.2f}` | *{item['Category']}*")
                        tags_str = " ".join([f"`#{t}`" for t in item.get("Vibe_Tags", [])[:2]])
                        st.markdown(tags_str)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "recommendations": rec_items
    })
