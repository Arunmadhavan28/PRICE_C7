"""
Evaluation Rubrics and Specifications for Retail AI Vibe-Coding Challenge.

Each team is graded out of 100 raw points, scaled to 25 final marks (Score / 4).
The 5 standard evaluation pillars:
1. Architecture & File Structure (20 pts)
2. Algorithmic Logic & Unit Tests (30 pts)
3. Interactive UI & Dashboard Readiness (20 pts)
4. Data Schema & Quality Conformance (15 pts)
5. Documentation & Vibe-Coding Prompt Log (15 pts)
"""

TEAM_SPECS = {
    1: {
        "folder": "team01_vibe_shift",
        "name": "The 'Vibe-Shift' Trend Forecaster",
        "category": "Demand Forecasting",
        "engine_file": "forecaster.py",
        "data_files": ["data/trend_sales_data.csv"],
        "required_columns": ["Date", "Item_Category", "Historical_Sales_Volume", "Social_Media_Trend_Score"],
        "min_rows": 30,
        "ui_elements": ["st.title", "plotly", "slider", "st.image", "st.columns"],
        "key_functions": ["forecast_demand", "load_trend_data"],
        "description": "Predicts upcoming demand surges by combining sales velocity with cultural signals."
    },
    2: {
        "folder": "team02_sassy_stylist",
        "name": "The Sassy Stylist Bot",
        "category": "Conversational AI",
        "engine_file": "stylist_engine.py",
        "data_files": ["data/catalog_50.json"],
        "required_json_keys": ["Product_Name", "Category", "Price", "Vibe_Tags", "Image_URL"],
        "min_items": 40,  # Target 50
        "ui_elements": ["st.chat_message", "st.chat_input", "st.image", "st.columns"],
        "key_functions": ["recommend_outfit", "load_catalog", "get_sassy_stylist_response"],
        "description": "Conversational stylist that recommends grounded items with an opinionated persona."
    },
    3: {
        "folder": "team03_dynamic_pricing",
        "name": "The 'Happy Hour' Dynamic Pricing Engine",
        "category": "Pricing Analytics",
        "engine_file": "pricing_engine.py",
        "data_files": ["data/inventory.json"],
        "required_json_keys": ["Item", "Base_Price", "Current_Stock"],
        "min_items": 5,
        "ui_elements": ["st.slider", "st.selectbox", "st.metric", "st.dataframe"],
        "key_functions": ["calculate_dynamic_price", "apply_pricing_rules", "load_inventory"],
        "description": "Real-time rule-based dynamic pricing adjusted for time, weather, and inventory."
    },
    4: {
        "folder": "team04_color_shopper",
        "name": "Color-Palette Personal Shopper",
        "category": "Visual Commerce",
        "engine_file": "color_engine.py",
        "data_files": ["data/catalog.csv"],
        "required_columns": ["Product_Name", "Hex_Color_Code", "Image_URL"],
        "min_rows": 10,
        "ui_elements": ["st.file_uploader", "st.image", "st.columns", "st.color_picker"],
        "key_functions": ["extract_dominant_colors", "find_closest_products", "calculate_color_distance"],
        "description": "Extracts dominant colors from uploaded images and matches products via Euclidean distance."
    },
    5: {
        "folder": "team05_empathy_engine",
        "name": "The Empathy Engine",
        "category": "Sentiment Analysis",
        "engine_file": "empathy_engine.py",
        "data_files": ["data/customer_reviews.txt"],
        "min_lines": 20,
        "ui_elements": ["st.text_area", "plotly", "st.metric", "st.columns"],
        "key_functions": ["analyze_review", "analyze_bulk_reviews", "compute_emotion_distribution"],
        "description": "Categorizes qualitative customer reviews into distinct emotions (Joy, Frustration, Confusion)."
    },
    6: {
        "folder": "team06_markdown_optimizer",
        "name": "The 'Drop Culture' Markdown Optimizer",
        "category": "Clearance Analytics",
        "engine_file": "optimizer.py",
        "data_files": ["data/inventory_aging.csv"],
        "required_columns": ["Item_SKU", "Days_on_Shelf", "Target_Sell_Through_Rate", "Actual_Sell_Through_Rate", "Cost_Basis"],
        "min_rows": 10,
        "ui_elements": ["st.dataframe", "st.button", "st.metric", "st.columns"],
        "key_functions": ["identify_at_risk_items", "calculate_recommended_discount", "project_profit_recovery"],
        "description": "Computes clearance discounts for lagging items while strictly protecting cost basis."
    },
    7: {
        "folder": "team07_ethical_auditor",
        "name": "Ethical AI Auditor for Retail",
        "category": "Ethics & Privacy",
        "engine_file": "auditor.py",
        "data_files": ["data/audit_dataset.csv"],
        "required_columns": ["Customer_ZipCode", "Recommended_Item_Price", "Opt_in_Status"],
        "min_rows": 25,
        "ui_elements": ["st.warning", "plotly", "st.metric", "st.dataframe"],
        "key_functions": ["audit_privacy_breaches", "audit_bias_correlation", "generate_compliance_report"],
        "description": "Red-teaming auditor checking demographic pricing bias and opt-in privacy violations."
    },
    8: {
        "folder": "team08_tryon_analytics",
        "name": "The Virtual Try-On Feedback Loop",
        "category": "AR/VR Analytics",
        "engine_file": "funnel_engine.py",
        "data_files": ["data/session_logs.csv"],
        "required_columns": ["Session_ID", "AR_TryOn_Used", "Time_in_AR", "Purchase_Made"],
        "min_rows": 50,
        "ui_elements": ["plotly", "st.metric", "st.columns", "st.dataframe"],
        "key_functions": ["calculate_funnel_metrics", "calculate_conversion_lift", "segment_ar_vs_non_ar"],
        "description": "Funnel analysis measuring conversion lift and business impact of virtual try-on."
    },
    9: {
        "folder": "team09_artisan_stock",
        "name": "The Artisan Safety-Stock Planner",
        "category": "Inventory Optimization",
        "engine_file": "stock_engine.py",
        "data_files": ["data/artisan_materials.csv"],
        "required_columns": ["Material_Name", "Current_Level", "Lead_Time_Days", "Daily_Burn_Rate", "Upcoming_Events"],
        "min_rows": 8,
        "ui_elements": ["st.progress", "st.button", "st.columns", "st.download_button"],
        "key_functions": ["calculate_safety_stock", "calculate_runway_days", "generate_purchase_order"],
        "description": "Kanban inventory planner with runway alerts and automated purchase order generation."
    }
}
