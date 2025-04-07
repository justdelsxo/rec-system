# -*- coding: utf-8 -*-
"""Skntone product recommendation system

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-c0ZvZ_r8Kxi3kXweLbQJbpOKd1DwhPr
"""

#Customer Segmentation & Journey Mapping

import pandas as pd

# Dataset for Skntone's products
data = [
    {"product": "Ingrown Remedy", "concern": "ingrown hairs, razor bumps, redness, irritation", "key_ingredient": "Tea Tree Oil, Salicylic Acid", "product_type": "treatment"},
    {"product": "Blemish Butter", "concern": "blemishes, dark marks, hyperpigmentation", "key_ingredient": "Alpha Arbutin, Shea Butter, Licorice Root, Papaya Seed", "product_type": "cream"},
    {"product": "Bikini Area Mask", "concern": "blocked pores, blemishes, dark marks, hyperpigmentation, redness, dark marks", "key_ingredient": "Bentonite Clay, Turmeric, Aloe Vera", "product_type": "mask"},
    {"product": "Intimate Toner", "concern": "hyperpigmentation, blemishes, dark marks, texture irregularities, strawberry legs", "key_ingredient": "Glycolic Acid, Witch hazel, Aloe", "product_type": "toner"},
    {"product": "Body Oil Spray", "concern": "dry skin, sensitive skin", "key_ingredient": "Jojoba Oil, Oat Oil, Soya Bean Oil", "product_type": "oil"},
    {"product": "Salt Body Scrub", "concern": "rough skin, dry skin", "key_ingredient": "Dead Sea Salt, Himalayan Salt, Almond Oil", "product_type": "scrub"},
    {"product": "Intimate Wash", "concern": "unbalanced pH balance, intimate odour, menstrual cramps", "key_ingredient": "Aloe, Cranberry Extract, Lavender, Chamomile", "product_type": "wash"}
]

# Create a pandas DataFrame
prods = pd.DataFrame(data)

# Display the dataset
prods

import matplotlib.pyplot as plt
import seaborn as sns

# Visualise skin concerns per product
concerns = prods['concern'].str.split(',').explode().str.strip().value_counts()

# Plotting the distribution of skin concerns across products
plt.figure(figsize=(10, 6))
sns.barplot(x=concerns.index, y=concerns.values, hue=concerns.index, palette='viridis', legend=False)
plt.xticks(rotation=45, ha='right')
plt.title("Distribution of Skin Concerns Across Skntone Products")
plt.xlabel("Skin Concern")
plt.ylabel("Number of Products Addressing Concern")
plt.show()

# Visualise product types
product_types = prods['product_type'].value_counts()

# Plot the distribution of product types
plt.figure(figsize=(8, 6))
sns.barplot(x=product_types.index, y=product_types.values, hue=product_types.index, palette='Set2', legend=False)
plt.title("Distribution of Product Types in Skntone")
plt.xlabel("Product Type")
plt.ylabel("Number of Products")
plt.show()

# Get user input for skin concern
import streamlit as st

user_concern = st.text_input("What skin concern would you like to address? (e.g. ingrowns, hyperpigmentation, dark marks)").lower()

if user_concern:
    results = multi_concern_recommender(user_concern)
    st.markdown("### Here's what we recommend:")
    st.dataframe(results[['product', 'matched_concern', 'sentiment']])

# Filter the products based on the user’s concern
recommended_products = prods[prods['concern'].str.contains(user_concern)]

if not recommended_products.empty:
    print("Here's what we recommend based on your concerns:")
    print(recommended_products[['product', 'key_ingredient']])
else:
    print("No exact match found. Try entering other concerns.")

# help the system understand a variation of words that may be inputted

synonym_map = {
    'ingrowns': 'ingrown hairs',
    'dark spots': 'hyperpigmentation',
    'razor burn': 'razor bumps',
    'bikini bumps': 'razor bumps',
    'discoloration': 'discolouration',
    'uneven tone': 'hyperpigmentation',
    'dark area' : 'hyperpigmenation',
'dark inner thighs': 'hyperpigmentation'


}

def clean_input(text):
    for slang, standard in synonym_map.items():
        text = text.replace(slang, standard)
    return text

def recommend_products(user_input, top_n=3):
    user_input = user_input.lower()
    user_input = clean_input(user_input)

    user_vec = vectorizer.transform([user_input])
    similarity_scores = cosine_similarity(user_vec, tfidf_matrix).flatten()

    top_indices = similarity_scores.argsort()[::-1][:top_n]
    return prods.iloc[top_indices][['product', 'concern', 'key_ingredient']]

# Testing the system with fuzzy/slang input
user_input = "I need help with ingrowns and razor burn"
recommendations = recommend_products(user_input)

# Show results
print("Top Recommended Products:\n")
recommendations

"""Add reviews for further advancements"""

#Load reviews file
reviews=pd.read_csv("reviews.csv")
reviews

# Map product names to correlate with product recommendation system names

product_name_map = {
    'ingrown-remedy-30ml':'Ingrown Remedy',
    'body-oil-spray-150ml':'Body Oil Spray',
    'bikini-area-blemish-butter-100ml':'Blemish Butter',
    'bikini-area-mask':'Bikini Area Mask',
    'intimate-toner':'Intimate Toner',
    'salt-body-polish-250g':'Salt Body Scrub',
    'intimate-wash':'Intimate Wash'
}

# Create new column with standadised product names
reviews['product'] = reviews['product_handle'].map(product_name_map)

# drop unecessary columns
reviews_final = reviews.drop(columns=[
    'reply',
    'reply_date',
    'picture_urls',
    'ip_address',
    'metaobject_handle',
    'product_handle',
    'source',
    'curated',
    'reviewer_email',
    'product_id'
    ])
reviews_final

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

# Assign sentiment score using VADER
reviews_final['sentiment'] = reviews_final['body'].apply(lambda x: sia.polarity_scores(x)['compound'])

avg_sentiment = reviews_final.groupby('product')['sentiment'].mean().reset_index()

prods = prods.merge(avg_sentiment, on='product', how='left')
prods['sentiment'] = prods['sentiment'].fillna(0.0)  # fill products without reviews

from sklearn.metrics.pairwise import cosine_similarity

def recommend_products(user_input, top_n=3):
    user_input = user_input.lower()
    user_input = clean_input(user_input)  # including synonym map (slang and fuzzy words)

    user_vec = vectorizer.transform([user_input])
    similarity_scores = cosine_similarity(user_vec, tfidf_matrix).flatten()

    # Combine similarity score + sentiment
    combined_scores = similarity_scores + prods['sentiment'] * 0.3

    top_indices = combined_scores.argsort()[::-1][:top_n]
    return prods.iloc[top_indices][['product', 'concern', 'sentiment']]

import matplotlib.pyplot as plt

top_rated = prods[['product', 'sentiment']].sort_values(by='sentiment', ascending=False)

plt.figure(figsize=(10, 5))
plt.bar(top_rated['product'], top_rated['sentiment'], color='lightgreen')
plt.title("Top Rated Skntone Products by Review Sentiment")
plt.xticks(rotation=45)
plt.ylabel("Average Sentiment Score")
plt.tight_layout()
plt.show()

"""# Improve functionality by allowing multiple recommendations"""

# Create a known concerns list to try to cover all possibly inputs for Skntones products based on data from google analytics and shopify

known_concerns = [
    "ingrown hairs", "dark bikini area", "razor bumps", "redness", "irritation",
    "dark marks", "blemishes", "hyperpigmentation",
    "dry skin", "discolouration", "texture irregularities",
    "pH balance", "odour", "menstrual cramps",
    "exfoliation", "strawberry legs", "uneven tone", "itchiness"
]

from sklearn.metrics.pairwise import cosine_similarity

def extract_mapped_concerns(user_input, known_concerns, synonym_map):
    # Step 1: Replace slang with standard terms using your synonym map
    cleaned_input = user_input.lower()
    for slang, standard in synonym_map.items():
        cleaned_input = cleaned_input.replace(slang, standard)

    # Step 2: Match concerns
    matched = [c for c in known_concerns if c in cleaned_input]
    return matched

def multi_concern_recommender(user_input, threshold=0.2):
    matched_concerns = extract_mapped_concerns(user_input, known_concerns, synonym_map)
    all_matches = pd.DataFrame()

    for concern in matched_concerns:
        concern_vec = vectorizer.transform([concern])
        sim_scores = cosine_similarity(concern_vec, tfidf_matrix).flatten()

        # Combine with sentiment
        combined_scores = sim_scores + prods['sentiment'].fillna(0.0) * 0.3

        # Keep all products that are a good match
        matched_prods = prods[combined_scores > threshold].copy()
        matched_prods['match_score'] = combined_scores[combined_scores > threshold]
        matched_prods['matched_concern'] = concern

        all_matches = pd.concat([all_matches, matched_prods], ignore_index=True)

    # Remove duplicates (if multiple concerns lead to same product)
    all_matches = all_matches.drop_duplicates(subset='product')

    # Sort by match score
    all_matches = all_matches.sort_values(by='match_score', ascending=False)

    return all_matches[['product', 'matched_concern', 'concern', 'product_type', 'sentiment', 'match_score']]

multi_concern_recommender("I have ingrowns and dark inner thighs")
