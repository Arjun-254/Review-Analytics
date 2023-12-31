from google_play_scraper import app, Sort, reviews, reviews_all
import pandas as pd
import numpy as np
from datetime import date, datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import ngrams
from collections import Counter
import streamlit as st
import altair as alt
import joblib
import plotly.graph_objects as go
from func import analyze_reviews

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


st.markdown('<h1 style="font-size: 70px; color: #E3142D;"> Angel One </h1>',
            unsafe_allow_html=True)
st.markdown('<h1 style="font-size: 70px; color: #9347ED;">Customer Review Analytics</h1>',
            unsafe_allow_html=True)


# Set the cache expiry time to 24 hours
@st.cache_resource(ttl=86400)
def get_reviews():
    MAX_REVIEWS = 5000
    count = 200
    g_reviews = []
    continuation_token = None
    while len(g_reviews) < MAX_REVIEWS:
        reviews_batch, continuation_token = reviews(
            'com.msf.angelmobile',
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=count,
            continuation_token=continuation_token
        )
        g_reviews.extend(reviews_batch)
        if continuation_token is None:
            break

        # Adjust the remaining count based on the already scraped reviews
        remaining_reviews = MAX_REVIEWS - len(g_reviews)
        count = min(remaining_reviews, count)
    g_df = pd.DataFrame(np.array(g_reviews), columns=['review'])
    g_df2 = g_df.join(pd.DataFrame(g_df.pop('review').tolist()))

    g_df2.drop(columns={'userImage', 'reviewCreatedVersion'}, inplace=True)
    g_df2.rename(columns={'score': 'rating', 'userName': 'user_name', 'reviewId': 'review_id', 'content': 'review_description', 'at': 'review_date',
                          'replyContent': 'developer_response', 'repliedAt': 'developer_response_date', 'thumbsUpCount': 'thumbs_up'}, inplace=True)
    g_df2.insert(loc=0, column='source', value='Google Play')
    g_df2.insert(loc=3, column='review_title', value=None)

    df = g_df2

    df.drop('review_title', axis=1, inplace=True)
    df.drop('developer_response', axis=1, inplace=True)
    df.drop('developer_response_date', axis=1, inplace=True)
    return df


df = get_reviews()


stop_words = {'angel', 'one', 'please',
              'able', 'bank', 'app', 'good', 'nice', 'best'}
analyze_reviews(df, stop_words)
