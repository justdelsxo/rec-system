
    # -*- coding: utf-8 -*-
"""Skntone product recommendation system

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-c0ZvZ_r8Kxi3kXweLbQJbpOKd1DwhPr
"""
# Product recommendation system for skntone - Intimate body care

import streamlit as st
st.set_page_config(page_title="Product Recommendations", layout="centered")
st.markdown(
    """
    <style>
    /* Style the input box */
    div[data-baseweb="input"] > div {
        background-color: #f5f5f5 !important;
        border: 2px solid black !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }

    /* Style the user input text */
    input {
        color: black !important;
        font-size: 16px !important;
        font-family: 'Arial', sans-serif !important;
    }

    /* Style the placeholder (faded) text */
    input::placeholder {
        color: black !important;
        opacity: 0.6 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('vader_lexicon')


# Add a personalised touch by using the Skntone branded company logo
# Setting the background, text colours, font and positioning

st.markdown(
    """
    <style>
        .stApp {
            background-color: #ffffff;
            color: #000000;
        }
        body, div, p, h1, h2, h3, h4, h5 {
            color: #000000;
            font-family: Arial, sans-serif;
        }
        .css-18ni7ap, .css-1d391kg {
            background-color: #fad79c;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="text-align: center; padding-bottom: 6px;">
        <img src="https://cdn.shopify.com/s/files/1/0474/0661/2645/files/Skntone_coloured_logo_transparent.png?v=1650906263" alt="SKNTONE Logo" width="200">
    </div>
    """,
    unsafe_allow_html=True)

st.markdown(
    """
    <h1 style='text-align: center; color: black; font-family: Arial;'>✨Product Recommendations✨</h1>
    """,
    unsafe_allow_html=True
)
st.markdown("Tell me what your skin’s going through — I’ll show you what’s worked for girls just like you.")

# Heres where i have listed all the products sold by skntone, the key concerns and ingredients for each product and the product pictures
# This is the foundation of what powers the recommendation system

product_data = [
    {"product": "Ingrown Remedy", "concern": "ingrown hairs, razor bumps, redness, irritation", "key_ingredient": "Tea Tree Oil, Salicylic Acid", "product_type": "treatment", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3339.jpg?v=1678575718"},
    {"product": "Blemish Butter", "concern": "blemishes, dark marks, hyperpigmentation", "key_ingredient": "Alpha Arbutin, Shea Butter, Licorice Root, Papaya Seed", "product_type": "cream", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3329.jpg?v=1678576957"},
    {"product": "Bikini Area Mask", "concern": "blocked pores, dark marks, hyperpigmentation, redness", "key_ingredient": "Bentonite Clay, Turmeric, Aloe Vera", "product_type": "mask", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3357.jpg?v=1678575811"},
    {"product": "Intimate Toner", "concern": "hyperpigmentation, dark marks, texture irregularities, strawberry legs", "key_ingredient": "Glycolic Acid, Witch hazel, Aloe", "product_type": "toner", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3351.jpg?v=1678577474"},
    {"product": "Body Oil Spray", "concern": "dry skin, sensitive skin", "key_ingredient": "Jojoba Oil, Oat Oil, Soya Bean Oil", "product_type": "oil", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3364_db661095-455c-4c85-ad0f-e7515452b832.jpg?v=1678575843"},
    {"product": "Salt Body Scrub", "concern": "rough skin, flakey skin", "key_ingredient": "Dead Sea Salt, Himalayan Salt, Almond Oil", "product_type": "scrub", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3366.jpg?v=1678575911"},
    {"product": "Intimate Wash", "concern": "unbalanced pH balance, intimate odour, menstrual cramps", "key_ingredient": "Aloe, Cranberry Extract, Lavender, Chamomile", "product_type": "wash", "image": "https://cdn.shopify.com/s/files/1/0474/0661/2645/products/IMG_3388.jpg?v=1678577003"}
]
prods = pd.DataFrame(product_data)

# Lets bring in our customer reviews so we can see what paying customers have said about each product
# Iv cleaned the data, linked each review to its product and used sentiment analysis to score how pisitive the reviews are.
# This helps recommend products that not only match conerncs but are rated highly by customers.

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

# Turning the product information (concerns and ingredients) into something the system can understand. 
# Helping understand which products are similar to what somesones looking for based on keywords

prods['search_text'] = prods['concern'] + ' ' + prods['key_ingredient']
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(prods['search_text'])

#People describe skin concerns in different ways, so this section helps the system understand common slan or variations
# for example, if someone says ingrowns instead of ingrown hairs, itll still be recognised.

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
        filtered = prods[prods['concern'].str.contains(concern, case=False, na=False)].copy()
        if filtered.empty:
            continue

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

#This is where users tell me what their skin concerns are 
#Based on the input, well recommend products thatll help with those concerns

# Custom prompt above the input box
st.markdown("**What do you want help with?**")

# Input box with faded placeholder text
user_input = st.text_input(
    label="",
    placeholder="ingrowns, dry skin, dark marks?",
)

if user_input:
    recommendations = multi_concern_recommender(user_input)

    if not recommendations.empty:
        st.subheader("For this, I recommend either one or a combination of the following products:")

        num_cols = 3
        rows = [recommendations[i:i+num_cols] for i in range(0, recommendations.shape[0], num_cols)]

        for row_chunk in rows:
            cols = st.columns(len(row_chunk))
            for col, (_, row) in zip(cols, row_chunk.iterrows()):
                with col:
                    st.image(row['image'], use_container_width=True)
                    st.markdown(f"**{row['product']}**")
                    st.markdown(f"_Concern:_ {row['matched_concern']}")
                    score = int((row['sentiment'] + 1) / 2 * 100)
                    st.markdown(f"**{score}% of customers with the same concern bought this**")
    else:
        st.warning("Hmm, I couldn’t find an exact match. Try different wording or concerns!")
