# -*- coding: utf-8 -*-
"""Skntone product recommendation system

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-c0ZvZ_r8Kxi3kXweLbQJbpOKd1DwhPr
"""
# SKNTONE Product Recommender Streamlit App

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
# Load Product Data
# -----------------------------
product_data = [
    {"product": "Ingrown Remedy", "concern": "ingrown hairs, razor bumps, redness, irritation", "key_ingredient": "Tea Tree Oil, Salicylic Acid", "product_type": "treatment"},
    {"product": "Blemish Butter", "concern": "blemishes, dark marks, hyperpigmentation", "key_ingredient": "Alpha Arbutin, Shea Butter, Licorice Root, Papaya Seed", "product_type": "cream"},
    {"product": "Bikini Area Mask", "concern": "blocked pores, blemishes, dark marks, hyperpigmentation, redness", "key_ingredient": "Bentonite Clay, Turmeric, Aloe Vera", "product_type": "mask"},
    {"product": "Intimate Toner", "concern": "hyperpigmentation, blemishes, dark marks, texture irregularities, strawberry legs", "key_ingredient": "Glycolic Acid, Witch hazel, Aloe", "product_type": "toner"},
    {"product": "Body Oil Spray", "concern": "dry skin, sensitive skin", "key_ingredient": "Jojoba Oil, Oat Oil, Soya Bean Oil", "product_type": "oil"},
    {"product": "Salt Body Scrub", "concern": "rough skin, dry skin", "key_ingredient": "Dead Sea Salt, Himalayan Salt, Almond Oil", "product_type": "scrub"},
    {"product": "Intimate Wash", "concern": "unbalanced pH balance, intimate odour, menstrual cramps", "key_ingredient": "Aloe, Cranberry Extract, Lavender, Chamomile", "product_type": "wash"}
]
prods = pd.DataFrame(product_data)

# -----------------------------
# Load and Clean Reviews
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

# -----------------------------
# Sentiment Analysis
# -----------------------------
sia = SentimentIntensityAnalyzer()
reviews_final['sentiment'] = reviews_final['body'].apply(lambda x: sia.polarity_scores(str(x))['compound'])
avg_sentiment = reviews_final.groupby('product')['sentiment'].mean().reset_index()
prods = prods.merge(avg_sentiment, on='product', how='left')
prods['sentiment'] = prods['sentiment'].fillna(0.0)

# -----------------------------
# TF-IDF Vectorization
# -----------------------------
prods['search_text'] = prods['concern'] + ' ' + prods['key_ingredient']
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(prods['search_text'])

# -----------------------------
# Synonyms & Fuzzy Mapping
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
    matched = [c for c in known_concerns if c in cleaned_input]
    return matched

def multi_concern_recommender(user_input, threshold=0.2):
    matched_concerns = extract_mapped_concerns(user_input, known_concerns, synonym_map)
    all_matches = pd.DataFrame()

    for concern in matched_concerns:
        concern_vec = vectorizer.transform([concern])
        sim_scores = cosine_similarity(concern_vec, tfidf_matrix).flatten()
        combined_scores = sim_scores + prods['sentiment'] * 0.3

        matched_prods = prods[combined_scores > threshold].copy()
        matched_prods['match_score'] = combined_scores[combined_scores > threshold]
        matched_prods['matched_concern'] = concern
        all_matches = pd.concat([all_matches, matched_prods], ignore_index=True)

    all_matches = all_matches.drop_duplicates(subset='product')
    all_matches = all_matches.sort_values(by='match_score', ascending=False)

    return all_matches[['product', 'matched_concern', 'concern', 'product_type', 'sentiment', 'match_score']]

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="SKNTONE Recommender", layout="centered")

st.title("SKNTONE Product Recommendation System")
st.markdown("Tell us your skin concerns and we’ll recommend the best product(s) for you.")

user_input = st.text_input("Enter your skin concerns (e.g. ingrowns, dark marks, dry skin)")

if user_input:
    recommendations = multi_concern_recommender(user_input)
    st.subheader("Recommended Products for You:")
    for index, row in recommendations.iterrows():
    st.markdown(f"""
    **{row['product']}**
    - Concern: _{row['matched_concern']}_
    - Sentiment Score: `{round(row['sentiment'], 2)}`
    """)

# -----------------------------
# Optional Charts
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
