# -*- coding: utf-8 -*-
"""Skntone product recommendation system

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-c0ZvZ_r8Kxi3kXweLbQJbpOKd1DwhPr
"""
# SKNTONE Product Recommender App with Brand Styling + Images

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('vader_lexicon')

# -----------------------------
# Streamlit Styling (Brand Color)
# -----------------------------
SKNTONE_COLOR = "#000000"
st.set_page_config(page_title="Skntone Product Recommendation System", layout="centered")
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: black;
        }}
        h1, h2, h3, h4 {{
            color: {SKNTONE_COLOR};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Skntone Product Recommendation System")
st.markdown("Tell me your skin concerns and we’ll recommend the best product(s) for you.")

# -----------------------------
# Product Data + Image URLs
# -----------------------------
product_data = [
    {"product": "Ingrown Remedy", "concern": "ingrown hairs, razor bumps, redness, irritation", "key_ingredient": "Tea Tree Oil, Salicylic Acid", "product_type": "treatment", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3339.jpg?v=1678575718"},
    {"product": "Blemish Butter", "concern": "blemishes, dark marks, hyperpigmentation", "key_ingredient": "Alpha Arbutin, Shea Butter, Licorice Root, Papaya Seed", "product_type": "cream", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3329.jpg?v=1678576957"},
    {"product": "Bikini Area Mask", "concern": "blocked pores, blemishes, dark marks, hyperpigmentation, redness", "key_ingredient": "Bentonite Clay, Turmeric, Aloe Vera", "product_type": "mask", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3329.jpg?v=1678576957"},
    {"product": "Intimate Toner", "concern": "hyperpigmentation, blemishes, dark marks, texture irregularities, strawberry legs", "key_ingredient": "Glycolic Acid, Witch hazel, Aloe", "product_type": "toner", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3351.jpg?v=1678577474"},
    {"product": "Body Oil Spray", "concern": "dry skin, sensitive skin", "key_ingredient": "Jojoba Oil, Oat Oil, Soya Bean Oil", "product_type": "oil", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3364_db661095-455c-4c85-ad0f-e7515452b832.jpg?v=1678575843"},
    {"product": "Salt Body Scrub", "concern": "rough skin, dry skin", "key_ingredient": "Dead Sea Salt, Himalayan Salt, Almond Oil", "product_type": "scrub", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3357.jpg?v=1678575811"},
    {"product": "Intimate Wash", "concern": "unbalanced pH balance, intimate odour, menstrual cramps", "key_ingredient": "Aloe, Cranberry Extract, Lavender, Chamomile", "product_type": "wash", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3388.jpg?v=1678577003"}
]
prods = pd.DataFrame(product_data)

# -----------------------------
# Load and Process Reviews
# -----------------------------
reviews = pd.read_csv("reviews.csv")

product_name_map = {
    'ingrown-remedy-30ml': 'Ingrown Remedy',
    'body-oil-spray-150ml': 'Body Oil Spray',
    'bikini-area-blemish-butter-100ml': 'Blemish Butter',
    'bikini-area-mask': 'Bikini Area Mask',
    'intimate-toner': 'Intimate Toner',
    'salt-body-polish-250g': 'Salt Body Scrub',
    'intimate-wash': 'Intimate Wash'
}
reviews['product'] = reviews['product_handle'].map(product_name_map)

reviews_final = reviews.drop(columns=[
    'reply', 'reply_date', 'picture_urls', 'ip_address', 'metaobject_handle',
    'product_handle', 'source', 'curated', 'reviewer_email', 'product_id'
])

sia = SentimentIntensityAnalyzer()
reviews_final['sentiment'] = reviews_final['body'].apply(lambda x: sia.polarity_scores(str(x))['compound'])
avg_sentiment = reviews_final.groupby('product')['sentiment'].mean().reset_index()
prods = prods.merge(avg_sentiment, on='product', how='left')
prods['sentiment'] = prods['sentiment'].fillna(0.0)

# -----------------------------
# TF-IDF Vectorizer
# -----------------------------
prods['search_text'] = prods['concern'] + ' ' + prods['key_ingredient']
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(prods['search_text'])

# -----------------------------
# Concern Synonym Mapping
# -----------------------------
synonym_map = {
    'ingrowns': 'ingrown hairs',
    'dark spots': 'hyperpigmentation',
    'razor burn': 'razor bumps',
    'bikini bumps': 'razor bumps',
    'discoloration': 'discolouration',
    'uneven tone': 'hyperpigmentation',
    'dark area': 'hyperpigmentation',
    'dark inner thighs': 'hyperpigmentation'
}

known_concerns = [
    "ingrown hairs", "dark bikini area", "razor bumps", "redness", "irritation",
    "dark marks", "blemishes", "hyperpigmentation", "dry skin", "discolouration",
    "texture irregularities", "pH balance", "odour", "menstrual cramps",
    "exfoliation", "strawberry legs", "uneven tone", "itchiness"
]

def clean_input(text):
    for slang, standard in synonym_map.items():
        text = text.replace(slang, standard)
    return text

def extract_mapped_concerns(user_input, known_concerns, synonym_map):
    cleaned_input = clean_input(user_input.lower())
    return [c for c in known_concerns if c in cleaned_input]

def multi_concern_recommender(user_input, threshold=0.2):
    matched_concerns = extract_mapped_concerns(user_input, known_concerns, synonym_map)
    all_matches = pd.DataFrame()

    if not matched_concerns:
        return pd.DataFrame()

    for concern in matched_concerns:
        # Filter products that explicitly mention the concern
        filtered = prods[prods['concern'].str.contains(concern, case=False, na=False)].copy()

        if filtered.empty:
            continue

        # Compute similarity + sentiment score
        concern_vec = vectorizer.transform([concern])
        sim_scores = cosine_similarity(concern_vec, tfidf_matrix).flatten()
        similarity_scores = pd.Series(sim_scores, index=prods.index).loc[filtered.index]

        sentiment_scores = filtered['sentiment'].fillna(0.0)
        combined = similarity_scores + sentiment_scores * 0.3

        filtered['match_score'] = combined
        filtered['matched_concern'] = concern

        all_matches = pd.concat([all_matches, filtered], ignore_index=True)

    if all_matches.empty:
        return pd.DataFrame()

    all_matches = all_matches.drop_duplicates(subset='product')
    return all_matches.sort_values(by='match_score', ascending=False)
# -----------------------------
# User Input + Display Options
# -----------------------------
user_input = st.text_input("What skin concern would you like to address?")

if user_input:
    recommendations = multi_concern_recommender(user_input)

    st.subheader("Your Personalized Recommendations:")

    # Show products in a grid (3 per row)
    num_cols = 3
    rows = [recommendations[i:i+num_cols] for i in range(0, recommendations.shape[0], num_cols)]

    for row_chunk in rows:
        cols = st.columns(len(row_chunk))
        for col, (_, row) in zip(cols, row_chunk.iterrows()):
            with col:
                st.image(row['image'], use_column_width=True)
                st.markdown(f"**{row['product']}**")
                st.markdown(f"_Concern:_ {row['matched_concern']}")

                score = int((row['sentiment'] + 1) / 2 * 100)
                st.markdown(f"**Loved by SKNTONE customers:** {score}%")

# -----------------------------
# Visual Charts
# -----------------------------
st.subheader("Skin Concerns Covered by SKNTONE")
concerns = prods['concern'].str.split(',').explode().str.strip().value_counts()
fig1, ax1 = plt.subplots()
sns.barplot(x=concerns.index, y=concerns.values, ax=ax1, palette='viridis')
plt.xticks(rotation=45, ha='right')
st.pyplot(fig1)

st.subheader("Top Rated Products by Sentiment")
top_rated = prods[['product', 'sentiment']].sort_values(by='sentiment', ascending=False)
fig2, ax2 = plt.subplots()
ax2.bar(top_rated['product'], top_rated['sentiment'], color='lightgreen')
plt.xticks(rotation=45)
st.pyplot(fig2)
