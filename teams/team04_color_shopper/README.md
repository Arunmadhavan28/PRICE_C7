# 🎨 Team 4: Color-Palette Personal Shopper (Visual Commerce)

## 👥 Team Information
- **Track**: Visual Commerce & Computer Vision Color Matching
- **Application Name**: Color-Palette Personal Shopper
- **Team Members**:
  - Member 1: [Full Name (@github_handle)]
  - Member 2: [Full Name (@github_handle)]
  - Member 3: [Full Name (@github_handle)]

---

## 🎯 The Core Problem Solved
Customers struggle to manually search e-commerce catalogs for items that match the exact aesthetic, wall paint, or color scheme of their physical living room, bedroom, or existing wardrobe. Traditional text searches like *"terracotta chair"* return hundreds of misaligned shades.

**The Solution**: An intelligent visual commerce application that allows users to upload a photo of their physical space, extracts the dominant color palette using quantization, and performs Euclidean distance calculations across a catalog to rank and display the closest matching products.

## 🛍️ Target End Customer
- **Primary**: Home Decor, Furniture, Interior Design, or Apparel Shoppers (B2C).
- **Secondary**: Interior staging professionals and boutique decor curators.

---

## 📊 Technical & Data Requirements
1. **Data**: `data/catalog.csv` containing:
   - `Product_Name`
   - `Category` (Furniture, Lighting, Rugs, Decor)
   - `Hex_Color_Code` (e.g. `#C85A32`)
   - `RGB_R`, `RGB_G`, `RGB_B`
   - `Price` (USD)
   - `Image_URL`
2. **Logic (`color_engine.py`)**:
   - `extract_dominant_colors(image_source, num_colors)`: Uses PIL fast octree quantization to identify dominant color swatches and their area percentages.
   - `calculate_color_distance(rgb1, rgb2)`: Computes 3D Euclidean distance: $\sqrt{(R_1-R_2)^2 + (G_1-G_2)^2 + (B_1-B_2)^2}$.
   - `find_closest_products(target_hex, catalog_df, top_n)`: Ranks catalog items by color proximity and calculates match confidence scores (0-100%).
3. **UI / Dashboard (`app.py`)**:
   - Web interface featuring image uploader (`st.file_uploader`) and preset room photos.
   - Interactive palette display with hex codes and share percentages.
   - Responsive multi-column grid displaying matched products with photos, prices, color chips, and match scores.

---

## 🤖 Vibe-Coding Execution Strategy & Prompt Log
*Students used the following curated AI prompts to build this application:*

### Prompt 1: Color Quantization & Euclidean Proximity
> *"Write a Python script using Pillow and numpy to extract 3 dominant hex colors from an uploaded image. Then write a function that takes a target hex code and calculates the Euclidean distance against a pandas DataFrame containing product hex codes, returning the top 4 closest matches with a 0-100% confidence score."*

### Prompt 2: Streamlit Visual Commerce UI
> *"Create a Streamlit application with a side-by-side layout. On the left, allow uploading an image or selecting sample room photos, and display the extracted color swatches. On the right, display a 2-column card grid of the closest matching catalog products with product image, price, color dot, and match percentage."*

### Prompt 3: Unit Testing Color Math
> *"Write pytest tests that verify hex-to-RGB conversion, check that identical colors have distance 0, confirm max RGB distance is ~441.67, and ensure catalog items are sorted by closest distance."*

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
# Run pytest for Team 4
pytest tests/test_team04.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 4
```

## 🏆 Evaluation Rubric (100 Points -> 25 Marks)
- **Architecture (20 pts)**: Directory structure, `app.py`, `color_engine.py`, clean requirements.
- **Logic & Unit Tests (30 pts)**: Accurate RGB Euclidean distance, color extraction, test suite passes.
- **Interactive UI (20 pts)**: Image uploader, swatch palette, responsive product cards.
- **Data Quality (15 pts)**: Full catalog with valid Hex and RGB coordinates.
- **Documentation (15 pts)**: Complete prompt log, customer definition, run instructions.
